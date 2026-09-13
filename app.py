import os
import sys

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_ATUAL not in sys.path:
    sys.path.insert(0, DIRETORIO_ATUAL)

from flask import Flask, render_template, request, redirect, url_for
from database.connection import criar_tabelas
from database.produtos import cadastrar_produto, listar_produtos, obter_metricas_estoque, deletar_produto
from database.vendas import registrar_venda, buscar_vendas_web
from database.caixa import obter_caixa_atual, abrir_caixa, fechar_caixa

app = Flask(__name__)

criar_tabelas()

def formatar_moeda(valor):
    if valor is None:
        valor = 0.0
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

app.jinja_env.filters['moeda'] = formatar_moeda

@app.route("/")
@app.route("/produtos")
def pagina_produtos():
    produtos = listar_produtos()
    metricas = obter_metricas_estoque()
    caixa = obter_caixa_atual()
    return render_template("produtos.html", produtos=produtos, metricas=metricas, caixa=caixa)

@app.route("/produtos/cadastrar", methods=["POST"])
def rota_cadastrar_produto():
    nome = request.form.get("nome", "").strip()
    categoria = request.form.get("categoria", "").strip()
    preco_texto = request.form.get("preco", "").strip().replace(",", ".")
    qtd_texto = request.form.get("quantidade", "").strip()

    try:
        preco = float(preco_texto)
        quantidade = int(qtd_texto)
        cadastrar_produto(nome, categoria, preco, quantidade)
    except ValueError:
        pass

    return redirect("/produtos")

@app.route("/produtos/deletar/<int:id>")
def rota_deletar_produto(id):
    deletar_produto(id)
    return redirect("/produtos")

@app.route("/vendas")
def pagina_vendas():
    produtos = listar_produtos()
    vendas, faturamento = buscar_vendas_web()
    caixa = obter_caixa_atual()
    return render_template("vendas.html", produtos=produtos, vendas=vendas, total_faturamento=faturamento, caixa=caixa)

@app.route("/vendas/registrar", methods=["POST"])
def rota_registrar_venda():
    caixa = obter_caixa_atual()
    if not caixa:
        return redirect("/vendas")

    produto_id_texto = request.form.get("produto_id", "").strip()
    qtd_texto = request.form.get("quantidade", "").strip()
    forma_pagamento = request.form.get("forma_pagamento", "Dinheiro").strip()

    try:
        produto_id = int(produto_id_texto)
        quantidade = int(qtd_texto)
        registrar_venda(produto_id, quantidade, forma_pagamento)
    except ValueError:
        pass

    return redirect("/vendas")

@app.route("/caixa/abrir", methods=["POST"])
def rota_abrir_caixa():
    valor_inicial_texto = request.form.get("valor_inicial", "0").strip().replace(",", ".")
    try:
        valor_inicial = float(valor_inicial_texto)
        abrir_caixa(valor_inicial)
    except ValueError:
        pass
    return redirect("/vendas")

@app.route("/caixa/fechar", methods=["POST"])
def rota_fechar_caixa():
    fechar_caixa()
    return redirect("/vendas")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)