import psycopg2
from werkzeug.security import generate_password_hash
from database.connection import conectar

def popular_banco_demonstracao():
    """Popula o banco PostgreSQL com dados fictícios para demonstração e testes."""
    conexao = conectar()
    if not conexao:
        print("Erro ao conectar ao banco de dados para popular os dados.")
        return

    try:
        cursor = conexao.cursor()

        # 1. Usuários 
        usuarios_ficticios = [
            ("Carlos Silva", "carlos.vendedor", generate_password_hash("123456"), "vendedor"),
            ("Mariana Souza", "mariana.vendedora", generate_password_hash("123456"), "vendedor")
        ]

        for nome, login, senha_hash, cargo in usuarios_ficticios:
            cursor.execute("""
                INSERT INTO usuarios (nome, usuario, senha, cargo)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (usuario) DO NOTHING;
            """, (nome, login, senha_hash, cargo))

        # 2. Clientes 
        clientes_ficticios = [
            ("Lucas Mendes", "123.456.789-00", "(11) 98765-4321", "lucas.mendes@email.com"),
            ("Tech Solutions Ltda", "12.345.678/0001-90", "(11) 3344-5566", "contato@techsolutions.com")
        ]

        for nome, cpf_cnpj, telefone, email in clientes_ficticios:
            cursor.execute("""
                INSERT INTO clientes (nome, cpf_cnpj, telefone, email)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM clientes WHERE cpf_cnpj = %s);
            """, (nome, cpf_cnpj, telefone, email, cpf_cnpj))

        # 3. Produtos de Eletrônicos 
        produtos_ficticios = [
            ("Notebook Dell Inspiron 15", "Notebooks", 3499.90, 12),
            ("Smartphone Samsung Galaxy S23", "Smartphones", 4199.00, 8),
            ("Monitor Gamer LG UltraGear 27'", "Monitores", 1399.00, 15),
            ("Teclado Mecânico Logitech G Pro", "Periféricos", 549.90, 25),
            ("Mouse Sem Fio Logitech MX Master 3S", "Periféricos", 629.00, 18),
            ("Headset Gamer HyperX Cloud II", "Áudio", 489.90, 20),
            ("Cadeira Gamer ThunderX3", "Acessórios", 1199.00, 5),
            ("SSD NVMe Kingston 1TB", "Hardware", 429.90, 30)
        ]

        for nome, categoria, preco, qtd in produtos_ficticios:
            cursor.execute("""
                INSERT INTO produtos (nome, categoria, preco, quantidade)
                SELECT %s, %s, %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM produtos WHERE nome = %s);
            """, (nome, categoria, preco, qtd, nome))

        conexao.commit()
        cursor.close()
        conexao.close()
        print("Banco de dados povoado com sucesso com dados de demonstração (Eletrônicos, Funcionários e Clientes)!")

    except Exception as e:
        print(f" Erro ao popular banco de dados: {e}")

if __name__ == "__main__":
    popular_banco_demonstracao()