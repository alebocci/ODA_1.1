FROM python:3.11-slim
# imposto la workdir e ci copio tutti i file
WORKDIR /app
COPY . .
# Installo le dipendenze
RUN pip3 install -r requirements.txt  --break-system-packages --no-cache-dir
# espongo la porta all'esterno del container
EXPOSE 50100 
# setto la variabile d'ambiente per flask
ENV FLASK_APP=web_data_transformer.py  
# avvio l'app Flask
CMD ["gunicorn", "--bind", "0.0.0.0:50100", "web_data_transformer:app"]