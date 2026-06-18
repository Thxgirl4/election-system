import os
import uuid
import hashlib
import random
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text

# 1. Configurações Iniciais
load_dotenv(find_dotenv())

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

def gerar_hash_id(voto_id):
    """Gera o hash SHA-256 para o voto, seguindo o padrão do main.py"""
    hash_obj = hashlib.sha256(voto_id.encode('utf-8'))
    return hash_obj.hexdigest()[:100]

# 2. Mapeamento de Candidatos fornecidos (ID_CARGO: [LISTA_DE_ID_CANDIDATO])
# Cargo 1: Presidente, Cargo 2: Governador, Cargo 3: Senador
CANDIDATOS_MAP = {
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    2: [11, 12, 13, 14, 15, 16, 17],
    3: [21, 22, 23, 24, 28, 29, 30],
    4: [31, 32, 36, 37, 38, 39, 40],
    5: [41, 42, 43, 44, 45, 49, 50]
}

def simular_votacao(qtd_eleitores=30, id_urna=1):
    """
    Insere votos no banco de dados para uma urna específica.
    Cada eleitor simulado gera um voto para cada um dos 3 cargos listados.
    """
    print(f"🗳️ Iniciando simulação de {qtd_eleitores} eleitores na Urna {id_urna}...")
    
    total_inserido = 0
    
    with engine.begin() as conn:
        for _ in range(qtd_eleitores):
            # O eleitor vota em cada cargo disponível
            for id_cargo, candidatos in CANDIDATOS_MAP.items():
                voto_uuid = uuid.uuid4().hex
                hash_voto = gerar_hash_id(voto_uuid)
                
                # Lógica simples de distribuição de votos:
                # 90% Válidos, 5% Brancos, 5% Nulos
                sorteio = random.random()
                id_candidato = None
                tipo_voto = "VALIDO"
                
                if sorteio < 0.05:
                    tipo_voto = "BRANCO"
                elif sorteio < 0.10:
                    tipo_voto = "NULO"
                else:
                    id_candidato = random.choice(candidatos)
                
                # Inserção na tabela voto
                conn.execute(
                    text("""
                        INSERT INTO voto (hash, id_cargo, id_urna, id_candidato, tipo_voto)
                        VALUES (:hash, :id_cargo, :id_urna, :id_candidato, :tipo_voto)
                    """),
                    {
                        "hash": hash_voto,
                        "id_cargo": id_cargo,
                        "id_urna": id_urna,
                        "id_candidato": id_candidato,
                        "tipo_voto": tipo_voto
                    }
                )
                total_inserido += 1
                
    print(f"✅ Sucesso! {total_inserido} registros de votos inseridos.")

if __name__ == "__main__":
    # Executa a simulação para 30 eleitores (ajuste conforme necessário)
    simular_votacao(qtd_eleitores=200000, id_urna=1)
    print("Finalizado.")