#build cache-serv go

FROM golang:1.21 as modules
ADD ./main/cache-serv/go.mod ./main/cache-serv/go.sum /m/
RUN cd /m && go mod download

FROM golang:1.21 as builder
COPY --from=modules /go/pkg /go/pkg
RUN mkdir -p /cache-serv

COPY ./main/cache-serv /cache-serv

WORKDIR /cache-serv
# Собираем бинарный файл GOARCH=arm64 pi | amd64 x86
# main - это результирующий exe файл в корне билдера
RUN GOOS=linux GOARCH=arm64 CGO_ENABLED=0 \
   go build -o /main ./cmd/cache-serv


FROM python:3.9.6-alpine
# set environment variables
ENV PYTHONDONTWRITEBYTECODE TRUE
ENV PYTHONUNBUFFERED TRUE
# Install Memcached
RUN apk update #&& apk add memcached
# install dependencies
RUN apk update && apk add zlib-dev jpeg-dev gcc musl-dev libffi-dev
RUN pip install --upgrade pip
RUN apk --update add gcc build-base freetype-dev libpng-dev openblas-dev
RUN pip install --no-cache-dir matplotlib pandas numpy

#RUN pip install wheel
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./main /main
#WORKDIR /main


RUN mkdir -p /cache-serv
COPY --from=builder /main /cache-serv/main

COPY ./gunicorn.sh .
RUN chmod +x /gunicorn.sh
#RUN useradd -u 1001 user
#user needed to run memcached inside container
RUN adduser -D -g '' user
EXPOSE 8080
# Set Flask secret key as environment variable
ENV FLASK_SECRET_KEY=$FLASK_SECRET_KEY
ENTRYPOINT ["./gunicorn.sh"]