from flask import Flask, request, render_template, jsonify, make_response
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import uuid
from flask_socketio import SocketIO, emit
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import hashlib

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave_secreta_para_sockets')
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ELEICAO_ATUAL = '202610'
ID_URNA_ATUAL = 1

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
    pool_size=10,
    max_overflow=20
)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"csv"}

def gerar_hash_id(voto_id):
    hash_obj = hashlib.sha256(voto_id.encode('utf-8'))
    return hash_obj.hexdigest()[:100]

# ==============================================================================
# CLASSES PARA GERAÇÃO DE PDFs (REPORTLAB)
# ==============================================================================

class ZeroeximaPDF:
    def __init__(self, numero_urna, secao, zona, municipio, estado="SP"):
        self.numero_urna = numero_urna
        self.secao = secao
        self.zona = zona
        self.municipio = municipio
        self.estado = estado
        self.data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    def _criar_estilos(self):
        styles = getSampleStyleSheet()
        return {
            'titulo': ParagraphStyle('Z_Tit', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold'),
            'subtitulo': ParagraphStyle('Z_Sub', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#555555'), spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold'),
            'normal': ParagraphStyle('Z_Norm', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=4, alignment=TA_LEFT),
            'centrado': ParagraphStyle('Z_Cent', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=4, alignment=TA_CENTER)
        }
    
    def gerar(self, candidatos=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=30, rightMargin=30)
        estilos = self._criar_estilos()
        elementos = []
        
        elementos.append(Paragraph("JUSTIÇA ELEITORAL", estilos['subtitulo']))
        elementos.append(Paragraph("ZERÉSIMA DA URNA ELETRÔNICA", estilos['titulo']))
        elementos.append(Paragraph(f"Emissão: {self.data_hora}", estilos['centrado']))
        elementos.append(Spacer(1, 15))
        
        dados_urna = [
            [Paragraph("<b>Município:</b>", estilos['normal']), Paragraph(f"{self.municipio} - {self.estado}", estilos['normal']),
             Paragraph("<b>Zona Eleitoral:</b>", estilos['normal']), Paragraph(self.zona, estilos['normal'])],
            [Paragraph("<b>Seção:</b>",通estilos['normal']), Paragraph(self.secao, estilos['normal']),
             Paragraph("<b>Número da Urna:</b>", estilos['normal']), Paragraph(self.numero_urna, estilos['normal'])]
        ]
        t_urna = Table(dados_urna, colWidths=[2.5*10, 5.5*10, 3*10, 4.5*10])
        t_urna.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F5F5F5')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_urna)
        elementos.append(Spacer(1, 20))
        
        elementos.append(Paragraph("<b>Relação de Candidatos e Contabilidade de Votos</b>", estilos['subtitulo']))
        elementos.append(Spacer(1, 5))
        
        dados_cand = [[
            Paragraph("<b>Cargo</b>", estilos['normal']),
            Paragraph("<b>Nº Urna</b>", estilos['centrado']),
            Paragraph("<b>Nome do Candidato</b>", estilos['normal']),
            Paragraph("<b>Partido</b>", estilos['centrado']),
            Paragraph("<b>Votos</b>", estilos['centrado'])
        ]]
        
        for cand in (candidatos or []):
            dados_cand.append([
                Paragraph(cand.get('cargo', 'N/A'), estilos['normal']),
                Paragraph(cand.get('numero', 'N/A'),通estilos['centrado']),
                Paragraph(cand.get('nome', 'N/A'), estilos['normal']),
                Paragraph(cand.get('partido', 'N/A'), estilos['centrado']),
                Paragraph("0", estilos['centrado'])
            ])
            
        t_cand = Table(dados_cand, colWidths=[3.5*10, 2*10, 6.5*10, 2*10, 1.5*10])
        t_cand.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9F9F9')]),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elementos.append(t_cand)
        elementos.append(Spacer(1, 30))
        
        elementos.append(Paragraph("O conteúdo desta urna foi verificado e devidamente zerado antes da abertura da sessão eleitoral.", estilos['normal']))
        elementos.append(Spacer(1, 40))
        
        d_ass = [
            [Paragraph("___________________________", estilos['centrado']), Paragraph("___________________________", estilos['centrado'])],
            [Paragraph("<b>Presidente de Mesa</b>", estilos['centrado']), Paragraph("<b>Mesário Adjunto</b>", estilos['centrado'])]
        ]
        t_ass = Table(d_ass, colWidths=[8*10, 8*10])
        t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elementos.append(t_ass)
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class BoletimPDF:
    def __init__(self, numero_urna, secao, zona, municipio, estado="SP"):
        self.numero_urna = numero_urna
        self.secao = secao
        self.zona = zona
        self.municipio = municipio
        self.estado = estado
        self.data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        
    def _criar_estilos(self):
        styles = getSampleStyleSheet()
        return {
            'titulo': ParagraphStyle('B_Tit', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#003366'), spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica-Bold'),
            'subtitulo': ParagraphStyle('B_Sub', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#555555'), spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold'),
            'normal': ParagraphStyle('B_Norm', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=4, alignment=TA_LEFT),
            'centrado': ParagraphStyle('B_Cent', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#222222'), spaceAfter=4, alignment=TA_CENTER)
        }
        
    def gerar(self, votos_por_candidato=None):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=20, leftMargin=30, rightMargin=30)
        estilos = self._criar_estilos()
        elementos = []
        
        elementos.append(Paragraph("JUSTIÇA ELEITORAL", estilos['subtitulo']))
        elementos.append(Paragraph("BOLETIM DE URNA (BU)", estilos['titulo']))
        elementos.append(Paragraph(f"Encerramento: {self.data_hora}", estilos['centrado']))
        elementos.append(Spacer(1, 15))
        
        dados_urna = [
            [Paragraph("<b>Município:</b>", estilos['normal']), Paragraph(f"{self.municipio} - {self.estado}", estilos['normal']),
             Paragraph("<b>Zona Eleitoral:</b>",投estilos['normal']), Paragraph(self.zona, estilos['normal'])],
            [Paragraph("<b>Seção:</b>", estilos['normal']), Paragraph(self.secao, estilos['normal']),
             Paragraph("<b>Número da Urna:</b>", estilos['normal']), Paragraph(self.numero_urna, estilos['normal'])]
        ]
        t_urna = Table(dados_urna, colWidths=[2.5*10, 5.5*10, 3*10, 4.5*10])
        t_urna.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F5F5F5')),
            ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#F5F5F5')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elementos.append(t_urna)
        elementos.append(Spacer(1, 20))
        
        elementos.append(Paragraph("<b>Apuração dos Votos Computados</b>", estilos['subtitulo']))
        elementos.append(Spacer(1, 5))
        
        dados_votos = [[
            Paragraph("<b>Cargo</b>", estilos['normal']),
            Paragraph("<b>Nº Urna</b>",通estilos['centrado']),
            Paragraph("<b>Nome do Candidato / Tipo Voto</b>", estilos['normal']),
            Paragraph("<b>Partido</b>", estilos['centrado']),
            Paragraph("<b>Votos obtidos</b>", estilos['centrado'])
        ]]
        
        total_geral = 0
        for cand in (votos_por_candidato or []):
            qtd_votos = int(cand.get('votos', 0))
            total_geral += qtd_votos
            dados_votos.append([
                Paragraph(cand.get('cargo', 'N/A'), estilos['normal']),
                Paragraph(cand.get('numero', 'N/A'), estilos['centrado']),
                Paragraph(cand.get('nome', 'N/A'), estilos['normal']),
                Paragraph(cand.get('partido', 'N/A'),  estilos['centrado']),
                Paragraph(str(qtd_votos),  estilos['centrado'])
            ])
            
        dados_votos.append([
            Paragraph("", estilos['normal']),
            Paragraph("",  estilos['centrado']),
            Paragraph("<b>TOTAL DE VOTOS APURADOS</b>",  estilos['normal']),
            Paragraph("",  estilos['centrado']),
            Paragraph(f"<b>{total_geral}</b>",  estilos['centrado'])
        ])
        
        t_votos = Table(dados_votos, colWidths=[3.5*10, 2*10, 6.5*10, 2*10, 1.5*10])
        t_votos.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EAEAEA')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F9F9F9')]),
            ('PADDING', (0,0), (-1,-1), 5),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elementos.append(t_votos)
        elementos.append(Spacer(1, 35))
        
        d_ass = [
            [Paragraph("___________________________", estilos['centrado']), Paragraph("___________________________", estilos['centrado'])],
            [Paragraph("<b>Presidente da Sessão</b>",  estilos['centrado']), Paragraph("<b>Fiscal de Partido / Membro</b>",  estilos['centrado'])]
        ]
        t_ass = Table(d_ass, colWidths=[8*10, 8*10])
        t_ass.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elementos.append(t_ass)
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer

# ==============================================================================
# ROTAS FLASK
# ==============================================================================

@app.route("/")
def index():
    return render_template("Seleção.html")

@app.route("/eleitor", methods=["GET", "POST"])
def eleitor():
    if request.method == "POST":
        if "file" not in request.files:
            return "Nenhum arquivo enviado", 400
        file = request.files["file"]
        if file.filename == "":
            return "Nenhum arquivo selecionado", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Arquivo de eleitores salvo com sucesso', 200

    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM eleitor ORDER BY nome ASC"))
        eleitores = result.fetchall()
    return render_template("eleitores.html", eleitores=eleitores)

@app.route("/candidato", methods=["GET", "POST"])
def candidato():
    if request.method == "POST":
        if "file" not in request.files:
            return "Nenhum arquivo enviado", 400
        file = request.files["file"]
        if file.filename == "":
            return "Nenhum arquivo selecionado", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Arquivo de candidatos salvo com sucesso', 200

    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT c.id_candidato, c.nome_candidato, c.id_partido, c.id_cargo, ca.nome_cargo, p.nome_partido 
                FROM candidato c
                JOIN cargo ca ON c.id_cargo = ca.id_cargo 
                JOIN partido p ON c.id_partido = p.num_partido
                ORDER BY ca.nome_cargo, c.nome_candidato
            """)
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
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            return jsonify({"erro": "A votação nesta urna já foi encerrada e não aceita mais votos!"}), 403

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
                try:
                    num_filtrado = int(numero_digitado)
                except (ValueError, TypeError):
                    num_filtrado = -1 

                candidato_db = connection.execute(
                    text("SELECT id_candidato FROM candidato WHERE numero_urna = :num AND id_cargo = :id_cargo"),
                    {"num": num_filtrado, "id_cargo": id_cargo}
                ).fetchone()

                if candidato_db:
                    id_candidato = candidato_db[0]
                else:
                    tipo_voto = "NULO"

            voto_dados = uuid.uuid4().hex
            hash_voto = gerar_hash_id(voto_dados)
            
            connection.execute(
                text("""
                    INSERT INTO voto (hash, id_cargo, id_urna, id_candidato, tipo_voto)
                    VALUES (:hash, :id_cargo, :id_urna, :id_candidato, :tipo_voto)
                """),
                {
                    "hash": hash_voto,
                    "id_cargo": id_cargo,
                    "id_urna": ID_URNA_ATUAL,
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
        
        candidato_db = connection.execute(query, {"numero": int(numero) if numero.isdigit() else -1, "id_cargo": id_cargo}).fetchone()

        if candidato_db:
            return jsonify({
                "nome": candidato_db[0],
                "partido": candidato_db[1],
                "foto": candidato_db[2] 
            }), 200
        else:
            return jsonify({"nome": "VOTO NULO"}), 404

@app.route("/votacao", methods=["GET"])
def votacao():
    return render_template("votacao.html")

@app.route("/inicializar_urna", methods=["POST"])
def inicializar_urna():
    """Rota administrativa e segura para limpar dados antigos e preparar a urna."""
    try:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM voto WHERE id_urna = :id_urna"), {"id_urna": ID_URNA_ATUAL})
            connection.execute(text("DELETE FROM comparecimento WHERE anomes = :anomes"), {"anomes": ELEICAO_ATUAL})
            connection.execute(text("UPDATE urna_eleicao SET status = 'ABERTA' WHERE id_urna = :id_urna AND anomes = :anomes"), {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL})
        return jsonify({"mensagem": "Urna reinicializada com sucesso (Zerar Votos)!"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro na inicialização: {str(e)}"}), 500

@app.route("/cargos_eleicao", methods=["GET"])
def cargos_eleicao():
    anomes = request.args.get("anomes", ELEICAO_ATUAL)
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT c.id_cargo, c.nome_cargo, c.num_digitos
                FROM cargo c
                INNER JOIN eleicao_cargo ec ON c.id_cargo = ec.id_cargo
                WHERE ec.anomes = :anomes
                ORDER BY c.id_cargo ASC
            """)
            cargos_db = connection.execute(query, {"anomes": anomes}).fetchall()
            
            cargos = [{"id": cargo[0], "titulo": cargo[1], "digitos": cargo[2]} for cargo in cargos_db]
            return jsonify({"cargos": cargos}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/zeroesima", methods=["GET"])
def zeroesima():
    try:
        with engine.connect() as connection:
            candidatos_query = text("""
                SELECT c.numero_urna, c.nome_candidato, p.sigla, ca.nome_cargo
                FROM candidato c
                JOIN partido p ON c.id_partido = p.num_partido
                JOIN cargo ca ON c.id_cargo = ca.id_cargo
                ORDER BY ca.id_cargo, c.numero_urna
            """)
            candidatos_result = connection.execute(candidatos_query).fetchall()
            
            candidatos = [{
                "numero": str(cand[0]), 
                "nome": cand[1],
                "partido": cand[2],
                "cargo": cand[3]
            } for cand in candidatos_result]
        
        pdf_gen = ZeroeximaPDF(str(ID_URNA_ATUAL), "0051", "102", "Pinheiro Machado", "RS")
        pdf_buffer = pdf_gen.gerar(candidatos=candidatos)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=zeroesima_urna_{ID_URNA_ATUAL}.pdf'
        return response
    except Exception as e:
        return jsonify({"erro": f"Erro ao emitir documento: {str(e)}"}), 500

@app.route("/boletim", methods=["GET"])
def boletim():
    try:
        with engine.connect() as connection:
            votos_query = text("""
                SELECT c.numero_urna, c.nome_candidato, p.sigla, ca.nome_cargo, COUNT(v.hash) as qtd_votos
                FROM voto v
                LEFT JOIN candidato c ON v.id_candidato = c.id_candidato
                LEFT JOIN partido p ON c.id_partido = p.num_partido
                LEFT JOIN cargo ca ON v.id_cargo = ca.id_cargo
                WHERE v.id_urna = :id_urna AND v.tipo_voto = 'VALIDO'
                GROUP BY ca.id_cargo, ca.nome_cargo, c.numero_urna, c.nome_candidato, p.sigla
                
                UNION ALL
                
                SELECT null, 'VOTO EM BRANCO', null, ca.nome_cargo, COUNT(v.hash)
                FROM voto v
                JOIN cargo ca ON v.id_cargo = ca.id_cargo
                WHERE v.id_urna = :id_urna AND v.tipo_voto = 'BRANCO'
                GROUP BY ca.id_cargo, ca.nome_cargo
                
                UNION ALL
                
                SELECT null, 'VOTO NULO', null, ca.nome_cargo, COUNT(v.hash)
                FROM voto v
                JOIN cargo ca ON v.id_cargo = ca.id_cargo
                WHERE v.id_urna = :id_urna AND v.tipo_voto = 'NULO'
                GROUP BY ca.id_cargo, ca.nome_cargo
                
                ORDER BY nome_cargo, numero_urna ASC NULLS LAST
            """)
            votos_result = connection.execute(votos_query, {"id_urna": ID_URNA_ATUAL}).fetchall()
            
            votos_por_candidato = [{
                "numero": str(voto[0]) if voto[0] is not NULL else "-",
                "nome": voto[1],
                "partido": voto[2] if voto[2] else "-",
                "cargo": voto[3],
                "votos": voto[4]
            } for voto in votos_result]
        
        pdf_gen = BoletimPDF(str(ID_URNA_ATUAL), "0051", "102", "Pinheiro Machado", "RS")
        pdf_buffer = pdf_gen.gerar(votos_por_candidato=votos_por_candidato)
        
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=boletim_urna_{ID_URNA_ATUAL}.pdf'
        return response
    except Exception as e:
        return jsonify({"erro": f"Erro ao emitir boletim: {str(e)}"}), 500

@app.route("/mesario")
def mesario():
    return render_template("mesario.html")

# ==============================================================================
# EVENTOS TEMPO REAL - FLASK SOCKETIO
# ==============================================================================

@socketio.on('mesario_libera_urna')
def handle_liberar(data):
    titulo = data.get('titulo')
    
    with engine.begin() as connection:
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            emit('status_mesario', {'status': 'A votação foi encerrada pelo presidente de sessão. Urna indisponível.', 'cor': 'red'})
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
    with engine.connect() as connection:
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            emit('status_mesario', {'status': 'A votação foi encerrada pelo presidente de sessão!', 'cor': 'red'}, broadcast=True)
            return
            
    emit('status_mesario', {'status': 'Votação concluída. Aguardando próximo eleitor.', 'cor': 'blue'}, broadcast=True)

# ==============================================================================
# SESSÃO PRESIDENTE DA MESA
# ==============================================================================

@app.route("/login_presidente", methods=["POST"])
def login_presidente():
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
        
        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "id_presidente": presidente[0],
            "nome_presidente": presidente[1],
            "usuario": presidente[2]
        }), 200

@app.route("/encerrar_sessao", methods=["POST"])
def encerrar_sessao():
    with engine.begin() as connection:
        urna_status = connection.execute(
            text("SELECT status FROM urna_eleicao WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL}
        ).fetchone()
        
        if urna_status and urna_status[0] == 'ENCERRADA':
            return jsonify({"erro": "A urna já foi encerrada anteriormente."}), 400
        
        connection.execute(
            text("UPDATE urna_eleicao SET status = 'ENCERRADA' WHERE id_urna = :id_urna AND anomes = :anomes"),
            {"id_urna": ID_URNA_ATUAL, "anomes": ELEICAO_ATUAL}
        )
    
    socketio.emit('urna_encerrada', {
        'mensagem': 'A votação foi encerrada pelo presidente de sessão!',
        'urna_status': 'ENCERRADA',
        'id_urna': ID_URNA_ATUAL
    })
    
    return jsonify({
        "mensagem": "Votação encerrada com sucesso! A urna foi bloqueada.",
        "urna_status": "ENCERRADA"
    }), 200

if __name__ == "__main__":
    socketio.run(app, debug=True)