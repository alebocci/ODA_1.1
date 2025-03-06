import logging
import requests
import sys
import json
import os
from flask import Flask, make_response, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
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
Base = declarative_base()

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# modelli per la creazione delle tabelle nel database
class MappingFunction(Base):
    __tablename__ = 'mapping_functions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_name = Column(String(255), unique=True, nullable=False)
    mapping_function = Column(Text, nullable=False)
    schema_dest = Column(JSON)
    schema_input = Column(JSON)
    schema_dest_name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

class MappingDGLink(Base):
    __tablename__ = 'mapping_dg_links'
    mapping_id = Column(Integer, ForeignKey('mapping_functions.id'), primary_key=True)
    generator_id = Column(String(255), primary_key=True)
    topic = Column(String(255), primary_key=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


# funzione per controllo sql-injection
def checkSQLInjection(data):
    if not isinstance(data, str):
        data = str(data)
    # Lista di pattern comuni utilizzati negli attacchi SQL Injection
    sqlPatterns = [
        "'--", 
        "' OR '1'='1", 
        "' OR '1'='1'--", 
        '" OR "1"="1', 
        '" OR "1"="1"--',
        "SELECT",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "DROP",
        "TRUNCATE",
        "EXECUTE",
        "EXEC",
        "UNION SELECT", 
        "DROP TABLE", 
        "INSERT INTO", 
        "DELETE FROM", 
        "UPDATE SET",
        ";--", 
        "1=1--", 
        "OR 1=1",
        "EXEC(",
        "CHAR(",
        "CAST(",
        "DECLARE",
        "SELECT * FROM",
        "' OR 'a'='a",
        '" OR "a"="a',
        "' OR 1=1#",
        '" OR 1=1#',
        "' OR 'x'='x",
        '" OR "x"="x',
        "' OR ''='",
        "OR ' ' = ' ",
        "' OR 1=1--",
        "'; EXEC xp_cmdshell('dir');--",
        "' OR '1'='1'/*",
        "OR 1=1 LIMIT 1",
        "SLEEP(5)#",
        "'; WAITFOR DELAY '00:00:05'--",
        "HAVING 1=1",
        "ORDER BY 1--",
        "' OR EXISTS(SELECT * FROM users)--",
        "' UNION SELECT NULL,NULL--",
        "'; DROP DATABASE test;--"
    ]
    # porto tutto in minuscolo
    dataLower = data.lower()
    # Controlla la presenza di ogni pattern
    for pattern in sqlPatterns:
        if pattern.lower() in dataLower:
            return True
    return False


# funzione per la creazione di una connessione al database MySQL
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# inzializzazione del database
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logging.error(f"Error during database initialization: {e}")


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
        # Controllo SQL Injection
        if checkSQLInjection(mappingName):
            app.logger.warning(f"Potential SQL injection detected in mapping name: {mappingName}")
            return jsonify({'error': 'Potenziale tentativo di sql-injection'}), 400
        if checkSQLInjection(schemaDestName):
            app.logger.warning(f"Potential SQL injection detected in schemaDestName: {schemaDestName}")
            return jsonify({'error': 'Potenziale tentativo di sql-injection'}), 400
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
        # Controllo SQL Injection
        if checkSQLInjection(mappingName):
            app.logger.warning(f"Potential SQL injection detected in mapping name: {mappingName}")
            return jsonify({'error': 'Potenziale tentativo di sql-injection'}), 400
        if not mappingName:
            return jsonify({'error': 'Nome mapping mancante'}), 400
        # Estraggo i dettagli del mapping dal db utilizzando SQLAlchemy
        mapping = db.query(MappingFunction).filter(MappingFunction.mapping_name == mappingName).first()
        if not mapping:
            app.logger.info(f"Mapping '{mappingName}' not found in the database")
            return make_response(f"Mapping '{mappingName}' non trovato", 404)
        response = {
            "mapping_function": mapping.mapping_function,
            "schema_dest": mapping.schema_dest,
            "schema_input": mapping.schema_input,
            "schema_dest_name": mapping.schema_dest_name
        }
        app.logger.info(f"Returning mapping details for mapping: {mappingName}")
        return make_response(jsonify(response), 200)
    except SQLAlchemyError as e:
        app.logger.error(f"Error getting mapping details: {e}")
        return make_response(f"Errore durante il recupero dei dettagli", 500)
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
        if checkSQLInjection(mappingName) or checkSQLInjection(topic) or checkSQLInjection(generatorId):
            app.logger.warning("Potential SQL injection detected")
            return jsonify({'error': 'Potenziale tentativo di sql-injection'}), 400
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
        x = requests.post(URL, json=msg, params={'zip': 'false'})
        x.raise_for_status()
        data = x.json()
        transformData = []
        for record in data:
            generatorId = record.get('generator_id')
            topic = record.get('topic')
            mappingFunctionCode = getMappingFunction(generatorId, topic, transformParameter)
            if mappingFunctionCode:
                namespace = {}
                exec(mappingFunctionCode, namespace)
                transformedRecord = namespace['mappingFunction'](record)
                if transformedRecord is not None:
                    app.logger.info(f"Data transformed for generatorId: {generatorId}, topic: {topic} to {transformParameter}")
                    transformData.append(transformedRecord)
                else:
                    app.logger.error(f"Error in mapping function for generatorId: {generatorId}, topic: {topic}, impossible to transform this data in {transformParameter}")
            else:
                app.logger.error(f"No valid mapping function found for generatorId: {generatorId}, topic: {topic}")
        return make_response(jsonify(transformData), 200)
    except requests.exceptions.RequestException as e:
        app.logger.error(f"HTTP request error: {str(e)}")
        return make_response(f"HTTP request error: {str(e)}", 500)
    except ValueError as e:
        app.logger.error(f"Value error: {str(e)}")
        return make_response(f"Value error: {str(e)}", 400)
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return make_response(f"Unexpected error: {str(e)}", 500)