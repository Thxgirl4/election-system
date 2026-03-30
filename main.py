from flask import Flask, request, render_template
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from flask import jsonify, request

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


engine = create_engine(
    f"postgresql+psycopg2://{os.getenv("UserBd")}:{os.getenv("PasswordBd")}@{os.getenv("HostBd")}/{os.getenv("nomeBd")}"
)


@app.route("/")
def index():
    return render_template("Seleção.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"csv"}


""" @app.route('/eleitor', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded', 400
        
        file = request.files['file']
        if file.filename == ' ':
            return 'No file selected', 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.upload(file_path)

            file.save(file_path)
"""


@app.route("/eleitor", methods=["GET", "POST"])
def eleitor():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'File uploaded successfully', 200
    
            file.save(os.path.join("election-system", filename))
            return "File uploaded successfully", 200

    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM eleitor"))
        eleitores = result.fetchall()
    return render_template("eleitores.html", eleitores=eleitores)


@app.route("/candidato", methods=["GET", "POST"])
def candidato():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file uploaded", 400

        file = request.files["file"]
        if file.filename == "":
            return "No file selected", 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'File uploaded successfully', 200
    
            file.save(os.path.join("/tmp", filename))
            return "File uploaded successfully", 200

    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT candidato.id_candidato, candidato.nome_candidato, candidato.id_partido, candidato.id_cargo, cargo.nome_cargo, partido.nome_partido FROM candidato JOIN cargo ON candidato.id_cargo = cargo.id_cargo JOIN partido ON candidato.id_partido = partido.num_partido"
            )
        )
        candidatos = result.fetchall()
        print(candidatos)
    return render_template("candidatos.html", candidatos=candidatos)

@app.route("/votar", methods=["POST"])
def votar():
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    titulo_eleitor = data.get("eleitor")
    votos = data.get("votos") 

    with engine.begin() as connection:
        
        check_eleitor = connection.execute(
            text("SELECT id_eleitor FROM eleitor WHERE titulo = :titulo"),
            {"titulo": titulo_eleitor}
        ).fetchone()

        if not check_eleitor:
            return jsonify({"erro": "Eleitor não encontrado no sistema."}), 404

        id_urna_atual = 1

        for nome_cargo, numero_digitado in votos.items():
            
            cargo_db = connection.execute(
                text("SELECT id_cargo FROM cargo WHERE nome_cargo = :nome_cargo"),
                {"nome_cargo": nome_cargo}
            ).fetchone()

            if not cargo_db:
                continue
            
            id_cargo = cargo_db[0]
            id_candidato = None
            tipo_voto = "VALIDO"

            if numero_digitado == "BRANCO":
                tipo_voto = "BRANCO"
            else:
                candidato_db = connection.execute(
                    text("SELECT id_candidato FROM candidato WHERE numero_urna = :num AND id_cargo = :id_cargo"),
                    {"num": numero_digitado, "id_cargo": id_cargo}
                ).fetchone()

                if candidato_db:
                    id_candidato = candidato_db[0]
                else:
                    tipo_voto = "NULO"

            hash_voto = uuid.uuid4().hex 
            connection.execute(
                text("""
                    INSERT INTO voto (hash, id_cargo, id_urna, id_candidato, tipo_voto)
                    VALUES (:hash, :id_cargo, :id_urna, :id_candidato, :tipo_voto)
                """),
                {
                    "hash": hash_voto,
                    "id_cargo": id_cargo,
                    "id_urna": id_urna_atual,
                    "id_candidato": id_candidato,
                    "tipo_voto": tipo_voto
                }
            )

    return jsonify({"mensagem": "Votos computados com sucesso!"}), 201

@app.route("/buscar_candidato", methods=["GET"])
def buscar_candidato():
    numero = request.args.get("numero")
    nome_cargo = request.args.get("cargo")

    if not numero or not nome_cargo:
        return jsonify({"erro": "Parâmetros inválidos"}), 400

    with engine.connect() as connection:
        cargo_db = connection.execute(
            text("SELECT id_cargo FROM cargo WHERE nome_cargo = :nome_cargo"),
            {"nome_cargo": nome_cargo}
        ).fetchone()

        if not cargo_db:
            return jsonify({"erro": "Cargo não encontrado"}), 404
        
        id_cargo = cargo_db[0]

        query = text("""
            SELECT c.nome_candidato, p.sigla 
            FROM candidato c
            JOIN partido p ON c.id_partido = p.num_partido
            WHERE c.numero_urna = :numero AND c.id_cargo = :id_cargo
        """)
        
        candidato_db = connection.execute(query, {"numero": numero, "id_cargo": id_cargo}).fetchone()

        if candidato_db:
            return jsonify({
                "nome": candidato_db[0],
                "partido": candidato_db[1]
            }), 200
        else:
            return jsonify({"nome": "VOTO NULO"}), 404


@app.route("/votacao", methods=["GET"])
def votacao():
    return render_template("votacao.html")


if __name__ == "__main__":
    app.run(debug=True)
