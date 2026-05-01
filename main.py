from flask import Flask, request, render_template, jsonify, make_response
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from flask_socketio import SocketIO, emit
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.pagesizes import A4
import hashlib
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta_para_sockets'
socketio = SocketIO(app)

UPLOAD_FOLDER = 'tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ELEICAO_ATUAL = '202610'

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"csv"}

def gerar_hash_id(voto_id):
    hash_obj = hashlib.sha256(voto_id.encode('utf-8'))
    return hash_obj.hexdigest()[:100] 

################################ ROTAS ################################

@app.route("/")
def index():
    return render_template("Seleção.html")

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

    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT candidato.id_candidato, candidato.nome_candidato, candidato.id_partido, candidato.id_cargo, cargo.nome_cargo, partido.nome_partido FROM candidato JOIN cargo ON candidato.id_cargo = cargo.id_cargo JOIN partido ON candidato.id_partido = partido.num_partido"
            )
        )
        candidatos = result.fetchall()
    return render_template("candidatos.html", candidatos=candidatos)

@app.route("/votar", methods=["POST"])
def votar():
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400

    titulo_eleitor = data.get("eleitor")
    votos = data.get("votos") 

    with engine.begin() as connection:
        # Verificar se a urna está encerrada
        id_urna_atual = 1
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            return jsonify({"erro": "A urna foi encerrada e não aceita mais votos!"}), 403
        eleitor_db = connection.execute(
            text("SELECT id_eleitor FROM eleitor WHERE titulo = :titulo"),
            {"titulo": titulo_eleitor}
        ).fetchone()

        if not eleitor_db:
            return jsonify({"erro": "Eleitor não encontrado no sistema."}), 404

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
                    text("SELECT id_candidato FROM candidato WHERE id_partido = :num AND id_cargo = :id_cargo"),
                    {"num": numero_digitado, "id_cargo": id_cargo}
                ).fetchone()

                if candidato_db:
                    id_candidato = candidato_db[0]
                else:
                    tipo_voto = "NULO"

            voto_dados = uuid.uuid4().hex
            hash_voto = gerar_hash_id(voto_dados)
            print(f"Voto para {nome_cargo}: {tipo_voto} (Hash: {hash_voto})")
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
            SELECT c.nome_candidato, p.sigla, c.foto_url 
            FROM candidato c
            JOIN partido p ON c.id_partido = p.num_partido
            WHERE c.numero_urna = :numero AND c.id_cargo = :id_cargo
        """)
        
        candidato_db = connection.execute(query, {"numero": numero, "id_cargo": id_cargo}).fetchone()

        if candidato_db:
            return jsonify({
                "nome": candidato_db[0],
                "partido": candidato_db[1],
                "foto": candidato_db[2] 
            }), 200
        else:
            return jsonify({"nome": "VOTO NULO"}), 404

@app.route("/votacao", methods=["GET", "POST"])
def votacao():
    if request.method == "GET":
        id_urna_atual = 1 
        
        with engine.connect() as connection:
            connection.execute(text("DELETE FROM voto WHERE id_urna = :id_urna"), {"id_urna": id_urna_atual})
            connection.execute(text("DELETE FROM comparecimento WHERE anomes = :anomes"), {"anomes": ELEICAO_ATUAL})
            connection.execute(text("UPDATE urna_eleicao SET status = 'ABERTA' WHERE id_urna = :id_urna AND anomes = :anomes"), {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL})
            connection.commit()
    
    return render_template("votacao.html")

@app.route("/relatorio", methods=["GET"])
def relatorio():
    id_urna_atual = 1 
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

        print(votos_count)
        
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        margin_left = 50
        margin_right = 50
        y_pos = height - 50
        
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, y_pos, "Relatório da Urna - Zerésima")
        
        y_pos -= 40
        
        pdf.setFont("Helvetica", 11)
        pdf.drawString(margin_left, y_pos, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y_pos -= 18
        pdf.drawString(margin_left, y_pos, f"ID da Urna: {id_urna_atual}")
        
        y_pos -= 35
        
        if urna_data:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_left, y_pos, "Dados da Urna:")
            y_pos -= 18
            
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left + 20, y_pos, f"ID: {urna_data[0]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Ano/Mês: {urna_data[1]}")
            
            y_pos -= 30
            
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_left, y_pos, "Contagem de Votos:")
            y_pos -= 18
            
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left + 20, y_pos, f"Votos Válidos: {votos_count[0]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Votos em Branco: {votos_count[1]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Votos Nulos: {votos_count[2]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Total de Votos: {votos_count[3]}")
        else:
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left, y_pos, "Urna não encontrada no sistema.")
        
        y_pos -= 50
        
        pdf.setFont("Helvetica", 11)
        pdf.drawString(margin_left, y_pos, "Todos os votos desta urna foram zerados.")
        y_pos -= 16
        pdf.drawString(margin_left, y_pos, "A urna está pronta para receber novos votos.")
        
        y_pos -= 30
        
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawCentredString(width / 2, y_pos, "Tribunal Regional do TADS")
        
        pdf.save()
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=zeresima_urna_{id_urna_atual}.pdf'
        return response

@app.route("/relatorio_final", methods=["GET"])
def relatorio_final():
    id_urna_atual = 1 
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

        votos_candidatos = connection.execute(text("""
            SELECT v.tipo_voto, u.data_comparecimento, c.nome_candidato, p.nome_partido, p.num_partido, ca.nome_cargo, COUNT(*) AS total_votos
            FROM voto v
            JOIN urna u ON v.id_urna = u.id_urna
            JOIN candidato c ON v.id_candidato = c.id_candidato
            JOIN partido p ON c.id_partido = p.num_partido
            JOIN cargo ca ON c.id_cargo = ca.id_cargo
            WHERE v.id_urna = :id_urna AND v.tipo_voto = 'VALIDO'
            GROUP BY v.tipo_voto, u.data_comparecimento, c.nome_candidato, p.nome_partido, p.num_partido, ca.nome_cargo
        """), {"id_urna": id_urna_atual}).fetchall()   

        print(votos_candidatos)    
        print(urna_data)
        print(votos_count)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        margin_left = 50
        margin_right = 50
        y_pos = height - 50
        
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, y_pos, "Relatório da Urna - Encerramento")
        
        y_pos -= 40
        
        pdf.setFont("Helvetica", 11)
        pdf.drawString(margin_left, y_pos, f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y_pos -= 18
        pdf.drawString(margin_left, y_pos, f"ID da Urna: {id_urna_atual}")
        
        y_pos -= 35
        
        if urna_data:
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_left, y_pos, "Dados da Urna:")
            y_pos -= 18
            
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left + 20, y_pos, f"ID: {urna_data[0]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Ano/Mês: {urna_data[1]}")
            
            y_pos -= 30
            
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_left, y_pos, "Contagem de Votos:")
            y_pos -= 18
            
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left + 20, y_pos, f"Votos Válidos: {votos_count[0]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Votos em Branco: {votos_count[1]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Votos Nulos: {votos_count[2]}")
            y_pos -= 16
            pdf.drawString(margin_left + 20, y_pos, f"Total de Votos: {votos_count[3]}")

            y_pos -= 30

            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(margin_left, y_pos, "Votos por Candidato:")
            y_pos -= 18

            pdf.setFont("Helvetica", 11)
            for voto in votos_candidatos:
                tipo_voto, data_comparecimento, nome_candidato, nome_partido, num_partido, nome_cargo, total_votos = voto
                pdf.drawString(margin_left + 20, y_pos, f"{nome_candidato} ({nome_partido} - {num_partido}) para {nome_cargo}: {total_votos} votos")
                y_pos -= 16
                if y_pos < 100:  
                    pdf.showPage()
                    y_pos = height - 50
        else:
            pdf.setFont("Helvetica", 11)
            pdf.drawString(margin_left, y_pos, "Urna não encontrada no sistema.")
        
        y_pos -= 50
        
        pdf.setFont("Helvetica", 11)
        pdf.drawString(margin_left, y_pos, "Todos os votos desta urna foram contabilizados.")
        y_pos -= 16
        pdf.drawString(margin_left, y_pos, "Esta urna foi encerrada.")
        
        y_pos -= 30
        
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawCentredString(width / 2, y_pos, "Tribunal Regional do TADS")
        
        pdf.save()
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=zeresima_urna_{id_urna_atual}.pdf'
        return response

@app.route("/mesario")
def mesario():
    return render_template("mesario.html")

@socketio.on('mesario_libera_urna')
def handle_liberar(data):
    titulo = data.get('titulo')
    id_urna_atual = 1
    
    with engine.begin() as connection:
        # Verificar se a urna foi encerrada pelo presidente
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            emit('status_mesario', {'status': 'A votação foi encerrada pelo presidente de sessão. Não é possível liberar mais urnas!', 'cor': 'red'})
            return
        
        query = text("""
            SELECT e.id_eleitor, e.nome, 
            (SELECT 1 FROM comparecimento c WHERE c.id_eleitor = e.id_eleitor AND c.anomes = :anomes) as ja_votou
            FROM eleitor e WHERE e.titulo = :titulo
        """)
        
        result = connection.execute(query, {"titulo": titulo, "anomes": ELEICAO_ATUAL}).fetchone()

        if result:
            id_eleitor, nome_eleitor, ja_votou = result
            
            if ja_votou:
                emit('status_mesario', {'status': f'ALERTA: {nome_eleitor} já votou ou está votando!', 'cor': 'red'})
            else:
                connection.execute(
                    text("INSERT INTO comparecimento (id_eleitor, anomes) VALUES (:id_e, :ano)"),
                    {"id_e": id_eleitor, "ano": ELEICAO_ATUAL}
                )
                
                emit('urna_destravada', {'titulo': titulo, 'nome': nome_eleitor}, broadcast=True)
                emit('status_mesario', {'status': f'Urna liberada para: {nome_eleitor}', 'cor': 'green'})
        else:
            emit('status_mesario', {'status': 'Título não encontrado!', 'cor': 'red'})

@socketio.on('urna_bloqueada')
def handle_bloquear():
    id_urna_atual = 1
    
    with engine.connect() as connection:
        # Verificar se a urna foi encerrada pelo presidente
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            emit('status_mesario', {'status': 'A votação foi encerrada pelo presidente de sessão!', 'cor': 'red'}, broadcast=True)
            return
    
    emit('status_mesario', {'status': 'Votação concluída. Aguardando próximo eleitor.', 'cor': 'blue'}, broadcast=True)

@app.route("/login_presidente", methods=["POST"])
def login_presidente():
    """
    Rota de login para o presidente de sessão.
    Recebe usuario e senha e valida as credenciais.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"erro": "Dados inválidos"}), 400
    
    usuario = data.get("usuario")
    senha = data.get("senha")
    
    if not usuario or not senha:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 400
    
    with engine.connect() as connection:
        presidente = connection.execute(
            text("SELECT id_presidente, nome_presidente, usuario FROM presidente_sessao WHERE usuario = :usuario AND senha = :senha"),
            {"usuario": usuario, "senha": senha}
        ).fetchone()
        
        if not presidente:
            return jsonify({"erro": "Usuário ou senha inválidos"}), 401
        
        id_presidente, nome_presidente, usuario_db = presidente
        
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "id_presidente": id_presidente,
            "nome_presidente": nome_presidente,
            "usuario": usuario_db
        }), 200

@app.route("/encerrar_sessao", methods=["POST"])
def encerrar_sessao():
    """
    Rota para o presidente de sessão encerrar a votação.
    Marca a urna como ENCERRADA, bloqueando-a para novos votos.
    """
    id_urna_atual = 1
    
    with engine.begin() as connection:
        # Verificar se a urna já está encerrada
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            return jsonify({"erro": "A urna já foi encerrada anteriormente."}), 400
        
        # Marcar a urna como ENCERRADA
        connection.execute(
            text("""
                UPDATE urna_eleicao 
                SET status = 'ENCERRADA' 
                WHERE id_urna = :id_urna AND anomes = :anomes
            """),
            {"id_urna": id_urna_atual, "anomes": ELEICAO_ATUAL}
        )
    
    # Notificar todos os clientes em tempo real via SocketIO
    socketio.emit('urna_encerrada', {
        'mensagem': 'A votação foi encerrada pelo presidente de sessão!',
        'urna_status': 'ENCERRADA',
        'id_urna': id_urna_atual
    })
    
    return jsonify({
        "mensagem": "Votação encerrada com sucesso! A urna foi bloqueada.",
        "urna_status": "ENCERRADA"
    }), 200

if __name__ == "__main__":
    socketio.run(app, debug=True)