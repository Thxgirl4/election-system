import os
import random
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

load_dotenv(find_dotenv())

print("Host:", os.getenv('DB_HOST'))
print("User:", os.getenv('DB_USER'))
print("Banco:", os.getenv('NOME_BD'))

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

PARTIDOS = [
    (13, 'Partido dos Trabalhadores', 'PT'),
    (22, 'Partido Liberal', 'PL'),
    (15, 'Movimento Democrático Brasileiro', 'MDB'),
    (45, 'Partido da Social Democracia Brasileira', 'PSDB'),
    (12, 'Partido Democrático Trabalhista', 'PDT'),
    (40, 'Partido Socialista Brasileiro', 'PSB'),
    (50, 'Partido Socialismo e Liberdade', 'PSOL'),
    (11, 'Progressistas', 'PP'),
    (55, 'Partido Social Democrático', 'PSD'),
    (44, 'União Brasil', 'UNIÃO')
]

NOMES = ["Carlos", "Ana", "João", "Maria", "Pedro", "Paula", "Lucas", "Mariana", "Luiz", "Fernanda", "Marcos", "Juliana", "Rafael", "Camila", "Rodrigo", "Amanda"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida"]

print("Iniciando o Seed do Banco de Dados...")

with engine.begin() as conn:
    # 1. Adiciona as colunas necesárias (se não existirem)
    conn.execute(text("ALTER TABLE candidato ADD COLUMN IF NOT EXISTS foto_url VARCHAR(255);"))
    conn.execute(text("ALTER TABLE candidato ADD COLUMN IF NOT EXISTS numero_urna INT;"))
    
    conn.execute(text("DELETE FROM urna_candidato;"))
    conn.execute(text("DELETE FROM voto;"))
    conn.execute(text("DELETE FROM candidato;"))
    conn.execute(text("DELETE FROM partido;"))

    for p in PARTIDOS:
        conn.execute(text("INSERT INTO partido (num_partido, nome_partido, sigla) VALUES (:num, :nome, :sigla)"), 
                     {"num": p[0], "nome": p[1], "sigla": p[2]})

    numeros_usados = {1: set(), 2: set()} 

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
        """), {
            "id": i,
            "nome": nome_cand,
            "id_partido": id_partido,
            "id_cargo": id_cargo,
            "numero": numero_urna,
            "foto": foto_url
        })

print("Seed finalizado! 30 candidatos gerados e vinculados às fotos.")