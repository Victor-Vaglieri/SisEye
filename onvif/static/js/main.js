// Função que chama o Python para controle PTZ
async function ptz(cmd) {
    const logElement = document.getElementById('log');
    if (logElement) logElement.innerText = "Enviando: " + cmd;
    
    try {
        const response = await fetch(`/api/ptz/${cmd}`);
        const data = await response.json();
        if (data.status === "error") {
            console.error("Erro PTZ:", data.msg);
        }
    } catch (e) {
        console.error("Erro na requisição PTZ:", e);
    }
}

// Controle via Teclado
document.addEventListener('keydown', (e) => {
    if (e.repeat) return;
    switch(e.key) {
        case "ArrowUp": ptz('up'); break;
        case "ArrowDown": ptz('down'); break;
        case "ArrowLeft": ptz('left'); break;
        case "ArrowRight": ptz('right'); break;
    }
});

document.addEventListener('keyup', (e) => {
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key)) {
        ptz('stop');
    }
});
