import psycopg2
from database.connection import conectar

def obter_caixa_atual():
    """Retorna o registro do caixa atual se estiver aberto."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()
        cursor.execute("SELECT id, valor_inicial, status, TO_CHAR(data_abertura, 'DD/MM/YYYY HH24:MI') FROM caixa WHERE status = 'ABERTO' ORDER BY id DESC LIMIT 1")
        caixa = cursor.fetchone()
        cursor.close()
        conexao.close()
        return caixa
    except Exception as e:
        print(f"Erro ao obter caixa atual: {e}")
        return None

def abrir_caixa(valor_inicial):
    """Abre um novo caixa no sistema."""
    if obter_caixa_atual():
        return False, "Já existe um caixa aberto!"

    try:
        conexao = conectar()
        if not conexao:
            return False, "Erro de conexão com o banco."
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO caixa (valor_inicial, status) VALUES (%s, 'ABERTO')", (valor_inicial,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True, "Caixa aberto com sucesso!"
    except Exception as e:
        print(f"Erro ao abrir caixa: {e}")
        return False, f"Erro ao abrir caixa: {e}"

def fechar_caixa():
    """Fecha o caixa atual e calcula o total acumulado nas vendas."""
    caixa_atual = obter_caixa_atual()
    if not caixa_atual:
        return False, "Não há nenhum caixa aberto para fechar."

    caixa_id = caixa_atual[0]
    valor_inicial = float(caixa_atual[1])

    try:
        conexao = conectar()
        if not conexao:
            return False, "Erro de conexão com o banco."
        cursor = conexao.cursor()

        # Soma todas as vendas realizadas enquanto o caixa esteve aberto
        cursor.execute("SELECT COALESCE(SUM(total_venda), 0.0) FROM vendas WHERE data_venda >= (SELECT data_abertura FROM caixa WHERE id = %s)", (caixa_id,))
        total_vendas = float(cursor.fetchone()[0])

        valor_final = valor_inicial + total_vendas

        cursor.execute("""
            UPDATE caixa 
            SET valor_final = %s, status = 'FECHADO', data_fechamento = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (valor_final, caixa_id))

        conexao.commit()
        cursor.close()
        conexao.close()
        return True, f"Caixa fechado com sucesso! Total em caixa: R$ {valor_final:.2f}"
    except Exception as e:
        print(f"Erro ao fechar caixa: {e}")
        return False, f"Erro ao fechar caixa: {e}"