import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def gerar_recibo_pdf(venda_id, cliente_nome, cliente_cpf, total_venda, forma_pagamento, data_venda, itens, caminho_saida):
    """Gera o recibo individual da venda em formato PDF para o StockFlow."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    # Topo Header
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, altura - 80, largura, 80, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#38bdf8"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, altura - 45, "STOCKFLOW")
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(50, altura - 60, "Gestão de Estoque & Ponto de Venda | Comprovante de Venda")

    # Detalhes da Venda e Cliente
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, altura - 110, f"Recibo Nº #{venda_id}")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(50, altura - 125, f"Data/Hora: {data_venda}")
    c.drawString(50, altura - 138, f"Forma de Pagamento: {forma_pagamento}")

    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(320, altura - 110, f"Cliente: {cliente_nome}")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(320, altura - 125, f"CPF/CNPJ: {cliente_cpf}")

    # Tabela de Itens
    y = altura - 170
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(50, y - 5, 512, 20, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(60, y, "PRODUTO")
    c.drawString(290, y, "QTD")
    c.drawString(360, y, "PREÇO UN.")
    c.drawString(480, y, "SUBTOTAL")

    y -= 20
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#0f172a"))

    for item in itens:
        nome_prod, qtd, preco_unit, subtotal = item
        c.drawString(60, y, str(nome_prod)[:32])
        c.drawString(290, y, f"{qtd} un.")
        c.drawString(360, y, f"R$ {float(preco_unit):,.2f}".replace(".", ","))
        c.drawString(480, y, f"R$ {float(subtotal):,.2f}".replace(".", ","))
        y -= 18

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(50, y, 562, y)

    # Bloco Totalizador
    y -= 30
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.rect(340, y - 10, 222, 35, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 11)
    c.drawString(350, y, "TOTAL PAGO:")
    c.setFillColor(colors.HexColor("#059669"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(450, y, f"R$ {float(total_venda):,.2f}".replace(".", ","))

    # Rodapé
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 40, "StockFlow Systems - Guarde este comprovante para eventuais trocas.")

    c.showPage()
    c.save()

def gerar_relatorio_fechamento_pdf(dados_caixa, usuario_operador, caminho_saida):
    """Gera o PDF do Fechamento de Caixa para o StockFlow."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, altura - 80, largura, 80, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#38bdf8"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, altura - 45, "STOCKFLOW - FECHAMENTO DE CAIXA")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(50, altura - 60, f"Caixa #{dados_caixa['caixa_id']} | Operador: {usuario_operador}")

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica", 9)
    c.drawString(50, altura - 110, f"Abertura: {dados_caixa['data_abertura']}")
    c.drawString(300, altura - 110, f"Fechamento: {dados_caixa['data_fechamento']}")

    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(50, altura - 190, 512, 60, fill=True, stroke=True)

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(65, altura - 145, "FUNDO INICIAL")
    c.drawString(245, altura - 145, "TOTAL VENDAS")
    c.drawString(415, altura - 145, "SALDO FINAL")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(65, altura - 170, f"R$ {dados_caixa['valor_inicial']:,.2f}".replace(".", ","))
    c.drawString(245, altura - 170, f"R$ {dados_caixa['total_vendas']:,.2f}".replace(".", ","))
    
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#059669"))
    c.drawString(415, altura - 170, f"R$ {dados_caixa['valor_final']:,.2f}".replace(".", ","))

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, altura - 215, "Resumo por Forma de Pagamento")

    y = altura - 238
    c.setFont("Helvetica", 9)
    for forma, valor in dados_caixa["detalhes_pagamento"].items():
        c.drawString(65, y, f"• {forma}")
        c.drawString(420, y, f"R$ {valor:,.2f}".replace(".", ","))
        y -= 18

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(50, 90, "________________________________________")
    c.drawString(50, 78, "Assinatura do Operador")
    c.drawString(330, 90, "________________________________________")
    c.drawString(330, 78, "Assinatura da Gerência")

    c.showPage()
    c.save()