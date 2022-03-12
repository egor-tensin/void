#!/usr/bin/env python3

# Copyright (c) 2022 Egor Tensin <Egor.Tensin@gmail.com>
# This file is part of the "void" project.
# For details, see https://github.com/egor-tensin/void.
# Distributed under the MIT License.

import argparse
import cgi
from enum import Enum
import http.server
import os
import sys
from threading import Lock


class Response:
    DEFAULT_STATUS = http.server.HTTPStatus.OK

    def __init__(self, body, status=None):
        if status is None:
            status = Response.DEFAULT_STATUS
        self.status = status
        self.body = body

    def headers(self):
        yield 'Content-Type', 'text/html; charset=utf-8'

    def encode_body(self):
        return self.body.encode(errors='replace')

    def write_as_cgi_script(self):
        self.write_headers_as_cgi_script()
        self.write_body_as_cgi_script()

    def write_headers_as_cgi_script(self):
        for name, val in self.headers():
            print(f'{name}: {val}')
        print()

    def write_body_as_cgi_script(self):
        if self.body is not None:
            print(self.body)

    def write_to_request_handler(self, handler):
        handler.send_response(self.status)
        self.write_headers_to_request_handler(handler)
        self.write_body_to_request_handler(handler)

    def write_headers_to_request_handler(self, handler):
        for name, val in self.headers():
            handler.send_header(name, val)
        handler.end_headers()

    def write_body_to_request_handler(self, handler):
        if self.body is not None:
            handler.wfile.write(self.encode_body())


class Void:
    def __init__(self, backup_path):
        self.lck = Lock()
        self.cnt = 0
        self.backup_path = backup_path
        if backup_path is not None:
            self.backup_path = os.path.abspath(backup_path)

    def __enter__(self):
        if self.backup_path is not None and os.path.exists(self.backup_path):
            self.restore(self.backup_path)
        return self

    def __exit__(self, type, value, traceback):
        if self.backup_path is not None:
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            self.save(self.backup_path)

    def write(self, fd):
        with self.lck:
            cnt = self.cnt
        fd.write(str(cnt))

    def read(self, fd):
        src = fd.read()
        cnt = int(src)
        with self.lck:
            self.cnt = cnt

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as fd:
            self.write(fd)

    def restore(self, path):
        with open(path, encoding='utf-8') as fd:
            self.read(fd)

    def scream_once(self):
        with self.lck:
            self.cnt += 1
            cnt = self.cnt
        return Response(str(cnt))

    def get_numof_screams(self):
        with self.lck:
            cnt = self.cnt
        return Response(str(cnt))


class Request(Enum):
    SCREAM_ONCE = 'scream'
    HOW_MANY_SCREAMS = 'screams'

    def __str__(self):
        return self.value

    @staticmethod
    def from_http_path(path):
        if not path or path[0] != '/':
            raise ValueError('HTTP path must start with a forward slash /')
        return Request(path[1:])

    def process(self, void):
        if self is Request.SCREAM_ONCE:
            return void.scream_once()
        if self is Request.HOW_MANY_SCREAMS:
            return void.get_numof_screams()
        raise NotImplementedError(f'unknown request: {self}')


def process_cgi_request(void):
    params = cgi.FieldStorage()
    what = params['what'].value
    Request(what).process(void).write_as_cgi_script()


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--void', metavar='PATH', dest='backup',
                        help='set path to the void')
    return parser.parse_args(args)


def main(args=None):
    args = parse_args(args)
    with Void(args.backup) as void:
        process_cgi_request(void)


if __name__ == '__main__':
    main()
