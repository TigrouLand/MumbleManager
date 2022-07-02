FROM python:3.10.5-alpine3.16

WORKDIR /app

COPY . .

RUN apk add build-base openssl-dev bzip2-dev && \
    rm -rf /var/cache/apk/*

RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]