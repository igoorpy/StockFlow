import psycopg2
from database.connection import conectar

def cadastrar_produto(nome, categoria, preco, quantidade):
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, categoria, preco, quantidade) VALUES (%s, %s, %s, %s)",
            (nome, categoria, preco, quantidade)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return False

def listar_produtos(termo_busca=""):
    try:
        conexao = conectar()
        if not conexao:
            return []
        cursor = conexao.cursor()
        
        if termo_busca:
            query = """
                SELECT id, nome, categoria, preco, quantidade 
                FROM produtos 
                WHERE nome ILIKE %s OR categoria ILIKE %s 
                ORDER BY id ASC
            """
            parametro = f"%{termo_busca}%"
            cursor.execute(query, (parametro, parametro))
        else:
            cursor.execute("SELECT id, nome, categoria, preco, quantidade FROM produtos ORDER BY id ASC")
            
        produtos = cursor.fetchall()
        cursor.close()
        conexao.close()
        return produtos
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        return []

def obter_produto_por_id(produto_id):
    """Busca os dados de um único produto pelo ID."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, categoria, preco, quantidade FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
        cursor.close()
        conexao.close()
        return produto
    except Exception as e:
        print(f"Erro ao obter produto por id: {e}")
        return None

def atualizar_produto(produto_id, nome, categoria, preco, quantidade):
    """Atualiza as informações de um produto no banco de dados."""
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE produtos 
            SET nome = %s, categoria = %s, preco = %s, quantidade = %s 
            WHERE id = %s
        """, (nome, categoria, preco, quantidade, produto_id))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        return False

def deletar_produto(produto_id):
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao deletar produto: {e}")
        return False

def obter_metricas_estoque():
    try:
        conexao = conectar()
        if not conexao:
            return {"total_itens": 0, "valor_total": 0.0, "itens_criticos": 0}
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(preco * quantidade), 0.0) FROM produtos")
        res_geral = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= 3")
        res_criticos = cursor.fetchone()

        cursor.close()
        conexao.close()

        return {
            "total_itens": res_geral[0],
            "valor_total": float(res_geral[1]),
            "itens_criticos": res_criticos[0]
        }
    except Exception as e:
        print(f"Erro ao obter métricas de estoque: {e}")
        return {"total_itens": 0, "valor_total": 0.0, "itens_criticos": 0}