# The cgi module was removed in 3.13.
FROM python:3.12-alpine

RUN mkdir -p /var/lib/void

COPY [".", "/usr/src/"]
WORKDIR /usr/src

# I don't know why, but in Docker, simple print() statements show nothing:
# https://stackoverflow.com/q/29663459
# Fixed by adding the -u flag:
CMD ["python3", "-u", "./server.py", "--void", "/var/lib/void/void.state"]
