import os
import sys
from functools import wraps

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_ATUAL not in sys.path:
    sys.path.insert(0, DIRETORIO_ATUAL)

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from database.connection import criar_tabelas
from database.produtos import cadastrar_produto, listar_produtos, obter_metricas_estoque, deletar_produto
from database.vendas import registrar_venda, buscar_vendas_web
from database.caixa import obter_caixa_atual, abrir_caixa, fechar_caixa
from database.usuarios import autenticar_usuario
from utils.recibo import gerar_recibo_pdf

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao_estoque"

criar_tabelas()

def formatar_moeda(valor):
    if valor is None:
        valor = 0.0
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

app.jinja_env.filters['moeda'] = formatar_moeda

# --- DECORADORES DE CONTROLE DE ACESSO ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("pagina_login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("cargo") != "admin":
            return redirect(url_for("pagina_vendas"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route("/login", methods=["GET", "POST"])
def pagina_login():
    if "usuario_id" in session:
        return redirect(url_for("pagina_produtos"))

    erro = None
    if request.method == "POST":
        usuario_input = request.form.get("usuario", "").strip()
        senha_input = request.form.get("senha", "").strip()
        
        usuario = autenticar_usuario(usuario_input, senha_input)
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            session["usuario"] = usuario["usuario"]
            session["cargo"] = usuario["cargo"]
            return redirect(url_for("pagina_produtos" if usuario["cargo"] == "admin" else "pagina_vendas"))
        else:
            erro = "Usuário ou senha incorretos."

    return render_template("login.html", erro=erro)

@app.route("/logout")
def rota_logout():
    session.clear()
    return redirect(url_for("pagina_login"))

# --- ROTAS DE PRODUTOS ---
@app.route("/")
@app.route("/produtos")
@login_required
@admin_required
def pagina_produtos():
    termo_busca = request.args.get("busca", "").strip()
    produtos = listar_produtos(termo_busca)
    metricas = obter_metricas_estoque()
    caixa = obter_caixa_atual()
    return render_template("produtos.html", produtos=produtos, metricas=metricas, caixa=caixa, termo_busca=termo_busca)

@app.route("/produtos/cadastrar", methods=["POST"])
@login_required
@admin_required
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
@login_required
@admin_required
def rota_deletar_produto(id):
    deletar_produto(id)
    return redirect("/produtos")

# --- ROTAS DE VENDAS E CAIXA ---
@app.route("/vendas")
@login_required
def pagina_vendas():
    produtos = listar_produtos()
    vendas, faturamento = buscar_vendas_web()
    caixa = obter_caixa_atual()
    return render_template("vendas.html", produtos=produtos, vendas=vendas, total_faturamento=faturamento, caixa=caixa)

@app.route("/vendas/registrar", methods=["POST"])
@login_required
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

@app.route("/vendas/recibo/<int:venda_id>")
@login_required
def rota_baixar_recibo(venda_id):
    vendas, _ = buscar_vendas_web()
    venda_selecionada = next((v for v in vendas if v[0] == venda_id), None)

    if not venda_selecionada:
        return redirect("/vendas")

    _, produto_nome, quantidade, preco_unitario, total_venda, forma_pagamento, data_venda = venda_selecionada

    caminho_pdf = f"/tmp/recibo_venda_{venda_id}.pdf"
    gerar_recibo_pdf(venda_id, produto_nome, quantidade, float(preco_unitario), float(total_venda), forma_pagamento, data_venda, caminho_pdf)

    return send_file(caminho_pdf, as_attachment=True, download_name=f"recibo_venda_{venda_id}.pdf")

@app.route("/caixa/abrir", methods=["POST"])
@login_required
def rota_abrir_caixa():
    valor_inicial_texto = request.form.get("valor_inicial", "0").strip().replace(",", ".")
    try:
        valor_inicial = float(valor_inicial_texto)
        abrir_caixa(valor_inicial)
    except ValueError:
        pass
    return redirect("/vendas")

@app.route("/caixa/fechar", methods=["POST"])
@login_required
def rota_fechar_caixa():
    fechar_caixa()
    return redirect("/vendas")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)