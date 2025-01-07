// variabili globali per il parsing degli schemi
let inputJsonStructure = {};
let destJsonStructure = {};


// funzione per il caricamento del file JSON con lo schema di input
document.getElementById('uploadInputSchema').onsubmit = function(event) {
    // blocco del comportamento di default
    event.preventDefault();
    var formData = new FormData(event.target);
    // Invia la richiesta POST al server con corpo il file sottomesso nel form
    fetch('/uploadInputSchema', {
        method: 'POST',
        body: formData
    })
    // converto la risposta in json
    .then(response => response.json())
    .then(data => {
        // se la risposta del server contiene il campo error stampo l'errore
        if (data.error) {
            showInputError(data.error);
        } else {
            // estrago la struttura del json che mi ritorna il server
            inputJsonStructure = data.jsonStructure;
            // genero il codice necesssario per modificare i campi del json
            const editor = document.getElementById('inputJsonStructure');
            editor.innerHTML = generateInputSchemaEditor(inputJsonStructure);
            // mostro l'editor altrimenti nascosto
            document.getElementById('inputJsonEditor').style.display = 'block';
            document.getElementById('inputJsonEditor').classList.remove('hidden');
        }
    })
    // catturo eventuali errori
    .catch(error => console.error('Errore:', error));
};


// funzione per inviare e caricare lo schema di destinazione scelto
document.getElementById("uploadDestSchema").onsubmit = function(event) {
    // Blocca il comportamento di default (evitare il refresh della pagina)
    event.preventDefault();
    // Ottieni il valore selezionato dal dropdown
    var selectedSchema = document.getElementById("destSchema").value;
    // Controlla se un'opzione è stata selezionata
    if (selectedSchema === "") {
        showDestError("Seleziona un formato di destinazione.");
        return;
    }
    // Invia la richiesta al server
    fetch('/uploadDestSchema', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ destSchema: selectedSchema })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showDestError(data.error);
        } else {
            // Usa la struttura JSON per visualizzare il risultato
            const destJsonStructure = data.jsonStructure;
            const editor = document.getElementById('destJsonStructure');
            editor.innerHTML = generateDestDroppableCardPOLIMI(destJsonStructure);
            // mostro l'editor altrimenti nascosto
            document.getElementById('destJsonEditor').style.display = 'block';
            document.getElementById('destJsonEditor').classList.remove('hidden');
        }
    })
    .catch(error => console.error('Errore:', error));
};

// funzione per mostrare l'errore metà di input
function showInputError(message) {
    const errorMessage = document.getElementById('errorMessageInput');
    const errorText = document.getElementById('errorTextInput');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}


// funzione per mostrare messaggio di successo metà di input
function showInputSuccess(message) {
    const successMessage = document.getElementById('successMessageInput');
    const successText = document.getElementById('successTextInput');
    successText.textContent = message;
    successMessage.style.display = 'flex';
}


// funzione per mostrare l'errore metà di destinazione
function showDestError(message) {
    const errorMessage = document.getElementById('errorMessageDest');
    const errorText = document.getElementById('errorTextDest');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}


// funzione per mostrare messaggio di successo metà di destinazione
function showDestSuccess(message) {
    const successMessage = document.getElementById('successMessageDest');
    const successText = document.getElementById('successTextDest');
    successText.textContent = message;
    successMessage.style.display = 'flex';
}


// Funzione per chiudere il messaggio di errore o successo
function closeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.classList.remove('d-flex');
    messageElement.style.display = 'none';
}


// funzione per generare il codice necessario per modificare i campi dello schema di input
function generateInputSchemaEditor(jsonStructure, parentKey = '') {
    let html = '';
    for (let key in jsonStructure) {
        const currentKey = parentKey ? `${parentKey}.${key}` : key;
        const value = jsonStructure[key];

        if (Array.isArray(value)) {
            // Se la proprietà è un array
            html += `
                <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
                    <span class="key-text fw-bold">${key} (Array)</span>
                    <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${currentKey}')">Elimina</button>
                </div>
            `;
            // Aggiungiamo gli elementi dell'array senza una indentazione extra
            value.forEach((item, index) => {
                const arrayItemKey = `${currentKey}[${index}]`;
                if (typeof item === 'object' && item !== null) {
                    // Se l'elemento dell'array è un oggetto, chiamata ricorsiva
                    html += generateInputSchemaEditor(item, arrayItemKey);
                } else {
                    // Se l'elemento dell'array è un valore primitivo
                    html += `
                        <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${arrayItemKey}" id="${arrayItemKey}">
                            <span class="key-text fw-bold">${arrayItemKey}</span>
                            <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${arrayItemKey}')">Elimina</button>
                        </div>
                    `;
                }
            });
        } else if (typeof value === 'object' && value !== null) {
            // Se la proprietà è un oggetto, chiamata ricorsiva
            html += `
                <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
                    <span class="key-text fw-bold">${key} (Object)</span>
                    <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${currentKey}')">Elimina</button>
                </div>
                <div class="nested-items">
                    ${generateInputSchemaEditor(value, currentKey)}
                </div>
            `;
        } else {
            // Se la proprietà è un valore primitivo
            html += `
                <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
                    <span class="key-text fw-bold">${key}</span>
                    <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${currentKey}')">Elimina</button>
                </div>
            `;
        }
    }
    return html;
}

    
// Funzione per rimuovere un elemento dato il suo ID unico
function removeInputSchemaElement(uniqueId) {
    const item = document.getElementById(uniqueId);
    if (item) {
        item.remove();
    }
}


// Funzione per generare il codice necessario per creare le card dei campi a seconda dello schema di destinazione (per ora solo POLIMI)
function generateDestDroppableCardPOLIMI(destJsonStructure) {
    let html = '';
    // Iteriamo su ogni chiave della struttura del JSON di destinazione
    for (let key in destJsonStructure) {
        // se la chiave è data creo la card per permettere di aggiungere l'unita di misura e il valore
        if (key === 'data') {
            html += `
                <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-attributes">
                    <div class="card-header text-white">
                        <p class="card-title">Data</p>
                    </div>
                    <div class="card-body">
                        <div class="dropzone" id="dropzone-attributes" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                    </div>
                </div>
            `;
            continue;
        }
        // Per ogni chiave, creiamo una card
        html += `
            <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${key}">
                <div class="card-header text-white">
                    <p class="card-title">${key}</p>
                </div>
                <div class="card-body">
                    <div class="dropzone" id="dropzone-${key}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                </div>
            </div>
        `;
    }
    return html;
}


// Permette di trascinare sopra una zona
function allowDrop(ev) {
    ev.preventDefault();
}
  

// Funzione per gestire il drag
function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
}


// Funzione per gestire il drop
function drop(ev) {
    ev.preventDefault();
    const data = ev.dataTransfer.getData("text");
    const draggedElement = document.getElementById(data);
    // Verifica se l'elemento è stato droppato nella dropzone degli attributi
    if (ev.target.classList.contains("dropzone")) {
        // Verifica se l'elemento è già nella dropzone
        if (!ev.target.contains(draggedElement)) {
            // Aggiungi l'elemento alla dropzone degli attributi
            ev.target.appendChild(draggedElement);
            // Aggiungi i campi per valore e unità di misura solo se è la dropzone degli attributi
            if(ev.target.id === "dropzone-attributes") {
                addUnitInput(draggedElement);
            }
            // Aggiungi un pulsante per il ripristino
            if (!draggedElement.querySelector(".restore-button")) {
                const restoreButton = document.createElement("button");
                restoreButton.textContent = "Indietro";
                restoreButton.className = "restore-button btn btn-secondary btn-sm ms-2";
                restoreButton.onclick = () => restoreToOrigin(draggedElement, ev.target.id);
                draggedElement.appendChild(restoreButton);
            }
            // Rimuovi il bottone di eliminazione se esiste
            const deleteButton = draggedElement.querySelector(".remove-button");
            if (deleteButton) {
                deleteButton.remove();
            }
            // Regola l'altezza della dropzone
            adjustDropzoneHeight(ev.target);
            // aggiunge il bottone per il mapping
            document.getElementById('mapButton').classList.remove('hidden');
        }
    }
}


// Funzione per aggiungere i campi di valore e unità di misura
function addUnitInput(draggedElement) {
    const inputContainer = document.createElement("div");
    inputContainer.classList.add("d-flex", "align-items-center", "mt-2");
    const unitInput = document.createElement("input");
    unitInput.classList.add("form-control", "me-2");
    unitInput.placeholder = "Inserisci unità";
    inputContainer.appendChild(unitInput);
    draggedElement.appendChild(inputContainer);
}


// Funzione per ripristinare un elemento alla sezione di origine
function restoreToOrigin(element, idDropzone) {
    const originSection = document.getElementById("inputJsonStructure");
    const restoreButton = element.querySelector(".restore-button");
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    
    // Rimuoviamo il pulsante di ripristino
    if (restoreButton) {
        restoreButton.remove();
    }
    // Ripristina l'elemento alla sua sezione originale
    originSection.appendChild(element);
    // Rimuovi i campi valore e unità quando l'elemento viene ripristinato
    const valueUnitContainer = element.querySelector(".d-flex");
    if (valueUnitContainer) {
        valueUnitContainer.remove();
    }
    // Aggiungi di nuovo il bottone di eliminazione
    const deleteButton = document.createElement("button");
    deleteButton.classList.add("remove-button", "btn", "btn-danger", "btn-sm");
    deleteButton.textContent = "Elimina";
    deleteButton.onclick = () => removeInputSchemaElement(element.id); // Associa la rimozione
    // Aggiungi il bottone di eliminazione all'elemento ripristinato
    element.appendChild(deleteButton);
    adjustDropzoneHeight(document.getElementById(idDropzone));
    // Nascondi il mapButton se tutte le dropzone sono vuote
    let allDropzonesEmpty = true;
    for (const dropzone of dropzones) {
        if (dropzone.childElementCount > 0) {
            allDropzonesEmpty = false;
            break;
        }
    }
    if (allDropzonesEmpty) {
        document.getElementById('mapButton').classList.add('hidden');
    }
}


// Funzione per aggiustare l'altezza della dropzone e ripristinare la scritta iniziale se vuota
function adjustDropzoneHeight(dropzone) {
    const children = dropzone.children;
    const dropzoneHeight = 60 + (children.length * 60); 
    dropzone.style.minHeight = `${dropzoneHeight}px`;
    dropzone.style.maxHeight = "300px";
    dropzone.style.overflowY = "auto";
}


// Funzione per raccogliere il mapping e inviarlo al backend
document.getElementById('mapButton').onclick = function(event) {
    event.preventDefault();

    // Raccolta dei dati mappati
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    const mappingData = {};

    dropzones.forEach(dropzone => {
        const dropzoneId = dropzone.id.replace('dropzone-', '');
    
        // Se la dropzone è "attributes", dobbiamo accumulare gli attributi in un array
        if (dropzoneId === 'attributes') {
            mappingData[dropzoneId] = []; // Inizializziamo un array per gli attributi
            const children = dropzone.children;
            for (const child of children) {
                const key = child.dataset.key;
                const unitInput = child.querySelector('input[placeholder="Inserisci unità"]');
                // Aggiungiamo ogni attributo come oggetto con key, value e unit
                if (key) {
                    mappingData[dropzoneId].push({
                        key: key,
                        value: inputJsonStructure[key],
                        unit: unitInput.value ? unitInput.value : "None"
                    });
                }
            }
        } else {
            // Per altri dropzoneId, memorizziamo semplicemente il valore (chiave) come stringa
            const children = dropzone.children;
            for (const child of children) {
                const key = child.dataset.key;
                if (key) {
                    mappingData[dropzoneId] = key;
                }
            }
        }
    });
    // Invia il mapping al backend
    fetch('/generateMappingFunction', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(mappingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Errore: ${data.error}`);
        } else {
            // Visualizza la funzione di mapping nel frontend
            document.getElementById('mappingFunctionContainer').textContent = data.mappingFunction;
            mappingFunctionContainer.style.display = 'block';
            document.getElementById('mappingFunctionContainer').classList.remove('hidden');
            document.getElementById('mappingFunctionContainer').scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => console.error('Errore:', error));
};