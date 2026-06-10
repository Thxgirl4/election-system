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
    # Distribuindo os 20 eleitores em seções diferentes
    (1, 'Ana Silva', '419283746501', 1),
    (2, 'Bruno Santos', '592837461029', 15),
    (3, 'Carlos Oliveira', '837465019283', 30),
    (4, 'Daniela Souza', '102938475610', 45),
    (5, 'Eduardo Costa', '564738291039', 60),
    (6, 'Fernanda Pereira', '918273645012', 75),
    (7, 'Gabriel Alves', '746583920184', 90),
    (8, 'Helena Ribeiro', '293847561029', 105),
    (9, 'Igor Carvalho', '847561029384', 120),
    (10, 'Julia Lopes', '102938475621', 135),
    (11, 'Mariana Costa', '321654987012', 150),
    (12, 'Pedro Almeida', '654987321098', 165),
    (13, 'Lucas Rodrigues', '987321654032', 180),
    (14, 'Amanda Ferreira', '147258369014', 195),
    (15, 'Rafael Gomes', '258369147025', 210),
    (16, 'Beatriz Martins', '369147258036', 225),
    (17, 'Thiago Rocha', '753951852075', 240),
    (18, 'Carolina Mendes', '951753852095', 255),
    (19, 'Gustavo Lima', '852963741085', 270),
    (20, 'Juliana Castro', '159357258015', 287)
]

ELEICOES = [('202610', 1, 2026), ('202410', 1, 2024)]
URNAS = [
    (1, '2026-10-04', 23),  # Urna 1 → Seção 1
    (2, '2026-10-04', 29),  # Urna 2 → Seção 3
    (3, '2024-10-06', 8),  # Urna 3 → Seção 1
]
URNA_ELEICAO = [(1, '202610'), (2, '202610'), (3, '202410')]
ELEICAO_CARGO = [('202610', 1), ('202610', 2), ('202610', 3), ('202610', 4), ('202610', 5)]

PRESIDENTES = [
    ('Beatriz Mendes', 'beatriz', 'poder2026', 23),  # Seção 1
    ('Camila Santos', 'camila', 'votacao123', 29),   # Seção 3
]

NOMES = ["Carlos", "Ana", "João", "Maria", "Pedro", "Paula", "Lucas", "Mariana", "Luiz", "Fernanda", "Marcos", "Juliana", "Rafael", "Camila", "Rodrigo", "Amanda"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida"]

ZONAS = [
    (1, '07', 'Bagé', 'RS'),      # id_zona=1
    (2, '142', 'Bagé', 'RS')     # id_zona=2
]

# SEÇÕES ELEITORAIS - Zona 1 (id_zona = 1)
SECOES = [
    # ZONA 1 - Seções agrupadas por local de votação
    (23, 1, 'A.A.B.B.'), (102, 1, 'A.A.B.B.'), (146, 1, 'A.A.B.B.'), (190, 1, 'A.A.B.B.'), (242, 1, 'A.A.B.B.'), (261, 1, 'A.A.B.B.'), (299, 1, 'A.A.B.B.'), (340, 1, 'A.A.B.B.'),
    (184, 1, 'CAPELA SAGRADA FAMILIA'), (228, 1, 'CAPELA SAGRADA FAMILIA'), (292, 1, 'CAPELA SAGRADA FAMILIA'),
    (17, 1, 'CASA DE CULTURA PEDRO WAYNE'), (50, 1, 'CASA DE CULTURA PEDRO WAYNE'), (65, 1, 'CASA DE CULTURA PEDRO WAYNE'), (96, 1, 'CASA DE CULTURA PEDRO WAYNE'), (132, 1, 'CASA DE CULTURA PEDRO WAYNE'), (167, 1, 'CASA DE CULTURA PEDRO WAYNE'), (178, 1, 'CASA DE CULTURA PEDRO WAYNE'), (195, 1, 'CASA DE CULTURA PEDRO WAYNE'), (231, 1, 'CASA DE CULTURA PEDRO WAYNE'),
    (58, 1, 'CORUJAO'), (143, 1, 'CORUJAO'), (222, 1, 'CORUJAO'),
    (1, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (62, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (69, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (101, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (115, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (250, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (287, 1, 'CRECHE NOSSA SENHORA DO CARMO'), (326, 1, 'CRECHE NOSSA SENHORA DO CARMO'),
    (14, 1, 'ESCOLA ANTENOR GONCALVES PEREIRA'), (19, 1, 'ESCOLA ANTENOR GONCALVES PEREIRA'), (151, 1, 'ESCOLA ANTENOR GONCALVES PEREIRA'), (212, 1, 'ESCOLA ANTENOR GONCALVES PEREIRA'), (213, 1, 'ESCOLA ANTENOR GONCALVES PEREIRA'),
    (16, 1, 'ESCOLA AUXILIADORA'), (18, 1, 'ESCOLA AUXILIADORA'), (43, 1, 'ESCOLA AUXILIADORA'), (45, 1, 'ESCOLA AUXILIADORA'), (54, 1, 'ESCOLA AUXILIADORA'), (114, 1, 'ESCOLA AUXILIADORA'), (166, 1, 'ESCOLA AUXILIADORA'), (209, 1, 'ESCOLA AUXILIADORA'), (260, 1, 'ESCOLA AUXILIADORA'),
    (3, 1, 'ESCOLA BRADESCO'), (10, 1, 'ESCOLA BRADESCO'), (134, 1, 'ESCOLA BRADESCO'), (142, 1, 'ESCOLA BRADESCO'), (144, 1, 'ESCOLA BRADESCO'), (159, 1, 'ESCOLA BRADESCO'), (170, 1, 'ESCOLA BRADESCO'), (210, 1, 'ESCOLA BRADESCO'), (223, 1, 'ESCOLA BRADESCO'), (227, 1, 'ESCOLA BRADESCO'), (252, 1, 'ESCOLA BRADESCO'), (254, 1, 'ESCOLA BRADESCO'),
    (2, 1, 'ESCOLA CARLOS KLUWE'), (51, 1, 'ESCOLA CARLOS KLUWE'), (123, 1, 'ESCOLA CARLOS KLUWE'), (168, 1, 'ESCOLA CARLOS KLUWE'), (185, 1, 'ESCOLA CARLOS KLUWE'), (225, 1, 'ESCOLA CARLOS KLUWE'), (257, 1, 'ESCOLA CARLOS KLUWE'), (300, 1, 'ESCOLA CARLOS KLUWE'),
    (12, 1, 'ESCOLA ESPIRITO SANTO'), (52, 1, 'ESCOLA ESPIRITO SANTO'), (112, 1, 'ESCOLA ESPIRITO SANTO'), (136, 1, 'ESCOLA ESPIRITO SANTO'), (202, 1, 'ESCOLA ESPIRITO SANTO'),
    (22, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (93, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (111, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (139, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (165, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (183, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (204, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (232, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (280, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'), (328, 1, 'ESCOLA FELIX CONTREIRAS RODRIGUES'),
    (35, 1, 'ESCOLA FREI PLACIDO'), (95, 1, 'ESCOLA FREI PLACIDO'), (120, 1, 'ESCOLA FREI PLACIDO'), (147, 1, 'ESCOLA FREI PLACIDO'), (174, 1, 'ESCOLA FREI PLACIDO'), (196, 1, 'ESCOLA FREI PLACIDO'), (226, 1, 'ESCOLA FREI PLACIDO'), (286, 1, 'ESCOLA FREI PLACIDO'), (339, 1, 'ESCOLA FREI PLACIDO'),
    (6, 1, 'ESCOLA KALIL A. KALIL'), (103, 1, 'ESCOLA KALIL A. KALIL'), (133, 1, 'ESCOLA KALIL A. KALIL'), (180, 1, 'ESCOLA KALIL A. KALIL'), (248, 1, 'ESCOLA KALIL A. KALIL'), (265, 1, 'ESCOLA KALIL A. KALIL'),
    (44, 1, 'ESCOLA MASCARENHAS DE MORAES'), (110, 1, 'ESCOLA MASCARENHAS DE MORAES'), (154, 1, 'ESCOLA MASCARENHAS DE MORAES'),
    (21, 1, 'ESCOLA RENY COLARES'), (122, 1, 'ESCOLA RENY COLARES'), (182, 1, 'ESCOLA RENY COLARES'), (249, 1, 'ESCOLA RENY COLARES'), (295, 1, 'ESCOLA RENY COLARES'), (314, 1, 'ESCOLA RENY COLARES'), (318, 1, 'ESCOLA RENY COLARES'),
    (9, 1, 'ESCOLA SILVEIRA MARTINS'), (106, 1, 'ESCOLA SILVEIRA MARTINS'), (135, 1, 'ESCOLA SILVEIRA MARTINS'), (172, 1, 'ESCOLA SILVEIRA MARTINS'), (200, 1, 'ESCOLA SILVEIRA MARTINS'), (243, 1, 'ESCOLA SILVEIRA MARTINS'), (338, 1, 'ESCOLA SILVEIRA MARTINS'),
    (33, 1, 'ESCOLA TEO VAZ OBINO'), (34, 1, 'ESCOLA TEO VAZ OBINO'), (98, 1, 'ESCOLA TEO VAZ OBINO'), (127, 1, 'ESCOLA TEO VAZ OBINO'), (140, 1, 'ESCOLA TEO VAZ OBINO'), (162, 1, 'ESCOLA TEO VAZ OBINO'), (197, 1, 'ESCOLA TEO VAZ OBINO'), (207, 1, 'ESCOLA TEO VAZ OBINO'), (237, 1, 'ESCOLA TEO VAZ OBINO'), (294, 1, 'ESCOLA TEO VAZ OBINO'), (329, 1, 'ESCOLA TEO VAZ OBINO'),
    (15, 1, 'PREFEITURA MUNICIPAL'), (40, 1, 'PREFEITURA MUNICIPAL'), (59, 1, 'PREFEITURA MUNICIPAL'), (71, 1, 'PREFEITURA MUNICIPAL'), (119, 1, 'PREFEITURA MUNICIPAL'), (155, 1, 'PREFEITURA MUNICIPAL'),
    (5, 1, 'URCAMP'), (91, 1, 'URCAMP'), (100, 1, 'URCAMP'), (121, 1, 'URCAMP'), (141, 1, 'URCAMP'), (157, 1, 'URCAMP'), (179, 1, 'URCAMP'), (193, 1, 'URCAMP'), (219, 1, 'URCAMP'), (234, 1, 'URCAMP'), (256, 1, 'URCAMP'),
    
    # ZONA 2 - Seções agrupadas por local de votação
    (56, 2, 'CAMPUS RURAL DA URCAMP'),
    (7, 2, 'CENTRO ADMINISTRATIVO'), (41, 2, 'CENTRO ADMINISTRATIVO'), (89, 2, 'CENTRO ADMINISTRATIVO'), (109, 2, 'CENTRO ADMINISTRATIVO'), (137, 2, 'CENTRO ADMINISTRATIVO'), (161, 2, 'CENTRO ADMINISTRATIVO'), (187, 2, 'CENTRO ADMINISTRATIVO'), (194, 2, 'CENTRO ADMINISTRATIVO'), (240, 2, 'CENTRO ADMINISTRATIVO'), (349, 2, 'CENTRO ADMINISTRATIVO'),
    (4, 2, 'CENTRO SOCIAL URBANO'), (99, 2, 'CENTRO SOCIAL URBANO'), (128, 2, 'CENTRO SOCIAL URBANO'), (169, 2, 'CENTRO SOCIAL URBANO'), (186, 2, 'CENTRO SOCIAL URBANO'), (203, 2, 'CENTRO SOCIAL URBANO'), (238, 2, 'CENTRO SOCIAL URBANO'), (288, 2, 'CENTRO SOCIAL URBANO'),
    (32, 2, 'CIEP'), (131, 2, 'CIEP'), (181, 2, 'CIEP'), (247, 2, 'CIEP'), (357, 2, 'CIEP'),
    (81, 2, 'ESCOLA ANA MOGLIA'),
    (61, 2, 'ESCOLA CANDIDO BASTOS'), (245, 2, 'ESCOLA CANDIDO BASTOS'), (333, 2, 'ESCOLA CANDIDO BASTOS'),
    (278, 2, 'ESCOLA CARLOS MARIO MERCIO DA SILVEIRA'), (302, 2, 'ESCOLA CARLOS MARIO MERCIO DA SILVEIRA'), (317, 2, 'ESCOLA CARLOS MARIO MERCIO DA SILVEIRA'), (351, 2, 'ESCOLA CARLOS MARIO MERCIO DA SILVEIRA'), (362, 2, 'ESCOLA CARLOS MARIO MERCIO DA SILVEIRA'),
    (334, 2, 'ESCOLA CREUSA GIORGIS'), (358, 2, 'ESCOLA CREUSA GIORGIS'), (367, 2, 'ESCOLA CREUSA GIORGIS'),
    (11, 2, 'ESCOLA DARCY AZAMBUJA'), (126, 2, 'ESCOLA DARCY AZAMBUJA'), (205, 2, 'ESCOLA DARCY AZAMBUJA'), (275, 2, 'ESCOLA DARCY AZAMBUJA'), (312, 2, 'ESCOLA DARCY AZAMBUJA'), (350, 2, 'ESCOLA DARCY AZAMBUJA'),
    (188, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (198, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (214, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (224, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (244, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (251, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (263, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (298, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'), (331, 2, 'ESCOLA ESTADUAL DE ENSINO MEDIO FARROUPILHA'),
    (49, 2, 'ESCOLA FREDERCIO PETRUCCI'), (104, 2, 'ESCOLA FREDERCIO PETRUCCI'), (152, 2, 'ESCOLA FREDERCIO PETRUCCI'), (189, 2, 'ESCOLA FREDERCIO PETRUCCI'), (239, 2, 'ESCOLA FREDERCIO PETRUCCI'),
    (192, 2, 'ESCOLA JOAO SEVERIANO DA FONSECA'), (324, 2, 'ESCOLA JOAO SEVERIANO DA FONSECA'), (356, 2, 'ESCOLA JOAO SEVERIANO DA FONSECA'),
    (46, 2, 'ESCOLA JULINHA TABORDA'), (116, 2, 'ESCOLA JULINHA TABORDA'), (156, 2, 'ESCOLA JULINHA TABORDA'), (199, 2, 'ESCOLA JULINHA TABORDA'), (233, 2, 'ESCOLA JULINHA TABORDA'), (330, 2, 'ESCOLA JULINHA TABORDA'),
    (36, 2, 'ESCOLA LUIZ MERCIO TEIXEIRA'), (113, 2, 'ESCOLA LUIZ MERCIO TEIXEIRA'), (158, 2, 'ESCOLA LUIZ MERCIO TEIXEIRA'), (216, 2, 'ESCOLA LUIZ MERCIO TEIXEIRA'), (343, 2, 'ESCOLA LUIZ MERCIO TEIXEIRA'),
    (342, 2, 'ESCOLA MARIA DE LURDES MOLINA'), (363, 2, 'ESCOLA MARIA DE LURDES MOLINA'),
    (73, 2, 'ESCOLA MARTINHO SARAIVA'),
    (27, 2, 'ESCOLA MELANIE GRANIER'), (37, 2, 'ESCOLA MELANIE GRANIER'), (39, 2, 'ESCOLA MELANIE GRANIER'), (138, 2, 'ESCOLA MELANIE GRANIER'), (206, 2, 'ESCOLA MELANIE GRANIER'),
    (24, 2, 'ESCOLA MONSENHOR COSTABILE HIPOLITO'), (163, 2, 'ESCOLA MONSENHOR COSTABILE HIPOLITO'), (258, 2, 'ESCOLA MONSENHOR COSTABILE HIPOLITO'),
    (347, 2, 'ESCOLA MUNICIPAL SANTOS DUMONT'), (354, 2, 'ESCOLA MUNICIPAL SANTOS DUMONT'),
    (129, 2, 'ESCOLA PADRE AQUINO ROCHA'), (145, 2, 'ESCOLA PADRE AQUINO ROCHA'), (153, 2, 'ESCOLA PADRE AQUINO ROCHA'), (164, 2, 'ESCOLA PADRE AQUINO ROCHA'), (176, 2, 'ESCOLA PADRE AQUINO ROCHA'), (337, 2, 'ESCOLA PADRE AQUINO ROCHA'), (346, 2, 'ESCOLA PADRE AQUINO ROCHA'),
    (72, 2, 'ESCOLA RURAL SIMOES PIRES'), (80, 2, 'ESCOLA RURAL SIMOES PIRES'),
    (13, 2, 'ESCOLA SAO JUDAS TADEU'), (105, 2, 'ESCOLA SAO JUDAS TADEU'), (125, 2, 'ESCOLA SAO JUDAS TADEU'), (177, 2, 'ESCOLA SAO JUDAS TADEU'), (217, 2, 'ESCOLA SAO JUDAS TADEU'),
    (29, 2, 'ESCOLA SAO PEDRO'), (90, 2, 'ESCOLA SAO PEDRO'), (92, 2, 'ESCOLA SAO PEDRO'), (94, 2, 'ESCOLA SAO PEDRO'), (107, 2, 'ESCOLA SAO PEDRO'), (118, 2, 'ESCOLA SAO PEDRO'), (296, 2, 'ESCOLA SAO PEDRO'), (319, 2, 'ESCOLA SAO PEDRO'), (344, 2, 'ESCOLA SAO PEDRO'), (360, 2, 'ESCOLA SAO PEDRO'), (366, 2, 'ESCOLA SAO PEDRO'),
    (68, 2, 'ESCOLA VISCONDE RIBEIRO DE MAGALHAES'), (148, 2, 'ESCOLA VISCONDE RIBEIRO DE MAGALHAES'), (220, 2, 'ESCOLA VISCONDE RIBEIRO DE MAGALHAES'), (355, 2, 'ESCOLA VISCONDE RIBEIRO DE MAGALHAES'),
    (8, 2, 'ESCOLA WALDEMAR MACHADO'), (124, 2, 'ESCOLA WALDEMAR MACHADO'), (173, 2, 'ESCOLA WALDEMAR MACHADO'), (221, 2, 'ESCOLA WALDEMAR MACHADO'), (271, 2, 'ESCOLA WALDEMAR MACHADO'), (293, 2, 'ESCOLA WALDEMAR MACHADO'), (340, 2, 'ESCOLA WALDEMAR MACHADO'), (364, 2, 'ESCOLA WALDEMAR MACHADO'),
    (20, 2, 'PARQUE DA ASSOCIACAO RURAL'), (117, 2, 'PARQUE DA ASSOCIACAO RURAL'), (160, 2, 'PARQUE DA ASSOCIACAO RURAL'), (215, 2, 'PARQUE DA ASSOCIACAO RURAL'), (279, 2, 'PARQUE DA ASSOCIACAO RURAL'), (335, 2, 'PARQUE DA ASSOCIACAO RURAL'),
]

print("Iniciando o Seed do Banco de Dados...")

# ==========================================
# 2. LIMPEZA TOTAL (Ordem das Chaves Estrangeiras)
# ==========================================
print("Limpando registros antigos...")
with engine.begin() as conn:
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
    conn.execute(text("DELETE FROM secao_eleitoral;"))
    conn.execute(text("DELETE FROM zona_eleitoral"))

# ==========================================
# 3. POPULANDO AS TABELAS
# ==========================================
print("Inserindo Cargos e Partidos...")
with engine.begin() as conn:
    for c in CARGOS:
        conn.execute(text("INSERT INTO cargo (id_cargo, num_digitos, nome_cargo) VALUES (:id, :dig, :nome)"), {"id": c[0], "dig": c[1], "nome": c[2]})
    for p in PARTIDOS:
        conn.execute(text("INSERT INTO partido (num_partido, nome_partido, sigla) VALUES (:num, :nome, :sigla)"), {"num": p[0], "nome": p[1], "sigla": p[2]})

print("Inserindo Zonas Eleitorais e Seções...")
with engine.begin() as conn:
    for z in ZONAS:
        conn.execute(text("""
            INSERT INTO zona_eleitoral (id_zona, nome_zona, municipio, estado)
            VALUES (:id, :nome, :municipio, :estado)
        """), {"id": z[0], "nome": z[1], "municipio": z[2], "estado": z[3]})
    print(f"  ✓ {len(ZONAS)} zonas inseridas")

    for s in SECOES:
        conn.execute(text("""
            INSERT INTO secao_eleitoral (numero_secao, id_zona, local_votacao)
            VALUES (:numero, :id_zona, :local)
        """), {"numero": s[0], "id_zona": s[1], "local": s[2]})
    print(f"  ✓ {len(SECOES)} seções inseridas")

with engine.begin() as conn:
    
    print("Inserindo Eleitores, Eleições e Urnas...")
    
    # Mapear numero_secao -> id_secao para usar os IDs corretos
    secoes_map = {}
    secoes_db = conn.execute(text("SELECT id_secao, numero_secao FROM secao_eleitoral")).fetchall()
    for sec in secoes_db:
        secoes_map[int(sec[1])] = sec[0]  # numero_secao (int) -> id_secao
    
    # Atualizar ELEITORES com os id_secao corretos
    for e in ELEITORES:
        numero_secao_original = e[3]  # Este era id_secao antes
        # Mapear para seção real baseado na distribuição pretendida
        # numero_secao_original de 1 a 287 precisa ser convertido para os id_secao disponíveis
        if numero_secao_original in secoes_map:
            id_secao_real = secoes_map[numero_secao_original]
        else:
            # Se numero_secao não existe exatamente, usar a primeira seção disponível
            id_secao_real = secoes_map[min(secoes_map.keys())]
        
        conn.execute(text("""
            INSERT INTO eleitor (id_eleitor, nome, titulo, id_secao)
            VALUES (:id, :nome, :tit, :id_secao)
        """), {"id": e[0], "nome": e[1], "tit": e[2], "id_secao": id_secao_real})
    
    for el in ELEICOES:
        conn.execute(text("INSERT INTO eleicao (anomes, eleicao_nro, ano_eleicao) VALUES (:anomes, :nro, :ano)"), {"anomes": el[0], "nro": el[1], "ano": el[2]})
    
    for u in URNAS:
        numero_secao = u[2]
        id_secao_real = secoes_map.get(numero_secao, list(secoes_map.values())[0])
        conn.execute(text("""
            INSERT INTO urna (id_urna, data_comparecimento, id_secao)
            VALUES (:id, :data, :id_secao)
        """), {"id": u[0], "data": u[1], "id_secao": id_secao_real})
    
    for ue in URNA_ELEICAO:
        conn.execute(text("INSERT INTO urna_eleicao (id_urna, anomes) VALUES (:id, :anomes)"), {"id": ue[0], "anomes": ue[1]})
    for ec in ELEICAO_CARGO:
        conn.execute(text("INSERT INTO eleicao_cargo (anomes, id_cargo) VALUES (:anomes, :id)"), {"anomes": ec[0], "id": ec[1]})
    
    for pres in PRESIDENTES:
        numero_secao = pres[3]
        id_secao_real = secoes_map.get(numero_secao, list(secoes_map.values())[0])
        conn.execute(text("""
            INSERT INTO presidente_sessao (nome_presidente, usuario, senha, id_secao)
            VALUES (:nome, :user, :senha, :id_secao)
        """), {"nome": pres[0], "user": pres[1], "senha": pres[2], "id_secao": id_secao_real})

    print("Gerando candidatos para todos os 5 cargos e vinculando às Urnas...")
    
    # Distribuição: 10 candidatos por cargo
    candidatos_por_cargo = {
        1: 10,  # Presidente - 2 dígitos
        2: 10,  # Governador - 2 dígitos
        3: 10,  # Senador - 3 dígitos
        4: 10,  # Dep. Federal - 4 dígitos
        5: 10   # Dep. Estadual - 5 dígitos
    }
    
    # Geradores de números apropriados para cada cargo
    numero_geradores = {
        1: lambda cargoid, idx: 10 + idx,                    # 10-19 (2 dígitos)
        2: lambda cargoid, idx: 20 + idx,                    # 20-29 (2 dígitos)
        3: lambda cargoid, idx: 100 + (idx * 10),           # 100, 110, 120... (3 dígitos)
        4: lambda cargoid, idx: 1000 + (idx * 100),         # 1000, 1100, 1200... (4 dígitos)
        5: lambda cargoid, idx: 10000 + (idx * 1000)        # 10000, 11000, 12000... (5 dígitos)
    }
    
    candidato_id = 1
    nomes_gerados = set()  # Set para armazenar os nomes já criados e evitar repetições
    
    for id_cargo in range(1, 6):
        num_cargos = candidatos_por_cargo[id_cargo]
        
        for idx in range(num_cargos):
            
            # Validação para gerar um nome único
            while True:
                nome_cand = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"
                if nome_cand not in nomes_gerados:
                    nomes_gerados.add(nome_cand)
                    break
                    
            partido = random.choice(PARTIDOS)
            id_partido = partido[0]
            
            # Gerar número de urna apropriado para o cargo
            numero_urna = numero_geradores[id_cargo](id_cargo, idx)
            
            # Fotos se repetem (agora com 50 arquivos disponíveis)
            numero_foto = ((candidato_id - 1) % 50) + 1
            foto_url = f"img/candidatos/{numero_foto}.jpg"
            
            conn.execute(text("""
                INSERT INTO candidato (id_candidato, nome_candidato, id_partido, id_cargo, numero_urna, foto_url)
                VALUES (:id, :nome, :id_partido, :id_cargo, :numero, :foto)
            """), {
                "id": candidato_id,
                "nome": nome_cand,
                "id_partido": id_partido,
                "id_cargo": id_cargo,
                "numero": numero_urna,
                "foto": foto_url
            })
            
            # Vincula candidatos nas urnas 1 e 2 para testes
            conn.execute(text("INSERT INTO urna_candidato (id_urna, id_candidato) VALUES (:id_u1, :id_c), (:id_u2, :id_c)"), 
                        {"id_u1": 1, "id_u2": 2, "id_c": candidato_id})
            
            candidato_id += 1

    print("\n=== VALIDAÇÃO PÓS-SEED ===")
    resultado = conn.execute(text("""
        SELECT 
            (SELECT COUNT(*) FROM zona_eleitoral) as zonas,
            (SELECT COUNT(*) FROM secao_eleitoral) as secoes,
            (SELECT COUNT(*) FROM eleitor) as eleitores,
            (SELECT COUNT(*) FROM eleitor WHERE id_secao IS NOT NULL) as eleitores_com_secao,
            (SELECT COUNT(*) FROM candidato) as candidatos,
            (SELECT COUNT(*) FROM urna) as urnas,
            (SELECT COUNT(*) FROM urna WHERE id_secao IS NOT NULL) as urnas_com_secao
    """)).fetchone()

    print(f"✓ Zonas: {resultado[0]}")
    print(f"✓ Seções: {resultado[1]}")
    print(f"✓ Eleitores: {resultado[2]}")
    print(f"✓ Eleitores com seção: {resultado[3]}")
    print(f"✓ Candidatos: {resultado[4]}")
    print(f"✓ Urnas: {resultado[5]}")
    print(f"✓ Urnas com seção: {resultado[6]}")

    if resultado[2] != resultado[3]:
        print("❌ ERRO: Alguns eleitores não têm seção!")
    else:
        print("✅ Seed finalizado com sucesso!")