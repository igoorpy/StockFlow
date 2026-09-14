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

def gerar_relatorio_fechamento_pdf(dados_caixa, usuario_operador, caminho_saida):
    """Gera o PDF consolidado do Fechamento de Caixa."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    # Cabecalho do Relatorio
    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, altura - 60, "RELATÓRIO DE FECHAMENTO DE CAIXA")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(80, altura - 75, f"Caixa Nº #{dados_caixa['caixa_id']} | Operador: {usuario_operador}")

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(80, altura - 85, 520, altura - 85)

    # Informacoes de Turno
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(80, altura - 110, f"Abertura: {dados_caixa['data_abertura']}")
    c.drawString(300, altura - 110, f"Fechamento: {dados_caixa['data_fechamento']}")

    # Quadro de Saldos
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.rect(80, altura - 190, 440, 65, fill=True, stroke=True)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(90, altura - 145, "FUNDO INICIAL (TROCO)")
    c.drawString(250, altura - 145, "TOTAL VENDAS")
    c.drawString(390, altura - 145, "SALDO FINAL EM CAIXA")

    c.setFont("Helvetica", 11)
    c.drawString(90, altura - 170, f"R$ {dados_caixa['valor_inicial']:,.2f}".replace(".", ","))
    c.drawString(250, altura - 170, f"R$ {dados_caixa['total_vendas']:,.2f}".replace(".", ","))
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#059669"))
    c.drawString(390, altura - 170, f"R$ {dados_caixa['valor_final']:,.2f}".replace(".", ","))

    # Tabela de Formas de Pagamento
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, altura - 220, "Detalhamento por Forma de Pagamento")

    y = altura - 250
    detalhes = dados_caixa["detalhes_pagamento"]

    c.setFont("Helvetica", 10)
    for forma, valor in detalhes.items():
        c.drawString(100, y, f"• {forma}")
        c.drawString(380, y, f"R$ {valor:,.2f}".replace(".", ","))
        y -= 20

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(80, y - 10, 520, y - 10)

    # Resumo Final
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(80, y - 30, f"Total de Transações Realizadas: {dados_caixa['qtd_vendas']} vendas")

    # Assinaturas
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(80, 100, "________________________________________")
    c.drawString(80, 85, "Assinatura do Operador de Caixa")

    c.drawString(320, 100, "________________________________________")
    c.drawString(320, 85, "Assinatura da Gerência / Conferencia")

    c.showPage()
    c.save()