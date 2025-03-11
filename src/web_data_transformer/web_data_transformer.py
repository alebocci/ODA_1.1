from datetime import datetime
import json
import logging
import os
import sys
from flask import Flask, render_template, request, jsonify, session
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Configurazione della sessione
app.secret_key = 'ODA1.1secret_key'
# Cartelle per salvare i file di input e output
INPUT_FOLDER = 'static/inputSchema_files'
DEST_FOLDER = 'static/destSchema_files'
DEST_DEFAULT_FOLDER = 'static/destSchema_defaults'
app.config['INPUT_FOLDER'] = INPUT_FOLDER
app.config['DEST_FOLDER'] = DEST_FOLDER
app.config['DEST_DEFAULT_FOLDER'] = DEST_DEFAULT_FOLDER
# se non esistono creo le cartelle
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(DEST_FOLDER, exist_ok=True)
os.makedirs(DEST_DEFAULT_FOLDER, exist_ok=True)
DATA_TRANSFORMER_PORT = os.environ["DATA_TRANSFORMER_PORT"]
DATA_TRANSFORMER_URL = "http://datatransformer:"+DATA_TRANSFORMER_PORT

# Funzione per caricare uno schema specifico dalla caretella di default
def loadSchema(schemaName):
    schemaPath = os.path.join(app.config['DEST_DEFAULT_FOLDER'], f"{schemaName}.json")
    if not os.path.exists(schemaPath):
        return None  # Schema non trovato
    with open(schemaPath, 'r') as f:
        return json.load(f)
    

# endpoint per la pagina principale
@app.route('/')
def index():
    app.logger.info("Serving home page")
    return render_template('index.html')

@app.route('/generateFunction')
def generateFunction():
    app.logger.info("Serving generate function page")
    return render_template('generateFunction.html')

@app.route('/mappings')
def mappings():
    app.logger.info("Serving mappings page")
    return render_template('mappings.html')

# Endpoint per inoltrare la richiesta di visualizzazione dei mapping a data_transformer
@app.route('/showMapping', methods=['GET'])
def showMapping():
    try:
        # Inoltra la richiesta al backend data_transformer
        URL = DATA_TRANSFORMER_URL + '/showMapping'
        app.logger.info("Sending request to URL: " + URL)
        response = requests.get(URL)
        app.logger.info("Request sent to data_transformer")
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': f"Errore durante il recupero dei mapping: {response.status_code}"}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500

# endpoint per inoltrare la richiesta di visualizzazione dei dettagli di un mapping
@app.route('/mappingDetails/<string:mappingName>', methods=['GET'])
def mappingDetails(mappingName):
    try:
        # Inoltra la richiesta al backend data_transformer
        URL = DATA_TRANSFORMER_URL + '/mappingDetails/'+mappingName
        app.logger.info("Sending request to URL: " + URL)
        response = requests.get(URL)
        app.logger.info("Request sent to data_transformer")
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': f"Errore durante il recupero dei mapping: {response.status_code}"}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500

# endpoint per la statistica numero di collegamenti
@app.route('/numberOfLink', methods=['GET'])
def numberOfLink():
    try:
        # Inoltra la richiesta al backend data_transformer
        URL = DATA_TRANSFORMER_URL + '/numberOfLink'
        app.logger.info("Sending request to URL: " + URL)
        response = requests.get(URL)
        app.logger.info("Request sent to data_transformer")
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': f"Errore durante il recupero del numero di collegamenti dei mapping: {response.status_code}"}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500

# endpoint per inoltrare la richiesta di collegare un DG a un mapping
@app.route('/linkMapping', methods=['POST'])
def linkMapping():
    try:
        URL = DATA_TRANSFORMER_URL + '/linkMapping'
        app.logger.info("Sending request to URL: " + URL)
        data = request.json
        response = requests.post(URL, json=data)
        app.logger.info("Request sent to data_transformer")
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': response.json()['error']}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500

# endpoint per inoltrare la richiesta di collegare un DG a un mapping
@app.route('/unlinkMapping', methods=['POST'])
def unlinkMapping():
    try:
        URL = DATA_TRANSFORMER_URL + '/unlinkMapping'
        app.logger.info("Sending request to URL: " + URL)
        data = request.json
        response = requests.post(URL, json=data)
        app.logger.info("Request sent to data_transformer")
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': response.json()['error']}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500
    
# endpoint per inoltrare la richiesta di eliminare un mapping
@app.route('/deleteMapping', methods=['DELETE'])
def deleteMapping():
    try:
        # Ottieni i dati inviati dal frontend
        mappingData = request.get_json()
        mappingName = mappingData.get('mappingName')
        
        # Verifica che il nome del mapping sia fornito
        if not mappingName:
            return jsonify({'error': 'Nome del mapping mancante'}), 400
        
        # Inoltra la richiesta al backend data_transformer
        URL = DATA_TRANSFORMER_URL + '/deleteMapping'
        app.logger.info("Sending request to URL: " + URL)
        response = requests.delete(URL, json={'mappingName': mappingName})
        app.logger.info("Request sent to data_transformer")
        
        # Se la richiesta è andata a buon fine, restituisci la risposta
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({'error': f"Errore durante l'eliminazione del mapping: {response.status_code}"}), response.status_code
    except Exception as e:
        # Se c'è un errore, restituisci un messaggio di errore
        return jsonify({'error': f"Errore durante l'inoltro della richiesta: {str(e)}"}), 500

# endpoint per il caricamento del file JSON con lo schema di partenza e ritornare la struttura del json al frontend
@app.route('/uploadInputSchema', methods=['POST'])
def uploadInputSchema():
    try:
        # Carico il file JSON dal form frontend (name="inputSchema")
        file = request.files['inputSchema']
        # Verifico che il file sia un file JSON
        if not file.filename.endswith('.json'):
            # se non lo è restituisco un errore
            return jsonify({'error': 'Il file deve essere un file JSON'}), 400
        # creo il path completo del file e lo salvo
        inputFilename = secure_filename(file.filename)
        # salvo il nome nella sessione
        session['inputFilename'] = inputFilename
        # creo il path completo e lo salvo
        inputSchemaPath = os.path.join(app.config['INPUT_FOLDER'], inputFilename)
        file.save(inputSchemaPath)
        # Leggo il contenuto del file
        with open(inputSchemaPath, 'r') as f:
            lines = f.read()
        # Cerco di caricare il contenuto come JSON
        try:
            jsonData = json.loads(lines)
            session['inputSchemaStructure'] = jsonData
        except json.JSONDecodeError as e:
            # se la decodifica fallisce restituisco un errore
            return jsonify({'error': f"Errore nella decodifica del file JSON: {e}"}), 400
        # se tutto va bene salvo la struttura del json della sessione e la restituisco al frontend
        session['inputSchemaStructure'] = jsonData
        app.logger.info("Schema input uploaded")
        return jsonify({'jsonStructure': jsonData}), 200
    except Exception as e:
        # se ci sono errori restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante il caricamento del file JSON: {e}"}), 500

# endpoint per il caricamento del file JSON con lo schema di arrivo e ritornare la struttura di POLIMI al frontend
@app.route('/uploadDestSchema', methods=['POST'])
def uploadDestSchema():
    try:
        # Ottieni il nome dello schema inviato dal frontend
        requestJson = request.get_json()
        # Estrai il valore della destinazione (destSchema, o POLIMI o SCP)
        selectedSchema = requestJson.get('destSchema')
        session['selectedSchemaName'] = selectedSchema
        # carico il json dello schema richiesto
        jsonStructure = loadSchema(selectedSchema)
        # salvo lo schema nella sessione
        session['destSchemaStructure'] = jsonStructure
        # se non trovo il nome dello schema restituisco un errore
        if jsonStructure is None:
            return jsonify({'error': 'Schema non trovato'}), 404
        # restituisco la struttura del json al frontend
        app.logger.info(f"Schema {selectedSchema} uploaded")
        return jsonify({'jsonStructure': jsonStructure})
    except Exception as e:
        # Se c'è un errore restituiamo un messaggio di errore
        return jsonify({'error': str(e)}), 500
    
# endpoint per il caricamento del file JSON con lo schema destinazione generico e ritornare la struttura al frontend
@app.route('/uploadDestSchemaFile', methods=['POST'])
def uploadDestSchemaFile():
    try:
        # Carico il file JSON dal form frontend (name="destSchemaFile")
        file = request.files['destSchemaFile']
        # Verifico che il file sia un file JSON
        if not file.filename.endswith('.json'):
            # se non lo cerco restituisco un errore
            return jsonify({'error': 'Il file deve essere un file JSON'}), 400
        # creo il path completo del file e lo salvo
        destFilename = secure_filename(file.filename)
        # salvo il nome nella sessione
        session['destFilename'] = destFilename
        session['selectedSchemaName'] = destFilename
        # creo il path completo e lo salvo
        destSchemaPath = os.path.join(app.config['DEST_FOLDER'], destFilename)
        file.save(destSchemaPath)
        # Leggo il contenuto del file
        with open(destSchemaPath, 'r') as f:
            lines = f.read()
        try:
            jsonData = json.loads(lines)
            session['destSchemaStructure'] = jsonData
        except json.JSONDecodeError as e:
            # se la decodifica fallisce restituisco un errore
            return jsonify({'error': f"Errore nella decodifica del file JSON: {e}"}), 400
        # se tutto va bene salvo la struttura del json della sessione e la restituisco al frontend
        session['destSchemaStructure'] = jsonData
        app.logger.info("Schema dest uploaded")
        return jsonify({'jsonStructure': jsonData}), 200
    except Exception as e:
        # se ci sono errori restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante il caricamento del file JSON: {e}"}), 500

# endpoint per la generazione della funzione di mapping per POLIMI
@app.route('/generateMappingFunctionPOLIMI', methods=['POST'])
def generateMappingFunctionPOLIMI():
    try:
        # Ottieni i dati inviati dal frontend
        mappingData = request.get_json()
        # Controllo per timestamp
        if 'timestamp' not in mappingData:
            mappingData['timestamp'] = {'value': 'timestamp di arrivo del dato ad ODA', 'isConstant': True}
        # Genera il codice della funzione di mapping
        functionLines = []
        functionLines.append("import json")
        functionLines.append("def mappingFunction(inputData):")
        functionLines.append("    mappedData = {}")
        functionLines.append("    if isinstance(inputData.get('data'), str):")
        functionLines.append("        inputData['data'] = json.loads(inputData['data'])")
        for key, items in mappingData.items():
            # se sono nel campo data gli attributi devono essere oggetti con campi value e unit
            if key == "data":
                functionLines.append("    mappedData['data'] = {}")
                for attribute in items:
                    # attribute: {'key': 'k1.k2.k3...', , 'value': 'any', 'unit': 'unità', isArrayValue: }
                    # estraggo il percorso della chiave
                    pathArray = attribute['key'].split('.')
                    # creo la stringa per il path per referenziare l'attributo da mappare
                    path = 'inputData'
                    for p in pathArray:
                        path = path + f"['{p}']"
                    # se l'attributo è il valore di un array
                    if attribute['isArrayValue']:
                        # Gestione dei valori
                        arrayPath = 'inputData'
                        for p in pathArray[:-1]:
                            arrayPath = arrayPath + f"['{p}']"
                        item = pathArray[-1]
                        # creo un array vuoto e per ogni valore dell'array creo un campo valore e unità 
                        # con all'interno i valori e l'unita dell'elemento dell'array
                        functionLines.append(f"    mappedData['data']['{item}'] = []")
                        functionLines.append(f"    for i, item in enumerate({arrayPath}):")
                        functionLines.append(f"        mappedData['data']['{item}'].append({{")
                        functionLines.append(f"            'value': item['{item}'],")
                        functionLines.append(f"            'unit': '{attribute['unit']}'")
                        functionLines.append("        })")
                    else:
                        # Gestione di attributi semplici e oggetti
                        functionLines.append(f"    mappedData['data']['{pathArray[-1]}'] = {{")
                        functionLines.append(f"        'value': {path},")
                        functionLines.append(f"        'unit': '{attribute['unit']}'")
                        functionLines.append("    }")
            elif key in ["generator_id", "topic", "timestamp"]:
                # Distinzione tra costanti e valori drag-and-drop
                value = items['value']
                is_constant = items.get('isConstant', False)
                if is_constant:
                    # Se è una costante, inserisci direttamente il valore
                    functionLines.append(f"    mappedData['{key}'] = '{value}'")
                else:
                    # Se è un valore drag-and-drop, usa inputData
                    functionLines.append(f"    mappedData['{key}'] = inputData.get('{value}')")
        # ritorno del mappedData
        functionLines.append("    return mappedData")
        # Unisci il codice in un'unica stringa
        mappingFunction = "\n".join(functionLines)
        app.logger.info("Mapping function generated")
        # Restituisci la funzione di mapping al frontend
        return jsonify({'mappingFunction': mappingFunction}), 200
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante la generazione della funzione di mapping: {str(e)}"}), 500


# endpoint per la generazione della funzione di mapping per FILE generico
@app.route('/generateMappingFunctionFILE', methods=['POST'])
def generateMappingFunctionFILE():
    try:
        # Ottengo i dati inviati dal frontend
        mappingData = request.get_json()
        # salavo in sessione la struttura di destinazione
        destSchemaStructure = session.get('destSchemaStructure')
        # Controllo per timestamp
        if 'timestamp' not in mappingData:
            mappingData['timestamp'] = [{'value': 'timestamp di arrivo del dato ad ODA', 'isConstant': True}]
        # Funzione per ottenere le chiavi che sono array
        def getArrayKeys(destSchemaStructure):
            arrayKeys = []
            # scorro la struttura di destinazione per trovare gli array
            def findArrays(structure, currentPath=""):
                if isinstance(structure, dict):
                    for key, value in structure.items():
                        newPath = f"{currentPath}.{key}" if currentPath else key
                        if isinstance(value, list):
                            arrayKeys.append(key)
                        elif isinstance(value, dict):
                            findArrays(value, newPath)
            findArrays(destSchemaStructure)
            return arrayKeys
        # controllo quali elementi sono stati mappati dall'utente per inizializzare la struttura di mappedData
        allAttPresents = mappingData.keys()
        allAttArray = []
        for att in allAttPresents:
            allAtt = att.split('.')
            for a in allAtt:
                if a not in allAttArray:
                    allAttArray.append(a)
        # inizializzo la struttura di mappedData basata sui campi presenti in mappingData
        def initializeMappedData(destSchemaStructure):
            # Funzione ricorsiva per creare la struttura di mappedData
            def createStructure(structure):
                if isinstance(structure, dict):
                    return {key: createStructure(value) for key, value in structure.items() if key in allAttArray}
                elif isinstance(structure, list):
                    return []
                else:
                    return 'None'
            # creo il dato per ODA nella forma corretta
            return {'data': createStructure(destSchemaStructure)}
        # Ottengo le chiavi che sono array
        arrays = getArrayKeys(destSchemaStructure)
        # Genero il codice della funzione di mapping
        functionLines = []
        functionLines.append("import json")
        functionLines.append("def mappingFunction(inputData):")
        functionLines.append("    if isinstance(inputData.get('data'), str):")
        functionLines.append("        inputData['data'] = json.loads(inputData['data'])")
        mappedData = initializeMappedData(destSchemaStructure)
        # creo i campi obbligatori per ODA
        if 'topic' not in mappedData:
            mappedData['topic'] = 'None'
        if 'generator_id' not in mappedData:
            mappedData['generator_id'] = 'None'
        if 'timestamp' not in mappedData:
            mappedData['timestamp'] = 'None'
        functionLines.append("    mappedData = " + json.dumps(mappedData))
        # Funzione ricorsiva per gestire strutture nidificate
        def processMapping(key, items, indentLevel=1):
            indent = "    " * indentLevel
            outPathArray = key.split('.')
            # creo il percorso in maniera corretta per evitare di accedere a valori sbagliati 
            if outPathArray[-1] == 'topic' or outPathArray[-1] == 'generator_id' or outPathArray[-1] == 'timestamp':
                outPath = 'mappedData'
            else:
                outPath = "mappedData['data']"
            for p in outPathArray:
                outPath += f"['{p}']"
            if isinstance(items, dict):
                items = [items]
            for item in items:
                # Se è una costante, usa direttamente il valore
                if item.get('isConstant', False):
                    functionLines.append(f"{indent}{outPath} = '{item.get('value')}'")
                    continue
                isArray = any(el in key.split('.') for el in arrays)
                if isArray:
                    inPathArray = item.get('value', '').split('.')
                    arrayIn, attribute = inPathArray[:-1], inPathArray[-1]
                    arrayOut, attribute = outPathArray[:-1], outPathArray[-1]
                    inPath = 'inputData'
                    # gli array sono per forza all'interno del campo data quindi inizializzo il percorso da lì
                    outPath = "mappedData['data']"
                    for p in arrayIn:
                        inPath += f"['{p}']"
                    for p in arrayOut:
                        outPath += f"['{p}']"
                    # Inizializzo l'array una sola volta
                    if not any(line.startswith(f"{indent}{outPath} = [{{}} for _ in range(len({inPath}))]") for line in functionLines):
                        functionLines.append(f"{indent}{outPath} = [{{}} for _ in range(len({inPath}))]")
                    functionLines.append(f"{indent}for i,elem in enumerate({inPath}):")
                    functionLines.append(f"{indent}    {outPath}[i]['{attribute}'] = {inPath}[i]['{attribute}']")               
                else:
                    inPathArray = item.get('value', '').split('.')
                    inPath = 'inputData'
                    for p in inPathArray:
                        inPath += f"['{p}']"
                    functionLines.append(f"{indent}{outPath} = {inPath}")   
        # Elaboro ogni campo nel mappingData
        for key, items in mappingData.items():
            processMapping(key, items)
        functionLines.append("    return mappedData")
        # Unisco il codice in un'unica stringa
        mappingFunction = "\n".join(functionLines)
        app.logger.info("Mapping function generated")
        # ritorno del mappedData
        return jsonify({'mappingFunction': mappingFunction}), 200
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante la generazione della funzione di mapping: {str(e)}"}), 500    
    

# endpoint per la generazione della funzione di mapping per SCP
@app.route('/generateMappingFunctionSCP', methods=['POST'])
def generateMappingFunctionSCP():
    try:
        # Ottieni i dati inviati dal frontend
        mappingData = request.get_json()
        schemaInput = session.get('inputSchemaStructure')
        # estraggo le chiavi che sono array
         # Funzione ricorsiva per trovare le chiavi che sono array
        def findArrayKeys(schema, tmp=None):
            if tmp is None:
                tmp = []
                
            if isinstance(schema, dict):
                # Per ogni chiave nel dizionario
                for key, value in schema.items():
                    # Se il valore è un array o è dichiarato come tale lo aggiungo a tmp e richiamo ricorsivamente
                    if isinstance(value, list) or (isinstance(value, dict) and value.get('type') == 'array'):
                        if key not in tmp:
                            tmp.append(key)
                    # Continuo la ricerca ricorsiva
                    findArrayKeys(value, tmp)
            elif isinstance(schema, list):
                # Esploro ricorsivamente ogni elemento della lista
                for item in schema:
                    findArrayKeys(item, tmp)
            return tmp
        # Estraggo le chiavi che sono array
        arrayKeys = findArrayKeys(schemaInput)
        # timestamp se non mappato
        if 'timestamp' not in mappingData:
            mappingData['timestamp'] = {'value': 'timestamp di arrivo del dato ad ODA', 'isConstant': True}
        # Genero il codice della funzione di mapping
        functionLines = []
        functionLines.append("import json")
        functionLines.append("def mappingFunction(inputData):")
        functionLines.append("    from datetime import datetime, timedelta")
        functionLines.append("    mappedData = {}")
        functionLines.append("    if isinstance(inputData.get('data'), str):")
        functionLines.append("        inputData['data'] = json.loads(inputData['data'])")
        keys = []
        # Mappo i campi obbligatori per ODA
        for key in mappingData.keys():
            if key in ['timestamp', 'generator_id', 'topic']:
                value = mappingData[key]['value']
                isConstant = mappingData[key].get('isConstant', False)
                if isConstant:
                    functionLines.append(f"    mappedData['{key}'] = '{value}'")
                else:
                    functionLines.append(f"    mappedData['{key}'] = inputData.get('{value}')")
            else:
                keys.append(key)
        # funzione per ottenere il percorso del valore nello schema input
        def getPath(key, mappingData):
            value = mappingData[key]['value']
            if mappingData[key]['isConstant']:
                if key == 'latitude' or key == 'longitude':
                    return value
                else:
                    return f"'{value}'" 
            else:
                array = value.split('.')
                path = 'inputData'
                for p in array:
                    if p in arrayKeys:
                        path += f"['{p}'][0]"
                    else:
                        path += f"['{p}']"
                return path
        # estraggo i percorsi
        start = getPath('start_ts', mappingData)
        end = getPath('end_ts', mappingData)
        timezone = getPath('timeZone', mappingData)
        timestampODA = mappingData.get('timestamp')['value']
        timestampODAArray = timestampODA.split('.')
        pathTime = 'inputData'
        for p in timestampODAArray:
            pathTime += f"['{p}']"
        deltaHour = timezone.strip("'").replace('UTC', '').split(':')[0]
        if deltaHour.startswith('+0') or deltaHour.startswith('-0'):
            deltaHour = deltaHour[0] + deltaHour[2:]
        elif deltaHour.startswith('0'):
            deltaHour = deltaHour[1:]
        latitude = getPath('latitude', mappingData)
        longitude = getPath('longitude', mappingData)
        buildingID = getPath('BuildingID', mappingData)
        buildingName = getPath('BuildingName', mappingData)
        electricConsumption = getPath('ElectricConsumption', mappingData)
        # Mappo in mappedData la struttura di SCP
        functionLines.append("    mappedData['data'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset']['context'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset']['context']['producer'] = {'id': 'Solution-ID'}")
        functionLines.append(f"    mappedData['data']['UrbanDataset']['context']['timeZone'] = {timezone}")
        functionLines.append(f"    baseTimestamp = datetime.fromisoformat({pathTime})")
        functionLines.append(f"    adjustedTimestamp = baseTimestamp + timedelta(hours=int({deltaHour}))")
        functionLines.append(f"    mappedData['data']['UrbanDataset']['context']['timestamp'] = adjustedTimestamp.strftime('%Y-%m-%dT%H:%M:%S')")
        functionLines.append(f"    mappedData['data']['UrbanDataset']['context']['coordinates'] = {{'latitude': {latitude}, 'longitude': {longitude}}}")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification']['id'] = {'value': 'BuildingElectricConsumption-2.0'}")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification']['name'] = 'Building Electric Consumption'")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification']['uri'] = 'https://smartcityplatform.enea.it/specification/semantic/2.0/ontology/scps-ontology-2.0.owl#BuildingElectricConsumption'")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification']['properties'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset']['specification']['properties']['propertyDefinition'] = [")
        functionLines.append("        {'propertyName': 'BuildingID', 'dataType': 'string', 'unitOfMeasure': 'dimensionless'},")
        functionLines.append("        {'propertyName': 'BuildingName', 'dataType': 'string', 'unitOfMeasure': 'dimensionless'},")
        functionLines.append("        {'propertyName': 'ElectricConsumption', 'dataType': 'double', 'unitOfMeasure': 'kilowattHour', 'measurementType': 'average'},")
        functionLines.append("        {'propertyName': 'period', 'subProperties': {'propertyName': ['start_ts', 'end_ts']}},")
        functionLines.append("        {'propertyName': 'start_ts', 'dataType': 'dateTime', 'unitOfMeasure': 'dimensionless'},")
        functionLines.append("        {'propertyName': 'end_ts', 'dataType': 'dateTime', 'unitOfMeasure': 'dimensionless'}")
        functionLines.append("    ]")
        functionLines.append("    mappedData['data']['UrbanDataset']['values'] = {}")
        functionLines.append("    mappedData['data']['UrbanDataset']['values']['line'] = [")
        functionLines.append("        {")
        functionLines.append("            'id': 1,")
        functionLines.append(f"            'period': {{'start_ts': ({start}).replace('Z',''), 'end_ts': ({end}).replace('Z','')}},")
        functionLines.append("            'property': [")
        functionLines.append(f"                {{'name': 'BuildingID', 'val': {buildingID}}},")
        functionLines.append(f"                {{'name': 'BuildingName', 'val': {buildingName}}},")
        functionLines.append(f"                {{'name': 'ElectricConsumption', 'val': str({electricConsumption})}}")
        functionLines.append("            ]")
        functionLines.append("        }")
        functionLines.append("    ]")
        functionLines.append("    return mappedData")
        # UniscO il codice in un'unica stringa
        mappingFunction = "\n".join(functionLines)
        app.logger.info("Mapping function generated")
        # RestituiSCO la funzione di mapping al frontend
        return jsonify({'mappingFunction': mappingFunction}), 200
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante la generazione della funzione di mapping: {str(e)}"}), 500
    

# endpoint per il salvataggio della funzione di mapping e del suo nome
@app.route('/saveMappingFunction', methods=['POST'])
def saveMappingFunction():
    try:
        # Ottiengo i dati inviati dal frontend
        mappingData = request.get_json()
        mappingFunction = mappingData['mappingFunction']
        mappingName = mappingData['mappingName']
        schemaDest = session.get('destSchemaStructure')
        schemaInput = session.get('inputSchemaStructure')
        schemaDestName = mappingData['destSchemaName']
        # Verifica che siano forniti tutti i dati necessari
        if not mappingName or not mappingFunction:
            return jsonify({'error': "Nome o funzione di mapping mancanti"}), 400
        # creo il pacchetto da inviare a data_transformer
        payload = {
            'mappingFunction': mappingFunction,
            'mappingName': mappingName,
            'schemaDest': schemaDest,
            'schemaInput': schemaInput,
            'schemaDestName': schemaDestName
        }
        URL = DATA_TRANSFORMER_URL + '/saveMappingFunction'
        app.logger.info("Sending request to URL: " + URL)
        response = requests.post(URL, json=payload)
        app.logger.info("request sent")
        # Se la richiesta è andata a buon fine restituisco il messaggio di successo
        if response.status_code == 201:
            return jsonify({'response': response.json()}), 200
        else:
            return jsonify({'error': f"{response.json().get('error')}"}), response.status_code
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante il salvataggio della funzione di mapping"}), 500