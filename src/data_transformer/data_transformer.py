from datetime import datetime
import json
import os
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Configurazione della sessione
app.secret_key = 'ODA1.1secret_key'
# Cartelle per salvare i file di input e output
INPUT_FOLDER = 'static/inputSchema_files'
DEST_FOLDER = 'static/destSchema_files'
app.config['INPUT_FOLDER'] = INPUT_FOLDER
app.config['DEST_FOLDER'] = DEST_FOLDER
# se non esistono creo le cartelle
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(DEST_FOLDER, exist_ok=True)

SCHEMA_DEST_DEFAULT = {"POLIMI": {
                        "timestamp": "integer", 
                        "generator_id": "string", 
                        "topic": "string", 
                        "data": {
                            "attribute_name": {
                                "value": "any",
                                "unit": "string or null"
                            }
                        }
                    },
            "SCP": {
                    "timestamp": "integer",
                    "generator_id": "string",
                    "topic": "string",
                    "data": {
                            "UrbanDataset" : {
                            "context" : {
                                "producer" : {
                                    "id" : "Solution-ID",
                                    "schemeID" : "SCPS"
                                },
                                "timeZone" : "UTC+1",
                                "timestamp" : "2024-11-26T15:09:46",
                                "coordinates" : {
                                    "format" : "WGS84-DD",
                                    "latitude" : 0.0,
                                    "longitude" : 0.0,
                                    "height" : 0.0
                                },
                                "language" : "IT",
                                "note" : ""
                            },
                            "specification" : {
                                "version" : "2.0",
                                "id" : {
                                    "value" : "BuildingElectricConsumption-2.0",
                                    "schemeID" : "SCPS"
                                },
                                "name" : "Building Electric Consumption",
                                "uri" : "https://smartcityplatform.enea.it/specification/semantic/2.0/ontology/scps-ontology-2.0.owl#BuildingElectricConsumption",
                                "properties" : {
                                    "propertyDefinition" : [
                                        {
                                            "propertyName" : "BuildingID",
                                            "propertyDescription" : "Identificatore dell'edificio",
                                            "dataType" : "string",
                                            "unitOfMeasure" : "dimensionless"
                                        },
                                        {
                                            "propertyName" : "BuildingName",
                                            "propertyDescription" : "Etichetta associata all'edificio",
                                            "dataType" : "string",
                                            "unitOfMeasure" : "dimensionless"
                                        },
                                        {
                                            "propertyName" : "ElectricConsumption",
                                            "propertyDescription" : "Consumo energia elettrica",
                                            "dataType" : "double",
                                            "unitOfMeasure" : "kilowattHour",
                                            "measurementType" : "average"
                                        },
                                        {
                                            "propertyName" : "period",
                                            "propertyDescription" : "Periodo durante il quale sono stati rilevati i dati riportati nella riga",
                                            "subProperties" : {
                                                "propertyName" : [
                                                    "start_ts",
                                                    "end_ts"
                                                ]
                                            }
                                        },
                                        {
                                            "propertyName" : "start_ts",
                                            "propertyDescription" : "Marca temporale indicante l'inizio del periodo",
                                            "dataType" : "dateTime",
                                            "unitOfMeasure" : "dimensionless"
                                        },
                                        {
                                            "propertyName" : "end_ts",
                                            "propertyDescription" : "Marca temporale indicante la fine del periodo",
                                            "dataType" : "dateTime",
                                            "unitOfMeasure" : "dimensionless"
                                        }
                                    ]
                                }
                            },
                            "values" : {
                                "line" : [
                                    {
                                        "id" : 1,
                                        "period" : {
                                            "start_ts" : "2000-12-31T00:00:00",
                                            "end_ts" : "2000-12-31T23:59:00"
                                        },
                                        "property" : [
                                            {
                                                "name" : "BuildingID",
                                                "val" : " "
                                            },
                                            {
                                                "name" : "BuildingName",
                                                "val" : " "
                                            },
                                            {
                                                "name" : "ElectricConsumption",
                                                "val" : " "
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }

# endpoint per la pagina principale
@app.route('/')
def index():
    return render_template('index.html')

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
        if not selectedSchema in SCHEMA_DEST_DEFAULT.keys():
            # se non c'è il nome dello schema restituisco un errore
            return jsonify({'error': 'Non esiste lo schema selezionato'}), 400
        # Schema POLIMI o SCP (successivamente saranno file JSON con la struttura di POLIMI o SCP)
        jsonStructure = SCHEMA_DEST_DEFAULT[selectedSchema]
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
        return jsonify({'jsonStructure': jsonData}), 200
    except Exception as e:
        # se ci sono errori restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante il caricamento del file JSON: {e}"}), 500

# endpoint per la generazione della funzione di mapping 
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
        functionLines.append("def mappingFunction(inputData):")
        functionLines.append("    mappedData = {}")
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
        # Restituisci la funzione di mapping al frontend
        return jsonify({'mappingFunction': mappingFunction}), 200
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante la generazione della funzione di mapping: {str(e)}"}), 500


# endpoint per la generazione della funzione di mapping per FILE generico
@app.route('/generateMappingFunctionFILE', methods=['POST'])
def generateMappingFunctionFILE():
    try:
        # Ottieni i dati inviati dal frontend
        mappingData = request.get_json()
        destSchemaStructure = session.get('destSchemaStructure')
        print(json.dumps(mappingData, indent=4))
        # Controllo per timestamp
        if 'timestamp' not in mappingData:
            mappingData['timestamp'] = [{'value': 'timestamp di arrivo del dato ad ODA', 'isConstant': True}]
        
        def get_array_keys(destSchemaStructure):
            array_keys = []

            def find_arrays(structure, current_path=""):
                if isinstance(structure, dict):
                    for key, value in structure.items():
                        new_path = f"{current_path}.{key}" if current_path else key
                        if isinstance(value, list):
                            array_keys.append(key)
                        elif isinstance(value, dict):
                            find_arrays(value, new_path)

            find_arrays(destSchemaStructure)
            return array_keys


        def initialize_mapped_data(destSchemaStructure):
            """Funzione che inizializza la struttura di mappedData."""
            def create_structure(structure):
                if isinstance(structure, dict):
                    return {key: create_structure(value) for key, value in structure.items()}
                elif isinstance(structure, list):
                    return [initialize_mapped_data(structure[0])]
                else:
                    return 'None'

            return create_structure(destSchemaStructure)

        arrays = get_array_keys(destSchemaStructure)
        arrayKey = []
        # Genera il codice della funzione di mapping
        functionLines = []
        functionLines.append("def mappingFunction(inputData):")
        functionLines.append("    mappedData = " + json.dumps(initialize_mapped_data(destSchemaStructure)))
        # Funzione ricorsiva per gestire strutture nidificate
        def process_mapping(key, items, indent_level=1):
            indent = "    " * indent_level
            outPathArray = key.split('.')
            outPath = 'mappedData'
            for p in outPathArray:
                outPath += f"['{p}']"
            if isinstance(items, dict):
                items = [items]
            for item in items:
                # Se è una costante, usa direttamente il valore di 'key'
                if item.get('isConstant', False):
                    functionLines.append(f"{indent}{outPath} = '{item.get('value')}'")
                    continue
                isArray = any(el in key.split('.') for el in arrays)
                if isArray:
                    array, attribute = outPathArray, outPathArray[-1]   
                    for p in array:
                        array += f"['{p}']"
                    functionLines.append(f"{indent}for elem in {array}:")               
                else:
                    inPathArray = item.get('value', '').split('.')
                    inPath = 'inputData'
                    for p in inPathArray:
                        inPath += f"['{p}']"
                    functionLines.append(f"{indent}{outPath} = {inPath}")   
        # Elabora ogni campo nel mappingData
        for key, items in mappingData.items():
            process_mapping(key, items)
        functionLines.append("    return mappedData")
        # Unisci il codice in un'unica stringa
        mappingFunction = "\n".join(functionLines)
        # ritorno del mappedData
        return jsonify({'mappingFunction': mappingFunction}), 200
    except Exception as e:
        # Se c'è un errore restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante la generazione della funzione di mapping: {str(e)}"}), 500    