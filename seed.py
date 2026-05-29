import os
import random
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv())

print("Conectando ao banco...")
engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

# ==========================================
# 1. DADOS FIXOS PARA INSERÇÃO
# ==========================================
CARGOS = [
    (1, 2, 'Presidente'), (2, 2, 'Governador'), (3, 3, 'Senador'),
    (4, 4, 'Dep. Federal'), (5, 5, 'Dep. Estadual')
]

PARTIDOS = [
    (13, 'Partido dos Trabalhadores', 'PT'), (22, 'Partido Liberal', 'PL'),
    (15, 'Movimento Democrático Brasileiro', 'MDB'), (45, 'Partido da Social Democracia Brasileira', 'PSDB'),
    (12, 'Partido Democrático Trabalhista', 'PDT'), (40, 'Partido Socialista Brasileiro', 'PSB'),
    (50, 'Partido Socialismo e Liberdade', 'PSOL'), (11, 'Progressistas', 'PP'),
    (55, 'Partido Social Democrático', 'PSD'), (44, 'União Brasil', 'UNIÃO')
]

ELEITORES = [
    (1, 'Ana Silva', '419283746501', '012', '0451'), (2, 'Bruno Santos', '592837461029', '054', '0192'),
    (3, 'Carlos Oliveira', '837465019283', '103', '0834'), (4, 'Daniela Souza', '102938475610', '088', '0023'),
    (5, 'Eduardo Costa', '564738291039', '201', '0567'), (6, 'Fernanda Pereira', '918273645012', '310', '0890'),
    (7, 'Gabriel Alves', '746583920184', '005', '0112'), (8, 'Helena Ribeiro', '293847561029', '124', '0345'),
    (9, 'Igor Carvalho', '847561029384', '076', '0678'), (10, 'Julia Lopes', '102938475621', '019', '0901'),
    (11, 'Mariana Costa', '321654987012', '045', '0123'), (12, 'Pedro Almeida', '654987321098', '089', '0456'),
    (13, 'Lucas Rodrigues', '987321654032', '112', '0789'), (14, 'Amanda Ferreira', '147258369014', '034', '0258'),
    (15, 'Rafael Gomes', '258369147025', '067', '0369'), (16, 'Beatriz Martins', '369147258036', '090', '0147'),
    (17, 'Thiago Rocha', '753951852075', '120', '0852'), (18, 'Carolina Mendes', '951753852095', '015', '0963'),
    (19, 'Gustavo Lima', '852963741085', '078', '0741'), (20, 'Juliana Castro', '159357258015', '056', '0159')
]

ELEICOES = [('202610', 1, 2026), ('202410', 1, 2024)]
URNAS = [(1, '2026-10-04'), (2, '2026-10-04'), (3, '2024-10-06')]
URNA_ELEICAO = [(1, '202610'), (2, '202610'), (3, '202410')]
ELEICAO_CARGO = [('202610', 1), ('202610', 2), ('202610', 3), ('202610', 4), ('202610', 5)]
PRESIDENTES = [('Beatriz Mendes', 'beatriz', 'poder2026'), ('Camila Santos', 'camila', 'votacao123')]

NOMES = ["Carlos", "Ana", "João", "Maria", "Pedro", "Paula", "Lucas", "Mariana", "Luiz", "Fernanda", "Marcos", "Juliana", "Rafael", "Camila", "Rodrigo", "Amanda"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida"]

print("Iniciando o Seed do Banco de Dados...")

with engine.begin() as conn:
    # ==========================================
    # 2. LIMPEZA TOTAL (Ordem das Chaves Estrangeiras)
    # ==========================================
    print("Limpando registros antigos...")
    conn.execute(text("DELETE FROM comparecimento;"))
    conn.execute(text("DELETE FROM voto;"))
    conn.execute(text("DELETE FROM urna_candidato;"))
    conn.execute(text("DELETE FROM eleicao_cargo;"))
    conn.execute(text("DELETE FROM urna_eleicao;"))
    conn.execute(text("DELETE FROM candidato;"))
    conn.execute(text("DELETE FROM presidente_sessao;"))
    conn.execute(text("DELETE FROM urna;"))
    conn.execute(text("DELETE FROM eleicao;"))
    conn.execute(text("DELETE FROM eleitor;"))
    conn.execute(text("DELETE FROM cargo;"))
    conn.execute(text("DELETE FROM partido;"))

    # ==========================================
    # 3. POPULANDO AS TABELAS
    # ==========================================
    print("Inserindo Cargos e Partidos...")
    for c in CARGOS:
        conn.execute(text("INSERT INTO cargo (id_cargo, num_digitos, nome_cargo) VALUES (:id, :dig, :nome)"), {"id": c[0], "dig": c[1], "nome": c[2]})
    for p in PARTIDOS:
        conn.execute(text("INSERT INTO partido (num_partido, nome_partido, sigla) VALUES (:num, :nome, :sigla)"), {"num": p[0], "nome": p[1], "sigla": p[2]})

    print("Inserindo Eleitores, Eleições e Urnas...")
    for e in ELEITORES:
        conn.execute(text("INSERT INTO eleitor (id_eleitor, nome, titulo, zona, sessao) VALUES (:id, :nome, :tit, :zona, :sessao)"), {"id": e[0], "nome": e[1], "tit": e[2], "zona": e[3], "sessao": e[4]})
    for el in ELEICOES:
        conn.execute(text("INSERT INTO eleicao (anomes, eleicao_nro, ano_eleicao) VALUES (:anomes, :nro, :ano)"), {"anomes": el[0], "nro": el[1], "ano": el[2]})
    for u in URNAS:
        conn.execute(text("INSERT INTO urna (id_urna, data_comparecimento) VALUES (:id, :data)"), {"id": u[0], "data": u[1]})
    for ue in URNA_ELEICAO:
        conn.execute(text("INSERT INTO urna_eleicao (id_urna, anomes) VALUES (:id, :anomes)"), {"id": ue[0], "anomes": ue[1]})
    for ec in ELEICAO_CARGO:
        conn.execute(text("INSERT INTO eleicao_cargo (anomes, id_cargo) VALUES (:anomes, :id)"), {"anomes": ec[0], "id": ec[1]})
    for pres in PRESIDENTES:
        conn.execute(text("INSERT INTO presidente_sessao (nome_presidente, usuario, senha) VALUES (:nome, :user, :senha)"), {"nome": pres[0], "user": pres[1], "senha": pres[2]})

    print("Gerando 30 Candidatos aleatórios e vinculando às Urnas...")
    numeros_usados = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}

    for i in range(1, 31):
        nome_cand = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"
        partido = random.choice(PARTIDOS)
        id_partido = partido[0]
        id_cargo = 1 if i <= 15 else 2
        
        numero_urna = id_partido
        while numero_urna in numeros_usados[id_cargo]:
            numero_urna = random.randint(10, 99)
        numeros_usados[id_cargo].add(numero_urna)
        
        foto_url = f"img/candidatos/{i}.jpg" 

        conn.execute(text("""
            INSERT INTO candidato (id_candidato, nome_candidato, id_partido, id_cargo, numero_urna, foto_url)
            VALUES (:id, :nome, :id_partido, :id_cargo, :numero, :foto)
        """), {"id": i, "nome": nome_cand, "id_partido": id_partido, "id_cargo": id_cargo, "numero": numero_urna, "foto": foto_url})

        # Vincula todos os candidatos gerados nas urnas 1 e 2 para podermos testar a votação
        conn.execute(text("INSERT INTO urna_candidato (id_urna, id_candidato) VALUES (1, :id_c), (2, :id_c)"), {"id_c": i})

print("Seed finalizado com sucesso! Seu sistema está 100% populado e pronto para rodar.")