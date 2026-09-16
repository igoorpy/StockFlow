import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def gerar_recibo_pdf(venda_id, cliente_nome, cliente_cpf, total_venda, forma_pagamento, data_venda, itens, caminho_saida):
    """Gera PDF de recibo multi-item."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, altura - 60, "SISTEMA DE GESTÃO DE ESTOQUE")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(80, altura - 75, "Comprovante de Venda / Recibo Comercial")

    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(80, altura - 85, 520, altura - 85)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(80, altura - 105, f"Recibo Nº: #{venda_id}")

    c.setFont("Helvetica", 10)
    c.drawString(80, altura - 120, f"Data/Hora: {data_venda}")
    c.drawString(80, altura - 135, f"Forma de Pagamento: {forma_pagamento}")
    c.drawString(300, altura - 120, f"Cliente: {cliente_nome}")
    c.drawString(300, altura - 135, f"CPF/CNPJ: {cliente_cpf}")

    # Cabecalho da Tabela
    y = altura - 175
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.rect(80, y - 5, 440, 20, fill=True, stroke=True)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(90, y, "PRODUTO")
    c.drawString(280, y, "QTD")
    c.drawString(350, y, "PREÇO UN.")
    c.drawString(450, y, "SUBTOTAL")

    y -= 20
    c.setFont("Helvetica", 9)
    for item in itens:
        nome_prod, qtd, preco_unit, subtotal = item
        c.drawString(90, y, str(nome_prod)[:28])
        c.drawString(280, y, f"{qtd} un.")
        c.drawString(350, y, f"R$ {float(preco_unit):,.2f}".replace(".", ","))
        c.drawString(450, y, f"R$ {float(subtotal):,.2f}".replace(".", ","))
        y -= 18

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(80, y, 520, y)

    # Totalizador
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#059669"))
    c.drawString(350, y - 25, f"TOTAL: R$ {float(total_venda):,.2f}".replace(".", ","))

    # Rodapé
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(80, 60, "Obrigado pela preferência! Guarde este comprovante para eventuais trocas.")

    c.showPage()
    c.save()

def gerar_relatorio_fechamento_pdf(dados_caixa, usuario_operador, caminho_saida):
    """Gera o PDF do Fechamento de Caixa."""
    c = canvas.Canvas(caminho_saida, pagesize=letter)
    largura, altura = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(80, altura - 60, "RELATÓRIO DE FECHAMENTO DE CAIXA")
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(80, altura - 75, f"Caixa Nº #{dados_caixa['caixa_id']} | Operador: {usuario_operador}")

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(80, altura - 85, 520, altura - 85)

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(80, altura - 110, f"Abertura: {dados_caixa['data_abertura']}")
    c.drawString(300, altura - 110, f"Fechamento: {dados_caixa['data_fechamento']}")

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

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(80, altura - 220, "Detalhamento por Forma de Pagamento")

    y = altura - 250
    for forma, valor in dados_caixa["detalhes_pagamento"].items():
        c.drawString(100, y, f"• {forma}")
        c.drawString(380, y, f"R$ {valor:,.2f}".replace(".", ","))
        y -= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(80, y - 30, f"Total de Transações Realizadas: {dados_caixa['qtd_vendas']} vendas")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(80, 100, "________________________________________")
    c.drawString(80, 85, "Assinatura do Operador de Caixa")
    c.drawString(320, 100, "________________________________________")
    c.drawString(320, 85, "Assinatura da Gerência / Conferencia")

    c.showPage()
    c.save()