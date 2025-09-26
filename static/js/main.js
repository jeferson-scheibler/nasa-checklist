// Cronômetro de Contagem Regressiva
const deadline = new Date("Oct 5, 2025 23:59:59").getTime();
const countdownElement = document.getElementById("countdown");

if (countdownElement) {
    setInterval(function() {
        const now = new Date().getTime();
        const distance = deadline - now;
        
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        countdownElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        
        if (distance < 0) {
            countdownElement.innerHTML = "PRAZO ENCERRADO!";
        }
    }, 1000);
}

// Função para atualizar o checklist
function updateItem(checkbox) {
    const itemId = checkbox.dataset.itemId;
    const isComplete = checkbox.checked;

    fetch('/update_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            item_id: parseInt(itemId),
            is_complete: isComplete
        })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert('Erro ao atualizar. Tente novamente.');
            checkbox.checked = !isComplete; // Reverte a mudança se der erro
        }
    });
}