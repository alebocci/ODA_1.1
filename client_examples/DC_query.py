import gzip
from io import BytesIO
import json
import logging
import requests


# Configurazione del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL dell'API
url = "http://localhost:50005/query"

# Parametri di default per la query
TOPIC = "BuildingConsumption"
GENERATOR_ID = "gen_test1"
DEST_FORMAT = ['POLIMI', 'SCP']
HEADERS = {"Content-Type": "application/json"}

def send_post_request(url, payload):
    try:
        response = requests.post(url, json=payload, headers=HEADERS)
        response.raise_for_status()
        logger.info(f"Risposta:")
        print(json.dumps(response.json(), indent=4))
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante la richiesta POST: {e}")


def main():
    try:
        # Costruisci il payload della query
        payload = {
            "topic": TOPIC,
            "generator_id": GENERATOR_ID,
        }
        logger.info("Invio della query...")
        # Invia la richiesta POST per la query classica
        send_post_request(url, payload)
        for destFormat in DEST_FORMAT:
            logger.info(f"Invio della query con trasformazione in formato {destFormat}...")
            # Invia la richiesta POST per la query con trasformazione
            send_post_request(url + "?transform=" + destFormat, payload)
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}")



if __name__ == "__main__":
    main()