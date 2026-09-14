import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def gerar_recibo_pdf(venda_id, produto_nome, quantidade, preco_unitario, total_venda, forma_pagamento, data_venda, caminho_saida):
    """Gera um arquivo PDF com o recibo simplificado da venda."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    # Cabecalho do Recibo
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, altura - 80, "SISTEMA DE GESTÃO DE ESTOQUE")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(100, altura - 95, "Comprovante de Venda / Recibo Comercial")

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(100, altura - 105, 500, altura - 105)

    # Informacoes Gerais da Transacao
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(100, altura - 130, f"Recibo Nº: #{venda_id}")

    c.setFont("Helvetica", 10)
    c.drawString(100, altura - 150, f"Data/Hora: {data_venda}")
    c.drawString(100, altura - 165, f"Forma de Pagamento: {forma_pagamento}")

    # Tabela de Itens
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(100, altura - 240, 400, 50, fill=True, stroke=True)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(110, altura - 205, "PRODUTO")
    c.drawString(280, altura - 205, "QTD")
    c.drawString(340, altura - 205, "PREÇO UNIT.")
    c.drawString(430, altura - 205, "TOTAL")

    c.setFont("Helvetica", 10)
    c.drawString(110, altura - 225, str(produto_nome)[:25])
    c.drawString(280, altura - 225, f"{quantidade} un.")
    c.drawString(340, altura - 225, f"R$ {preco_unitario:,.2f}".replace(".", ","))
    c.drawString(430, altura - 225, f"R$ {total_venda:,.2f}".replace(".", ","))

    # Totalizador
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#10b981"))
    c.drawString(340, altura - 270, f"TOTAL PAGO: R$ {total_venda:,.2f}".replace(".", ","))

    # Rodape
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(100, altura - 320, "Obrigado pela preferência! Guarde este comprovante para eventuais trocas.")

    c.showPage()
    c.save()