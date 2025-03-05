from confluent_kafka import Producer
import json, random, time, requests, sys, logging
from datetime import datetime, timezone
from argparse import ArgumentParser

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Parse command-line arguments
parser = ArgumentParser(prog='ODA_Schema_Generator.py',
                    description='Data Generator for ODA service with schemaInputArray.json format.')

parser.add_argument('--number_of_msg', '-n', type=int, help='Set the number of messages to send, default: 1', default=1)
parser.add_argument('--registered', '-r', help='Set the Kafka endpoint if registered previously')
parser.add_argument('--apigateway', '-a', help='Set the API Gateway URL, default: http://127.0.0.1:50005', default="http://127.0.0.1:50005")
parser.add_argument('--timeout', '-t', type=int, help='Set the sending packet timeout in seconds, default: 0', default=0)

args = parser.parse_args()

# Initialize variables from command-line arguments
_TIMEOUT_MSGS = int(args.timeout)
registered = args.registered
API_GATEWAY_URL = args.apigateway
n_msg = int(args.number_of_msg)

# Fixed generator_id and topic
generator_id = "prova_ODA_transform"
topic = "topic_prova_transform_1"

# Check if the Kafka endpoint is provided as an argument otherwise register to the API Gateway
if registered:
    KAFKA_ENDPOINT = registered
else:
    try:
        logging.info("Registering to API Gateway...")
        msg = {"topics": [topic]}
        logging.info(f"Registering topics: {msg}")
        x = requests.post(API_GATEWAY_URL + f'/register/dg', json=msg)
        x.raise_for_status()
        msg = x.json()
        KAFKA_ENDPOINT = msg["KAFKA_ENDPOINT"]
        logging.info(f"Obtained KAFKA_ENDPOINT: {KAFKA_ENDPOINT}")
    except Exception as e:
        logging.info(repr(e))
        exit(1)

# Generate random data in the format of schemaInputArray.json
def generate_data():
    building_id = f"building_{random.randint(1, 100)}"
    n_of_floors = random.randint(1, 10)
    building_name = f"Building {random.randint(1, 100)}"
    rooms = []
    for _ in range(random.randint(1, 2)):
        room = {
            "area": round(random.uniform(20.0, 100.0), 2),
            "nOfPeople": random.randint(1, 10),
            "floor": random.randint(1, n_of_floors),
            "roomId": random.randint(1, 100)
        }
        rooms.append(room)
    electric_consumption = round(random.uniform(100.0, 1000.0), 2)
    period = {
        "start_ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end_ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    data = {
        "buildingId": building_id,
        "nOfFloors": n_of_floors,
        "buildingName": building_name,
        "rooms": rooms,
        "electricConsumption": electric_consumption,
        "period": period
    }
    return str(data).replace("'", "\"") # Convert to string and replace single quotes with double quotes to make it valid JSON

# Create a packet with the data to send
def create_packet(timestamp, generator_id, topic, data):
    if not timestamp:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    packet = {
        "timestamp": timestamp,
        "generator_id": generator_id,
        "topic": topic,
        "data": data
    }
    return packet

# Delivery report callback after the message has been delivered to Kafka
def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logging.info('Message delivery failed: {}'.format(err))
    else:
        value = msg.value().decode('utf-8')
        logging.info(f'Message delivered to {msg.topic()}: {value}')

# Initialize the Kafka producer
p = Producer({'bootstrap.servers': KAFKA_ENDPOINT})
logging.info("Connected to Kafka")

# Send the messages
for i in range(1, n_msg + 1):
    time.sleep(_TIMEOUT_MSGS)

    p.poll(0)
    data = generate_data()
    packet = create_packet(None, generator_id, topic, data)
    toSend = json.dumps(packet, indent=4)
    logging.info(f'Sending message n {i}...')
    p.produce(packet["topic"], toSend.encode('utf-8'), callback=delivery_report)
    p.flush()