    function ir(rota) { 
        // Abre em uma nova guia se for a Urna ou o Mesário, para facilitar o teste
        if(rota === '/mesario' || rota === '/votacao') {
            window.open(rota, '_blank');
        } else {
            window.location.href = rota; 
        }
    }

    function abrirModalEncerramento() {
      document.getElementById('modalEncerramento').style.display = 'block';
      document.getElementById('usuarioInput').value = '';
      document.getElementById('senhaInput').value = '';
      document.getElementById('mensagemModal').style.display = 'none';
      document.getElementById('usuarioInput').focus();
    }

    function fecharModalEncerramento() {
      document.getElementById('modalEncerramento').style.display = 'none';
      document.getElementById('mensagemModal').style.display = 'none';
    }

    function validarEEncerrar() {
      const usuario = document.getElementById('usuarioInput').value.trim();
      const senha = document.getElementById('senhaInput').value.trim();
      const mensagemDiv = document.getElementById('mensagemModal');

      // Validar campos vazios
      if(!usuario || !senha) {
        mensagemDiv.className = 'modal-message error';
        mensagemDiv.textContent = 'Usuário e senha são obrigatórios!';
        mensagemDiv.style.display = 'block';
        return;
      }

      // Validar horário
      const agora = new Date();
      const hora = agora.getHours();

      if(hora < 17) {
        mensagemDiv.className = 'modal-message warning';
        mensagemDiv.textContent = `Encerramento permitido apenas após as 17h. Hora atual: ${hora}h`;
        mensagemDiv.style.display = 'block';
        return;
      }

      // Validar credenciais
      fetch('/login_presidente', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          usuario: usuario,
          senha: senha
        })
      })
      .then(response => response.json())
      .then(data => {
        if(data.erro) {
          mensagemDiv.className = 'modal-message error';
          mensagemDiv.textContent = 'Usuário ou senha inválidos. Tente novamente!';
          mensagemDiv.style.display = 'block';
          document.getElementById('senhaInput').value = '';
          return;
        }

        // Credenciais válidas e horário correto
        mensagemDiv.className = 'modal-message success';
        mensagemDiv.textContent = `Bem-vindo, ${data.nome_presidente}! Encerrando sessão...`;
        mensagemDiv.style.display = 'block';

        // Aguardar um momento e disparar o encerramento
        setTimeout(() => {
          fetch('/encerrar_sessao', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          })
          .then(response => response.json())
          .then(resultado => {
            setTimeout(() => {
              fecharModalEncerramento();
              alert('Sucesso: ' + resultado.mensagem);
            }, 500);
          })
          .catch(error => {
            console.error('Erro:', error);
            mensagemDiv.className = 'modal-message error';
            mensagemDiv.textContent = 'Erro ao encerrar a sessão!';
            mensagemDiv.style.display = 'block';
          });
        }, 1000);
      })
      .catch(error => {
        console.error('Erro:', error);
        mensagemDiv.className = 'modal-message error';
        mensagemDiv.textContent = 'Erro ao validar credenciais!';
        mensagemDiv.style.display = 'block';
      });
    }

    // Fechar modal ao clicar fora dele
    window.onclick = function(event) {
      const modal = document.getElementById('modalEncerramento');
      if(event.target == modal) {
        fecharModalEncerramento();
      }
    }

    // Permitir encerrar com Enter
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('senhaInput').addEventListener('keypress', function(e) {
        if(e.key === 'Enter') {
          validarEEncerrar();
        }
      });
    });