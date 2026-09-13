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
    
def deletar_produto(produto_id):
    """Remove um produto do banco de dados pelo ID."""
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

def atualizar_produto(produto_id, nome, categoria, preco, quantidade):
    """Atualiza as informações de um produto existente."""
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

def obter_metricas_estoque():
    try:
        conexao = conectar()
        if not conexao:
            return {"total_itens": 0, "valor_total": 0.0, "itens_criticos": 0}
        cursor = conexao.cursor()
        cursor.execute("SELECT quantidade, preco FROM produtos")
        produtos = cursor.fetchall()
        cursor.close()
        conexao.close()

        total_itens = len(produtos)
        valor_total_estoque = sum(float(p[0]) * float(p[1]) for p in produtos) if produtos else 0.0
        itens_criticos = sum(1 for p in produtos if p[0] <= 3)

        return {
            "total_itens": total_itens,
            "valor_total": valor_total_estoque,
            "itens_criticos": itens_criticos
        }
    except Exception as e:
        print(f"Erro ao calcular metricas: {e}")
        return {"total_itens": 0, "valor_total": 0.0, "itens_criticos": 0}
    