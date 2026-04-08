from flask import Flask, request, render_template, make_response
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from flask import jsonify, request
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


engine = create_engine(
    f"postgresql+psycopg2://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}"
)


@app.route("/")
def index():
    return render_template("Seleção.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"csv"}




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

        # troquei o c.numero_urna por p.num_partido
        query = text("""
            SELECT c.nome_candidato, p.sigla 
            FROM candidato c
            JOIN partido p ON c.id_partido = p.num_partido
            WHERE p.num_partido = :numero AND c.id_cargo = :id_cargo
        """)
        
        candidato_db = connection.execute(query, {"numero": numero, "id_cargo": id_cargo}).fetchone()

        if candidato_db:
            return jsonify({
                "nome": candidato_db[0],
                "partido": candidato_db[1]
            }), 200
        else:
            return jsonify({"nome": "VOTO NULO"}), 404


# zera a tabela de votos para cada nova votação
# falta implementar o relatorio de votos zerados
@app.route("/votacao", methods=["GET", "POST"])
def votacao():
    if request.method == "GET":
        id_urna_atual = 1 # mudar logica para pegar o id da urna dinamicamente
        
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM voto WHERE id_urna = :id_urna"), {"id_urna": id_urna_atual})
            connection.commit()
    
        return render_template("votacao.html")

# rota para gerar primeiro relatório
@app.route("/relatorio", methods=["GET"])
def relatorio():
        id_urna_atual = 1 # mudar logica para pegar o id da urna dinamicamente
        with engine.connect() as connection:    
            urna_data = connection.execute(
                text("SELECT id_urna, anomes FROM urna_eleicao WHERE id_urna = :id_urna"),
                {"id_urna": id_urna_atual}
            ).fetchone()

            votos_count = connection.execute(
                text("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN tipo_voto = 'VALIDO' THEN 1 ELSE 0 END), 0) as validos,
                        COALESCE(SUM(CASE WHEN tipo_voto = 'BRANCO' THEN 1 ELSE 0 END), 0) as brancos,
                        COALESCE(SUM(CASE WHEN tipo_voto = 'NULO' THEN 1 ELSE 0 END), 0) as nulos,
                        COALESCE(COUNT(*), 0) as total
                    FROM voto 
                    WHERE id_urna = :id_urna
                """),
                {"id_urna": id_urna_atual}
            ).fetchone()

            print(urna_data)
            print(votos_count)
            
            # Gera PDF com dados da urna
            buffer = BytesIO()
            pdf = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            pdf.setFont("Helvetica-Bold", 18)
            pdf.drawCentredString(width / 2, height - 50, "Relatório da Urna - Zerésima")
            
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, height - 100, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            pdf.drawString(50, height - 120, f"ID da Urna: {id_urna_atual}")
            
            if urna_data:
                y_pos = height - 160
                pdf.drawString(50, y_pos, "Dados da Urna:")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"ID: {urna_data[0]}")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"Ano/Mês: {urna_data[1]}")
                y_pos -= 30
                
                pdf.drawString(50, y_pos, "Contagem de Votos:")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"Votos Válidos: {votos_count[0]}")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"Votos em Branco: {votos_count[1]}")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"Votos Nulos: {votos_count[2]}")
                y_pos -= 20
                pdf.drawString(70, y_pos, f"Total de Votos: {votos_count[3]}")
            else:
                pdf.drawString(50, height - 160, "Urna não encontrada no sistema.")
            
            pdf.drawString(50, height - 320, "Todos os votos desta urna foram zerados.")
            pdf.drawString(50, height - 340, "A urna está pronta para receber novos votos.")
            
            pdf.save()
            buffer.seek(0)
            
            response = make_response(buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'inline; filename=zeresima_urna_{id_urna_atual}.pdf'
            return response

if __name__ == "__main__":
    app.run(debug=True)
