from confluent_kafka import Consumer, KafkaException
import json, requests, logging, sys, uuid
from time import sleep

# Configurazione di base per il consumer Kafka
AUTO_OFFSET_RESET = 'earliest'  # Per ricevere tutti i messaggi memorizzati in Kafka
AUTO_COMMIT_INTERVAL_MS = '1000'  # Per commitare l'offset ogni secondo

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# URL dell'API Gateway predefinito
API_GATEWAY_URL = "http://127.0.0.1:50005"

# Genera un group_id univoco per il consumer
GROUP_ID = str(uuid.uuid4())
logging.info(f"The consumer group id is: {GROUP_ID}")

# Funzione per ottenere l'endpoint Kafka e i topic disponibili da ODA
def get_kafka_endpoint_and_topics():
    try:
        logging.info("Registering to API Gateway...")
        response = requests.get(API_GATEWAY_URL + '/register/dc')
        response.raise_for_status()
        data = response.json()
        kafka_endpoint = data["KAFKA_ENDPOINT"]
        topics = data["topics"]
        logging.info(f"Obtained KAFKA_ENDPOINT: {kafka_endpoint}")
        logging.info(f"Obtained topics: {topics}")
        return kafka_endpoint, topics
    except Exception as e:
        logging.error(f"Failed to register to API Gateway: {repr(e)}")
        exit(1)

# Ottieni l'endpoint Kafka e i topic
KAFKA_ENDPOINT, topics = get_kafka_endpoint_and_topics()

# Inizializza il consumer Kafka
logging.info("Initializing consumer...")
consumer = Consumer({
    'bootstrap.servers': KAFKA_ENDPOINT,
    'group.id': GROUP_ID,
    'auto.offset.reset': AUTO_OFFSET_RESET,
    'auto.commit.interval.ms': AUTO_COMMIT_INTERVAL_MS
})

# Sottoscrizione a tutti i topic disponibili
try:
    logging.info(f"Subscribing to all topics: {topics}")
    consumer.subscribe(topics)
except KafkaException as ke:
    logging.error(f"KafkaException: {repr(ke)}")
    exit(1)

# Avvio del polling per ricevere i messaggi
logging.info("Starting polling from Kafka...")
while True:
    sleep(1)  # Timeout di 1 secondo tra un poll e l'altro
    msg = consumer.poll(1.0)  # Polling con timeout di 1 secondo
    if msg is None:
        continue
    if msg.error():
        logging.error(f"Message error: {msg.error()}")
        continue
    try:
        # Decodifica e stampa il messaggio ricevuto
        message_value = msg.value().decode('utf-8')
        logging.info("Received message:")
        logging.info(json.loads(message_value))
    except Exception as e:
        logging.error(f'Exception: {repr(e)}')