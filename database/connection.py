import psycopg2

def conectar():
    """Estabelece conexão com o banco de dados PostgreSQL rodando no Docker."""
    try:
        conexao = psycopg2.connect(
            host="localhost",
            port=5432,
            database="estoque_db",
            user="igor",
            password="postgrespassword"
        )
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None

def criar_tabelas():
    """Cria as tabelas do sistema no PostgreSQL se não existirem."""
    conexao = conectar()
    if not conexao:
        return

    try:
        cursor = conexao.cursor()

        # Tabela de Produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                categoria VARCHAR(100) NOT NULL,
                preco NUMERIC(10, 2) NOT NULL,
                quantidade INT NOT NULL DEFAULT 0
            );
        """)

        # Tabela de Vendas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                produto_id INT NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
                quantidade INT NOT NULL,
                preco_unitario NUMERIC(10, 2) NOT NULL,
                total_venda NUMERIC(10, 2) NOT NULL,
                forma_pagamento VARCHAR(50) DEFAULT 'Dinheiro',
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabela de Controle de Caixa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caixa (
                id SERIAL PRIMARY KEY,
                valor_inicial NUMERIC(10, 2) NOT NULL,
                valor_final NUMERIC(10, 2) DEFAULT 0.0,
                status VARCHAR(20) NOT NULL DEFAULT 'ABERTO',
                data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_fechamento TIMESTAMP
            );
        """)

        conexao.commit()
        cursor.close()
        conexao.close()
        print("Tabelas verificadas/criadas com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao criar tabelas no PostgreSQL: {e}")