import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import conectar

def autenticar_usuario(usuario_input, senha_input):
    """Verifica as credenciais do usuário e valida a senha criptografada."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()

        cursor.execute("""
            SELECT id, nome, usuario, senha, cargo 
            FROM usuarios 
            WHERE usuario = %s
        """, (usuario_input,))
        
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if usuario and check_password_hash(usuario[3], senha_input):
            return {
                "id": usuario[0],
                "nome": usuario[1],
                "usuario": usuario[2],
                "cargo": usuario[4]
            }
        return None
    except Exception as e:
        print(f"Erro ao autenticar usuário: {e}")
        return None

def listar_usuarios():
    """Retorna todos os usuários cadastrados no sistema."""
    try:
        conexao = conectar()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, usuario, cargo, TO_CHAR(data_criacao, 'DD/MM/YYYY HH24:MI') FROM usuarios ORDER BY id ASC")
        usuarios = cursor.fetchall()
        cursor.close()
        conexao.close()
        return usuarios
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []

def cadastrar_usuario(nome, usuario, senha, cargo="vendedor"):
    """Insere um novo operador no banco com senha criptografada."""
    try:
        conexao = conectar()
        if not conexao:
            return False, "Erro de conexão com o banco de dados."
        cursor = conexao.cursor()

        senha_hash = generate_password_hash(senha)
        cursor.execute("""
            INSERT INTO usuarios (nome, usuario, senha, cargo)
            VALUES (%s, %s, %s, %s)
        """, (nome, usuario, senha_hash, cargo))

        conexao.commit()
        cursor.close()
        conexao.close()
        return True, "Usuário cadastrado com sucesso."
    except psycopg2.IntegrityError:
        return False, "Nome de usuário (login) já está em uso."
    except Exception as e:
        print(f"Erro ao cadastrar usuário: {e}")
        return False, f"Erro ao cadastrar usuário: {e}"

def redefinir_senha_usuario(usuario_id, nova_senha):
    """Atualiza a senha do usuário informado gerando um novo hash."""
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()

        senha_hash = generate_password_hash(nova_senha)
        cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (senha_hash, usuario_id))

        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao redefinir senha: {e}")
        return False