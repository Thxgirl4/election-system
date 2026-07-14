CREATE TABLE IF NOT EXISTS partido (
    num_partido INT PRIMARY KEY,
    nome_partido VARCHAR(100) NOT NULL,
    sigla VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS cargo (
    id_cargo SERIAL PRIMARY KEY,
    nome_cargo VARCHAR(100) NOT NULL,
    num_digitos INT
);

CREATE TABLE IF NOT EXISTS eleitor (
    id_eleitor SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    titulo VARCHAR(20) UNIQUE NOT NULL,
    zona VARCHAR(10) NOT NULL,
    sessao VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS eleicao (
    anomes VARCHAR(6) PRIMARY KEY,
    eleicao_nro INT NOT NULL,
    ano_eleicao INT NOT NULL
);

CREATE TABLE IF NOT EXISTS urna (
    id_urna SERIAL PRIMARY KEY,
    data_comparecimento DATE
);


CREATE TABLE IF NOT EXISTS candidato (
    id_candidato SERIAL PRIMARY KEY,
    nome_candidato VARCHAR(150) NOT NULL,
    id_partido INT NOT NULL,
    id_cargo INT NOT NULL,
    numero_urna VARCHAR(10),
    foto_url VARCHAR(255),
    CONSTRAINT fk_candidato_partido FOREIGN KEY (id_partido) REFERENCES partido(num_partido),
    CONSTRAINT fk_candidato_cargo FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo)
);

CREATE TABLE IF NOT EXISTS voto (
    hash VARCHAR(255) PRIMARY KEY,
    id_cargo INT NOT NULL,
    id_urna INT NOT NULL,
    CONSTRAINT fk_voto_cargo FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo),
    CONSTRAINT fk_voto_urna FOREIGN KEY (id_urna) REFERENCES urna(id_urna)
);

CREATE TABLE IF NOT EXISTS urna_eleicao (
    id_urna INT NOT NULL,
    anomes VARCHAR(6) NOT NULL,
    PRIMARY KEY (id_urna, anomes),
    CONSTRAINT fk_urnaeleicao_urna FOREIGN KEY (id_urna) REFERENCES urna(id_urna),
    CONSTRAINT fk_urnaeleicao_eleicao FOREIGN KEY (anomes) REFERENCES eleicao(anomes)
);

CREATE TABLE IF NOT EXISTS eleicao_cargo (
    anomes VARCHAR(6) NOT NULL,
    id_cargo INT NOT NULL,
    PRIMARY KEY (anomes, id_cargo),
    CONSTRAINT fk_eleicaocargo_eleicao FOREIGN KEY (anomes) REFERENCES eleicao(anomes),
    CONSTRAINT fk_eleicaocargo_cargo FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo)
);

CREATE TABLE IF NOT EXISTS urna_candidato (
    id_urna INT NOT NULL,
    id_candidato INT NOT NULL,
    PRIMARY KEY (id_urna, id_candidato),
    CONSTRAINT fk_urnacandidato_urna FOREIGN KEY (id_urna) REFERENCES urna(id_urna),
    CONSTRAINT fk_urnacandidato_candidato FOREIGN KEY (id_candidato) REFERENCES candidato(id_candidato)
);


ALTER TABLE voto ADD COLUMN id_candidato INT NULL;
ALTER TABLE voto ADD COLUMN tipo_voto VARCHAR(10) DEFAULT 'VALIDO'; -- 'VALIDO', 'BRANCO', 'NULO'
ALTER TABLE voto ADD CONSTRAINT fk_voto_candidato FOREIGN KEY (id_candidato) REFERENCES candidato(id_candidato);


-- adicionado hoje pascoa

CREATE TABLE IF NOT EXISTS comparecimento (
    id_eleitor INT NOT NULL,
    anomes VARCHAR(6) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_eleitor, anomes),
    CONSTRAINT fk_comparecimento_eleitor FOREIGN KEY (id_eleitor) REFERENCES eleitor(id_eleitor),
    CONSTRAINT fk_comparecimento_eleicao FOREIGN KEY (anomes) REFERENCES eleicao(anomes)
);

# criar presidente de sessão
CREATE TABLE IF NOT EXISTS presidente_sessao (
    id_presidente SERIAL PRIMARY KEY,
    nome_presidente VARCHAR(150) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ################## inicio refatoração banco de dados ###########################
-- Contém as zonas eleitorais que existem no município
CREATE TABLE IF NOT EXISTS zona_eleitoral (
    id_zona SERIAL PRIMARY KEY,
    nome_zona VARCHAR(100) NOT NULL,
    municipio VARCHAR(100),
    estado VARCHAR(2),
    UNIQUE(nome_zona, municipio)
);

-- Cada seção pertence a uma zona
CREATE TABLE IF NOT EXISTS secao_eleitoral (
    id_secao SERIAL PRIMARY KEY,
    numero_secao VARCHAR(10) NOT NULL,
    id_zona INT NOT NULL,
    local_votacao VARCHAR(200),
    CONSTRAINT fk_secao_zona FOREIGN KEY (id_zona) 
        REFERENCES zona_eleitoral(id_zona)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_secao_zona UNIQUE (numero_secao, id_zona)
);

-- Criar índice para melhorar performance
CREATE INDEX IF NOT EXISTS idx_secao_zona ON secao_eleitoral(id_zona);

ALTER TABLE eleitor ADD COLUMN IF NOT EXISTS id_secao INT DEFAULT NULL;

-- Extrai todas as zonas ÚNICAS de eleitor.zona e insere em zona_eleitoral
-- ON CONFLICT ignora duplicatas

INSERT INTO zona_eleitoral (nome_zona, municipio, estado)
SELECT DISTINCT 
    eleitor.zona AS nome_zona,
    'Bagé' AS municipio,
    'RS' AS estado
FROM eleitor
WHERE eleitor.zona IS NOT NULL
ON CONFLICT (nome_zona, municipio) DO NOTHING;

-- Combina zona + sessao dos eleitores para criar seções
-- Procura a zona_id correspondente

INSERT INTO secao_eleitoral (numero_secao, id_zona, local_votacao)
SELECT DISTINCT 
    eleitor.sessao AS numero_secao,
    zona_eleitoral.id_zona,
    'Escola Estadual' AS local_votacao
FROM eleitor
INNER JOIN zona_eleitoral ON eleitor.zona = zona_eleitoral.nome_zona
WHERE eleitor.sessao IS NOT NULL
ON CONFLICT (numero_secao, id_zona) DO NOTHING;

UPDATE eleitor e
SET id_secao = s.id_secao
FROM secao_eleitoral s
INNER JOIN zona_eleitoral z ON s.id_zona = z.id_zona
WHERE e.zona = z.nome_zona AND e.sessao = s.numero_secao;

-- Validação 3: Amostra dos dados
SELECT 'Amostra dos dados migrados:' AS info;
SELECT 
    e.id_eleitor, 
    e.nome, 
    z.nome_zona, 
    s.numero_secao,
    s.local_votacao
FROM eleitor e
LEFT JOIN secao_eleitoral s ON e.id_secao = s.id_secao
LEFT JOIN zona_eleitoral z ON s.id_zona = z.id_zona
LIMIT 10;

-- adiciona a restrição de FK
ALTER TABLE eleitor
ADD CONSTRAINT fk_eleitor_secao
FOREIGN KEY (id_secao) REFERENCES secao_eleitoral(id_secao)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Adiciona coluna FK em urna
ALTER TABLE urna ADD COLUMN IF NOT EXISTS id_secao INT DEFAULT NULL;

-- Uma urna pode ser realocada, N:1
ALTER TABLE urna
ADD CONSTRAINT fk_urna_secao
FOREIGN KEY (id_secao) REFERENCES secao_eleitoral(id_secao)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Cada presidente trabalha em uma seção específica
ALTER TABLE presidente_sessao ADD COLUMN IF NOT EXISTS id_secao INT DEFAULT NULL;

ALTER TABLE presidente_sessao
ADD CONSTRAINT fk_presidente_secao
FOREIGN KEY (id_secao) REFERENCES secao_eleitoral(id_secao)
ON DELETE SET NULL
ON UPDATE CASCADE;

ALTER TABLE eleitor DROP COLUMN zona;
ALTER TABLE eleitor DROP COLUMN sessao;

-- segue a ordem e roda a seed.py depois
################## FIM refatoração banco de dados ###########################

-- 1. Inserindo Cargos
INSERT INTO cargo (id_cargo, num_digitos, nome_cargo) VALUES 
(1, 2, 'Presidente'),
(2, 2, 'Governador'),
(3, 3, 'Senador'),
(4, 4, 'Dep. Federal'),
(5, 5, 'Dep. Estadual');

-- 2. Inserindo Partidos
INSERT INTO partido (num_partido, nome_partido, sigla) VALUES 
(10, 'Partido do Amanhã', 'PDA'),
(11, 'União Cívica', 'UC'),
(12, 'Movimento Popular', 'MP'),
(13, 'Partido do Futuro', 'PF'),
(14, 'Frente Democrática', 'FD'),
(15, 'Partido da Nova Era', 'PNE'),
(16, 'Ação Cidadã', 'AC');

-- 3. Inserindo Candidatos 
INSERT INTO candidato (id_candidato, nome_candidato, id_partido, id_cargo) VALUES 
(1, 'Armando Nogueira', 10, 1),
(2, 'Bianca Leal', 11, 1),
(3, 'Celso Freitas', 12, 1),
(4, 'Dalva Rios', 13, 2),
(5, 'Eduardo Viana', 14, 2),
(6, 'Flavia Gusmão', 15, 2),
(7, 'Gilberto Assis', 16, 3),
(8, 'Helena Bastos', 10, 3),
(9, 'Igor Machado', 11, 3),
(10, 'Joana Diniz', 12, 4),
(11, 'Kleber Munhoz', 13, 4),
(12, 'Laura Peixoto', 14, 4),
(13, 'Marcos Valente', 15, 5),
(14, 'Natalia Cruz', 16, 5),
(15, 'Otavio Lemos', 10, 5),
(16, 'Patricia Luz', 11, 1),
(17, 'Renato Farias', 12, 1),
(18, 'Silvia Aguiar', 13, 1),
(19, 'Thiago Barros', 14, 2),
(20, 'Ursula Fontes', 15, 2),
(21, 'Valdir Meireles', 16, 2),
(22, 'Wagner Goulart', 10, 3),
(23, 'Xenia Dantas', 11, 3),
(24, 'Yuri Siqueira', 12, 3),
(25, 'Zeca Amador', 13, 4),
(26, 'Aline Cordeiro', 14, 4),
(27, 'Breno Antunes', 15, 4),
(28, 'Camila Resende', 16, 5),
(29, 'Danilo Silveira', 10, 5),
(30, 'Elisa Paim', 11, 5);

-- 4. Inserindo Eleitores 
INSERT INTO eleitor (id_eleitor, nome, titulo, zona, sessao) VALUES 
(1, 'Ana Silva', '419283746501', '012', '0451'),
(2, 'Bruno Santos', '592837461029', '054', '0192'),
(3, 'Carlos Oliveira', '837465019283', '103', '0834'),
(4, 'Daniela Souza', '102938475610', '088', '0023'),
(5, 'Eduardo Costa', '564738291039', '201', '0567'),
(6, 'Fernanda Pereira', '918273645012', '310', '0890'),
(7, 'Gabriel Alves', '746583920184', '005', '0112'),
(8, 'Helena Ribeiro', '293847561029', '124', '0345'),
(9, 'Igor Carvalho', '847561029384', '076', '0678'),
(10, 'Julia Lopes', '102938475621', '019', '0901'),
(11, 'Mariana Costa', '321654987012', '045', '0123'),
(12, 'Pedro Almeida', '654987321098', '089', '0456'),
(13, 'Lucas Rodrigues', '987321654032', '112', '0789'),
(14, 'Amanda Ferreira', '147258369014', '034', '0258'),
(15, 'Rafael Gomes', '258369147025', '067', '0369'),
(16, 'Beatriz Martins', '369147258036', '090', '0147'),
(17, 'Thiago Rocha', '753951852075', '120', '0852'),
(18, 'Carolina Mendes', '951753852095', '015', '0963'),
(19, 'Gustavo Lima', '852963741085', '078', '0741'),
(20, 'Juliana Castro', '159357258015', '056', '0159');

-- 5. Inserindo Eleições (Ex: 1º Turno de 2026 e 2024)
INSERT INTO eleicao (anomes, eleicao_nro, ano_eleicao) VALUES 
('202610', 1, 2026),
('202410', 1, 2024);

-- 6. Inserindo Urnas
INSERT INTO urna (id_urna, data_comparecimento) VALUES 
(1, '2026-10-04'),
(2, '2026-10-04'),
(3, '2024-10-06');

-- 7. Relacionando Urnas com as Eleições (Tabela Associativa: urna_eleicao)
-- A urna 1 e 2 foram usadas na eleição de 2026, a urna 3 na de 2024
INSERT INTO urna_eleicao (id_urna, anomes) VALUES 
(1, '202610'),
(2, '202610'),
(3, '202410');

-- 8. Relacionando Eleições com Cargos (Tabela Associativa: eleicao_cargo)
-- Na eleição de 2026, votou-se para todos os 5 cargos cadastrados
INSERT INTO eleicao_cargo (anomes, id_cargo) VALUES 
('202610', 1), -- Presidente
('202610', 2), -- Governador
('202610', 3), -- Senador
('202610', 4), -- Dep. Federal
('202610', 5); -- Dep. Estadual

-- 9. Direcionando Candidatos para as Urnas (Tabela Associativa: urna_candidato)
-- Simulando quais candidatos estavam disponíveis na Urna 1 (Ex: candidatos a Presidente)
INSERT INTO urna_candidato (id_urna, id_candidato) VALUES 
(1, 1),
(1, 2),
(1, 3),
(2, 1),
(2, 2);

ALTER TABLE voto ADD COLUMN id_candidato INT NULL;
ALTER TABLE voto ADD COLUMN tipo_voto VARCHAR(10) DEFAULT 'VALIDO';
ALTER TABLE voto ADD CONSTRAINT fk_voto_candidato FOREIGN KEY (id_candidato) REFERENCES candidato(id_candidato);

-- Adicionar coluna de status para rastrear se a urna está aberta ou encerrada
ALTER TABLE urna_eleicao ADD COLUMN status VARCHAR(20) DEFAULT 'ABERTA' CHECK (status IN ('ABERTA', 'ENCERRADA'));


ALTER TABLE voto ADD CONSTRAINT fk_voto_candidato FOREIGN KEY (id_candidato) REFERENCES candidato(id_candidato);    
ALTER TABLE candidato ALTER COLUMN numero_urna TYPE VARCHAR(10);

-- 1. Criar índice único para garantir integridade e performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_candidato_numero_urna ON candidato(numero_urna);

-- Limpa todos os números de urna para garantir que não haja conflitos
UPDATE candidato SET numero_urna = NULL;

-- 2. Atualiza usando um cálculo que garante unicidade absoluta baseada no ID único
-- Combinamos o id_partido + id_cargo + id_candidato para garantir que NUNCA haja repetição
UPDATE candidato c
SET numero_urna = sub.novo_id
FROM (
    SELECT 
        id_candidato,
        (id_partido * 100000 + id_cargo * 1000 + id_candidato)::TEXT AS novo_id
    FROM candidato
) AS sub
WHERE c.id_candidato = sub.id_candidato;

-- 3. Criar a função que define a regra de negócio do número
CREATE OR REPLACE FUNCTION gerar_numero_urna()
RETURNS TRIGGER AS $$
DECLARE
    contador INT;
BEGIN
    -- Conta quantos candidatos existem no mesmo partido e mesmo cargo
    SELECT COUNT(*) INTO contador
    FROM candidato 
    WHERE id_partido = NEW.id_partido AND id_cargo = NEW.id_cargo;

    -- Aplica as regras de convenção
    IF NEW.id_cargo IN (1, 2) THEN
        -- Presidente/Governador: Apenas o número do partido
        NEW.numero_urna := NEW.id_partido::TEXT;
        
    ELSIF NEW.id_cargo = 3 THEN
        -- Senador: Partido + 1 dígito (Ex: 130)
        NEW.numero_urna := (NEW.id_partido * 10 + contador)::TEXT;
        
    ELSIF NEW.id_cargo = 4 THEN
        -- Dep. Federal: Partido + 2 dígitos (Ex: 1300)
        NEW.numero_urna := (NEW.id_partido * 100 + contador)::TEXT;
        
    ELSIF NEW.id_cargo = 5 THEN
        -- Dep. Estadual: Partido + 3 dígitos (Ex: 13000)
        NEW.numero_urna := (NEW.id_partido * 1000 + contador)::TEXT;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Criar o gatilho (Trigger) que roda automaticamente antes de inserir novo candidato
DROP TRIGGER IF EXISTS trg_gerar_numero_urna ON candidato;

CREATE TRIGGER trg_gerar_numero_urna
BEFORE INSERT ON candidato
FOR EACH ROW
WHEN (NEW.numero_urna IS NULL)
EXECUTE FUNCTION gerar_numero_urna();

-- 5. Povoar a coluna para os candidatos que já existem na tabela
UPDATE candidato c
SET numero_urna = (
    SELECT 
        CASE 
            WHEN sub.id_cargo IN (1, 2) THEN sub.id_partido::TEXT
            WHEN sub.id_cargo = 3 THEN (sub.id_partido * 100 + (ROW_NUMBER() OVER(PARTITION BY sub.id_partido, sub.id_cargo ORDER BY sub.id_candidato) - 1))::TEXT
            WHEN sub.id_cargo = 4 THEN (sub.id_partido * 1000 + (ROW_NUMBER() OVER(PARTITION BY sub.id_partido, sub.id_cargo ORDER BY sub.id_candidato) - 1))::TEXT
            WHEN sub.id_cargo = 5 THEN (sub.id_partido * 10000 + (ROW_NUMBER() OVER(PARTITION BY sub.id_partido, sub.id_cargo ORDER BY sub.id_candidato) - 1))::TEXT
        END
    FROM candidato sub WHERE sub.id_candidato = c.id_candidato
)
WHERE numero_urna IS NULL;


--Testando
SELECT 
    c.id_candidato,
    c.nome_candidato,
    c.numero_urna,
    p.sigla AS partido,
    car.nome_cargo AS cargo
FROM candidato c
JOIN partido p ON c.id_partido = p.num_partido
JOIN cargo car ON c.id_cargo = car.id_cargo
ORDER BY car.id_cargo, p.sigla;

SELECT setval(pg_get_serial_sequence('candidato', 'id_candidato'), COALESCE(MAX(id_candidato), 1)) 
FROM candidato;

-- Não informe o id_candidato, o banco cria o próximo número.
-- Não informe o numero_urna, a Trigger cria o número.
INSERT INTO candidato (nome_candidato, id_partido, id_cargo) 
VALUES ('Candidato de Teste Final', 13, 4);

-- Verifique se ele apareceu com um número de urna único
SELECT * FROM candidato WHERE nome_candidato = 'Candidato de Teste Final';
SELECT * FROM candidato WHERE nome_candidato = 'Candidato de Teste Final';


ALTER TABLE urna_eleicao 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ABERTA' CHECK (status IN ('ABERTA', 'ENCERRADA'));
