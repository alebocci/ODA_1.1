FROM python:3.8-slim-buster
# imposto la workdir e ci copio tutti i file
WORKDIR /app
COPY . .
# Installo le dipendenze
RUN pip3 install -r requirements.txt  --break-system-packages --no-cache-dir
# espongo la porta all'esterno del container
EXPOSE 5000 
# setto la variabile d'ambiente per flask
ENV FLASK_APP=data_transformer.py  
# avvio l'app Flask
CMD ["flask", "run", "--host=0.0.0.0"]