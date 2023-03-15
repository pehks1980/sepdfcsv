FROM python:3.9.6-alpine
# set environment variables
ENV PYTHONDONTWRITEBYTECODE TRUE
ENV PYTHONUNBUFFERED TRUE

# install dependencies
RUN apk update && apk add zlib-dev jpeg-dev gcc musl-dev libffi-dev
RUN pip install --upgrade pip
RUN apk --update add gcc build-base freetype-dev libpng-dev openblas-dev
RUN pip install --no-cache-dir matplotlib pandas numpy

#RUN pip install wheel
COPY ./requirements.txt .
COPY ./gunicorn.sh .
RUN pip install -r requirements.txt

COPY ./main /main
#WORKDIR /main
RUN chmod +x /gunicorn.sh
EXPOSE 8080
ENTRYPOINT ["./gunicorn.sh"]
