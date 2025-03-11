function redirect_function() {
    window.location.href = "/generateFunction";
}

function redirect_mappings() {
    window.location.href = "/mappings";
}


function closeMessage(id) {
    document.getElementById(id).style.display = 'none';
}

// Funzione per caricare le statistiche
function fetchStats() {
    // Fetch per ottenere il numero totale di mapping
    fetch('/showMapping')
        .then(response => response.json())
        .then(data => {
            const totalMappings = data.length;
            document.getElementById('totalMappings').textContent = totalMappings;
        })
        .catch(error => {
            console.error('Errore durante il recupero dei mapping:', error);
        });

    // Fetch per ottenere il numero totale di legami (collegamenti DG e topic)
    fetch('/numberOfLink')
        .then(response => response.json())
        .then(data => {
            document.getElementById('numberOfLink').textContent = data.numberOfLink
        })
        .catch(error => {
            console.error('Errore durante il recupero del numero di collegamenti:', error);
        });
}

// Esegui il caricamento delle statistiche all'avvio della pagina
document.addEventListener('DOMContentLoaded', function() {
    fetchStats();
});