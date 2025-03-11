from confluent_kafka import Producer
import json, random, time, requests, sys, logging
from datetime import datetime, timezone, timedelta

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Configurazione del generatore
API_GATEWAY_URL = "http://127.0.0.1:50005"  
INTERVAL_SECONDS = 30  
TOPIC = "BuildingConsumption"  
GENERATOR_ID = "gen_test1"  
MAPPING_NAME = ["test1_to_polimi", "test1_to_scp", "testCloneScp"]  

def register_to_api_gateway():
    try:
        logging.info("Registrazione all'API Gateway...")
        msg = {"topics": [TOPIC]}
        logging.info(f"Registrazione topic: {msg}")
        response = requests.post(API_GATEWAY_URL + '/register/dg', json=msg)
        response.raise_for_status()
        data = response.json()
        kafka_endpoint = data["KAFKA_ENDPOINT"]
        logging.info(f"Ottenuto KAFKA_ENDPOINT: {kafka_endpoint}")
        return kafka_endpoint
    except Exception as e:
        logging.error(f"Errore durante la registrazione: {repr(e)}")
        # Se la registrazione fallisce, usa un endpoint predefinito
        return "localhost:9092"
    
# funzinone per collegare il mapping al DG con generator_id e topic
def link_mapping():
    try:
        payload = {
            "topic": TOPIC,
            "generator_id": GENERATOR_ID
        }
        for mapping in MAPPING_NAME:
            logging.info(f"Collegamento del mapping {MAPPING_NAME} al generatore {GENERATOR_ID} e al topic {TOPIC}...")
            response = requests.post(f"{API_GATEWAY_URL}/linkMapping/{mapping}", json=payload)
            response.raise_for_status()
            logging.info(f"Mapping {MAPPING_NAME} collegato con successo.")
    except Exception as e:
        logging.error(f"Errore durante il collegamento del mapping: {repr(e)}")

# funzione per generare dati casuali
def generate_random_data():
    buildings = [
        {"id": "B001", "name": "Palazzo A"},
        {"id": "B002", "name": "Palazzo B"},
        {"id": "B003", "name": "Palazzo C"},
        {"id": "B004", "name": "Palazzo D"},
        {"id": "B005", "name": "Palazzo E"},
        {"id": "B006", "name": "Palazzo F"},
        {"id": "B007", "name": "Palazzo G"},
        {"id": "B008", "name": "Palazzo H"},
        {"id": "B009", "name": "Palazzo I"},
        {"id": "B010", "name": "Palazzo J"}
    ]
    # Seleziona un edificio casuale
    building = random.choice(buildings)
    # Genera un periodo di tempo per period
    now = datetime.now(timezone.utc)
    end_time = now
    start_time = end_time - timedelta(hours=1)
    # Genera consumo casuale tra 50 e 500 kWh
    consumi = round(random.uniform(50, 500), 2)
    # creo il formato dei dati delo schema di input
    data ={
        "consumi": consumi,
        "inizio": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fine": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "buildingId": building["id"],
        "buildingName": building["name"]
    }
    return str(data).replace("'", "\"")

# funzione per creare il pacchetto completo da inviare ad ODA
def create_packet(data):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # impacchetto i dati nel formato per ODA
    packet = {
        "timestamp": timestamp,
        "generator_id": GENERATOR_ID,
        "topic": TOPIC,
        "data": data
    }
    return packet

# funzione per la consegna del messaggio (callBack)
def delivery_report(err, msg):
    if err is not None:
        logging.info(f'Errore nella consegna del messaggio: {err}')
    else:
        value = msg.value().decode('utf-8')
        logging.info(f'Messaggio consegnato a {msg.topic()}: {value}')

# funzione principale del generatore
def run_generator():
    # Registrazione e connessione a Kafka
    kafka_endpoint = register_to_api_gateway()
    producer = Producer({'bootstrap.servers': kafka_endpoint})
    logging.info(f"Connesso a Kafka: {kafka_endpoint}")
    # Collega il mapping al generatore e al topic
    #link_mapping()
    # Ciclo principale di generazione dati
    message_count = 0
    try:
        while True:
            message_count += 1
            # Genera dati casuali
            data = generate_random_data()
            # Crea il pacchetto completo
            packet = create_packet(data)
            # Converti in JSON e invia
            json_data = json.dumps(packet, indent=4)
            logging.info(f"Invio messaggio #{message_count} sul topic {TOPIC}...")
            producer.produce(packet["topic"], json_data.encode('utf-8'), callback=delivery_report)
            producer.flush()
            # Attendi il prossimo intervallo
            logging.info(f"In attesa per {INTERVAL_SECONDS} secondi...")
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Generatore interrotto dall'utente")
    except Exception as e:
        logging.error(f"Errore durante l'esecuzione: {repr(e)}")


# Esecuzione del generatore
if __name__ == "__main__":
    logging.info(f"Avvio generatore dati consumi con intervallo di {INTERVAL_SECONDS} secondi")
    run_generator()