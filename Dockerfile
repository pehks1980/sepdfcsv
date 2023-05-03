FROM python:3.9.6-alpine
# set environment variables
ENV PYTHONDONTWRITEBYTECODE TRUE
ENV PYTHONUNBUFFERED TRUE
# Install Memcached
RUN apk update && apk add memcached
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
COPY ./gunicorn.sh .
RUN chmod +x /gunicorn.sh
#RUN useradd -u 1001 user
#user needed to run memcached inside container
RUN adduser -D -g '' user
EXPOSE 8080
ENTRYPOINT ["./gunicorn.sh"]