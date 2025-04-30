FROM alpine

ARG DATA_TRANSFORMER_PORT
ENV SERVER_PORT="0.0.0.0:$DATA_TRANSFORMER_PORT"

WORKDIR /app

COPY . .

RUN apk add --update py3-pip

RUN apk add --update py3-setuptools

RUN pip3 install -r requirements.txt  --break-system-packages --no-cache-dir

EXPOSE $DATA_TRANSFORMER_PORT

CMD ["gunicorn", "-k", "gevent", "--bind", "${SERVER_PORT}", "data_transformer:app"] 
