#!/bin/sh
if [ "$1" = "-v" ]; then
    docker volume rm oda_influxdbdata
    docker volume rm oda_influxdbconfig
    docker volume rm oda_mysqldata
fi

if docker image ls | grep -q oda-topicmanager; then
    docker image rm -f oda-topicmanager
fi

if docker image ls | grep -q oda-datapump; then
    docker image rm -f oda-datapump
fi

if docker image ls | grep -q oda-dbmanager; then
    docker image rm -f oda-dbmanager
fi

if docker image ls | grep -q oda-apigateway; then
    docker image rm -f oda-apigateway
fi

if docker image ls | grep -q influxdb; then
    docker image rm -f influxdb:2.7
fi

if docker image ls | grep -q alebocci/odakafka; then
    docker image rm -f alebocci/odakafka
fi

if docker image ls | grep -q oda-data_transformer; then
    docker image rm -f oda-data_transformer
fi

if docker image ls | grep -q oda-web_data_transformer; then
    docker image rm -f oda-web_data_transformer
fi

if docker image ls | grep -q mysql; then
    docker image rm -f mysql:5.7 
fi