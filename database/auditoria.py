import psycopg2
from database.connection import conectar

def registrar_log(usuario_nome, acao, descricao):
    """Registra uma entrada na tabela de auditoria."""
    try:
        conexao = conectar()
        if not conexao:
            return False
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO logs_auditoria (usuario_nome, acao, descricao)
            VALUES (%s, %s, %s)
        """, (usuario_nome, acao, descricao))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as e:
        print(f"Erro ao registrar log de auditoria: {e}")
        return False

def listar_logs():
    """Retorna o histórico dos últimos 50 logs de auditoria."""
    try:
        conexao = conectar()
        if not conexao:
            return []
        cursor = conexao.cursor()
        cursor.execute("""
            SELECT id, usuario_nome, acao, descricao, TO_CHAR(data_hora, 'DD/MM/YYYY HH24:MI:SS')
            FROM logs_auditoria
            ORDER BY id DESC
            LIMIT 50
        """)
        logs = cursor.fetchall()
        cursor.close()
        conexao.close()
        return logs
    except Exception as e:
        print(f"Erro ao listar logs: {e}")
        return []