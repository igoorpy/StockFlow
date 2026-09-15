import psycopg2
from database.connection import conectar

def cadastrar_cliente(nome, cpf_cnpj, telefone, email):
    """Insere um novo cliente no banco de dados."""
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, cpf_cnpj, telefone, email)
            VALUES (%s, %s, %s, %s)
        """, (nome, cpf_cnpj, telefone, email))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {e}")
        return False

def listar_clientes():
    """Retorna a lista de todos os clientes cadastrados ordenados por nome."""
    try:
        conexao = conectar()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, cpf_cnpj, telefone, email FROM clientes ORDER BY nome ASC")
        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return clientes
    except Exception as e:
        print(f"Erro ao listar clientes: {e}")
        return []

def obter_cliente_por_id(cliente_id):
    """Busca um cliente específico pelo ID."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, cpf_cnpj, telefone, email FROM clientes WHERE id = %s", (cliente_id,))
        cliente = cursor.fetchone()
        cursor.close()
        conexao.close()
        return cliente
    except Exception as e:
        print(f"Erro ao obter cliente por id: {e}")
        return None