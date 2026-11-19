# HEIWA — Explorador de Argumentos

Protótipo Streamlit para explorar planilhas de anotação de argumentos com base no modelo de Toulmin.

## Executar localmente

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá o aplicativo localmente. Envie um arquivo `.xlsx`, `.xls` ou `.csv`.

## O que esta versão inclui

- Upload de Excel e CSV.
- Filtro por `Conversation_id` quando essa coluna existir.
- Busca textual.
- Grafo com claim, dado, warrant, rebuttal, backing e qualifier, quando houver conteúdo nas colunas.
- Painel para inspecionar uma afirmação e consultar o texto original e as justificativas disponíveis.
- Tabela de resultados e exportação da seleção filtrada em CSV.
- Limite configurável de linhas exibidas no grafo para evitar sobrecarga visual.

## Limitações metodológicas importantes

1. Cada linha é tratada como uma anotação independente.
2. Elementos da mesma linha são conectados à afirmação daquela linha.
3. O app não infere que duas afirmações iguais são o mesmo argumento.
4. O app não detecta automaticamente se uma refutação contesta uma afirmação de outra linha.
5. A conexão representa a estrutura usada pelo protótipo, não uma validação automática da força do argumento.

## Próximas melhorias recomendadas

- Adicionar uma coluna explícita `Source_ID` e `Target_ID` para relações entre afirmações de linhas diferentes.
- Criar uma visão alternativa em formato de cartão/timeline para usuários que não se sintam confortáveis com grafos.
- Permitir mapear manualmente colunas quando a planilha tiver cabeçalhos diferentes.
- Criar exemplos de dados para demonstração sem depender de dados sensíveis.
- Testar com usuários e observar se compreendem os tipos de nó e o significado das setas.
