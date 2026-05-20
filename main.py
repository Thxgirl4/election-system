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
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageTemplate, Frame, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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

################################ CLASSES PARA GERAÇÃO DE PDFs ################################

class ZeroeximaPDF:
    """Gera PDF da Zerésima da Urna com layout profissional."""
    
    def __init__(self, numero_urna, secao, zona, municipio, estado="SP"):
        self.numero_urna = numero_urna
        self.secao = secao
        self.zona = zona
        self.municipio = municipio
        self.estado = estado
        self.data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    def _criar_estilos(self):
        """Define estilos de parágrafo."""
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'CustomTitulo',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitulo',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        centrado_style = ParagraphStyle(
            'CustomCentrado',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4,
            alignment=TA_CENTER
        )
        
        return {
            'titulo': titulo_style,
            'subtitulo': subtitulo_style,
            'normal': normal_style,
            'centrado': centrado_style
        }
    
    def _criar_cabecalho(self, estilos):
        """Cria cabeçalho do documento."""
        elementos = []
        elementos.append(Paragraph("JUSTIÇA ELEITORAL", estilos['subtitulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("ZERÉSIMA DA URNA ELETRÔNICA", estilos['titulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph(f"Data: {self.data_hora}", estilos['centrado']))
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_tabela_informacoes(self, estilos):
        """Cria tabela com informações da urna."""
        dados = [
            [Paragraph("<b>Número da Urna:</b>", estilos['normal']), 
             Paragraph(self.numero_urna, estilos['normal'])],
            [Paragraph("<b>Seção:</b>", estilos['normal']), 
             Paragraph(self.secao, estilos['normal'])],
            [Paragraph("<b>Zona:</b>", estilos['normal']), 
             Paragraph(self.zona, estilos['normal'])],
            [Paragraph("<b>Município:</b>", estilos['normal']), 
             Paragraph(self.municipio, estilos['normal'])],
            [Paragraph("<b>Estado:</b>", estilos['normal']), 
             Paragraph(self.estado, estilos['normal'])],
        ]
        
        tabela = Table(dados, colWidths=[4*cm, 8*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        return tabela
    
    def _criar_tabela_candidatos(self, candidatos, estilos):
        """Cria tabela de candidatos com votos zerados."""
        dados = [
            [Paragraph("<b>Número</b>", estilos['centrado']), 
             Paragraph("<b>Nome</b>", estilos['centrado']),
             Paragraph("<b>Partido</b>", estilos['centrado']),
             Paragraph("<b>Cargo</b>", estilos['centrado']),
             Paragraph("<b>Votos</b>", estilos['centrado'])]
        ]
        
        for cand in (candidatos or []):
            dados.append([
                Paragraph(str(cand.get('numero', '')), estilos['centrado']),
                Paragraph(cand.get('nome', 'N/A'), estilos['normal']),
                Paragraph(cand.get('partido', 'N/A'), estilos['centrado']),
                Paragraph(cand.get('cargo', 'N/A'), estilos['normal']),
                Paragraph("0", estilos['centrado'])
            ])
        
        tabela = Table(dados, colWidths=[1.5*cm, 5*cm, 2.5*cm, 2.5*cm, 1.5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        return tabela
    
    def _criar_rodape(self, estilos):
        """Cria rodapé com assinatura."""
        elementos = []
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(Paragraph(
            "Declaramos que a urna foi zerada antes da votação, com todos os candidatos apresentando zero votos.",
            estilos['normal']
        ))
        elementos.append(Spacer(1, 0.8*cm))
        
        # Tabela de assinatura
        dados_assinatura = [
            [Paragraph("_______________________", estilos['centrado']),
             Paragraph("_______________________", estilos['centrado']),
             Paragraph("_______________________", estilos['centrado'])],
            [Paragraph("<b>Mesário 1</b>", estilos['centrado']),
             Paragraph("<b>Mesário 2</b>", estilos['centrado']),
             Paragraph("<b>Observador</b>", estilos['centrado'])]
        ]
        
        tabela_assinatura = Table(dados_assinatura, colWidths=[4*cm, 4*cm, 4*cm])
        tabela_assinatura.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elementos.append(tabela_assinatura)
        return elementos
    
    def gerar(self, candidatos=None):
        """Gera o PDF em memória."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, 
                                leftMargin=1.5*cm, rightMargin=1.5*cm)
        
        estilos = self._criar_estilos()
        elementos = []
        
        # Cabeçalho
        elementos.extend(self._criar_cabecalho(estilos))
        
        # Informações da urna
        elementos.append(self._criar_tabela_informacoes(estilos))
        elementos.append(Spacer(1, 0.5*cm))
        
        # Tabela de candidatos
        elementos.append(Paragraph("<b>Candidatos - Votos Zerados</b>", estilos['subtitulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(self._criar_tabela_candidatos(candidatos, estilos))
        
        # Rodapé
        elementos.extend(self._criar_rodape(estilos))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer


class BoletimPDF:
    """Gera PDF do Boletim da Urna com resultado dos votos."""
    
    def __init__(self, numero_urna, secao, zona, municipio, estado="SP"):
        self.numero_urna = numero_urna
        self.secao = secao
        self.zona = zona
        self.municipio = municipio
        self.estado = estado
        self.data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    def _criar_estilos(self):
        """Define estilos de parágrafo."""
        styles = getSampleStyleSheet()
        
        titulo_style = ParagraphStyle(
            'CustomTitulo',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitulo_style = ParagraphStyle(
            'CustomSubtitulo',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4,
            alignment=TA_LEFT
        )
        
        centrado_style = ParagraphStyle(
            'CustomCentrado',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=4,
            alignment=TA_CENTER
        )
        
        return {
            'titulo': titulo_style,
            'subtitulo': subtitulo_style,
            'normal': normal_style,
            'centrado': centrado_style
        }
    
    def _criar_cabecalho(self, estilos):
        """Cria cabeçalho do documento."""
        elementos = []
        elementos.append(Paragraph("JUSTIÇA ELEITORAL", estilos['subtitulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph("BOLETIM DE URNA", estilos['titulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(Paragraph(f"Data: {self.data_hora}", estilos['centrado']))
        elementos.append(Spacer(1, 0.5*cm))
        return elementos
    
    def _criar_tabela_informacoes(self, estilos):
        """Cria tabela com informações da urna."""
        dados = [
            [Paragraph("<b>Número da Urna:</b>", estilos['normal']), 
             Paragraph(self.numero_urna, estilos['normal'])],
            [Paragraph("<b>Seção:</b>", estilos['normal']), 
             Paragraph(self.secao, estilos['normal'])],
            [Paragraph("<b>Zona:</b>", estilos['normal']), 
             Paragraph(self.zona, estilos['normal'])],
            [Paragraph("<b>Município:</b>", estilos['normal']), 
             Paragraph(self.municipio, estilos['normal'])],
            [Paragraph("<b>Estado:</b>", estilos['normal']), 
             Paragraph(self.estado, estilos['normal'])],
        ]
        
        tabela = Table(dados, colWidths=[4*cm, 8*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        return tabela
    
    def _criar_tabela_resultado(self, votos_por_candidato, estilos):
        """Cria tabela com resultado dos votos."""
        dados = [
            [Paragraph("<b>Número</b>", estilos['centrado']), 
             Paragraph("<b>Nome</b>", estilos['centrado']),
             Paragraph("<b>Partido</b>", estilos['centrado']),
             Paragraph("<b>Cargo</b>", estilos['centrado']),
             Paragraph("<b>Votos</b>", estilos['centrado'])]
        ]
        
        for cand in (votos_por_candidato or []):
            dados.append([
                Paragraph(str(cand.get('numero', '')), estilos['centrado']),
                Paragraph(cand.get('nome', 'N/A'), estilos['normal']),
                Paragraph(cand.get('partido', 'N/A'), estilos['centrado']),
                Paragraph(cand.get('cargo', 'N/A'), estilos['normal']),
                Paragraph(str(cand.get('votos', 0)), estilos['centrado'])
            ])
        
        # Linha de totais
        total_votos = sum(int(cand.get('votos', 0)) for cand in (votos_por_candidato or []))
        dados.append([
            Paragraph("", estilos['centrado']),
            Paragraph("", estilos['normal']),
            Paragraph("", estilos['centrado']),
            Paragraph("<b>TOTAL:</b>", estilos['centrado']),
            Paragraph(f"<b>{total_votos}</b>", estilos['centrado'])
        ])
        
        tabela = Table(dados, colWidths=[1.5*cm, 5*cm, 2.5*cm, 2.5*cm, 1.5*cm])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#CCCCCC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ]))
        return tabela
    
    def _criar_rodape(self, estilos):
        """Cria rodapé com assinatura."""
        elementos = []
        elementos.append(Spacer(1, 0.5*cm))
        elementos.append(Paragraph(
            "Certificamos que os votos contabilizados acima correspondem aos registros da urna eletrônica.",
            estilos['normal']
        ))
        elementos.append(Spacer(1, 0.8*cm))
        
        # Tabela de assinatura
        dados_assinatura = [
            [Paragraph("_______________________", estilos['centrado']),
             Paragraph("_______________________", estilos['centrado']),
             Paragraph("_______________________", estilos['centrado'])],
            [Paragraph("<b>Mesário 1</b>", estilos['centrado']),
             Paragraph("<b>Mesário 2</b>", estilos['centrado']),
             Paragraph("<b>Observador</b>", estilos['centrado'])]
        ]
        
        tabela_assinatura = Table(dados_assinatura, colWidths=[4*cm, 4*cm, 4*cm])
        tabela_assinatura.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elementos.append(tabela_assinatura)
        return elementos
    
    def gerar(self, votos_por_candidato=None):
        """Gera o PDF em memória."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                                leftMargin=1.5*cm, rightMargin=1.5*cm)
        
        estilos = self._criar_estilos()
        elementos = []
        
        # Cabeçalho
        elementos.extend(self._criar_cabecalho(estilos))
        
        # Informações da urna
        elementos.append(self._criar_tabela_informacoes(estilos))
        elementos.append(Spacer(1, 0.5*cm))
        
        # Tabela de resultado
        elementos.append(Paragraph("<b>Resultado dos Votos</b>", estilos['subtitulo']))
        elementos.append(Spacer(1, 0.3*cm))
        elementos.append(self._criar_tabela_resultado(votos_por_candidato, estilos))
        
        # Rodapé
        elementos.extend(self._criar_rodape(estilos))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer

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
                    text("SELECT id_candidato FROM candidato WHERE numero_urna = :num AND id_cargo = :id_cargo"),
                    {"num": int(numero_digitado), "id_cargo": id_cargo}
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

@app.route("/cargos_eleicao", methods=["GET"])
def cargos_eleicao():
    """
    Retorna lista de cargos ATIVOS para uma eleição.
    Usado pelo template votacao.html para saber quais votos permitir.
    """
    anomes = request.args.get("anomes", ELEICAO_ATUAL)
    
    try:
        with engine.connect() as connection:
            # Buscar cargos ativos nesta eleição
            query = text("""
                SELECT c.id_cargo, c.nome_cargo, c.num_digitos
                FROM cargo c
                INNER JOIN eleicao_cargo ec ON c.id_cargo = ec.id_cargo
                WHERE ec.anomes = :anomes
                ORDER BY c.id_cargo ASC
            """)
            
            cargos_db = connection.execute(query, {"anomes": anomes}).fetchall()
            
            # Transformar resultado em lista de dicts
            cargos = []
            for cargo in cargos_db:
                cargos.append({
                    "id": cargo[0],
                    "titulo": cargo[1],
                    "digitos": cargo[2]
                })
            
            return jsonify({"cargos": cargos}), 200
    
    except Exception as e:
        print(f"Erro ao buscar cargos: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route("/zeroesima", methods=["GET"])
def zeroesima():
    """Gera e retorna a Zerésima da Urna em PDF."""
    try:
        id_urna = request.args.get("id_urna", 1, type=int)
        
        with engine.connect() as connection:
            # Buscar dados da urna (a tabela urna_eleicao tem apenas id_urna e anomes)
            urna_query = text("SELECT id_urna FROM urna_eleicao WHERE id_urna = :id_urna LIMIT 1")
            urna_data = connection.execute(urna_query, {"id_urna": id_urna}).fetchone()
            
            if not urna_data:
                return jsonify({"erro": "Urna não encontrada"}), 404
            
            # Usando valores padrão para os dados da urna (podem ser customizados conforme necessário)
            numero_urna = str(id_urna)
            secao = "0001"  # Seção padrão
            zona = "001"    # Zona padrão
            municipio = "São Paulo"  # Município padrão
            estado = "SP"   # Estado padrão
            
            # Buscar candidatos
            candidatos_query = text("""
                SELECT c.id_candidato, c.nome_candidato, p.sigla, ca.nome_cargo
                FROM candidato c
                JOIN partido p ON c.id_partido = p.num_partido
                JOIN cargo ca ON c.id_cargo = ca.id_cargo
                ORDER BY ca.nome_cargo, c.id_candidato
            """)
            candidatos_result = connection.execute(candidatos_query).fetchall()
            
            candidatos = []
            for cand in candidatos_result:
                candidatos.append({
                    "numero": str(cand[0]).zfill(4),  # Usa ID do candidato como número, preenchido com zeros
                    "nome": cand[1] or "Sem nome",
                    "partido": cand[2] or "S/P",
                    "cargo": cand[3] or "Sem cargo"
                })
        
        # Gerar PDF
        pdf_gen = ZeroeximaPDF(numero_urna, secao, zona, municipio, estado)
        pdf_buffer = pdf_gen.gerar(candidatos=candidatos)
        
        # Retornar PDF
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=zeroesima_urna_{numero_urna}.pdf'
        return response
        
    except Exception as e:
        print(f"Erro ao gerar Zerésima: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao gerar PDF: {str(e)}"}), 500

@app.route("/boletim", methods=["GET"])
def boletim():
    """Gera e retorna o Boletim da Urna em PDF."""
    try:
        id_urna = request.args.get("id_urna", 1, type=int)
        
        with engine.connect() as connection:
            # Buscar dados da urna
            urna_query = text("SELECT id_urna FROM urna_eleicao WHERE id_urna = :id_urna LIMIT 1")
            urna_data = connection.execute(urna_query, {"id_urna": id_urna}).fetchone()
            
            if not urna_data:
                return jsonify({"erro": "Urna não encontrada"}), 404
            
            # Usando valores padrão para os dados da urna
            numero_urna = str(id_urna)
            secao = "0001"  # Seção padrão
            zona = "001"    # Zona padrão
            municipio = "São Paulo"  # Município padrão
            estado = "SP"   # Estado padrão
            
            # Buscar votos por candidato
            votos_query = text("""
                SELECT c.id_candidato, c.nome_candidato, p.sigla, ca.nome_cargo, COUNT(*) as votos
                FROM voto v
                LEFT JOIN candidato c ON v.id_candidato = c.id_candidato
                LEFT JOIN partido p ON c.id_partido = p.num_partido
                LEFT JOIN cargo ca ON v.id_cargo = ca.id_cargo
                WHERE v.id_urna = :id_urna AND v.tipo_voto = 'VALIDO'
                GROUP BY c.id_candidato, c.nome_candidato, p.sigla, ca.nome_cargo
                ORDER BY ca.nome_cargo, c.id_candidato
            """)
            votos_result = connection.execute(votos_query, {"id_urna": id_urna}).fetchall()
            
            votos_por_candidato = []
            for voto in votos_result:
                votos_por_candidato.append({
                    "numero": str(voto[0]).zfill(4) if voto[0] else "BRANCO",  # Usa ID como número
                    "nome": voto[1] or "Voto em Branco",
                    "partido": voto[2] or "N/A",
                    "cargo": voto[3] or "N/A",
                    "votos": voto[4]
                })
        
        # Gerar PDF
        pdf_gen = BoletimPDF(numero_urna, secao, zona, municipio, estado)
        pdf_buffer = pdf_gen.gerar(votos_por_candidato=votos_por_candidato)
        
        # Retornar PDF
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename=boletim_urna_{numero_urna}.pdf'
        return response
        
    except Exception as e:
        print(f"Erro ao gerar Boletim: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": f"Erro ao gerar PDF: {str(e)}"}), 500



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