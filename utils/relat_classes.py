################################ CLASSES PARA GERAÇÃO DE PDFs ################################

from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle



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