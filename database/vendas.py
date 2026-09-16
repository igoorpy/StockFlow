import psycopg2
from database.connection import conectar

def finalizar_venda_multi_item(carrinho, forma_pagamento="Dinheiro", cliente_id=None):
    """
    Processa a venda multi-item:
    1. Valida estoques de todos os itens
    2. Insere a venda principal
    3. Insere cada item na tabela itens_venda
    4. Atualiza o estoque dos produtos
    """
    if not carrinho:
        return False, "O carrinho está vazio."

    conexao = conectar()
    if not conexao:
        return False, "Erro ao conectar com o banco de dados PostgreSQL."

    try:
        cursor = conexao.cursor()

        # 1. Validação prévia de estoque e cálculo do total
        total_geral = 0.0
        for item in carrinho:
            cursor.execute("SELECT quantidade, preco FROM produtos WHERE id = %s", (item["produto_id"],))
            prod = cursor.fetchone()
            if not prod:
                conexao.close()
                return False, f"Produto ID #{item['produto_id']} não foi encontrado no banco."
            
            estoque_atual = prod[0]
            if estoque_atual < item["quantidade"]:
                conexao.close()
                return False, f"Estoque insuficiente para '{item['nome']}'. Disponível: {estoque_atual} un."
            
            total_geral += float(item["subtotal"])

        cid = int(cliente_id) if cliente_id and str(cliente_id).isdigit() and int(cliente_id) > 0 else None

        # 2. Criação da Venda Principal
        cursor.execute("""
            INSERT INTO vendas (cliente_id, total_venda, forma_pagamento)
            VALUES (%s, %s, %s) RETURNING id
        """, (cid, total_geral, forma_pagamento))
        
        venda_id = cursor.fetchone()[0]

        # 3. Inserção dos Itens e Baixa de Estoque
        for item in carrinho:
            cursor.execute("""
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                venda_id, 
                item["produto_id"], 
                item["quantidade"], 
                float(item["preco_unitario"]), 
                float(item["subtotal"])
            ))

            cursor.execute("""
                UPDATE produtos SET quantidade = quantidade - %s WHERE id = %s
            """, (item["quantidade"], item["produto_id"]))

        conexao.commit()
        cursor.close()
        conexao.close()
        return True, venda_id

    except Exception as e:
        if conexao:
            conexao.rollback()
            conexao.close()
        print(f"ERRO BANCO DE DADOS (finalizar_venda_multi_item): {e}")
        return False, f"Erro no banco PostgreSQL: {e}"

def buscar_vendas_web():
    """Retorna o histórico de vendas agregadas."""
    try:
        conexao = conectar()
        if not conexao:
            return [], 0.0
        cursor = conexao.cursor()

        query = """
            SELECT v.id, 
                   COALESCE(c.nome, 'Cliente Avulso'), 
                   v.total_venda, 
                   v.forma_pagamento, 
                   TO_CHAR(v.data_venda, 'DD/MM/YYYY HH24:MI'),
                   (SELECT COUNT(*) FROM itens_venda iv WHERE iv.venda_id = v.id) as total_itens,
                   COALESCE(c.cpf_cnpj, 'N/I')
            FROM vendas v
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

def obter_detalhes_venda(venda_id):
    """Busca os itens e o cabeçalho de uma venda específica para geração de recibo."""
    try:
        conexao = conectar()
        if not conexao:
            return None, []
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT v.id, COALESCE(c.nome, 'Cliente Avulso'), COALESCE(c.cpf_cnpj, 'N/I'),
                   v.total_venda, v.forma_pagamento, TO_CHAR(v.data_venda, 'DD/MM/YYYY HH24:MI')
            FROM vendas v
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.id = %s
        """, (venda_id,))
        venda = cursor.fetchone()

        cursor.execute("""
            SELECT p.nome, iv.quantidade, iv.preco_unitario, iv.subtotal
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = %s
        """, (venda_id,))
        itens = cursor.fetchall()

        cursor.close()
        conexao.close()
        return venda, itens
    except Exception as e:
        print(f"Erro ao obter detalhes da venda: {e}")
        return None, []