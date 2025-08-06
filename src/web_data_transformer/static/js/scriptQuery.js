let tempLink = null;
let schemaNames = []

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('queryForm');
    // carico dal db i nomi degli schemi
    fetch('/getSchemaNames')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            // data è una lista di nomi di schemi
            if (!Array.isArray(data.schema_names)) {
                throw new Error('Formato dei dati non valido');
            }
            // Popolo il select con i nomi degli schemi, e.g. ["schema1", "schema2"]
            schemaNames = data.schema_names;
            //schemaNames = data.schema_
            const schemaSelect = document.getElementById('schema');
            // Aggiungo le opzioni al select
            schemaNames.forEach(schema => {
                const option = document.createElement('option');
                option.value = schema;
                option.textContent = schema;
                schemaSelect.appendChild(option);
            });
        })
        .catch(error => {
            document.getElementById('errorText').textContent = 'Errore: ' + error.message;
            document.getElementById('errorMessage').style.display = 'flex';
        });
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // azzero l'anteprima
        document.getElementById('previewData').textContent = '';
        document.getElementById('previewContainer').style.display = 'none';
        // Controllo che almeno uno dei campi sia compilato
        const start = document.getElementById('start').value;
        const stop = document.getElementById('stop').value;
        const topic = document.getElementById('topic').value;
        const generator_id = document.getElementById('generator_id').value;
        const schema = document.getElementById('schema').value;
        if (!start && !stop && !topic && !generator_id) {
            document.getElementById('errorText').textContent = 'Errore: compilare almeno uno dei campi (start, stop, topic, generator_id).';
            document.getElementById('errorMessage').style.display = 'flex';
            return;
        }
        // Controllo del formato data per start e stop
        const dateFormatRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
        if (start && !dateFormatRegex.test(start)) {
            document.getElementById('errorText').textContent = 'Errore: il campo start deve essere nel formato YYYY-MM-DDTHH:MM:SSZ';
            document.getElementById('errorMessage').style.display = 'flex';
            return;
        }
        if (stop && !dateFormatRegex.test(stop)) {
            document.getElementById('errorText').textContent = 'Errore: il campo stop deve essere nel formato YYYY-MM-DDTHH:MM:SSZ';
            document.getElementById('errorMessage').style.display = 'flex';
            return;
        }
        // preparo il pacchetto con le richieste della query
        const formData = {
            start: start,
            stop: stop,
            topic: topic,
            generator_id: generator_id,
            schema: schema
        };
        // invio la richiesta di query
        fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            // Mostro l'anteprima dei primi record
            document.getElementById('previewData').textContent = JSON.stringify(data.preview, null, 2);
            document.getElementById('previewContainer').style.display = 'block';
            // messaggio di successo
            document.getElementById('successText').textContent = 'Query andata a buon fine!';
            document.getElementById('successMessage').style.display = 'flex';
            // Mostro il pulsante per il download
            const downloadButton = document.getElementById('downloadButton');
            downloadButton.style.display = 'block';
            // Rimuovo eventuali listener precedenti per evitare duplicazioni
            const newButton = downloadButton.cloneNode(true);
            downloadButton.parentNode.replaceChild(newButton, downloadButton);
            // Aggiungo l'evento per il download del file compresso
            newButton.addEventListener('click', function() {
                // Pulisco link precedenti
                if (tempLink && document.body.contains(tempLink)) {
                    document.body.removeChild(tempLink);
                    URL.revokeObjectURL(tempLink.href);
                }
                // Decodifico i dati Base64 ricevuti dal backend
                const compressedData = atob(data.compressed_data);
                // Converto la stringa decodificata in un array di byte
                const byteArray = new Uint8Array(compressedData.length);
                for (let i = 0; i < compressedData.length; i++) {
                    byteArray[i] = compressedData.charCodeAt(i);
                }
                // Creo un Blob con i dati compressi
                const blob = new Blob([byteArray], { type: 'application/octet-stream' });
                // Creo un URL temporaneo per il download
                const url = URL.createObjectURL(blob);
                // Creo un elemento <a> per avviare il download
                tempLink = document.createElement('a');
                tempLink.href = url;
                // Creo il nome del file
                let nomeFile = 'query_result';
                if (schema !== '') {
                    nomeFile += '_' + schema;
                }
                nomeFile += '.' + data.file_extension;
                tempLink.download = nomeFile;
                // Simula il click per avviare il download
                document.body.appendChild(tempLink);
                tempLink.click();
            });
        })
        .catch(error => {
            document.getElementById('errorText').textContent = 'Errore: ' + error.message;
            document.getElementById('errorMessage').style.display = 'flex';
        });
    });
});

function closeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.classList.remove('d-flex');
    messageElement.style.display = 'none';
}

function resetLink() {
    if (tempLink && document.body.contains(tempLink)) {
        document.body.removeChild(tempLink);
        URL.revokeObjectURL(tempLink.href);
        tempLink = null;
    }
}