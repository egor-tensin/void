FROM alpine:3.15

RUN apk add --no-cache python3
RUN mkdir -p /var/lib/void

COPY [".", "/usr/src/"]
WORKDIR /usr/src

# I don't know why, but in Docker, simple print() statements show nothing:
# https://stackoverflow.com/q/29663459
# Fixed by adding the -u flag:
CMD ["python3", "-u", "./server.py", "--void", "/var/lib/void/void.state"]
