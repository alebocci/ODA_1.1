import gzip
import logging
import requests
import sys
import json
import os
from flask import Flask, make_response, request, jsonify
from models import *
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Configurazione del database
MYSQL_HOST = 'mysql'
MYSQL_USER = 'user'  
MYSQL_PASSWORD = 'password'  
MYSQL_DATABASE = 'mysqldb'  
DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
DB_MANAGER_PORT= os.environ["DB_MANAGER_PORT"]
DB_MANAGER_URL = "http://dbmanager:"+DB_MANAGER_PORT
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# funzione per la creazione di una connessione al database MySQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# inzializzazione del database
def init_db():
    maxRetries = 10
    retryCount = 0
    while retryCount < maxRetries:
        try:
            Base.metadata.create_all(bind=engine)
            app.logger.info("Database tables created successfully")
            return
        except SQLAlchemyError as e:
            retryCount += 1
            app.logger.warning(f"Attempt {retryCount}/{maxRetries}: Error during database initialization: {e}")
            if retryCount < maxRetries:
                app.logger.info("Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                app.logger.error(f"Failed to initialize database after {maxRetries} attempts: {e}")

# inizializzo il database
init_db()


# Funzione per ottenere la funzione di mapping associata a un generator_id e topic
def getMappingFunction(generator_id, topic, destSchemaName):
    db = next(get_db())
    try:
        mapping = db.query(MappingFunction).join(MappingDGLink).filter(
            MappingDGLink.generator_id == generator_id,
            MappingDGLink.topic == topic,
            MappingFunction.schema_dest_name == destSchemaName
        ).first()
        if mapping:
            logging.info(f"Mapping function found for generator_id: {generator_id}, topic: {topic}, destSchemaName: {destSchemaName}")
            return mapping.mapping_function
        logging.warning(f"No mapping function found for generator_id: {generator_id}, topic: {topic}, destSchemaName: {destSchemaName}")
        return None
    except SQLAlchemyError as e:
        logging.error(f"Error getting mapping function: {e}")
        return None
    finally:
        db.close()


# Endpoint per il salvataggio di una funzione di mapping
@app.route('/saveMappingFunction', methods=['POST'])
def saveMappingFunction():
    try:
        db = next(get_db())
        # payload della richiesta
        data = request.json
        app.logger.info(f"Received a save request for mapping: {data['mappingName']}")
        # Estraggo i dati dal payload
        mappingName = data.get('mappingName')
        mappingFunction = data.get('mappingFunction')
        schemaDest = data.get('schemaDest')
        schemaInput = data.get('schemaInput')
        schemaDestName = data.get('schemaDestName')
        # Verifico che tutti i campi necessari siano presenti
        if not mappingName or not mappingFunction or not schemaDestName:
            return jsonify({'error': 'Nome mapping o funzione mancanti'}), 400
        # Controllo se esiste già un mapping con lo stesso nome
        existingMapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if existingMapping:
            return jsonify({'error': f'Esiste gia un mapping con il nome: {mappingName}'}), 409
        # se non esiste già un mapping con quel mome lo inserisco nel db
        new_mapping = MappingFunction(
            mapping_name=mappingName,
            mapping_function=mappingFunction,
            schema_dest=schemaDest,
            schema_input=schemaInput,
            schema_dest_name=schemaDestName
        )
        db.add(new_mapping)
        db.commit()
        app.logger.info(f"Mapping '{mappingName}' successfully saved")
        # ritrno un messaggio di successo
        return jsonify({
            'success': True,
            'message': f"Mapping '{mappingName}' salvato con successo"
        }), 201
    except SQLAlchemyError as e:
        db.rollback()
        logging.error(f"Error saving mapping: {e}")
        return jsonify({'error': f"Errore durante il salvataggio: {e}"}), 500
    finally:
        db.close()
    

# endpoint per mostrare i mapping nella pagina web
@app.route('/showMapping', methods=['GET'])
def showMapping():
    try:
        db = next(get_db())
        # Estraggo tutti i mapping dal db
        mappings = db.query(MappingFunction).all()
        
        if not mappings:
            app.logger.info("No mappings found in the database")
            return make_response(jsonify([]), 200)
        
        # Creo una lista di dizionari con i dati essenziali di ogni mapping
        mapping_list = []
        for mapping in mappings:
            mapping_data = {
                "mapping_name": mapping.mapping_name,
                "schema_input": mapping.schema_input,
                "schema_dest_name": mapping.schema_dest_name,
                "mapping_function": mapping.mapping_function
            }
            mapping_list.append(mapping_data)
        
        app.logger.info(f"Returning {len(mapping_list)} mappings")
        return make_response(jsonify(mapping_list), 200)
    except SQLAlchemyError as e:
        app.logger.error(f"Error getting mappings: {e}")
        return make_response(jsonify({"error": f"Errore durante il recupero dei mapping: {e}"}), 500)
    finally:
        db.close()


# endpoint per la lista dei nomi dei mapping salvati 
@app.route('/mappingList', methods=['GET'])
def mappingList():
    try:
        db = next(get_db())
        # Estraggo tutti i mapping dal db
        mappings = db.query(MappingFunction.mapping_name).all()
        if not mappings:
            app.logger.info("No mappings found in the database")
            return make_response("Non ci sono mapping nel database", 500)
        # mapping[0] contiene il nome del mapping
        mappingList = [mapping[0] for mapping in mappings]
        app.logger.info(f"Returning mapping list: {mappingList}")
        return make_response(mappingList, 200)
    except SQLAlchemyError as e:
        app.logger.error(f"Error getting mapping list: {e}")
        return make_response(f"Errore durante il recupero della lista", 500)
    finally:
        db.close()
    

# endpoint per i dettagli di un mapping
@app.route('/mappingDetails/<string:mappingName>', methods=['GET'])
def mappingDetails(mappingName):
    try:
        db = next(get_db())
        if not mappingName:
            return jsonify({'error': 'Nome mapping mancante'}), 400
        # Estraggo i dettagli del mapping dal db utilizzando SQLAlchemy
        mapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if not mapping:
            app.logger.info(f"Mapping '{mappingName}' not found in the database")
            return make_response(f"Mapping '{mappingName}' non trovato", 404)
        # Estraggo i collegamenti con DG e topic
        links = db.query(MappingDGLink).filter(MappingDGLink.mapping_id == mapping.id).all()
        linksData = [{"generator_id": link.generator_id, "topic": link.topic} for link in links]
        response = {
            "mapping_function": mapping.mapping_function,
            "schema_dest": mapping.schema_dest,
            "schema_input": mapping.schema_input,
            "schema_dest_name": mapping.schema_dest_name,
            "links": linksData
        }
        app.logger.info(f"Returning mapping details for mapping: {mappingName}")
        return make_response(jsonify(response), 200)
    except SQLAlchemyError as e:
        app.logger.error(f"Error getting mapping details: {e}")
        return make_response(f"Errore durante il recupero dei dettagli", 500)
    finally:
        db.close()


# endpoint per la statistica numero di collegamenti
@app.route('/numberOfLink', methods=['GET'])
def numberOfLink():
    try:
        db = next(get_db())
        # Contiamo il numero totale di collegamenti nella tabella mapping_dg_links
        numberOfLink = db.query(MappingDGLink).count()
        app.logger.info(f"Numero totale di collegamenti trovati: {numberOfLink}")
        # Restituiamo il numero totale di collegamenti
        return jsonify({"numberOfLink": numberOfLink}), 200
    except SQLAlchemyError as e:
        app.logger.error(f"Errore durante il recupero del numero di collegamenti: {e}")
        return jsonify({'error': f"Errore durante il recupero del numero di collegamenti: {e}"}), 500
    finally:
        db.close()


# endpoint per il collegamento di un mapping a un DG
@app.route('/linkMapping', methods=['POST'])
def linkMapping():
    try:
        db = next(get_db())
        # estraggo il payload dalla richiesta
        data = request.json
        if not data:
            return jsonify({'error': 'Empty request'}), 400
        mappingName = data.get('mappingName')
        topic = data.get('topic')
        generatorId = data.get('generator_id')
        if not mappingName or not topic or not generatorId:
            return jsonify({'error': 'Missing mappingName, topic or generator_id'}), 400
        # Estraggo l'id del mapping 
        mapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if not mapping:
            return jsonify({'error': f"Mapping '{mappingName}' non trovato"}), 404
        # Controlla se esiste già una tripla (mapping_id, topic, generator_id) nella tabella mapping_dg_links
        existingLink = db.query(MappingDGLink).filter(
            MappingDGLink.mapping_id == mapping.id,
            MappingDGLink.topic == topic,
            MappingDGLink.generator_id == generatorId
        ).first()
        if existingLink:
            return jsonify({'error': f"Il DG {generatorId} è già collegato al mapping con nome: {mappingName}"}), 409
        # Inserisco il legame tra mapping e DG nella tabella mapping_dg_links
        newLink = MappingDGLink(
            mapping_id=mapping.id,
            generator_id=generatorId,
            topic=topic
        )
        db.add(newLink)
        db.commit()
        app.logger.info(f"Mapping '{mappingName}' linked to {generatorId} and {topic}")
        return jsonify({'success': 'Mapping linked'}), 200
    except SQLAlchemyError as e:
        db.rollback()
        app.logger.error(f"Error linking mapping: {e}")
        return jsonify({'error': f"Errore durante il collegamento: {e}"}), 500
    finally:
        db.close()
    

# endpoint per rimuovere il collegamento di un mapping a un DG
@app.route('/unlinkMapping', methods=['POST'])
def unlinkMapping():
    try:
        db = next(get_db())
        # estraggo il payload dalla richiesta
        data = request.json
        if not data:
            return jsonify({'error': 'Empty request'}), 400
        mappingName = data.get('mappingName')
        topic = data.get('topic')
        generatorId = data.get('generator_id')
        if not mappingName or not topic or not generatorId:
            return jsonify({'error': 'Missing mappingName, topic or generator_id'}), 400
        # Estraggo l'id del mapping 
        mapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if not mapping:
            return jsonify({'error': f"Mapping '{mappingName}' non trovato"}), 404
        # Trova il collegamento da rimuovere
        link_to_remove = db.query(MappingDGLink).filter(
            MappingDGLink.mapping_id == mapping.id,
            MappingDGLink.topic == topic,
            MappingDGLink.generator_id == generatorId
        ).first()
        if not link_to_remove:
            return jsonify({'error': f"Il DG {generatorId} non è collegato al mapping con nome: {mappingName}"}), 404
        # Rimuovo il collegamento
        db.delete(link_to_remove)
        db.commit()
        app.logger.info(f"Mapping '{mappingName}' unlinked from {generatorId} and {topic}")
        return jsonify({'success': 'Mapping unlinked'}), 200
    except SQLAlchemyError as e:
        db.rollback()
        app.logger.error(f"Error unlinking mapping: {e}")
        return jsonify({'error': f"Errore durante la rimozione del collegamento: {e}"}), 500
    finally:
        db.close()


# endpoint per eliminare un mapping
@app.route('/deleteMapping', methods=['DELETE'])
def deleteMapping():
    try:
        db = next(get_db())
        # Estrai il nome del mapping dal payload
        data = request.json
        mappingName = data.get('mappingName')
        # Verifica che il nome del mapping sia fornito
        if not mappingName:
            return jsonify({'error': 'Nome del mapping mancante'}), 400

        # Trova il mapping da eliminare
        mapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if not mapping:
            return jsonify({'error': f"Mapping '{mappingName}' non trovato"}), 404
        # Elimina tutti i collegamenti associati al mapping
        db.query(MappingDGLink).filter(MappingDGLink.mapping_id == mapping.id).delete()
        # Elimina il mapping
        db.delete(mapping)
        db.commit()
        app.logger.info(f"Mapping '{mappingName}' eliminato con successo")
        return jsonify({'success': f"Mapping '{mappingName}' eliminato con successo"}), 200
    except SQLAlchemyError as e:
        db.rollback()
        app.logger.error(f"Error deleting mapping: {e}")
        return jsonify({'error': f"Errore durante l'eliminazione del mapping: {e}"}), 500
    finally:
        db.close()

 
# ednpoint per le query dei dati trasformati
@app.route("/queryTransformed", methods=["POST"])
def queryTransformed():
    try:
        msg = request.get_json()
        if not msg:
            return make_response("The request's body is empty", 400)
        transformParameter = request.args.get('transform')
        if not transformParameter:
            return make_response("Transform parameter is missing", 400)
        URL = DB_MANAGER_URL + '/query'
        app.logger.info(f"Sending query to {URL}")
        x = requests.post(URL, json=msg, params={'unzip': 'true'})
        if x.status_code == 404:
            return make_response("", 404)
        x.raise_for_status()
        payload = x.json()
        transformData = []
        for record in payload:
            app.logger.info(f"Processing record: {record}")
            timestamp = record.get('timestamp')
            generatorId = record.get('generator_id')
            topic = record.get('topic')
            data = record.get('data')
            if isinstance(data, str):
                data.replace("'", '"')
                data = json.loads(data)
            app.logger.info(f"Data after conversion: {data}")
            toTransform = {"timestamp": timestamp, "generator_id": generatorId, "topic": topic, "data": data}
            app.logger.info(f"Data to transform: {toTransform}")
            mappingFunctionCode = getMappingFunction(generatorId, topic, transformParameter)
            if mappingFunctionCode:
                namespace = {}
                exec(mappingFunctionCode, namespace)
                transformedRecord = namespace['mappingFunction'](toTransform)
                app.logger.info(f"Transformed record: {transformedRecord}")
                if transformedRecord is not None:
                    app.logger.info(f"Data transformed for generatorId: {generatorId}, topic: {topic} to {transformParameter}")
                    transformData.append(transformedRecord)
                else:
                    app.logger.error(f"Error in mapping function for generatorId: {generatorId}, topic: {topic}, impossible to transform this data in {transformParameter}")
            else:
                app.logger.error(f"No valid mapping function found for generatorId: {generatorId}, topic: {topic}")
        # Comprimere i dati trasformati e restituirli come file ZIP
        app.logger.info('Compressing transformed data')
        content = gzip.compress(json.dumps(transformData).encode('utf8'), mtime=0)
        response = make_response(content)
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    except requests.exceptions.RequestException as e:
        app.logger.error(f"HTTP request error: {str(e)}")
        return make_response(f"HTTP request error: {str(e)}", 500)
    except ValueError as e:
        app.logger.error(f"Value error: {str(e)}")
        return make_response(f"Value error: {str(e)}", 400)
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return make_response(f"Unexpected error: {str(e)}", 500)

# endpoint per prendere i nomi degli schemi dal db
@app.route('/getSchemaNames', methods=['GET'])
def getSchemaNames():
    try:
        db = next(get_db())
        # Estrai gli schemi dal database
        schemas = db.query(MappingFunction.schema_dest_name).distinct().all()
        schema_names = [schema[0] for schema in schemas]
        app.logger.info(f"Returning schema names: {schema_names}")
        return jsonify(schema_names), 200
    except SQLAlchemyError as e:
        app.logger.error(f"Error getting schema names: {e}")
        return jsonify({'error': f"Errore durante il recupero degli schemi: {e}"}), 500
    finally:
        db.close()