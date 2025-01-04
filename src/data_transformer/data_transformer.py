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

SCHEMA = {"POLIMI": {
                        "timestamp": "integer", 
                        "generator_id": "string", 
                        "topic": "string", 
                        "data": {
                            "attribute_name": {
                                "value": "any",
                                "unit": "string or null"
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
            return jsonify({'error': 'Il file deve essere un file JSON'}), 400
        # creo il path completo del file e lo salvo
        inputFilename = secure_filename(file.filename)
        session['inputFilename'] = inputFilename
        inputSchemaPath = os.path.join(app.config['INPUT_FOLDER'], inputFilename)
        file.save(inputSchemaPath)
        # Leggo il contenuto del file
        with open(inputSchemaPath, 'r') as f:
            lines = f.read()
        # Cerco di caricare il contenuto come JSON
        try:
            jsonData = json.loads(lines)
        except json.JSONDecodeError as e:
            # se la decodifica fallisce restituisco un errore
            return jsonify({'error': f"Errore nella decodifica del file JSON: {e}"}), 400
        # restituisce la struttura del JSON al frontend
        return jsonify({'jsonStructure': jsonData}), 200
    except Exception as e:
        # se ci sono errori restituisco un messaggio di errore
        return jsonify({'error': f"Errore durante il caricamento del file JSON: {e}"}), 500


@app.route('/uploadDestSchema', methods=['POST'])
def uploadDestSchema():
    try:
        # Ottieni il nome dello schema inviato dal frontend
        requestJson = request.get_json()
        # Estrai il valore della destinazione (destSchema)
        selectedSchema = requestJson.get('destSchema')
        if not selectedSchema in SCHEMA.keys():
            return jsonify({'error': 'Non esiste lo schema selezionato'}), 400
        # Schema POLIMI
        jsonStructure = SCHEMA[selectedSchema]
        return jsonify({'jsonStructure': jsonStructure})

    except Exception as e:
        # Se c'è un errore restituiamo un messaggio di errore
        return jsonify({'error': str(e)}), 500
