FROM python:3.11-slim
# imposto la workdir e ci copio tutti i file
WORKDIR /app
COPY . .
# Installo le dipendenze
RUN pip3 install -r requirements.txt  --break-system-packages --no-cache-dir
# espongo la porta all'esterno del container
EXPOSE 50007
# Comando per eseguire l'applicazione Flask
CMD ["python3", "data_transformer.py"]