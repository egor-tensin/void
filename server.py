#!/usr/bin/env python3

# Copyright (c) 2022 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "void" project.
# For details, see https://github.com/egor-tensin/void.
# Distributed under the MIT License.

import argparse
from contextlib import contextmanager
import http.server
import os
import signal
import sys
from threading import Condition, Lock, Thread
import traceback

from app import Request, Response, Void


DEFAULT_PORT = 23666
EXITING = False


def script_dir():
    return os.path.dirname(os.path.realpath(__file__))


def set_exiting():
    global EXITING
    with SignalHandler.LOCK:
        EXITING = True
        SignalHandler.CV.notify()


class SignalHandler:
    LOCK = Lock()
    CV = Condition(LOCK)

    def __init__(self, httpd):
        self.httpd = httpd
        self.thread = Thread(target=self.run)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, type, value, traceback):
        self.thread.join()

    def run(self):
        with SignalHandler.CV:
            while not EXITING:
                SignalHandler.CV.wait()
            self.httpd.shutdown()


def handle_sigterm(signum, frame):
    print('\nSIGTERM received, exiting...')
    set_exiting()


def handle_sigint():
    print('\nKeyboard interrupt received, exiting...')
    set_exiting()


@contextmanager
def setup_signal_handlers(httpd):
    handler_thread = SignalHandler(httpd)
    with handler_thread:
        signal.signal(signal.SIGTERM, handle_sigterm)
        yield
        # TODO: cleanup signal handlers?


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    VOID = None

    def address_string(self):
        if 'x-forwarded-for' in self.headers:
            return self.headers['x-forwarded-for'].split(',')[0].strip()
        if 'x-real-ip' in self.headers:
            return self.headers['x-real-ip']
        return super().address_string()

    def do_GET(self):
        try:
            request = Request.from_http_path(self.path)
        except ValueError:
            return super().do_GET()
        try:
            response = request.process(RequestHandler.VOID)
            response.write_to_request_handler(self)
        except:
            status = http.server.HTTPStatus.INTERNAL_SERVER_ERROR
            response = Response(traceback.format_exc(), status)
            response.write_to_request_handler(self)
            return


def make_server(port):
    addr = ('', port)
    server = http.server.HTTPServer
    if sys.version_info >= (3, 7):
        server = http.server.ThreadingHTTPServer
    return server(addr, RequestHandler)


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT',
                        type=int, default=DEFAULT_PORT,
                        help='set port number')
    parser.add_argument('-v', '--void', metavar='PATH', dest='backup',
                        help='set path to the void')
    return parser.parse_args(args)


def main(args=None):
    # It's a failsafe; this script is only allowed to serve the directory it
    # resides in.
    os.chdir(script_dir())

    args = parse_args(args)
    with Void(args.backup) as void:
        RequestHandler.VOID = void
        httpd = make_server(args.port)
        with setup_signal_handlers(httpd):
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                handle_sigint()


if __name__ == '__main__':
    main()
