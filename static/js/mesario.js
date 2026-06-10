    function ir(rota) { window.location.href = rota; }
    const socket = io();

    function liberarUrna() {
      const titulo = document.getElementById('titulo_input').value;
      if (!titulo) {
        alert("Digite o título do eleitor!");
        return;
      }
      
      const statusP = document.getElementById('status-text');
      statusP.innerText = "VERIFICANDO...";
      statusP.style.color = "#ffc107"; 

      socket.emit('mesario_libera_urna', { titulo: titulo });
    }

    socket.on('status_mesario', function(data) {
      const statusP = document.getElementById('status-text');
      statusP.innerText = data.status.toUpperCase();
      
      if(data.cor === 'green') {
         statusP.style.color = "#00ad5d";
         document.getElementById('titulo_input').value = "";
      } else if (data.cor === 'red') {
         statusP.style.color = "#ff4d4d";
      } else {
         statusP.style.color = "#4da6ff";
      }
    });