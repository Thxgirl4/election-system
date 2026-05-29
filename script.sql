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
    numero_urna INT,
    foto_url VARCHAR(255),
    CONSTRAINT fk_candidato_partido FOREIGN KEY (id_partido) REFERENCES partido(num_partido),
    CONSTRAINT fk_candidato_cargo FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo)
);

CREATE TABLE IF NOT EXISTS voto (
    hash VARCHAR(255) PRIMARY KEY,
    id_cargo INT NOT NULL,
    id_urna INT NOT NULL,
    id_candidato INT NULL,
    tipo_voto VARCHAR(10) DEFAULT 'VALIDO',
    CONSTRAINT fk_voto_cargo FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo),
    CONSTRAINT fk_voto_urna FOREIGN KEY (id_urna) REFERENCES urna(id_urna),
    CONSTRAINT fk_voto_candidato FOREIGN KEY (id_candidato) REFERENCES candidato(id_candidato)
);

CREATE TABLE IF NOT EXISTS urna_eleicao (
    id_urna INT NOT NULL,
    anomes VARCHAR(6) NOT NULL,
    status VARCHAR(20) DEFAULT 'ABERTA' CHECK (status IN ('ABERTA', 'ENCERRADA')),
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

CREATE TABLE IF NOT EXISTS comparecimento (
    id_eleitor INT NOT NULL,
    anomes VARCHAR(6) NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_eleitor, anomes),
    CONSTRAINT fk_comparecimento_eleitor FOREIGN KEY (id_eleitor) REFERENCES eleitor(id_eleitor),
    CONSTRAINT fk_comparecimento_eleicao FOREIGN KEY (anomes) REFERENCES eleicao(anomes)
);

CREATE TABLE IF NOT EXISTS presidente_sessao (
    id_presidente SERIAL PRIMARY KEY,
    nome_presidente VARCHAR(150) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);