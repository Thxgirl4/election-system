
CREATE TABLE IF NOT EXISTS eleitor (
    IDELEITOR INT PRIMARY KEY,
    NOME VARCHAR(150) NOT NULL,
    TITULO VARCHAR(12) NOT NULL UNIQUE,
    ZONA VARCHAR(4) NOT NULL,
    SECAO VARCHAR(4) NOT NULL 
);

CREATE TABLE IF NOT EXISTS cargo (
    IDCARGO INT PRIMARY KEY,
    NUMDIGITOS INT NOT NULL,
    NOMECARGO VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS partido (
    NUMPARTIDO INT PRIMARY KEY, 
    NOMEPARTIDO VARCHAR(100) NOT NULL,
    SIGLA VARCHAR(10) NOT NULL
);


CREATE TABLE IF NOT EXISTS candidato (
    IDCANDIDATO INT PRIMARY KEY,
    NOMECANDIDATO VARCHAR(150) NOT NULL,
    NUMPARTIDO INT NOT NULL,
    IDCARGO INT NOT NULL,
    CONSTRAINT fk_partido FOREIGN KEY (NUMPARTIDO) REFERENCES partido(NUMPARTIDO),
    CONSTRAINT fk_cargo FOREIGN KEY (IDCARGO) REFERENCES cargo(IDCARGO)
);



-- 1. Inserindo Cargos com a nova estrutura federal e estadual
INSERT INTO cargo (NUMDIGITOS, NOMECARGO) VALUES 
(2, 'Presidente'),
(2, 'Governador'),
(3, 'Senador'),
(4, 'Dep. Federal'),
(5, 'Dep. Estadual');

-- 2. Inserindo Partidos (A partir dos dados de candidatos.csv)
INSERT INTO partido (NUMPARTIDO, NOMEPARTIDO, SIGLA) VALUES 
(10, 'Partido do Amanhã', 'PDA'),
(11, 'União Cívica', 'UC'),
(12, 'Movimento Popular', 'MP'),
(13, 'Partido do Futuro', 'PF'),
(14, 'Frente Democrática', 'FD'),
(15, 'Partido da Nova Era', 'PNE'),
(16, 'Ação Cidadã', 'AC');

-- 3. Inserindo Candidatos 
-- Nota: Como todos os números presentes no seu arquivo candidatos.csv têm 2 dígitos 
-- (ex: 10, 11, 23, etc.), atribuí todos temporariamente a Presidente (IDCARGO = 1).
INSERT INTO candidato (NOMECANDIDATO, NUMPARTIDO, IDCARGO) VALUES 
('Armando Nogueira', 10, 1),
('Bianca Leal', 11, 1),
('Celso Freitas', 12, 1),
('Dalva Rios', 13, 1),
('Eduardo Viana', 14, 1),
('Flavia Gusmão', 15, 1),
('Gilberto Assis', 16, 1),
('Helena Bastos', 10, 1),
('Igor Machado', 11, 1),
('Joana Diniz', 12, 1),
('Kleber Munhoz', 13, 1),
('Laura Peixoto', 14, 1),
('Marcos Valente', 15, 1),
('Natalia Cruz', 16, 1),
('Otavio Lemos', 10, 1),
('Patricia Luz', 11, 1),
('Renato Farias', 12, 1),
('Silvia Aguiar', 13, 1),
('Thiago Barros', 14, 1),
('Ursula Fontes', 15, 1),
('Valdir Meireles', 16, 1),
('Wagner Goulart', 10, 1),
('Xenia Dantas', 11, 1),
('Yuri Siqueira', 12, 1),
('Zeca Amador', 13, 1),
('Aline Cordeiro', 14, 1),
('Breno Antunes', 15, 1),
('Camila Resende', 16, 1),
('Danilo Silveira', 10, 1),
('Elisa Paim', 11, 1);

-- 4. Inserindo Eleitores (Amostra dos 10 primeiros de eleitores.csv)
INSERT INTO eleitor (NOME, TITULO, ZONA, SECAO) VALUES 
('Ana Silva', '419283746501', '012', '0451'),
('Bruno Santos', '592837461029', '054', '0192'),
('Carlos Oliveira', '837465019283', '103', '0834'),
('Daniela Souza', '102938475610', '088', '0023'),
('Eduardo Costa', '564738291039', '201', '0567'),
('Fernanda Pereira', '918273645012', '310', '0890'),
('Gabriel Alves', '746583920184', '005', '0112'),
('Helena Ribeiro', '293847561029', '124', '0345'),
('Igor Carvalho', '847561029384', '076', '0678'),
('Julia Lopes', '102938475621', '019', '0901');