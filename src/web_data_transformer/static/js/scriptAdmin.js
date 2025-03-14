// Variabile globale per memorizzare il nome del mapping corrente
let currentMappingName = '';
let currentModal = null;

// funzione per mostrare l'errore metà di destinazione
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}

// funzione per mostrare messaggio di successo metà di destinazione
function showSuccess(message) {
    const successMessage = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    successText.textContent = message;
    successMessage.style.display = 'flex';
}

// Funzione per chiudere il messaggio di errore o successo
function closeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    messageElement.classList.remove('d-flex');
    messageElement.style.display = 'none';
}

// Funzione per caricare i mapping nella pagina
function loadMappings() {
    fetch('/showMapping', {
        method: 'GET',
    })
        .then(response => response.json())
        .then(response => {
            const mappingsTableBody = document.getElementById('mappingsTableBody');
            if (response && response.length > 0) {
                mappingsTableBody.innerHTML = '';
                response.forEach(mapping => {
                    const schemaInputPreview = JSON.stringify(mapping.schema_input).substring(0, 50) + '...';
                    const functionPreview = mapping.mapping_function.substring(0, 50) + '...';

                    // Fetch dei collegamenti DG e topic per ogni mapping
                    fetch(`/mappingDetails/${mapping.mapping_name}`, {
                        method: 'GET',
                    })
                        .then(detailsResponse => detailsResponse.json())
                        .then(detailsResponse => {
                            // Estrai i collegamenti DG e topic
                            const links = detailsResponse.links || [];
                            const linksPreview = links.length > 0 
                                ? `<ul><li><strong>Generator ID:</strong> ${links[0].generator_id}<br><strong>Topic:</strong> ${links[0].topic}</li>
                                    <li>...</li>
                                </ul>` 
                                : 'Nessun collegamento';

                            const row = `
                                <tr>
                                    <td>${mapping.mapping_name}</td>
                                    <td class="mapping-details">${schemaInputPreview}</td>
                                    <td>${mapping.schema_dest_name}</td>
                                    <td class="mapping-details">${functionPreview}</td>
                                    <td>${linksPreview}</td>
                                    <td>
                                        <button class="btn btn-secondary btn-sm" onclick="showDetails('${mapping.mapping_name}')">Dettagli</button>
                                    </td>
                                    <td>
                                        <button class="btn btn-success btn-sm" onclick="linkMapping('${mapping.mapping_name}')">Link</button>
                                    </td>
                                    <td>
                                        <button class="btn btn-warning btn-sm" onclick="unlinkMapping('${mapping.mapping_name}')">Unlink</button>
                                    </td>
                                    <td>
                                        <button class="btn btn-danger btn-sm" onclick="deleteMapping('${mapping.mapping_name}')">Elimina</button>
                                    </td>
                                </tr>
                            `;
                            mappingsTableBody.insertAdjacentHTML('beforeend', row);
                        })
                        .catch(error => {
                            console.error("Errore API:", error);
                            alert('Errore durante il caricamento dei dettagli del mapping.');
                        });
                });
            } else {
                mappingsTableBody.innerHTML = '<tr><td colspan="8">Nessun mapping trovato</td></tr>';
            }
        })
        .catch(error => {
            console.error("Errore API:", error);
            alert('Errore durante il caricamento dei mapping.');
        });
}

// Funzione per visualizzare i dettagli di un mapping
function showDetails(mappingName) {
    fetch(`/mappingDetails/${mappingName}`, {
        method: 'GET',
    })
        .then(response => response.json())
        .then(response => {
            if (response) {
                // Estrai i collegamenti DG e topic
                const links = response.links || [];
                const linksDetails = links.length > 0 
                    ? `<ul>${links.map(link => `<li><strong>Generator ID:</strong> ${link.generator_id}<br><strong>Topic:</strong> ${link.topic}</li>`).join('')}</ul>` 
                    : 'Nessun collegamento';

                const content = `
                    <h5>Schema Input:</h5>
                    <pre>${JSON.stringify(response.schema_input, null, 2)}</pre>
                    <h5>Funzione di Mapping:</h5>
                    <pre>${response.mapping_function}</pre>
                    <h5>Collegamenti generator_id e Topic:</h5>
                    ${linksDetails}
                `;
                document.getElementById('modalBodyContent').innerHTML = content;
                const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
                modal.show();
            }
        })
        .catch(() => {
            alert('Errore durante il caricamento dei dettagli del mapping.');
        });
}

// Funzione per collegare un mapping a un DG e a un topic
function linkMapping(mappingName) {
    currentMappingName = mappingName; // Memorizza il nome del mapping
    const modalElement = document.getElementById('linkMappingModal');
    // Pulisci i campi prima di mostrare il modal
    resetModalFields();
    // Crea e salva l'istanza del modal
    currentModal = new bootstrap.Modal(modalElement);
    currentModal.show();
    // Aggiungo un listener per il pulsante "Collega" nel modal
    document.getElementById('linkMappingButton').onclick = function () {
        // Recupero i valori inseriti dall'utente
        const generatorId = document.getElementById('generatorId').value.trim();
        const topic = document.getElementById('topic').value.trim();
        const errorContainer = document.getElementById('errorContainerLink');
        const successContainer = document.getElementById('successContainerLink');

        // Azzero i messaggi di errore e successo
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
        successContainer.textContent = '';
        successContainer.style.display = 'none';

        // Verifico che i campi siano stati inseriti
        if (!generatorId || !topic) {
            errorContainer.textContent = 'Devi inserire sia il generator_id che il topic.';
            errorContainer.style.display = 'block';
            return;
        }

        // Creo l'oggetto da inviare al backend
        const mappingData = {
            mappingName: currentMappingName,
            generator_id: generatorId,
            topic: topic
        };

        // Invio i dati al backend
        fetch('/linkMapping', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(mappingData)
        }
        ).then(response => response.json())
        .then(data => {
                if (data.error) {
                    errorContainer.textContent = data.error;
                    errorContainer.style.display = 'block';
                } else {
                    successContainer.textContent = 'Mapping collegato con successo!';
                    successContainer.style.display = 'block';
                    loadMappings();
                }
            })
            .catch(error => {
                console.error('Errore:', error);
                errorContainer.textContent = 'Errore durante il collegamento del mapping.';
                errorContainer.style.display = 'block';
            });
    };
}

// Ottiengo un riferimento all'elemento modal
const linkMappingModal = document.getElementById('linkMappingModal');

// Aggiungo un event listener per l'evento hidden.bs.modal
linkMappingModal.addEventListener('hidden.bs.modal', function () {
    // Resetta i valori degli input
    document.getElementById('generatorId').value = '';
    document.getElementById('topic').value = '';
    
    // Resetta i contenitori di errore e successo
    const errorContainer = document.getElementById('errorContainerLink');
    errorContainer.textContent = '';
    errorContainer.style.display = 'none';
    
    const successContainer = document.getElementById('successContainerLink');
    successContainer.textContent = '';
    successContainer.style.display = 'none';
});

// Funzione per azzerare manualmente i campi del modal
function resetModalFields() {
    document.getElementById('generatorId').value = '';
    document.getElementById('topic').value = '';
    document.getElementById('errorContainerLink').textContent = '';
    document.getElementById('errorContainerLink').style.display = 'none';
    document.getElementById('successContainerLink').textContent = '';
    document.getElementById('successContainerLink').style.display = 'none';
}

// Aggiungo l'evento per quando il modal viene nascosto
document.addEventListener('DOMContentLoaded', function() {
    const linkMappingModal = document.getElementById('linkMappingModal');
    
    // Usa un event listener forzato con capturing per assicurarsi di catturare l'evento
    linkMappingModal.addEventListener('hidden.bs.modal', function() {
        resetModalFields();
    }, true);
    
    // Aggiungi anche un listener per il pulsante di chiusura (x) nel modal
    const closeButton = linkMappingModal.querySelector('button.close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            resetModalFields();
        });
    }
    
    // Carica i mapping all'avvio della pagina
    loadMappings();
});

// Funzione per scollegare un mapping da un DG e un topic
function unlinkMapping(mappingName) {
    currentMappingName = mappingName; // Memorizza il nome del mapping
    const modalElement = document.getElementById('unlinkMappingModal');
    // Pulisci i campi prima di mostrare il modal
    resetUnlinkModalFields();
    // Crea e salva l'istanza del modal
    currentModal = new bootstrap.Modal(modalElement);
    currentModal.show();
    // Aggiungo un listener per il pulsante "Scollega" nel modal
    document.getElementById('unlinkMappingButton').onclick = function () {
        // Recupero i valori inseriti dall'utente
        const generatorId = document.getElementById('unlinkGeneratorId').value.trim();
        const topic = document.getElementById('unlinkTopic').value.trim();
        const errorContainer = document.getElementById('errorContainerUnlink');
        const successContainer = document.getElementById('successContainerUnlink');

        // Azzero i messaggi di errore e successo
        errorContainer.textContent = '';
        errorContainer.style.display = 'none';
        successContainer.textContent = '';
        successContainer.style.display = 'none';

        // Verifico che i campi siano stati inseriti
        if (!generatorId || !topic) {
            errorContainer.textContent = 'Devi inserire sia il generator_id che il topic.';
            errorContainer.style.display = 'block';
            return;
        }

        // Creo l'oggetto da inviare al backend
        const mappingData = {
            mappingName: currentMappingName,
            generator_id: generatorId,
            topic: topic
        };

        // Invio i dati al backend
        fetch('/unlinkMapping', {
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
                successContainer.textContent = 'Mapping scollegato con successo!';
                successContainer.style.display = 'block';
                loadMappings();
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            errorContainer.textContent = 'Errore durante lo scollegamento del mapping.';
            errorContainer.style.display = 'block';
        });
    };
}

// Funzione per azzerare manualmente i campi del modal di scollegamento
function resetUnlinkModalFields() {
    document.getElementById('unlinkGeneratorId').value = '';
    document.getElementById('unlinkTopic').value = '';
    document.getElementById('errorContainerUnlink').textContent = '';
    document.getElementById('errorContainerUnlink').style.display = 'none';
    document.getElementById('successContainerUnlink').textContent = '';
    document.getElementById('successContainerUnlink').style.display = 'none';
}

// Aggiungi manualmente l'evento per quando il modal di scollegamento viene nascosto
document.addEventListener('DOMContentLoaded', function() {
    const unlinkMappingModal = document.getElementById('unlinkMappingModal');
    
    // Usa un event listener forzato con capturing per assicurarsi di catturare l'evento
    unlinkMappingModal.addEventListener('hidden.bs.modal', function() {
        resetUnlinkModalFields();
    }, true);
    
    // Aggiungi anche un listener per il pulsante di chiusura (x) nel modal
    const closeButton = unlinkMappingModal.querySelector('button.close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            resetUnlinkModalFields();
        });
    }
});

// Funzione per eliminare un mapping
function deleteMapping(mappingName) {
    // Mostra il modal di conferma
    document.getElementById('mappingNameToDelete').textContent = mappingName;
    $('#confirmDeleteModal').modal('show');
    document.getElementById('confirmDeleteButton').onclick = function () {
        // Invia una richiesta POST al backend per eliminare il mapping
        fetch('/deleteMapping', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ mappingName: mappingName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
            } else {
                showSuccess(`Mapping "${mappingName}" eliminato con successo!`);
                // Ricarica la lista dei mapping dopo l'eliminazione
                loadMappings();
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            showError('Errore durante l\'eliminazione del mapping.');
        });
        // Chiudi il modal dopo l'eliminazione
        $('#confirmDeleteModal').modal('hide');
    }
}