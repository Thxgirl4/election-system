## cada um deve criar sua propria branch, para não dar conflitos
## depois só fazer o merge

## 1 passo --> criar uma venv - python -m venv .venv 
## 2 passo --> ativar a venv (ambiente virtual para guardar as libs do python) - source .venv/bin/activate (linux)
## 3 passo --> instalar as libs da aplicação - pip install -r requirements.txt 

## criar um arquivo .env, nesse arquivo deve conter os dados do banco de dados de vcs, na seguinte estrutura: 



DB_HOST = localhost
DB_USER = user_database
DB_PASSWORD = user_pass
DB_NAME = dbname


## 1. Banco de Dados (script.sql)
✅ Criação da tabela presidente_sessao com campos: id, nome, usuário, senha e data de criação
✅ Adição de coluna status na tabela urna_eleicao com valores ('ABERTA', 'ENCERRADA')
✅ Inserção de 5 presidentes com nomes femininos para testes
## 2. Rota de Login (main.py - /login_presidente)
✅ Endpoint POST para validar credenciais do presidente
✅ Retorna id_presidente, nome e usuário em caso de sucesso
✅ Validação de usuário e senha obrigatórios
## 3. Rota de Encerramento (main.py - /encerrar_sessao)
✅ Endpoint POST para encerrar a votação
✅ Verifica se urna já foi encerrada (impede duplo encerramento)
✅ Marca a urna como 'ENCERRADA' no banco de dados
✅ Emite evento SocketIO em tempo real para todos os clientes (urna_encerrada)
## 4. Proteção de Votos (main.py - /votar)
✅ Validação de status da urna antes de aceitar votos
✅ Bloqueia votos se urna estiver 'ENCERRADA'
✅ Retorna erro 403 com mensagem clara
## 5. Liberação de Urna (main.py - mesario_libera_urna)
✅ Verifica se urna foi encerrada antes de liberar
✅ Exibe mensagem de erro se tentar liberar após encerramento
✅ Mantém lógica original intacta
## 6. Bloqueio de Urna (main.py - urna_bloqueada)
✅ Verifica status da urna ao finalizar votação
✅ Exibe mensagem diferente se sessão foi encerrada
✅ Comportamento normal se urna está aberta
## 7. Reset de Urna (main.py - /votacao GET)
✅ Limpa votos, comparecimentos e reseta status para 'ABERTA'
✅ Permite retesting do sistema
## 8. Interface Principal (templates/Seleção.html)
✅ Novo botão "3. Encerrar Sessão" em vermelho
✅ Modal minimalista para validação de credenciais
✅ Validação de horário (apenas >= 17h permite encerramento)
✅ Mensagens contextualizadas: erro (vermelho), aviso (amarelo), sucesso (verde)
✅ Confirmação com usuário e senha do presidente
✅ Suporte a Enter para confirmar
## 9. Interface da Urna (templates/votacao.html)
✅ Novo evento SocketIO urna_encerrada capturado
✅ Exibe mensagem "SESSÃO ENCERRADA" quando presidente encerra
✅ Bloqueia urna imediatamente ao receber evento
✅ Informa eleitor sobre encerramento pelo presidente
## 10. Fluxo de Encerramento Completo
✅ Presidente acessa "Encerrar Sessão" na página inicial
✅ Modal pede usuário e senha
✅ Valida horário (>= 17h)
✅ Valida credenciais via /login_presidente
✅ Encerra via /encerrar_sessao
✅ Evento em tempo real notifica todas as urnas
✅ Urnas bloqueadas recebem mensagem de encerramento
## 11. Segurança Implementada
✅ Duplo encerramento bloqueado (retorna 400)
✅ Votos não podem ser computados após encerramento (403)
✅ Mesário não pode liberar urna após encerramento
✅ Validação de horário para encerramento
✅ Credenciais obrigatórias para ação