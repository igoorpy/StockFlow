import psycopg2
from werkzeug.security import generate_password_hash

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

        # Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                cargo VARCHAR(20) NOT NULL DEFAULT 'vendedor',
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

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

        # Tabela de Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(150) NOT NULL,
                cpf_cnpj VARCHAR(20),
                telefone VARCHAR(20),
                email VARCHAR(100),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tabela de Vendas (com cliente_id opcional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                produto_id INT NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
                cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL,
                quantidade INT NOT NULL,
                preco_unitario NUMERIC(10, 2) NOT NULL,
                total_venda NUMERIC(10, 2) NOT NULL,
                forma_pagamento VARCHAR(50) DEFAULT 'Dinheiro',
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Garante a coluna cliente_id caso a tabela vendas já existisse anteriormente
        cursor.execute("""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='vendas' AND column_name='cliente_id') THEN
                    ALTER TABLE vendas ADD COLUMN cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL;
                END IF;
            END $$;
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

        # Tabela de Logs de Auditoria
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_auditoria (
                id SERIAL PRIMARY KEY,
                usuario_nome VARCHAR(100) NOT NULL,
                acao VARCHAR(50) NOT NULL,
                descricao TEXT NOT NULL,
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conexao.commit()

        # Usuários padrão
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            senha_hash = generate_password_hash("admin123")
            cursor.execute("""
                INSERT INTO usuarios (nome, usuario, senha, cargo) 
                VALUES ('Administrador', 'admin', %s, 'admin')
            """, (senha_hash,))
            
            senha_vendedor = generate_password_hash("vendedor123")
            cursor.execute("""
                INSERT INTO usuarios (nome, usuario, senha, cargo) 
                VALUES ('Vendedor Teste', 'vendedor', %s, 'vendedor')
            """, (senha_vendedor,))
            
            conexao.commit()

        cursor.close()
        conexao.close()
        print("Tabelas verificadas/criadas com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao criar tabelas no PostgreSQL: {e}")