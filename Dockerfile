FROM alpine:3.15

RUN apk add --no-cache python3 tini
RUN mkdir -p /var/lib/void

COPY [".", "/usr/src/"]
WORKDIR /usr/src

ENTRYPOINT ["/sbin/tini", "--"]
CMD ./server.py --void /var/lib/void/void.state
