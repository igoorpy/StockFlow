# Sistema de Gestão de Estoque e Ponto de Venda (PDV)

Sistema web para controle de estoque, fluxo de caixa, gestão de vendas e cadastros de clientes com suporte a controle de acesso baseado em papéis (RBAC), emissão de comprovantes em PDF e rastreabilidade por logs de auditoria.


## Funcionamento do Sistema

### Autenticação e Controle de Acesso (RBAC)
O sistema possui dois perfis de acesso distintos:
* **Administrador (admin):** Acesso irrestrito a todas as áreas, incluindo cadastro/edição/exclusão de produtos, dashboard de métricas e visualização dos logs de auditoria.
* **Vendedor (vendedor):** Restrito às operações do Módulo de Vendas (PDV), abertura/fechamento de caixa e cadastro de clientes.

### Gestão de Estoque
Permite o cadastro de produtos informando Nome, Categoria, Preço e Quantidade. O banco de dados PostgreSQL gera o identificador único (`ID`) de forma automática via tipo `SERIAL`. O sistema calcula o valor total investido e sinaliza itens com estoque crítico (`<= 3` unidades).

### Gestão de Clientes
Oferece cadastro com Nome, CPF/CNPJ, Telefone e E-mail. Na realização de uma venda no PDV, o vendedor pode associar opcionalmente um cliente cadastrado à transação.

### Ponto de Venda (PDV) e Ciclo de Caixa
* **Abertura de Caixa:** Exige o lançamento de um valor inicial (fundo de troco) para habilitar o registro de vendas.
* **Registro de Vendas:** Valida a quantidade solicitada contra o estoque atual e subtrai os itens do banco de dados de forma atômica, registrando a forma de pagamento (Dinheiro, PIX, Cartão de Crédito ou Cartão de Débito).
* **Fechamento de Caixa:** Calcula o saldo final acumulado no turno, encerra a sessão do caixa e dispara o download automático do relatório de fechamento consolidado em PDF.

### Emissão de PDFs
* **Comprovante de Venda:** PDF contendo os detalhes do produto, quantidade, valor, meio de pagamento, data/hora e os dados do cliente associado.
* **Relatório de Fechamento de Caixa:** PDF consolidado com o total de vendas por forma de pagamento, saldo final e campos para assinatura do operador e da gerência.

### Auditoria e Rastreabilidade
Cada ação sensível (login, logout, criação/edição/exclusão de produtos, registro de vendas e abertura/fechamento de caixa) é gravada na tabela `logs_auditoria` com nome do usuário, tipo de ação, descrição detalhada e carimbo de data/hora.

