// variabili globali che contengono la struttura degli schemi di input e di destinazione
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
document.getElementById("uploadDestSchemaSelect").onsubmit = function(event) {
    // Blocca il comportamento di default (evitare il refresh della pagina)
    event.preventDefault();
    // Ottieni il valore selezionato dal dropdown
    var selectedSchema = document.getElementById("destSchema").value;
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
            if(selectedSchema === "POLIMI") {
                editor.innerHTML = generateDestDroppableCardPOLIMI(destJsonStructure);
            }else if(selectedSchema === "SCP") {
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
document.getElementById('uploadDestSchemaFile').onsubmit = function(event) {
    event.preventDefault();
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


// mostra il modal per i campi mancanti
function showMissingFieldsModal(fieldsList) {
    const modal = new bootstrap.Modal(document.getElementById('missingFieldsModal'));
    modal.show();
    const modalTitle = document.getElementById('missingFieldsModalLabel');
    if(fieldsList.length === 2) {
        modalTitle.textContent = "Inserisci i campi generator_id e topic";
    }else {
        modalTitle.textContent = "Inserisci il campo " + fieldsList[0];
    }
    const modalBody = document.getElementById('missingFieldsModalText');
    modalBody.innerHTML = '';
    // Creo un contenitore per gli input
    const container = document.createElement('div');
    container.classList.add('container', 'd-flex', 'flex-column');
    container.id = 'missingFieldsContainer';
    modalBody.appendChild(container);
    // Aggiungo un input per ciascun campo mancante
    for (const field of fieldsList) {
        const input = document.createElement('input');
        input.type = 'text';
        input.classList.add('form-control', 'mb-2');
        input.placeholder = "Inserisci " + field;
        input.dataset.fieldName = field;
        container.appendChild(input);
    }
    const dropzones = fieldsList.map(field => document.getElementById('dropzone-' + field));
    // Aggiungo l'evento onclick al bottone per verificare e aggiungere i campi
    document.getElementById('missingFieldsModalButton').onclick = () => {
        const inputs = document.querySelectorAll('#missingFieldsContainer input');
        let allFilled = true;
        // Verifica che nessun campo sia vuoto
        inputs.forEach(input => {
            if (input.value.trim() === '') {
                allFilled = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });
        // controllo se tutti i campi sono pieni
        if (!allFilled) {
            const errorMessage = document.createElement('div');
            errorMessage.classList.add('alert', 'alert-danger', 'mt-2');
            errorMessage.textContent = "Per favore, riempi tutti i campi prima di procedere.";
            if (!modalBody.querySelector('.alert')) {
                modalBody.appendChild(errorMessage);
            }
            return;
        }
        const values = Array.from(inputs).map(input => input.value.trim());
        let i = 0;
        // aggiungo il valore alla dropzone corretta con la possibilità di modificare e rimuoverlo
        for (const val of values) {
            let html = `
                <div class="constant-item draggable-item d-flex align-items-center justify-content-between p-2 mb-2 rounded bg-white shadow-sm" draggable="true" ondragstart="drag(event)" data-key="${val}" id="${val+'-constant'}">
                    <span class="key-text fw-bold">${val}</span>
                    <button class="modify-button btn btn-primary btn-sm" onclick="modifyInputSchemaElement('${val+'-constant'}', '${val}')">Modifica</button>
                    <button class="remove-button btn btn-danger btn-sm" onclick="removeInputSchemaElement('${val+'-constant'}')">Elimina</button>
                </div>
            `;
            dropzones[i].innerHTML += html;
            i++;
        }
        modal.hide();
    };
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
        if(currentKey.includes('[') && currentKey.includes(']')) { 
            currentKey = currentKey.substring(0, currentKey.indexOf('['));
            currentKey = currentKey + '.' + key
            console.log(currentKey)
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
                    <p class="card-title">${key}</p>
                </div>
                <div class="card-body">
                    <div class="dropzone" id="dropzone-${key}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
        `;
        if(key == "generator_id" || key == "topic") {
            html += `<button class="btn btn-primary" id="buttonAdd" onclick="showMissingFieldsModal(['${key}'])">+</button>`;
        }
        html += `</div></div>`;
    }
    return html;
}


// Funzione per generare il codice necessario per creare le card droppabili dei campi per SCP
function generateDestDroppableCardSCP(destJsonStructure) {
    let html = '';
    for(let key in destJsonStructure) {
        if(key == "data") {
            const propertyDefinitions = destJsonStructure?.data?.UrbanDataset?.specification?.properties?.propertyDefinition;
            if (Array.isArray(propertyDefinitions)) {
                // Itera su ogni proprietà definita
                propertyDefinitions.forEach((property) => {
                    const propertyName = property.propertyName || "Unknown";
                    const unitOfMeasure = property.unitOfMeasure || "Unknown";

                    // Crea una card per ogni proprietà
                    html += `
                        <div class="dest-card mb-3 p-2 border rounded shadow-sm" id="dest-card-${propertyName}">
                            <div class="card-header text-white">
                                <p class="card-title">${propertyName}</p>
                            </div>
                            <div class="card-body">
                                <div class="dropzone" id="dropzone-${propertyName}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
                            </div>
                        </div>
                    `;
                });
            }
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
    
    
    return html;
}


// Funzione per generare il codice necessario per creare le card droppabili dei campi per un FILE generico
function generateDestDroppableCardFILE(destJsonStructure, parentKey = '') {
    let html = '';

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
                        <div class="dropzone" id="dropzone-${currentKey}" ondrop="drop(event)" ondragover="allowDrop(event)"></div>
            `;

            // Itera sugli elementi dell'array
            value.forEach((item, index) => {
                const arrayItemKey = `${currentKey}[${index}]`;

                if (typeof item === 'object' && item !== null) {
                    // Ricorsione per gli oggetti all'interno dell'array
                    html += generateDestDroppableCardFILE(item, arrayItemKey);
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
                        ${generateDestDroppableCardFILE(value, currentKey)}
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
            if(key == "generator_id" || key == "topic" || key == "generatorId" || key == "generatorid") {
                html += `<button class="btn btn-primary" id="buttonAdd" onclick="showMissingFieldsModal(['${key}'])">+</button>`;
            }
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
    // data: percorso dell'elemento nel json (ex: data.buildingId...)
    const data = ev.dataTransfer.getData("text");
    const draggedElement = document.getElementById(data);
    // Verifico se l'elemento è stato droppato nella dropzone degli attributi
    if (ev.target.classList.contains("dropzone")) {
        // Verifico se l'elemento è già nella dropzone
        if (!ev.target.contains(draggedElement)) {
            // Aggiungo l'elemento alla dropzone degli attributi
            ev.target.appendChild(draggedElement);
            // Aggiungo i campi per valore e unità di misura solo se è la dropzone degli attributi
            if(ev.target.id === "dropzone-data") {
                // Se è un array aggiungo unità a ogni sottoelemento
                if (draggedElement.classList.contains("array-container")) {
                    // seleziono tutti gli elementi dell'array
                    const arrayItems = draggedElement.querySelectorAll(".draggable-item");
                    arrayItems.forEach(item => {
                        // aggiungo l'unità di misura
                        addUnitInput(item);
                        // Rimuovi il bottone di eliminazione se esiste
                        const deleteButton = item.querySelector(".remove-button");
                        if (deleteButton) {
                            deleteButton.remove();
                        }
                    });
                    // se è un oggetto aggiungo unità a ogni sottoelemento
                } else if (draggedElement.classList.contains("object-container")) {
                    const objectItems = draggedElement.querySelectorAll(".draggable-item");
                    objectItems.forEach(item => {
                        addUnitInput(item);
                        // Rimuovi il bottone di eliminazione se esiste
                        const deleteButton = item.querySelector(".remove-button");
                        if (deleteButton) {
                            deleteButton.remove();
                        }
                    });
                }
                addUnitInput(draggedElement);
                // Rimuovi il bottone di eliminazione se esiste
                const deleteButton = draggedElement.querySelector(".remove-button");
                if (deleteButton) {
                    deleteButton.remove();
                }
            }
            const deleteButton = draggedElement.querySelectorAll(".remove-button");
            deleteButton.forEach(button => button.remove());
            // Aggiungi un pulsante per il ripristino
            if (!draggedElement.querySelector(".restore-button")) {
                const restoreButton = document.createElement("button");
                restoreButton.textContent = "Indietro";
                restoreButton.className = "restore-button btn btn-secondary btn-sm ms-2";
                restoreButton.onclick = () => restoreToOrigin(draggedElement, ev.target.id);
                draggedElement.appendChild(restoreButton);
            }
            // Regola l'altezza della dropzone
            adjustDropzoneHeight(ev.target);
            // aggiunge il bottone per il mapping
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
    switch(elementName[lastIndex]) {
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
function restoreToOrigin(element, idDropzone) {
    const originSection = document.getElementById("inputJsonStructure");
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    if(element.id.includes('[') && element.id.includes(']')){
        indexStart = element.id.indexOf('[');
        indexEnd = element.id.indexOf(']');
        element.id = element.id.slice(0, indexStart) + element.id.slice(indexEnd + 1);
    }
    // Non aggiungeo il pulsante di eliminazione se non è possibile ripristinare l'elemento
    const position = element.id.split('.');
    if (position.length == 1) {
        // Ripristo l'elemento principale alla sua sezione originale
        originSection.appendChild(element);
    } else {
        let path = "";
        for (let i = 0; i <= position.length - 1; i++) {
            if (i == position.length - 2) {
                path += `${position[i]}`;
                break;
            } else {
                path += `${position[i]}.`;
            }
        }
        const container = originSection.querySelector(`[data-key="${path}"] .nested-items`);
        // Se il percorso non esiste, annullo l'operazione
        if (!container) {
            const errorMessage = document.createElement("div");
            errorMessage.id = "error-message-restore";
            errorMessage.classList.add("alert", "alert-danger", "mt-2");
            errorMessage.textContent = `Errore: L'elemento "${path}" non è presente nella sezione dello schema di input. Impossibile ripristinare l'elemento.`;
            originSection.insertBefore(errorMessage, originSection.firstChild);
            document.getElementById("error-message-restore").scrollIntoView({ behavior: "smooth" });
            // Rimuovo l'errore dopo 5 secondi
            setTimeout(() => {
                errorMessage.remove();
            }, 5000);
            // Mantengo il pulsante di ripristino e non aggiungo il pulsante di eliminazione
            return;
        } else {
            container.appendChild(element);
        }
    }
    // Rimuovo tutti i pulsanti di ripristino presenti nell'elemento
    const restoreButtons = element.querySelectorAll(".restore-button");
    restoreButtons.forEach(button => button.remove());
    // Rimuovo tutti i campi di input relativi all'unità di misura
    const unitInputs = element.querySelectorAll('input');
    unitInputs.forEach(input => input.remove());
    // Aggiungo il pulsante di eliminazione solo se il container esiste
    const header = element.querySelector(".object-header, .array-header");
    if (header) {
        const deleteButton = header.querySelector(".remove-button");
        if (!deleteButton) {
            const newDeleteButton = document.createElement("button");
            newDeleteButton.classList.add("remove-button", "btn", "btn-danger", "btn-sm", "ms-2");
            newDeleteButton.textContent = "Elimina";
            newDeleteButton.onclick = () => removeInputSchemaElement(element.id);
            header.appendChild(newDeleteButton);
        }
    }
    // Aggiungo il pulsante di eliminazione a ogni elemento interno (anche a oggetti e array nidificati)
    const nestedItems = element.querySelectorAll(".draggable-item");
    if (nestedItems.length === 0) {
        const deleteButton = document.createElement("button");
        deleteButton.classList.add("remove-button", "btn", "btn-danger", "btn-sm");
        deleteButton.textContent = "Elimina";
        deleteButton.onclick = () => removeInputSchemaElement(element.id);
        element.appendChild(deleteButton);
    } else {
        nestedItems.forEach(item => {
            if (item.textContent.trim().endsWith("}") || item.textContent.trim().endsWith("]")) {
                return;
            }
            // Rimuovo eventuali pulsanti di eliminazione esistenti per evitare duplicati
            const existingDeleteButton = item.querySelector(".remove-button");
            if (!existingDeleteButton) {
                const deleteButton = document.createElement("button");
                deleteButton.classList.add("remove-button", "btn", "btn-danger", "btn-sm");
                deleteButton.textContent = "Elimina";
                deleteButton.onclick = () => removeInputSchemaElement(item.id);
                item.appendChild(deleteButton);
            }
        });
    }
    // Regolo l'altezza della dropzone da cui è stato rimosso l'elemento
    adjustDropzoneHeight(document.getElementById(idDropzone));
    // Controllo se tutte le dropzone sono vuote per nascondere il mapButton
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
document.getElementById('mapButton').onclick = function(event) {
    event.preventDefault();
    const dropzones = document.querySelectorAll('[id^="dropzone"]');
    const mappingData = {};
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
    dropzones.forEach(dropzone => {
        const dropzoneId = dropzone.id.replace('dropzone-', '');
        // dropzone degli attributi
        if (dropzoneId === 'data') {
            mappingData[dropzoneId] = [];
            const children = dropzone.children;
            for (const child of children) {
                const key = child.dataset.key;
                if(key) {
                    const extractedData = extractRecursive(key, inputJsonStructure[key]);
                    extractedData.forEach(({ key: extractedKey, value: extractedValue, isArrayValue}) => {
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
    console.log(mappingData);
    // Invio il mapping al backend
    fetch('/generateMappingFunctionPOLIMI', {
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
            // Visualizzo la funzione di mapping nel frontend
            document.getElementById('mappingFunctionContainer').textContent = data.mappingFunction;
            mappingFunctionContainer.style.display = 'block';
            document.getElementById('mappingFunctionContainer').classList.remove('hidden');
            document.getElementById('mappingFunctionContainer').scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => console.error('Errore:', error));
};


// Funzione per estrarre i valori ricorsivamente (POLIMI)
function extractRecursive(keyPath, value) {
    const results = [];
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
