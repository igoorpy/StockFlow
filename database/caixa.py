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

def obter_resumo_fechamento_caixa(caixa_id):
    """Retorna o detalhamento das vendas do caixa por forma de pagamento."""
    try:
        conexao = conectar()
        if not conexao:
            return None
        cursor = conexao.cursor()

        # Busca dados basicos do caixa
        cursor.execute("""
            SELECT id, valor_inicial, valor_final, 
                   TO_CHAR(data_abertura, 'DD/MM/YYYY HH24:MI'), 
                   TO_CHAR(data_fechamento, 'DD/MM/YYYY HH24:MI')
            FROM caixa WHERE id = %s
        """, (caixa_id,))
        caixa = cursor.fetchone()

        if not caixa:
            conexao.close()
            return None

        data_abertura = caixa[3]

        # Busca soma por forma de pagamento durante o caixa
        query_pagamentos = """
            SELECT forma_pagamento, COALESCE(SUM(total_venda), 0.0), COUNT(id)
            FROM vendas
            WHERE data_venda >= (SELECT data_abertura FROM caixa WHERE id = %s)
            GROUP BY forma_pagamento
        """
        cursor.execute(query_pagamentos, (caixa_id,))
        vendas_por_forma = cursor.fetchall()

        cursor.close()
        conexao.close()

        # Consolida os totais por meio de pagamento
        totais = {"Dinheiro": 0.0, "PIX": 0.0, "Cartão de Crédito": 0.0, "Cartão de Débito": 0.0}
        qtd_vendas = 0
        total_vendas_geral = 0.0

        for item in vendas_por_forma:
            forma, valor, qtd = item[0], float(item[1]), item[2]
            totais[forma] = valor
            qtd_vendas += qtd
            total_vendas_geral += valor

        return {
            "caixa_id": caixa[0],
            "valor_inicial": float(caixa[1]),
            "valor_final": float(caixa[2]) if caixa[2] else (float(caixa[1]) + total_vendas_geral),
            "data_abertura": caixa[3],
            "data_fechamento": caixa[4],
            "total_vendas": total_vendas_geral,
            "qtd_vendas": qtd_vendas,
            "detalhes_pagamento": totais
        }
    except Exception as e:
        print(f"Erro ao gerar resumo de fechamento: {e}")
        return None

def fechar_caixa():
    """Fecha o caixa atual e calcula o total acumulado nas vendas."""
    caixa_atual = obter_caixa_atual()
    if not caixa_atual:
        return False, "Não há nenhum caixa aberto para fechar.", None

    caixa_id = caixa_atual[0]
    valor_inicial = float(caixa_atual[1])

    try:
        conexao = conectar()
        if not conexao:
            return False, "Erro de conexão com o banco.", None
        cursor = conexao.cursor()

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
        return True, f"Caixa fechado com sucesso! Total em caixa: R$ {valor_final:.2f}", caixa_id
    except Exception as e:
        print(f"Erro ao fechar caixa: {e}")
        return False, f"Erro ao fechar caixa: {e}", None