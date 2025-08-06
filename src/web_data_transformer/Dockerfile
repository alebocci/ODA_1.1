FROM alpine

ARG WEB_DATA_TRANSFORMER_PORT
ENV SERVER_PORT="0.0.0.0:$WEB_DATA_TRANSFORMER_PORT"

WORKDIR /app

COPY . .

RUN apk add --update py3-pip

RUN apk add --update py3-setuptools

RUN pip3 install -r requirements.txt  --break-system-packages --no-cache-dir

EXPOSE $WEB_DATA_TRANSFORMER_PORT

CMD ["sh", "-c", "gunicorn -k gevent --bind ${SERVER_PORT} web_data_transformer:app"]