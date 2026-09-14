import psycopg2
from database.connection import conectar
from werkzeug.security import check_password_hash

def buscar_usuario_por_login(usuario_login):
    """Busca um usuário no banco pelo nome de usuário."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome, usuario, senha, cargo FROM usuarios WHERE usuario = %s", (usuario_login,))
        usuario = cursor.fetchone()
        cursor.close()
        conexao.close()
        return usuario
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

def autenticar_usuario(usuario_input, senha_input):
    """Valida as credenciais e o hash da senha."""
    usuario = buscar_usuario_por_login(usuario_input)
    if not usuario:
        return None
    
    # Valida a senha informada com o hash salvo no banco
    if check_password_hash(usuario[3], senha_input):
        return {
            "id": usuario[0],
            "nome": usuario[1],
            "usuario": usuario[2],
            "cargo": usuario[4]
        }
    return None