from flask import Flask, redirect, request, make_response, jsonify
import logging, sys, os, requests, json
from requests.exceptions import HTTPError

#CONFIGURATION
DB_MANAGER_PORT= os.environ["DB_MANAGER_PORT"]
KAFKA_PORT= os.environ["KAFKA_PORT"]
KAFKA_ADDRESS= os.environ["KAFKA_ADDRESS"]

DB_MANAGER_URL = "http://dbmanager:"+DB_MANAGER_PORT
KAFKA_URL = KAFKA_ADDRESS+":"+KAFKA_PORT

TOPIC_MANAGER_PORT= os.environ["TOPIC_MANAGER_PORT"]
TOPIC_MANAGER_URL = "http://topicmanager:"+TOPIC_MANAGER_PORT

DATA_TRANSFORMER_PORT = os.environ["DATA_TRANSFORMER_PORT"]
DATA_TRANSFORMER_URL = "http://datatransformer:"+DATA_TRANSFORMER_PORT


app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


#QUERY DB SERVICE
'''
The payload for a query must be a JSON having at least one of the following fields:
"start": string formatted in ISO 8601 YYYY:MM:DDTHH:MM:SSZ
"stop": string formatted in ISO 8601 YYYY:MM:DDTHH:MM:SSZ
"topic": string
"generator_id": string

The response is an unsorted JSON array with all the records that match the query.
Each record has the following structure:
{
    "timestamp": string formatted in ISO 8601 YYYY:MM:DDTHH:MM:SSZ,
    "generator_id": string
    "topic": string
    "data": str
'''
@app.route("/query", methods=["POST"]) 
def query():
    try:
        msg = request.get_json()
        if not msg:
            return make_response("Empty query", 404)
        transformParameter = request.args.get('transform')
        if transformParameter:
            URL= DATA_TRANSFORMER_URL + '/queryTransformed'
            app.logger.info(f"Sending query to {URL}")
            app.logger.info(f"Query: {msg}")
            x = requests.post(URL, json=msg, params={"transform":transformParameter}, stream=True)
            x.raise_for_status()
            logging.info("Query sent to Data Transformer service")
            resp = make_response(x.raw.read(), x.status_code, x.headers.items())
            return resp
        else:
            URL= DB_MANAGER_URL + '/query'
            app.logger.info(f"Sending query to {URL}")
            app.logger.info(f"Query: {msg}")
            x = requests.post(URL, json=msg, stream=True)
            x.raise_for_status()
            logging.info("Query sent to DB service")
            resp = make_response(x.raw.read(), x.status_code, x.headers.items())
            return resp
        #return make_response(x.json(), 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)


@app.route("/register/dc", methods=["GET"]) 
def register_dc():
    try:
        URL= TOPIC_MANAGER_URL + '/topics'
        app.logger.info(f"Asking for topics to {URL}")
        x = requests.get(URL)
        x.raise_for_status()
        app.logger.info(f"Topics received: {x.content.decode('utf-8')}")
        resp = {}
        resp = json.loads(x.content.decode('utf-8'))
        resp["KAFKA_ENDPOINT"]=KAFKA_URL
        return make_response(json.dumps(resp), 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)


@app.route("/register/dg", methods=["POST"]) 
def register_dg():
    try:
        msg = request.get_json()
        if not msg:
            return make_response("Empty Registration", 400)
        URL= TOPIC_MANAGER_URL + '/register'
        app.logger.info(f"Sending registration to {URL}")
        app.logger.info(f"Registration topics: {msg}")
        x = requests.post(URL, json=msg)
        x.raise_for_status()
        logging.info("Registration sent to K Admin")
        return make_response(jsonify(KAFKA_ENDPOINT=KAFKA_URL), 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)
    

@app.route("/mappingList", methods=["GET"])
def mappingList():
    try:
        URL= DATA_TRANSFORMER_URL + '/mappingList'
        app.logger.info(f"Asking for mapping list to {URL}")
        x = requests.get(URL)
        x.raise_for_status()
        app.logger.info(f"Mapping list received: {x.content.decode('utf-8')}")
        return make_response(x.content.decode('utf-8'), 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)
    

@app.route("/mappingDetails/<string:mappingName>", methods=["GET"])
def mapingDetails(mappingName):
    try:
        URL= DATA_TRANSFORMER_URL + '/mappingDetails/'+mappingName
        app.logger.info(f"Asking for mapping details to {URL}")
        response = requests.get(URL)
        response.raise_for_status()
        response = response.json()
        app.logger.info(f"Mapping details received")
        # formatto l'output per renderlo più leggibile
        if "schema_dest" in response and isinstance(response["schema_dest"], str):
            try:
                response["schema_dest"] = json.loads(response["schema_dest"])
            except json.JSONDecodeError:
                pass 
        if "schema_input" in response and isinstance(response["schema_input"], str):
            try:
                response["schema_input"] = json.loads(response["schema_input"])
            except json.JSONDecodeError:
                pass
        return make_response(json.dumps(response, indent=4), 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)
    

@app.route("/linkMapping/<string:name>", methods=["POST"])
def linkMapping(name):
    try:
        msg = request.get_json()
        if not msg:
            return make_response("The request's body is empty", 400)
        topic = msg.get("topic")
        generator_id = msg.get("generator_id")
        if not topic or not generator_id:
            return make_response("Missing topic or generator_id", 400)
        payload = {"mappingName":name, "topic":topic, "generator_id":generator_id}
        URL = DATA_TRANSFORMER_URL + '/linkMapping'
        app.logger.info(f"Linking mapping {name} to {generator_id} and {topic}")
        x = requests.post(URL, json=payload)
        x.raise_for_status()
        app.logger.info(f"Mapping linked")
        return make_response("Mapping linked", 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)
    

@app.route("/unlinkMapping/<string:name>", methods=["POST"])
def unlinkMapping(name):
    try:
        msg = request.get_json()
        if not msg:
            return make_response("The request's body is empty", 400)
        topic = msg.get("topic")
        generator_id = msg.get("generator_id")
        if not topic or not generator_id:
            return make_response("Missing topic or generator_id", 400)
        payload = {"mappingName": name, "topic": topic, "generator_id": generator_id}
        URL = DATA_TRANSFORMER_URL + '/unlinkMapping'
        app.logger.info(f"Unlinking mapping {name} from {generator_id} and {topic}")
        x = requests.post(URL, json=payload)
        x.raise_for_status()
        app.logger.info(f"Mapping unlinked")
        return make_response("Mapping unlinked", 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)
    

@app.route("/deleteMapping/<string:name>", methods=["DELETE"])
def deleteMapping(name):
    try:
        URL = DATA_TRANSFORMER_URL + '/deleteMapping'
        app.logger.info(f"Deleting mapping {name}")
        x = requests.delete(URL, json={'mappingName': name})
        x.raise_for_status()
        app.logger.info(f"Mapping {name} deleted")
        return make_response("Mapping deleted", 200)
    except HTTPError as e:
        app.logger.error(f'HTTP error occurred: {e.response.url} - {e.response.status_code} - {e.response.text}')
        return make_response(e.response.text, e.response.status_code)
    except Exception as e:
        app.logger.error(repr(e))
        return make_response(repr(e), 500)