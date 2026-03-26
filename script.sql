
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



-- 1. Inserindo Cargos
INSERT INTO cargo (IDCARGO, NUMDIGITOS, NOMECARGO) VALUES 
(1, 2, 'Presidente'),
(2, 2, 'Governador'),
(3, 3, 'Senador'),
(4, 4, 'Dep. Federal'),
(5, 5, 'Dep. Estadual');

-- 2. Inserindo Partidos
-- Aqui o NUMPARTIDO já estava sendo passado, sendo ele a própria chave primária
INSERT INTO partido (NUMPARTIDO, NOMEPARTIDO, SIGLA) VALUES 
(10, 'Partido do Amanhã', 'PDA'),
(11, 'União Cívica', 'UC'),
(12, 'Movimento Popular', 'MP'),
(13, 'Partido do Futuro', 'PF'),
(14, 'Frente Democrática', 'FD'),
(15, 'Partido da Nova Era', 'PNE'),
(16, 'Ação Cidadã', 'AC');

-- 3. Inserindo Candidatos (com IDCANDIDATO sequencial)
INSERT INTO candidato (IDCANDIDATO, NOMECANDIDATO, NUMPARTIDO, IDCARGO) VALUES 
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

-- 4. Inserindo Eleitores (com IDELEITOR sequencial - Amostra)
INSERT INTO eleitor (IDELEITOR, NOME, TITULO, ZONA, SECAO) VALUES 
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