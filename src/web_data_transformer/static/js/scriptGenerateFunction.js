// variabili globali che contengono la struttura degli schemi di input e di destinazione
let inputJsonStructure = {};
let destJsonStructure = {};
let removedElements = [];
let selectedSchema;
let lastSubmitted = null;
let alwaysPresent = ['timestamp', 'generator_id', 'topic'];
let scpRequired = ['latitude', 'longitude', 'timeZone', 'BuildingID', 'BuildingName', 'ElectricConsumption', 'period'];

// funzione per il caricamento del file JSON con lo schema di input
document.getElementById('uploadInputSchema').onsubmit = function (event) {
    // blocco del comportamento di default
    event.preventDefault();
    var formData = new FormData(event.target);
    // Invia la richiesta POST al server con corpo il file sottomesso nel form
    fetch('/uploadInputSchema', {
        method: 'POST',
        body: formData
    })
        // converto la risposta in json (struttura json)
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
                // mostro la struttura del json caricato
                showModal("Formato schema di input caricato", JSON.stringify(inputJsonStructure, null, 2));
                // mostro l'editor altrimenti nascosto
                document.getElementById('inputJsonEditor').style.display = 'block';
                document.getElementById('inputJsonEditor').classList.remove('hidden');
            }
        })
        // catturo eventuali errori
        .catch(error => console.error('Errore:', error));
};


// funzione per inviare e caricare lo schema di destinazione scelto tra POLIMI e SCP
document.getElementById("uploadDestSchemaSelect").onsubmit = function (event) {
    // Blocca il comportamento di default (evitare il refresh della pagina)
    event.preventDefault();
    if (lastSubmitted === "uploadDestSchemaFile") {
        document.getElementById('uploadDestSchemaFile').reset();
    }
    lastSubmitted = "uploadDestSchemaSelect";
    // Ottieni il valore selezionato dal dropdown
    selectedSchema = document.getElementById("destSchema").value;
    // Controlla se un'opzione è stata selezionata
    if (selectedSchema === "") {
        showDestError("Seleziona un formato di destinazione.");
        return;
    }
    // nei casi di default invia la richiesta al server con lo schema json
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
                if (selectedSchema === "POLIMI") {
                    editor.innerHTML = generateDestDroppableCardPOLIMI(destJsonStructure);
                } else if (selectedSchema === "SCP") {
                    editor.innerHTML = generateDestDroppableCardSCP(destJsonStructure);
                }
                // mostro la struttura del json caricato
                showModal("Formato schema di destinazione caricato", JSON.stringify(destJsonStructure, null, 2));
                // mostro l'editor altrimenti nascosto
                document.getElementById('destJsonEditor').style.display = 'block';
                document.getElementById('destJsonEditor').classList.remove('hidden');
            }
        })
        // catturo eventuali errori
        .catch(error => console.error('Errore:', error));
};


// funzione per il caricamento del file JSON con lo schema di destinazione generico
document.getElementById('uploadDestSchemaFile').onsubmit = function (event) {
    event.preventDefault();
    if (lastSubmitted === "uploadDestSchemaSelect") {
        document.getElementById('uploadDestSchemaSelect').reset();
    }
    lastSubmitted = "uploadDestSchemaFile";
    selectedSchema = "FILE";
    var formData = new FormData(event.target);
    fetch('/uploadDestSchemaFile', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showDestError(data.error);
            } else {
                destJsonStructure = data.jsonStructure;
                showModal("Formato schema di destinazione caricato", JSON.stringify(destJsonStructure, null, 2));
                const editor = document.getElementById('destJsonStructure');
                editor.innerHTML = generateDestDroppableCardFILE(destJsonStructure);
                document.getElementById('destJsonEditor').style.display = 'block';
                document.getElementById('destJsonEditor').classList.remove('hidden');
            }
        })
        .catch(error => console.error('Errore:', error));
}


// Mostra il modal per schemi Json
function showModal(title, text) {
    const modal = new bootstrap.Modal(document.getElementById('autoHideModal'));
    modal.show();
    const modalTitle = document.getElementById('modalTitle');
    const modalText = document.getElementById('modalText');
    modalTitle.textContent = title;
    modalText.textContent = text;
}


// Mostra il modal per i campi mancanti
function showMissingFieldsModal(fieldsList) {
    const modal = new bootstrap.Modal(document.getElementById('missingFieldsModal'));
    modal.show();
    const modalTitle = document.getElementById('missingFieldsModalLabel');
    modalTitle.textContent = fieldsList.length >= 2 ? 
        "Inserisci i campi mancanti obbligatori per ODA" : 
        "Inserisci il campo " + fieldsList[0];

    const modalBody = document.getElementById('missingFieldsModalText');
    modalBody.innerHTML = '';

    const container = document.createElement('div');
    container.classList.add('container', 'd-flex', 'flex-column');
    container.id = 'missingFieldsContainer';
    modalBody.appendChild(container);

    fieldsList.forEach(field => {
        const input = document.createElement('input');
        input.type = 'text';
        input.classList.add('form-control', 'mb-2');
        input.placeholder = "Inserisci " + field;
        input.dataset.fieldName = field;
        container.appendChild(input);
    });

    const dropzones = fieldsList.map(field => document.getElementById('dropzone-' + field));

    document.getElementById('missingFieldsModalButton').onclick = () => {
        const inputs = document.querySelectorAll('#missingFieldsContainer input');
        let allValid = true;
        const errorMessages = [];

        inputs.forEach(input => {
            const fieldName = input.dataset.fieldName;
            const value = input.value.trim();
            input.classList.remove('is-invalid');

            if (!value) {
                allValid = false;
                input.classList.add('is-invalid');
                errorMessages.push(`Il campo ${fieldName} non può essere vuoto.`);
            } else {
                if ((fieldName === 'start_ts' || fieldName === 'end_ts') && !isValidDate(value)) {
                    allValid = false;
                    input.classList.add('is-invalid');
                    errorMessages.push(`Il campo ${fieldName} deve essere una data valida (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS).`);
                }
                if ((fieldName === 'latitude' || fieldName === 'longitude') && !isValidCoordinate(fieldName, value)) {
                    allValid = false;
                    input.classList.add('is-invalid');
                    errorMessages.push(`Il campo ${fieldName} deve essere un numero valido.`);
                }
            }
        });

        if (!allValid) {
            const errorMessageDiv = document.createElement('div');
            errorMessageDiv.classList.add('alert', 'alert-danger', 'mt-2');
            errorMessageDiv.innerHTML = errorMessages.join('<br>');
            if (!modalBody.querySelector('.alert')) {
                modalBody.appendChild(errorMessageDiv);
            }
            return;
        }

        inputs.forEach((input, i) => {
            const val = input.value.trim();
            const html = `
                <div class="constant-item draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-white shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${val}" id="${val + '-constant'}">
                    <span class="key-text fw-bold">${val}</span>
                    <button class="modify-button btn btn-primary btn-sm" onclick="modifyInputSchemaElement('${val + '-constant'}', '${val}')">Modifica</button>
                    <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${val + '-constant'}')">Elimina</button>
                </div>
            `;
            dropzones[i].innerHTML += html;
        });

        document.getElementById('mapButton').classList.remove('hidden');
        modal.hide();
    };
}


// controllo per la validità del formato data 
function isValidDate(dateString) {
    const regex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$/;
    if (!regex.test(dateString)) return false;
    const date = new Date(dateString);
    return !isNaN(date.getTime());
}


// controllo per la validità delle coordinate
function isValidCoordinate(fieldName, value) {
    const numericValue = parseFloat(value);
    if (isNaN(numericValue)) return false;
    if (fieldName === 'latitude') return numericValue >= -90 && numericValue <= 90;
    if (fieldName === 'longitude') return numericValue >= -180 && numericValue <= 180;
    return true;
}


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
    // la currentKey serve per identificare univocamente ogni elemento ed è creata come il percorso dell'elemento nel JSON separato da un punto
    // togliendo nel caso degli array la parte di indice
    let html = '';
    for (let key in jsonStructure) {
        let currentKey = parentKey ? `${parentKey}.${key}` : key;
        const value = jsonStructure[key];
        if (currentKey.includes('[') && currentKey.includes(']')) {
            currentKey = currentKey.substring(0, currentKey.indexOf('['));
            currentKey = currentKey + '.' + key
        }
        if (Array.isArray(value)) {
            // Se la proprietà è un array
            html += `
                <div class="draggable-item array-container p-3 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
                    <div class="array-header d-flex align-items-center justify-content-between">
                        <span class="key-text fw-bold">${key} [</span>
                        <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${currentKey}')">Elimina</button>
                    </div>
                    <div class="nested-items pl-3">
            `;
            // Aggiungo gli elementi dell'array indentati
            value.forEach((item) => {
                const arrayItemKey = `${currentKey}`;
                if (typeof item === 'object' && item !== null) {
                    // Se l'elemento dell'array è un oggetto, chiamata ricorsiva
                    html += generateInputSchemaEditor(item, arrayItemKey);
                } else {
                    // Se l'elemento dell'array è un valore primitivo
                    html += `
                        <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-white shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${arrayItemKey}" id="${arrayItemKey}">
                            <span class="key-text fw-bold">${arrayItemKey}</span>
                            <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${arrayItemKey}')">Elimina</button>
                        </div>
                    `;
                }
            });
            // Chiusura dell'array
            html += `
                    </div>
                    <div class="array-footer text-start key-text fw-bold">]</div>
                </div>
            `;
        } else if (typeof value === 'object' && value !== null) {
            // Se la proprietà è un oggetto
            html += `
                <div class="draggable-item object-container p-3 mb-2 rounded bg-light shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
                    <div class="object-header d-flex align-items-center justify-content-between">
                        <span class="key-text fw-bold">${key} {</span>
                        <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${currentKey}')">Elimina</button>
                    </div>
                    <div class="nested-items pl-3">
                        ${generateInputSchemaEditor(value, currentKey)}
                    </div>
                    <div class="object-footer text-start key-text fw-bold">}</div>
                </div>
            `;
        } else {
            // Se la proprietà è un valore primitivo
            html += `
                <div class="draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-white shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${currentKey}" id="${currentKey}">
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
        removedElements.push(uniqueId);
    }
}


// Funzione per generare il codice necessario per creare le card droppabili dei campi per POLIMI
function generateDestDroppableCardPOLIMI(destJsonStructure) {
    let html = '';
    // Iteriamo su ogni chiave della struttura del JSON di destinazione
    for (let key in destJsonStructure) {
        // Per ogni chiave, creiamo una card
        html += `
            <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${key}">
                <div class="card-header text-white">
                    <p class="card-title">${key} ${key === 'data' ? ' {' : ''}</p>
                </div>
                <div class="card-body">
                    <div class="dropzone" id="dropzone-${key}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
        `;
        if (key == "generator_id" || key == "topic") {
            html += `<button class="btn btn-primary" id="buttonAdd" onclick="showMissingFieldsModal(['${key}'])">+</button>`;
        }
        html += `</div>${key === 'data' ? '<div class="object-footer text-start key-text fw-bold">}</div>' : ''}</div>`;
    }
    return html;
}


// Funzione per generare il codice necessario per creare le card droppabili dei campi per SCP
function generateDestDroppableCardSCP(destJsonStructure) {
    let html = '';

    for (let key in destJsonStructure) {
        if(key != 'data') {
            html += `
            <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${key}">
                <div class="card-header text-white">
                    <p class="card-title">${key}</p>
                </div>
                <div class="card-body">
                    <div class="dropzone" id="dropzone-${key}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
            `;
            if (key == "generator_id" || key == "topic") {
                html += `<button class="btn btn-primary" id="buttonAdd" onclick="showMissingFieldsModal(['${key}'])">+</button>`;
            }
            html += `</div></div>`;
        }else {
            html +=  `
                    <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-data">
                        <div class="card-header text-white">
                            <p class="card-title">data {</p>
                        </div>
                        <div class="card-body">`;
            for(let key of scpRequired){
                if(key == 'period'){
                    html +=  `
                                <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-period">
                                    <div class="card-header text-white">
                                        <p class="card-title">period {</p>
                                    </div>
                                    <div class="card-body">
                                        <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-start_ts">
                                            <div class="card-header text-white">
                                                <p class="card-title">start_ts</p>
                                            </div>
                                            <div class="card-body">
                                                <div class="dropzone" id="dropzone-start_ts" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                                            </div>
                                        </div>

                                        <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-end_ts">
                                            <div class="card-header text-white">
                                                <p class="card-title">end_ts</p>
                                            </div>
                                            <div class="card-body">
                                                <div class="dropzone" id="dropzone-end_ts" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="object-footer text-start key-text fw-bold">}</div>
                                </div>
                            `;
                }else {
                    if(key == 'timeZone') {
                        html += `
                            <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${key}">
                                <div class="card-header text-white">
                                    <p class="card-title">${key} (UTC+/-n)</p>
                                </div>
                                <div class="card-body">
                                    <select class="form-select" id="dropzone-${key}">
                                        ${generateTimeZoneOptions()}
                                    </select>
                                </div>
                            </div>
                        `;
                    }else {
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
                }
            }
            html += `</div>
                        <div class="object-footer text-start key-text fw-bold">}</div>
                    </div>`;
        }
    }
    return html;
}


// Funzione per generare le opzioni del select per i fusi orari
function generateTimeZoneOptions() {
    const timeZones = [];
    for (let i = -12; i <= 14; i++) {
        const sign = i >= 0 ? '+' : '-';
        const padded = Math.abs(i).toString().padStart(2, '0');
        timeZones.push(`UTC${sign}${padded}:00`);
    }
    return timeZones.map(tz => `<option value="${tz}">${tz}</option>`).join('');
}


// Funzione per generare il codice necessario per creare le card droppabili dei campi per un FILE generico
function generateDestDroppableCardFILE(destJsonStructure, parentKey = '', isRoot=true) {
    let html = '';
    if(isRoot) {
        html +=  `
            <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-data">
                <div class="card-header text-white">
                    <p class="card-title">data {</p>
                </div>
                <div class="card-body">
                    ${generateDestDroppableCardFILE(destJsonStructure, parentKey, false)}
                </div>
                <div class="object-footer text-start key-text fw-bold">}</div>
            </div>
            `;
        for(let key of alwaysPresent){
            html += `
                    <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${key}">
                        <div class="card-header text-white">
                            <p class="card-title">${key}</p>
                        </div>
                        <div class="card-body">
                            <div class="dropzone" id="dropzone-${key}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                            ${(key === 'generator_id' || key === 'topic') ? `<button class="btn btn-primary" id="buttonAdd" onclick="showMissingFieldsModal(['${key}'])">+</button>` : ''}
                        </div>
                    </div>
                `;
        }
        
        return html;
    }
    
    for (let key in destJsonStructure) {
        let currentKey = parentKey ? `${parentKey}.${key}` : key;
        let value = destJsonStructure[key];

        if (Array.isArray(value)) {
            // Genera una card per l'array
            html += `
                <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${currentKey}">
                    <div class="card-header text-white">
                        <p class="card-title">${key} [</p>
                    </div>
                    <div class="card-body">
            `;

            // Itera sugli elementi dell'array
            value.forEach((item) => {
                const arrayItemKey = `${currentKey}`;

                if (typeof item === 'object' && item !== null) {
                    // Ricorsione per gli oggetti all'interno dell'array
                    html += generateDestDroppableCardFILE(item, arrayItemKey, false);
                } else {
                    // Genera una card per i valori primitivi
                    html += `
                        <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${arrayItemKey}">
                            <div class="card-header text-white">
                                <p class="card-title">${item}</p>
                            </div>
                            <div class="card-body">
                                <div class="dropzone" id="dropzone-${arrayItemKey}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                            </div>
                        </div>
                    `;
                }
            });

            // Chiude la card dell'array
            html += `
                    </div>
                    <div class="array-footer text-start key-text fw-bold">]</div>
                </div>
            `;
        } else if (typeof value === 'object' && value !== null) {
            // Ricorsione per oggetti annidati
            html += `
                <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${currentKey}">
                    <div class="card-header text-white">
                        <p class="card-title">${key} {</p>
                    </div>
                    <div class="card-body">
                        ${generateDestDroppableCardFILE(value, currentKey, false)}
                    </div>
                    <div class="object-footer text-start key-text fw-bold">}</div>
                </div>
            `;
        } else {
            // Genera una card per i valori primitivi
            html += `
                <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${currentKey}">
                    <div class="card-header text-white">
                        <p class="card-title">${key}</p>
                    </div>
                    <div class="card-body">
                        <div class="dropzone" id="dropzone-${currentKey}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
            `;
            html += `</div></div>`;
        }
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
    if (ev.target.classList.contains("dropzone")) {
        if (!ev.target.contains(draggedElement)) {
            // Crea una copia dell'elemento trascinato
            const clonedElement = draggedElement.cloneNode(true);
            // Aggiungi la copia alla dropzone
            ev.target.appendChild(clonedElement);
            // Aggiungi i campi per valore e unità di misura solo se è la dropzone degli attributi
            if (ev.target.id === "dropzone-data") {
                if (clonedElement.classList.contains("array-container")) {
                    const arrayItems = clonedElement.querySelectorAll(".draggable-item");
                    arrayItems.forEach(item => {
                        addUnitInput(item);
                        const deleteButton = item.querySelector(".remove-button");
                        if (deleteButton) {
                            deleteButton.remove();
                        }
                    });
                } else if (clonedElement.classList.contains("object-container")) {
                    const objectItems = clonedElement.querySelectorAll(".draggable-item");
                    objectItems.forEach(item => {
                        addUnitInput(item);
                        const deleteButton = item.querySelector(".remove-button");
                        if (deleteButton) {
                            deleteButton.remove();
                        }
                    });
                }
                addUnitInput(clonedElement);
                const deleteButton = clonedElement.querySelector(".remove-button");
                if (deleteButton) {
                    deleteButton.remove();
                }
            }
            const deleteButtons = clonedElement.querySelectorAll(".remove-button");
            deleteButtons.forEach(button => button.remove());
            if (!clonedElement.querySelector(".restore-button")) {
                const restoreButton = document.createElement("button");
                restoreButton.textContent = "Elimina";
                restoreButton.className = "restore-button btn btn-secondary btn-sm ms-2";
                restoreButton.onclick = () => deleteElement(clonedElement, ev.target.id);
                clonedElement.appendChild(restoreButton);
            }
            adjustDropzoneHeight(ev.target);
            document.getElementById('mapButton').classList.remove('hidden');
        }
    }
}


// Funzione per aggiungere i campi di valore e unità di misura (POLIMI)
function addUnitInput(draggedElement) {
    const inputContainer = document.createElement("div");
    inputContainer.classList.add("d-flex", "align-items-center", "mt-2");
    const unitInput = document.createElement("input");
    unitInput.id = draggedElement.id;
    unitInput.classList.add("form-control", "me-2");
    const elementName = draggedElement.id.split('.');
    const lastIndex = elementName.length - 1;
    // suggerimento dell'unità di misura
    switch (elementName[lastIndex]) {
        case "volume" || "volume":
            unitInput.placeholder = "m^3"
            break;
        case "humidity" || "umidità":
            unitInput.placeholder = "%"
            break;
        case "frequency" || "frequenza":
            unitInput.placeholder = "Hz";
            break;
        case "area":
            unitInput.placeholder = "m^2"
            break;
        case "temperature" || "temperatura":
            unitInput.placeholder = "°C"
            break;
        case "electricConsumption":
            unitInput.placeholder = "kWh";
            break;
        default:
            unitInput.placeholder = "Inserisci unità";
    }
    inputContainer.appendChild(unitInput);
    draggedElement.appendChild(inputContainer);
}


// Funzione per ripristinare un elemento alla sezione di origine (POLIMI)
function deleteElement(element, idDropzone) {
    // Elimina direttamente l'elemento dalla dropzone
    element.remove();
    // Regola l'altezza della dropzone da cui è stato rimosso l'elemento
    adjustDropzoneHeight(document.getElementById(idDropzone));
    // Controllo se tutte le dropzone sono vuote per nascondere il mapButton
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    let allDropzonesEmpty = true;
    for (const dropzone of dropzones) {
        if (dropzone.childElementCount > 0) {
            allDropzonesEmpty = false;
            break;
        }
    }
    if (allDropzonesEmpty) {
        document.getElementById('mapButton').classList.add('hidden');
        document.getElementById('mappingFunctionContainer').classList.add('hidden');
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


// Funzione per raccolgiere il mapping e inviarlo al server (POLIMI)
document.getElementById('mapButton').onclick = function (event) {
    event.preventDefault();
    const mappingData = {};
    let endpoint = "";
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    // Controllo per i campi mancanti
    const generatorDropzone = document.getElementById('dropzone-generator_id');
    const topicDropzone = document.getElementById('dropzone-topic');
    const missingFields = [];
    if (generatorDropzone.childElementCount === 0) missingFields.push('generator_id');
    if (topicDropzone.childElementCount === 0) missingFields.push('topic');
    // li faccio inserire all'utente
    if (missingFields.length > 0) {
        showMissingFieldsModal(missingFields);
        return;
    }
    if (selectedSchema === "POLIMI") {
        endpoint = '/generateMappingFunctionPOLIMI';
        dropzones.forEach(dropzone => {
            const dropzoneId = dropzone.id.replace('dropzone-', '');
            // dropzone degli attributi
            if (dropzoneId === 'data') {
                mappingData[dropzoneId] = [];
                const children = dropzone.children;
                for (const child of children) {
                    const key = child.dataset.key;
                    if (key) {
                        const extractedData = extractRecursive(key, inputJsonStructure[key]);
                        extractedData.forEach(({ key: extractedKey, value: extractedValue, isArrayValue }) => {
                            // Se la chiave è già stata trattata come array, evito duplicazioni
                            if (!mappingData[dropzoneId].some(item => item.key === extractedKey)) {
                                // Trovo l'input associato alla chiave
                                const correspondingInput = child.querySelector(`input[id="${extractedKey}"]`)
                                // Valore di default per l'unità
                                let unit = "None";
                                // Determino l'unità in base all'input trovato
                                if (correspondingInput) {
                                    if (correspondingInput.value) {
                                        // Uso il valore dell'input se esiste
                                        unit = correspondingInput.value;
                                    } else if (correspondingInput.placeholder && correspondingInput.placeholder !== "Inserisci unità") {
                                        // Uso il placeholder se valido
                                        unit = correspondingInput.placeholder;
                                    }
                                }
                                // creo l'oggetto con chiave, valore e unità
                                mappingData[dropzoneId].push({
                                    key: extractedKey,
                                    value: extractedValue,
                                    unit: unit,
                                    isArrayValue: isArrayValue
                                });
                            }
                        });
                    }
                }

            } else {
                // Per altri dropzoneId, memorizzo semplicemente il valore (chiave) come stringa
                // e il fatto se il valore è stato inserito dall'utente o droppato
                const children = dropzone.children;
                for (const child of children) {
                    const key = child.dataset.key;
                    const isConstant = child.classList.contains('constant-item');
                    if (key) {
                        mappingData[dropzoneId] = {
                            value: key,
                            isConstant: isConstant
                        };
                    }
                }
            }
        });
    } else if (selectedSchema === "SCP") {
        endpoint = '/generateMappingFunctionSCP';
        const missingFields = checkRequiredDropzones();
        if (missingFields.length > 0) {
            showMissingFieldsModal(missingFields);
            return;
        }
        dropzones.forEach(dropzone => {
            if (dropzone.childElementCount === 0) return;
            const dropzoneId = dropzone.id.replace('dropzone-', '');
            if (dropzoneId === 'timeZone') {
                // Recupera il valore dal select di timeZone
                const timeZoneSelect = document.getElementById('dropzone-timeZone');
                if (timeZoneSelect) {
                    mappingData['timeZone'] = {
                        value: timeZoneSelect.value,
                        isConstant: true
                    };
                }
            }else {
                mappingData[dropzoneId] = [];
                const children = dropzone.children;
                for (const child of children) {
                    const key = child.dataset.key;
                    const isConstant = child.classList.contains('constant-item');
                    if (key) {
                        mappingData[dropzoneId] = {
                            value: key,
                            isConstant: isConstant
                        };
                    }
                }
            }
        });
    } else if (selectedSchema === "FILE") {
        endpoint = '/generateMappingFunctionFILE';
        const dropzones = document.querySelectorAll('[id^="dropzone"]');
        dropzones.forEach(dropzone => {
            if (dropzone.childElementCount === 0) return;
            const dropzoneId = dropzone.id.replace('dropzone-', '');
            const children = dropzone.children;
            mappingData[dropzoneId] = [];
            for (const child of children) {
                const key = child.dataset.key;
                const isConstant = child.classList.contains('constant-item');
                if (key) {
                    mappingData[dropzoneId] = {
                        value: key,
                        isConstant: isConstant
                    };
                }
            }
            ;
        })
    }
    // Invio il mapping al backend
    fetch(endpoint, {
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
                console.error(data.error);
            } else {
                // Visualizzo la funzione di mapping nel frontend
                document.getElementById('mappingFunctionContainer').textContent = data.mappingFunction;
                document.getElementById('mappingFunctionContainer').style.display = 'block';
                document.getElementById('mappingFunctionContainer').classList.remove('hidden');
                document.getElementById('saveMapping').classList.remove('hidden');
                document.getElementById('mappingFunctionContainer').scrollIntoView({ behavior: 'smooth' });
            }
        })
        .catch(error => console.error('Errore:', error));
};


// Funzione per verificare che tutte le dropzone richieste per SCP siano mappate
function checkRequiredDropzones() {
    const missingFields = [];
    scpRequired.forEach(field => {
        if(field == 'timeZone') return;
        if(field == 'period'){
            const dropzone1 = document.getElementById(`dropzone-start_ts`);
            if (dropzone1.childElementCount === 0) {
                missingFields.push('start_ts');
            }
            const dropzone2 = document.getElementById(`dropzone-end_ts`);
            if (dropzone2.childElementCount === 0) {
                missingFields.push('end_ts');
            }
        }else {
            const dropzone = document.getElementById(`dropzone-${field}`);
            if (dropzone.childElementCount === 0) {
                missingFields.push(field);
            }
        }
    });
    return missingFields;
}


// Funzione per estrarre i valori ricorsivamente (POLIMI)
function extractRecursive(keyPath, value) {
    const results = [];
    key = keyPath.split('.').pop();
    if(removedElements.includes(keyPath)) {
        return results;
    }
    // se il valore é un array
    if (Array.isArray(value)) {
        // mi salvo l'array intero e poi itero su tutti i suoi elementi
        results.push({ key: keyPath, value: value, isArrayValue: false });
        value.forEach((item) => {
            results.push(...extractRecursive(keyPath, item).map(entry => ({
                // aggiungo il fatto che sono elementi di un array
                ...entry,
                isArrayValue: true
            })));
        });
        // se è un oggetto faccio lo stesso 
    } else if (typeof value === 'object' && value !== null) {
        results.push({ key: keyPath, value: value, isArrayValue: false });
        Object.entries(value).forEach(([subKey, subValue]) => {
            const newKeyPath = `${keyPath}.${subKey}`;
            results.push(...extractRecursive(newKeyPath, subValue));
        });
    } else {
        // se è un valore semplice lo pusho nell'array
        results.push({ key: keyPath, value: value, isArrayValue: false });
    }
    return results;
}


// funzione per la modifica di generator_id o topoic se inseriti come costanti
function modifyInputSchemaElement(elementId, currentValue) {
    // Recupero l'elemento 
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Elemento con ID ${elementId} non trovato.`);
        return;
    }
    // Mostro un input per modificare il valore
    const inputField = document.createElement('input');
    inputField.type = 'text';
    inputField.classList.add('form-control', 'mb-2');
    inputField.value = currentValue;
    inputField.placeholder = 'Modifica il valore';
    // Creo i pulsanti per confermare o annullare la modifica
    const saveButton = document.createElement('button');
    saveButton.classList.add('btn', 'btn-success', 'mb-2');
    saveButton.textContent = 'Salva';
    const cancelButton = document.createElement('button');
    cancelButton.classList.add('btn', 'btn-secondary', 'mb-2');
    cancelButton.textContent = 'Annulla';
    // Sostituisco il contenuto corrente con il campo di modifica e pulsanti
    element.innerHTML = '';
    element.appendChild(inputField);
    element.appendChild(saveButton);
    element.appendChild(cancelButton);
    // Gestisco il salvataggio della modifica
    saveButton.onclick = () => {
        const newValue = inputField.value.trim();
        if (newValue === '') {
            inputField.classList.add('is-invalid');
            return;
        }
        // Aggiorno il contenuto dell'elemento con il nuovo valore
        element.innerHTML = `
            <span class="key-text fw-bold">${newValue}</span>
            <button class="modify-button btn btn-primary btn-sm" onclick="modifyInputSchemaElement('${elementId}', '${newValue}')">Modifica</button>
            <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${elementId}')">Elimina</button>
        `;
        element.dataset.key = newValue;
    };
    // Gestisco l'annullamento della modifica
    cancelButton.onclick = () => {
        // Ripristino il contenuto originale dell'elemento
        element.innerHTML = `
            <span class="key-text fw-bold">${currentValue}</span>
            <button class="modify-button btn btn-primary btn-sm" onclick="modifyInputSchemaElement('${elementId}', '${currentValue}')">Modifica</button>
            <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${elementId}')">Elimina</button>
        `;
    };
}


// Funzione per salvare il mapping dentro ODA
function saveMapping() {
    const modal = new bootstrap.Modal(document.getElementById('saveMappingModal'));
    modal.show();
    // Mostra il campo per il nome dello schema di destinazione solo se lo schema è "FILE"
    const destSchemaNameContainer = document.getElementById('destSchemaNameContainer');
    if (selectedSchema === "FILE") {
        destSchemaNameContainer.style.display = 'block';
    } else {
        destSchemaNameContainer.style.display = 'none';
    }
    // Aggiungo un listener per il pulsante "Invia il mapping" nel modal
    document.getElementById('nameMappingFunction').onclick = function () {
        // Recupero il nome del mapping inserito dall'utente
        const mappingName = document.getElementById('mappingName').value.trim();
        const destSchemaName = selectedSchema === "FILE" ? document.getElementById('destSchemaName').value.trim() : selectedSchema;
        const errorContainer = document.getElementById('errorContainer');
        const successContainer = document.getElementById('successContainer');
        errorContainer.textContent = ''; 
        errorContainer.style.display = 'none';
        successContainer.textContent = ''; 
        successContainer.style.display = 'none';
        // Verifico che il nome del mapping sia stato inserito
        if (!mappingName) {
            errorContainer.textContent = 'Inserisci un nome per il mapping.';
            errorContainer.style.display = 'block';
            return;
        }
        // Verifico che il nome dello schema di destinazione sia stato inserito se lo schema è "FILE"
        if (selectedSchema === "FILE" && !destSchemaName) {
            errorContainer.textContent = 'Inserisci un nome per lo schema di destinazione.';
            errorContainer.style.display = 'block';
            return;
        }
        // Recupero la funzione di mapping generata
        const mappingFunction = document.getElementById('mappingFunctionContainer').textContent;
        // Creo l'oggetto da inviare al backend
        const mappingData = {
            mappingName: mappingName,
            mappingFunction: mappingFunction,
            destSchemaName: destSchemaName
        };
        // Invio i dati al backend 
        fetch('/saveMappingFunction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(mappingData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                errorContainer.textContent = data.error;
                errorContainer.style.display = 'block';
            } else {
                successContainer.textContent = data.response.message;
                successContainer.style.display = 'block';
                setTimeout(() => {
                    modal.hide();
                }, 3000);
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            errorContainer.textContent = data.error;
            errorContainer.style.display = 'block';
        });
    };
}


// funzione per azzerare il contenuto del modal
document.getElementById('saveMappingModal').addEventListener('hidden.bs.modal', function () {
    document.getElementById('mappingName').value = ''; 
    document.getElementById('destSchemaName').value = ''; 
    document.getElementById('errorContainer').textContent = ''; 
    document.getElementById('errorContainer').style.display = 'none';
    document.getElementById('successContainer').textContent = ''; 
    document.getElementById('successContainer').style.display = 'none';
});