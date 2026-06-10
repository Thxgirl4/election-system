const socket = io();
// Sons
const audioButtons = new Audio('/static/sounds/botoes.mpeg');
audioButtons.preload = 'auto';
const audioSomUrna = new Audio('/static/sounds/somUrna.mpeg');
audioSomUrna.preload = 'auto';
let tituloEleitorSessao = "";
let urnaBloqueada = true;

let etapas = []; // Array VAZIO inicialmente, será preenchido pelo carregarCargos()
let etapaAtual = 0;
let voto = "";
let votosSalvos = {};

// Carregar cargos do servidor ASSIM QUE A PÁGINA ABRIR
async function carregarCargos() {
    try {
        // Chamar rota GET /cargos_eleicao
        const response = await fetch('/cargos_eleicao?anomes=202610');
        const data = await response.json();

        // Validar resposta
        if (!data.cargos || data.cargos.length === 0) {
            console.error("Nenhum cargo encontrado!");
            document.getElementById('tela-bloqueio').innerHTML =
                "ERRO: Nenhum cargo disponível para votação";
            return;
        }

        // Preencher o array etapas com dados do servidor
        etapas = data.cargos.map(cargo => ({
            titulo: cargo.titulo,
            digitos: cargo.digitos
        }));

        console.log("Cargos carregados:", etapas);

    } catch (error) {
        console.error("Erro ao carregar cargos:", error);
        document.getElementById('tela-bloqueio').innerHTML =
            "ERRO ao carregar cargos da eleição";
    }
}

// Chamar ao abrir a página
document.addEventListener('DOMContentLoaded', carregarCargos);

// ====== Func PDFs
function gerarZeroesima() {
    const btnZeroesima = document.getElementById('btnZeroesima');
    const idUrna = 1; // ID da urna (pode ser dinâmico conforme necessário)

    btnZeroesima.classList.add('loading');
    btnZeroesima.disabled = true;
    btnZeroesima.innerText = 'Gerando Zerésima...';

    // Abrir PDF em nova aba
    window.open(`/zeroesima?id_urna=${idUrna}`, '_blank');

    // Restaurar botão após 1.5s
    setTimeout(() => {
        btnZeroesima.classList.remove('loading');
        btnZeroesima.disabled = false;
        btnZeroesima.innerText = 'Zerésima da Urna';
    }, 1500);
}

function gerarBoletim() {
    const btnBoletim = document.getElementById('btnBoletim');
    const idUrna = 1; // ID da urna (pode ser dinâmico conforme necessário)

    btnBoletim.classList.add('loading');
    btnBoletim.disabled = true;
    btnBoletim.innerText = 'Gerando Boletim...';

    // Abrir PDF em nova aba
    window.open(`/boletim?id_urna=${idUrna}`, '_blank');

    // Restaurar botão após 1.5s
    setTimeout(() => {
        btnBoletim.classList.remove('loading');
        btnBoletim.disabled = false;
        btnBoletim.innerText = 'Boletim da Urna';
    }, 1500);
}

// ====== Socket e funções da urna ======
socket.on('urna_destravada', function (data) {
    tituloEleitorSessao = data.titulo;
    urnaBloqueada = false;
    document.getElementById('tela-bloqueio').style.display = 'none';

    etapaAtual = 0;
    votosSalvos = {};
    iniciarEtapa();
});

socket.on('urna_encerrada', function (data) {
    urnaBloqueada = true;
    document.getElementById('tela-votacao').style.display = 'none';
    document.getElementById('tela-bloqueio').innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; gap: 20px; text-align: center;">
                <div style="font-size: 28px; font-weight: bold; letter-spacing: 2px;">SESSÃO ENCERRADA</div>
                <div style="font-size: 18px; line-height: 1.6;">
                    A votação foi encerrada pelo<br>presidente de sessão.<br><br>
                    A urna foi bloqueada.
                </div>
            </div>
        `;
    document.getElementById('tela-bloqueio').style.display = 'flex';
});

function iniciarEtapa() {
    let etapa = etapas[etapaAtual];
    voto = "";
    document.getElementById('nome-cargo').innerText = etapa.titulo;
    document.getElementById('rodape-instrucoes').style.display = 'none';
    document.getElementById('foto-candidato-container').style.display = 'none';

    let htmlNumeros = "";
    for (let i = 0; i < etapa.digitos; i++) {
        htmlNumeros += `<span id="digito${i}"></span>`;
    }
    document.getElementById('display-numeros').innerHTML = htmlNumeros;
    document.getElementById('nome-candidato').innerHTML = "";
}

function inserir(n) {
    if (urnaBloqueada) return;
    // som de botão
    try { audioButtons.currentTime = 0; audioButtons.play(); } catch (e) { /* autoplay bloqueado */ }

    let etapa = etapas[etapaAtual];
    if (voto.length < etapa.digitos) {
        voto += n;
        atualizarDisplay();
        if (voto.length === etapa.digitos) {
            buscarCandidato(voto, etapa.titulo);
        }
    }
}

function buscarCandidato(numeroDigitado, nomeCargo) {
    let divNome = document.getElementById('nome-candidato');
    divNome.innerHTML = "<em style='font-size:18px;'>Buscando...</em>";

    fetch(`/buscar_candidato?numero=${numeroDigitado}&cargo=${nomeCargo}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('rodape-instrucoes').style.display = 'block';

            if (data.nome === "VOTO NULO") {
                document.getElementById('foto-candidato-container').style.display = 'none';
                divNome.innerHTML = `
                        <div style="margin-top: 10px; font-size: 22px;">NÚMERO ERRADO</div>
                        <div style="font-size: 36px; font-weight: bold; margin-top: 15px; text-align: center; animation: piscar 1s infinite;">VOTO NULO</div>
                        <style>@keyframes piscar { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }</style>
                    `;
            } else if (data.nome) {
                divNome.innerHTML = `
                        <p><strong>Nome:</strong><br> ${data.nome}</p>
                        <p><strong>Partido:</strong><br> ${data.partido}</p>
                    `;

                if (data.foto) {
                    let imgElement = document.getElementById('foto-candidato');
                    imgElement.src = `/static/${data.foto}?t=${new Date().getTime()}`;
                    document.getElementById('foto-candidato-container').style.display = 'flex';
                } else {
                    console.log("Candidato encontrado, mas sem foto no banco.");
                    document.getElementById('foto-candidato-container').style.display = 'none';
                }
            }
        })
        .catch(err => {
            console.error("Erro na busca:", err);
            divNome.innerHTML = "Erro ao buscar candidato.";
        });
}

function corrigir() {
    if (urnaBloqueada) return;
    try { audioButtons.currentTime = 0; audioButtons.play(); } catch (e) { }
    voto = "";
    document.getElementById('nome-candidato').innerHTML = "";
    document.getElementById('rodape-instrucoes').style.display = 'none';
    document.getElementById('foto-candidato-container').style.display = 'none';

    if (document.getElementById('display-numeros').innerText === "VOTO EM BRANCO") {
        iniciarEtapa();
    } else {
        atualizarDisplay();
    }
}

function atualizarDisplay() {
    let etapa = etapas[etapaAtual];
    for (let i = 0; i < etapa.digitos; i++) {
        let span = document.getElementById(`digito${i}`);
        if (span) span.innerText = voto[i] || "";
    }
}

function votarBranco() {
    if (urnaBloqueada) return;
    try { audioButtons.currentTime = 0; audioButtons.play(); } catch (e) { }
    voto = "BRANCO";
    document.getElementById('display-numeros').innerHTML = `<div style="font-size: 32px; font-weight: bold; margin-top: 10px; animation: piscar 1s infinite;">VOTO EM BRANCO</div>`;
    document.getElementById('nome-candidato').innerHTML = "";
    document.getElementById('foto-candidato-container').style.display = 'none';
    document.getElementById('rodape-instrucoes').style.display = 'block';
}

function confirmar() {
    if (urnaBloqueada) return;
    try { audioButtons.currentTime = 0; audioButtons.play(); } catch (e) { }

    let etapa = etapas[etapaAtual];
    if (voto.length === etapa.digitos || voto === "BRANCO") {
        votosSalvos[etapa.titulo] = voto;
        etapaAtual++;

        if (etapaAtual < etapas.length) {
            iniciarEtapa();
        } else {
            finalizarVotacao();
        }
    }
}

function finalizarVotacao() {
    // tocar som de fim de votação
    try { audioSomUrna.currentTime = 0; audioSomUrna.play(); } catch (e) { }
    urnaBloqueada = true;
    document.getElementById('rodape-instrucoes').style.display = 'none';
    document.getElementById('foto-candidato-container').style.display = 'none';
    document.getElementById('display-numeros').innerHTML = '';
    document.getElementById('nome-cargo').innerText = '';

    document.getElementById('nome-candidato').innerHTML = `
        <div style="font-size: 60px; text-align: center; margin-top: 40px; font-weight: bold; letter-spacing: 5px;">FIM</div>
      `;

    const payload = {
        eleitor: tituloEleitorSessao,
        votos: votosSalvos
    };

    fetch('/votar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            if (data.erro) {
                alert("Erro: " + data.erro);
            } else {
                socket.emit('urna_bloqueada');

                setTimeout(() => {
                    document.getElementById('tela-bloqueio').style.display = 'flex';
                    document.getElementById('nome-candidato').innerHTML = '';
                }, 3000);
            }
        })
        .catch(err => console.error("Erro ao computar voto:", err));
}