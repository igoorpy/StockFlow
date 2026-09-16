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
    """Cria e atualiza as tabelas do sistema no PostgreSQL."""
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

        # Tabela de Vendas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL,
                total_venda NUMERIC(10, 2) NOT NULL,
                forma_pagamento VARCHAR(50) DEFAULT 'Dinheiro',
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # MIGRAÇÃO E CORREÇÃO DE COLUNAS DA TABELA VENDAS:
        # Permite que produto_id, quantidade e preco_unitario sejam nulos na tabela vendas
        # pois agora eles pertencem a tabela itens_venda
        cursor.execute("""
            DO $$ 
            BEGIN 
                -- Remove restricao NOT NULL de produto_id se ela existir
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='vendas' AND column_name='produto_id') THEN
                    ALTER TABLE vendas ALTER COLUMN produto_id DROP NOT NULL;
                END IF;

                -- Remove restricao NOT NULL de quantidade se ela existir
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='vendas' AND column_name='quantidade') THEN
                    ALTER TABLE vendas ALTER COLUMN quantidade DROP NOT NULL;
                END IF;

                -- Remove restricao NOT NULL de preco_unitario se ela existir
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='vendas' AND column_name='preco_unitario') THEN
                    ALTER TABLE vendas ALTER COLUMN preco_unitario DROP NOT NULL;
                END IF;

                -- Garante que cliente_id exista na tabela vendas
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='vendas' AND column_name='cliente_id') THEN
                    ALTER TABLE vendas ADD COLUMN cliente_id INT REFERENCES clientes(id) ON DELETE SET NULL;
                END IF;
            END $$;
        """)

        # Tabela de Itens da Venda (Carrinho Multi-Item)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_venda (
                id SERIAL PRIMARY KEY,
                venda_id INT NOT NULL REFERENCES vendas(id) ON DELETE CASCADE,
                produto_id INT REFERENCES produtos(id) ON DELETE SET NULL,
                quantidade INT NOT NULL,
                preco_unitario NUMERIC(10, 2) NOT NULL,
                subtotal NUMERIC(10, 2) NOT NULL
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

        # Usuários Padrão
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
        print("Migração de tabela executada com sucesso no PostgreSQL!")
    except Exception as e:
        print(f"Erro ao criar/atualizar tabelas no PostgreSQL: {e}")