import logging
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
        createTable = """
        CREATE TABLE IF NOT EXISTS mapping_functions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            mapping_name VARCHAR(255) UNIQUE NOT NULL,
            mapping_function TEXT NOT NULL,
            schema_dest JSON,
            schema_input JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(createTable)
        logging.info("mapping_function table successfully created")
        conn.commit()
    except Error as e:
        logging.error(f"Error during initialization of db: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# Endpoint per il salvataggio di una funzione di mapping
@app.route('/', methods=['POST'])
def saveMappingFunction():
    try:
        initDB()
        # payload della richiesta
        data = request.json
        logging.info(f"Received a save request for mapping: {data['mappingName']}")
        # Estraggo i dati dal payload
        mappingName = data.get('mappingName')
        mappingFunction = data.get('mappingFunction')
        schemaDest = json.dumps(data.get('schemaDest'))
        schemaInput = json.dumps(data.get('schemaInput'))
        # Verifico che tutti i campi necessari siano presenti
        if not mappingName or not mappingFunction:
            return jsonify({'error': 'Nome mapping o funzione mancanti'}), 400
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
            return jsonify({'error': f'Esiste già un mapping con il nome: {mappingName}'}), 409
        # se non esiste già un mapping con quel mome lo inserisco nel db
        insertQuery = """
        INSERT INTO mapping_functions (mapping_name, mapping_function, schema_dest, schema_input)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insertQuery, (mappingName, mappingFunction, schemaDest, schemaInput))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Mapping '{mappingName}' successfully saved")
        # ritrno un messaggio di successo
        return jsonify({
            'success': True,
            'message': f"Mapping '{mappingName}' salvato con successo"
        }), 201
    except Exception as e:
        logging.error(f"Error saving mapping: {str(e)}")
        return jsonify({'error': f"Errore durante il salvataggio: {str(e)}"}), 500
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('DATA_TRANSFORMER_PORT')))