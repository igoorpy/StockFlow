import os
import sys
from functools import wraps

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_ATUAL not in sys.path:
    sys.path.insert(0, DIRETORIO_ATUAL)

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from database.connection import criar_tabelas
from database.produtos import (
    cadastrar_produto, listar_produtos, obter_metricas_estoque, 
    deletar_produto, obter_produto_por_id, atualizar_produto
)
from database.vendas import registrar_venda, buscar_vendas_web
from database.clientes import cadastrar_cliente, listar_clientes
from database.caixa import obter_caixa_atual, abrir_caixa, fechar_caixa, obter_resumo_fechamento_caixa
from database.usuarios import autenticar_usuario
from database.auditoria import registrar_log, listar_logs
from utils.recibo import gerar_recibo_pdf, gerar_relatorio_fechamento_pdf

app = Flask(__name__)
app.secret_key = "chave_secreta_para_sessao_estoque"

criar_tabelas()

def formatar_moeda(valor):
    if valor is None:
        valor = 0.0
    return f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

app.jinja_env.filters['moeda'] = formatar_moeda

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
            registrar_log(usuario["nome"], "LOGIN", f"Usuário {usuario['usuario']} realizou login no sistema.")
            return redirect(url_for("pagina_produtos" if usuario["cargo"] == "admin" else "pagina_vendas"))
        else:
            erro = "Usuário ou senha incorretos."

    return render_template("login.html", erro=erro)

@app.route("/logout")
def rota_logout():
    if "nome" in session:
        registrar_log(session["nome"], "LOGOUT", "Usuário encerrou a sessão.")
    session.clear()
    return redirect(url_for("pagina_login"))

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
        if cadastrar_produto(nome, categoria, preco, quantidade):
            registrar_log(session.get("nome"), "CRIAR_PRODUTO", f"Cadastrou o produto '{nome}' (Categoria: {categoria}, Preço: R$ {preco:.2f}, Qtd: {quantidade}).")
    except ValueError:
        pass

    return redirect("/produtos")

@app.route("/produtos/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def rota_editar_produto(id):
    produto = obter_produto_por_id(id)
    if not produto:
        return redirect("/produtos")

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        categoria = request.form.get("categoria", "").strip()
        preco_texto = request.form.get("preco", "").strip().replace(",", ".")
        qtd_texto = request.form.get("quantidade", "").strip()

        try:
            preco = float(preco_texto)
            quantidade = int(qtd_texto)
            if atualizar_produto(id, nome, categoria, preco, quantidade):
                registrar_log(
                    session.get("nome"),
                    "EDITAR_PRODUTO",
                    f"Atualizou o produto ID #{id} ({nome}, R$ {preco:.2f}, Qtd: {quantidade})."
                )
        except ValueError:
            pass

        return redirect("/produtos")

    return render_template("editar_produto.html", produto=produto)

@app.route("/produtos/deletar/<int:id>")
@login_required
@admin_required
def rota_deletar_produto(id):
    deletar_produto(id)
    registrar_log(session.get("nome"), "EXCLUIR_PRODUTO", f"Excluiu o produto ID #{id} do banco de dados.")
    return redirect("/produtos")

# --- ROTAS DE CLIENTES ---
@app.route("/clientes")
@login_required
def pagina_clientes():
    clientes = listar_clientes()
    return render_template("clientes.html", clientes=clientes)

@app.route("/clientes/cadastrar", methods=["POST"])
@login_required
def rota_cadastrar_cliente():
    nome = request.form.get("nome", "").strip()
    cpf_cnpj = request.form.get("cpf_cnpj", "").strip()
    telefone = request.form.get("telefone", "").strip()
    email = request.form.get("email", "").strip()

    if nome:
        if cadastrar_cliente(nome, cpf_cnpj, telefone, email):
            registrar_log(session.get("nome"), "CRIAR_CLIENTE", f"Cadastrou o cliente '{nome}' (CPF/CNPJ: {cpf_cnpj}).")

    return redirect("/clientes")

# --- ROTAS DE VENDAS E CAIXA ---
@app.route("/vendas")
@login_required
def pagina_vendas():
    produtos = listar_produtos()
    clientes = listar_clientes()
    vendas, faturamento = buscar_vendas_web()
    caixa = obter_caixa_atual()
    return render_template("vendas.html", produtos=produtos, clientes=clientes, vendas=vendas, total_faturamento=faturamento, caixa=caixa)

@app.route("/vendas/registrar", methods=["POST"])
@login_required
def rota_registrar_venda():
    caixa = obter_caixa_atual()
    if not caixa:
        return redirect("/vendas")

    produto_id_texto = request.form.get("produto_id", "").strip()
    cliente_id_texto = request.form.get("cliente_id", "").strip()
    qtd_texto = request.form.get("quantidade", "").strip()
    forma_pagamento = request.form.get("forma_pagamento", "Dinheiro").strip()

    try:
        produto_id = int(produto_id_texto)
        quantidade = int(qtd_texto)
        cliente_id = int(cliente_id_texto) if cliente_id_texto else None

        if registrar_venda(produto_id, quantidade, forma_pagamento, cliente_id):
            registrar_log(session.get("nome"), "REGISTRAR_VENDA", f"Registrou venda do produto ID #{produto_id} ({quantidade} un. via {forma_pagamento}).")
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

    _, produto_nome, quantidade, preco_unitario, total_venda, forma_pagamento, data_venda, cliente_nome, cliente_cpf = venda_selecionada

    caminho_pdf = f"/tmp/recibo_venda_{venda_id}.pdf"
    gerar_recibo_pdf(
        venda_id, produto_nome, quantidade, float(preco_unitario), 
        float(total_venda), forma_pagamento, data_venda, 
        cliente_nome, cliente_cpf, caminho_pdf
    )

    return send_file(caminho_pdf, as_attachment=True, download_name=f"recibo_venda_{venda_id}.pdf")

@app.route("/auditoria")
@login_required
@admin_required
def pagina_auditoria():
    logs = listar_logs()
    return render_template("auditoria.html", logs=logs)

@app.route("/caixa/abrir", methods=["POST"])
@login_required
def rota_abrir_caixa():
    valor_inicial_texto = request.form.get("valor_inicial", "0").strip().replace(",", ".")
    try:
        valor_inicial = float(valor_inicial_texto)
        if abrir_caixa(valor_inicial)[0]:
            registrar_log(session.get("nome"), "ABRIR_CAIXA", f"Abriu o caixa com fundo inicial de R$ {valor_inicial:.2f}.")
    except ValueError:
        pass
    return redirect("/vendas")

@app.route("/caixa/fechar", methods=["POST"])
@login_required
def rota_fechar_caixa():
    sucesso, msg, caixa_id = fechar_caixa()
    if sucesso and caixa_id:
        registrar_log(session.get("nome"), "FECHAR_CAIXA", f"Encerrou o caixa #{caixa_id}.")
        resumo = obter_resumo_fechamento_caixa(caixa_id)
        if resumo:
            caminho_pdf = f"/tmp/relatorio_fechamento_caixa_{caixa_id}.pdf"
            gerar_relatorio_fechamento_pdf(resumo, session.get("nome", "Operador"), caminho_pdf)
            return send_file(caminho_pdf, as_attachment=True, download_name=f"relatorio_fechamento_caixa_{caixa_id}.pdf")
    return redirect("/vendas")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)