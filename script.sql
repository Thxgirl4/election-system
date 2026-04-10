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
(4, 'Dalva Rios', 13, 1),
(5, 'Eduardo Viana', 14, 1),
(6, 'Flavia Gusmão', 15, 1),
(7, 'Gilberto Assis', 16, 1),
(8, 'Helena Bastos', 10, 1),
(9, 'Igor Machado', 11, 1),
(10, 'Joana Diniz', 12, 1),
(11, 'Kleber Munhoz', 13, 1),
(12, 'Laura Peixoto', 14, 1),
(13, 'Marcos Valente', 15, 1),
(14, 'Natalia Cruz', 16, 1),
(15, 'Otavio Lemos', 10, 1),
(16, 'Patricia Luz', 11, 1),
(17, 'Renato Farias', 12, 1),
(18, 'Silvia Aguiar', 13, 1),
(19, 'Thiago Barros', 14, 1),
(20, 'Ursula Fontes', 15, 1),
(21, 'Valdir Meireles', 16, 1),
(22, 'Wagner Goulart', 10, 1),
(23, 'Xenia Dantas', 11, 1),
(24, 'Yuri Siqueira', 12, 1),
(25, 'Zeca Amador', 13, 1),
(26, 'Aline Cordeiro', 14, 1),
(27, 'Breno Antunes', 15, 1),
(28, 'Camila Resende', 16, 1),
(29, 'Danilo Silveira', 10, 1),
(30, 'Elisa Paim', 11, 1);

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
(10, 'Julia Lopes', '102938475621', '019', '0901');

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

-- 10. Inserindo Votos (Com hashes fictícios para simular a criptografia)
-- Lembre-se: o voto é sigiloso, por isso ele não se liga ao Eleitor, apenas à Urna e ao Cargo
INSERT INTO voto (hash, id_cargo, id_urna) VALUES 
('a8f5f167f44f4964e6c998dee827110c', 1, 1),
('b9d2e167f44f4964e6c998dee82711ab', 1, 1),
('c7x9f167f44f4964e6c998dee8271189', 2, 1),
('d4f5f167f44f4964e6c998dee82711xx', 1, 2),
('e1f5f167f44f4964e6c998dee82711zz', 3, 2);