import psycopg2
from database.connection import conectar
from database.produtos import obter_produto_por_id

def registrar_venda(produto_id, quantidade, forma_pagamento="Dinheiro", cliente_id=None):
    """Registra uma venda, baixa o estoque do produto e associa o cliente se informado."""
    if quantidade <= 0:
        return False

    produto = obter_produto_por_id(produto_id)
    if not produto:
        return False

    id_prod, nome_prod, cat_prod, preco_unitario, estoque_atual = produto

    if quantidade > estoque_atual:
        return False

    novo_estoque = estoque_atual - quantidade
    total_venda = float(preco_unitario) * quantidade

    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()

        # Atualiza o estoque do produto
        cursor.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (novo_estoque, produto_id))

        # Trata cliente_id opcional
        cid = cliente_id if cliente_id and cliente_id > 0 else None

        # Insere a venda
        cursor.execute("""
            INSERT INTO vendas (produto_id, cliente_id, quantidade, preco_unitario, total_venda, forma_pagamento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (produto_id, cid, quantidade, preco_unitario, total_venda, forma_pagamento))

        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar venda: {e}")
        return False

def buscar_vendas_web():
    """Retorna o histórico de vendas com dados do produto e cliente associado."""
    try:
        conexao = conectar()
        if not conexao:
            return [], 0.0
        cursor = conexao.cursor()

        query = """
            SELECT v.id, p.nome, v.quantidade, v.preco_unitario, v.total_venda, 
                   v.forma_pagamento, TO_CHAR(v.data_venda, 'DD/MM/YYYY HH24:MI'),
                   COALESCE(c.nome, 'Cliente Avulso'), COALESCE(c.cpf_cnpj, 'N/I')
            FROM vendas v
            JOIN produtos p ON v.produto_id = p.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            ORDER BY v.id DESC
        """
        cursor.execute(query)
        vendas = cursor.fetchall()

        cursor.execute("SELECT COALESCE(SUM(total_venda), 0.0) FROM vendas")
        faturamento_total = cursor.fetchone()[0]

        cursor.close()
        conexao.close()
        return vendas, float(faturamento_total)
    except Exception as e:
        print(f"Erro ao buscar vendas web: {e}")
        return [], 0.0