import logging
import requests
import sys
import json
import os
import mysql.connector
from flask import Flask, make_response, request, jsonify
from mysql.connector import Error

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# Configurazione database MySQL 
MYSQL_HOST = 'mysql'
MYSQL_USER = 'user'  
MYSQL_PASSWORD = 'password'  
MYSQL_DATABASE = 'mysqldb'  
DB_MANAGER_PORT= os.environ["DB_MANAGER_PORT"]
DB_MANAGER_URL = "http://dbmanager:"+DB_MANAGER_PORT

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
def getDBConnection():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        return conn
    except Error as e:
        logging.error(f"Error during the connection to db: {e}")
        return None


# inzializzazione del database
def initDB():
    conn = None
    try:
        # Prima connessione al server MySQL, senza specificare il database
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        # Creo il database se non esiste
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        logging.info(f"Database {MYSQL_DATABASE} successfully created")
        # Mi connetto al database creato
        cursor.execute(f"USE {MYSQL_DATABASE}")
        # Creo la tabella per i mapping se non esiste
        createMappingTable = """
        CREATE TABLE IF NOT EXISTS mapping_functions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mapping_name VARCHAR(255) UNIQUE NOT NULL,
            mapping_function TEXT NOT NULL,
            schema_dest JSON,
            schema_input JSON,
            schema_dest_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(createMappingTable)
        logging.info("mapping_function table successfully created")
        # creo la tabella per il legame tra mapping e DG
        createLinkTable = """
        CREATE TABLE IF NOT EXISTS mapping_dg_links (
            mapping_id INT NOT NULL,
            generator_id VARCHAR(255) NOT NULL,
            topic VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (mapping_id, generator_id, topic),
            FOREIGN KEY (mapping_id) REFERENCES mapping_functions(id)
        )
        """
        cursor.execute(createLinkTable)
        logging.info("mapping_dg_links table successfully created")
        conn.commit()
    except Error as e:
        logging.error(f"Error during initialization of db: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Funzione per ottenere la funzione di mapping associata a un generator_id e topic
def getMappingFunction(generator_id, topic, destSchemaName):
    try:
        conn = getDBConnection()
        if not conn:
            app.logger.error("Impossibile connettersi al database")
            return None
        
        cursor = conn.cursor()
        query = """
        SELECT mf.mapping_function, mf.created_at
        FROM mapping_functions mf
        JOIN mapping_dg_links mdl ON mf.id = mdl.mapping_id
        WHERE mdl.generator_id = %s AND mdl.topic = %s AND mf.schema_dest_name = %s
        """
        cursor.execute(query, (generator_id, topic, destSchemaName))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            mappingFunction, created_at = result
            app.logger.info(f"Mapping function found for generator_id: {generator_id}, topic: {topic}, destSchemaName: {destSchemaName}, created at: {created_at}")
            return mappingFunction
        app.logger.warning(f"No mapping function found for generator_id: {generator_id}, topic: {topic}, destSchemaName: {destSchemaName}")
        return None
    except Exception as e:
        app.logger.error(f"Error getting mapping function: {str(e)}")
        return None


# Endpoint per il salvataggio di una funzione di mapping
@app.route('/saveMappingFunction', methods=['POST'])
def saveMappingFunction():
    try:
        initDB()
        # payload della richiesta
        data = request.json
        app.logger.info(f"Received a save request for mapping: {data['mappingName']}")
        # Estraggo i dati dal payload
        mappingName = data.get('mappingName')
        mappingFunction = data.get('mappingFunction')
        schemaDest = json.dumps(data.get('schemaDest'))
        schemaInput = json.dumps(data.get('schemaInput'))
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
        # Connessione al database
        conn = getDBConnection()
        if not conn:
            return jsonify({'error': 'Impossibile connettersi al database'}), 500
        cursor = conn.cursor()
        # Controllo se esiste già un mapping con lo stesso nome
        checkQuery = "SELECT COUNT(*) FROM mapping_functions WHERE mapping_name = %s"
        cursor.execute(checkQuery, (mappingName,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return jsonify({'error': f'Esiste gia un mapping con il nome: {mappingName}'}), 409
        # se non esiste già un mapping con quel mome lo inserisco nel db
        insertQuery = """
        INSERT INTO mapping_functions (mapping_name, mapping_function, schema_dest, schema_input, schema_dest_name)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insertQuery, (mappingName, mappingFunction, schemaDest, schemaInput, schemaDestName))
        conn.commit()
        cursor.close()
        conn.close()
        app.logger.info(f"Mapping '{mappingName}' successfully saved")
        # ritrno un messaggio di successo
        return jsonify({
            'success': True,
            'message': f"Mapping '{mappingName}' salvato con successo"
        }), 201
    except Exception as e:
        app.logger.error(f"Error saving mapping: {str(e)}")
        return jsonify({'error': f"Errore durante il salvataggio: {str(e)}"}), 500
    

# endpoint per la lista dei nomi dei mapping salvati 
@app.route('/mappingList', methods=['GET'])
def mappingList():
    try:
        conn = getDBConnection()
        if not conn:
            app.logger.error("Impossibile connettersi al database")
            return make_response('Impossibile connettersi al database', 500)
        cursor = conn.cursor()
        # Estraggo tutti i mapping dal db
        selectQuery = "SELECT mapping_name FROM mapping_functions"
        cursor.execute(selectQuery)
        # row[0] contiene il nome del mapping
        mappingList = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        app.logger.info(f"Returning mapping list: {mappingList}")
        return make_response(mappingList, 200)
    except Exception as e:
        app.logger.error(f"Error getting mapping list: {str(e)}")
        return make_response(f"Errore durante il recupero della lista: {str(e)}", 500)
    

# endpoint per i dettagli di un mapping
@app.route('/mappingDetails/<string:mappingName>', methods=['GET'])
def mappingDetails(mappingName):
    try:
        # Controllo SQL Injection
        if checkSQLInjection(mappingName):
            app.logger.warning(f"Potential SQL injection detected in mapping name: {mappingName}")
            return make_response('Potenziale tentativo di sql-injection', 400)
        if not mappingName:
            return make_response('Nome mapping mancante', 400)
        conn = getDBConnection()
        if not conn:
            app.logger.error("Impossibile connettersi al database")
            return make_response('Impossibile connettersi al database', 500)
        cursor = conn.cursor()
        # Estraggo i dettagli del mapping dal db
        selectQuery = "SELECT mapping_function, schema_dest, schema_input, schema_dest_name FROM mapping_functions WHERE mapping_name = %s"
        cursor.execute(selectQuery, (mappingName,))
        mappingDetails = cursor.fetchone()
        cursor.close()
        conn.close()
        if not mappingDetails:
            return make_response(f"Mapping '{mappingName}' non trovato", 404)
        response = {
            "mapping_function": mappingDetails[0],
            "schema_dest": mappingDetails[1],
            "schema_input": mappingDetails[2],
            "schema_dest_name": mappingDetails[3]
        }
        app.logger.info(f"Returning mapping details for mapping: {mappingName}")
        return make_response(jsonify(response), 200)
    except Exception as e:
        app.logger.error(f"Error getting mapping details: {str(e)}")
        return make_response(f"Errore durante il recupero dei dettagli: {str(e)}", 500)
    

# endpoint per il collegamento di un mapping a un DG
@app.route('/linkMapping', methods=['POST'])
def linkMapping():
    try:
        # inizializzo il DB se necessario
        initDB()
        # estraggo il payload dalla richiesta
        data = request.json
        if not data:
            return make_response('Empty request', 400)
        mappingName = data.get('mappingName')
        topic = data.get('topic')
        generatorId = data.get('generator_id')
        if checkSQLInjection(mappingName) or checkSQLInjection(topic) or checkSQLInjection(generatorId):
            app.logger.warning("Potential SQL injection detected")
            return make_response('Potenziale tentativo di sql-injection', 400)
        if not mappingName or not topic or not generatorId:
            return make_response('Missing mappingName, topic or generator_id', 400)
        conn = getDBConnection()
        if not conn:
            app.logger.error("Impossibile connettersi al database")
            return make_response('Impossibile connettersi al database', 500)
        cursor = conn.cursor()
        # Estraggo l'id del mapping
        selectQuery = "SELECT id FROM mapping_functions WHERE mapping_name = %s"
        cursor.execute(selectQuery, (mappingName,))
        mappingId = cursor.fetchone()
        if not mappingId:
            cursor.close()
            conn.close()
            return make_response(f"Mapping '{mappingName}' non trovato", 404)
        # Controlla se esiste già una tripla (mapping_id, topic, generator_id) nella tabella mapping_dg_links
        checkQuery = """
        SELECT COUNT(*) FROM mapping_dg_links 
        WHERE mapping_id = %s AND topic = %s AND generator_id = %s
        """
        cursor.execute(checkQuery, (mappingId[0], topic, generatorId))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conn.close()
            return make_response(f"Il DG {generatorId} è già collegato al mapping con nome: {mappingName}"), 409
        # Inserisco il legame tra mapping e DG nella tabella mapping_dg_links
        insertQuery = """
        INSERT INTO mapping_dg_links (mapping_id, generator_id, topic)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insertQuery, (mappingId[0], generatorId, topic))
        conn.commit()
        cursor.close()
        conn.close()
        app.logger.info(f"Mapping '{mappingName}' linked to {generatorId} and {topic}")
        return make_response("Mapping linked", 200)
    except Exception as e:
        app.logger.error(f"Error linking mapping: {str(e)}")
        return make_response(f"Errore durante il collegamento: {str(e)}", 500)
    

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