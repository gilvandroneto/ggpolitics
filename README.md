# Dashboard Político com IA

Este dashboard interativo utiliza dados de redes sociais e análises com IA para visualizar tendências políticas, sentimentos e temas discutidos sobre o candidato Tarcísio.

## Funcionalidades

- Filtros por fonte, sentimento, perfil político e localidade
- Gráficos interativos com Plotly
- Integração com imagem ilustrativa
- Carregamento de dados via CSV
- Análise adicional de tópicos neutros (opcional)

## Como usar no Streamlit Cloud

1. Faça login em https://streamlit.io/cloud
2. Crie um novo app apontando para este repositório
3. Aponte para o arquivo `dashboard.py` como script principal
4. Suba os arquivos:
   - `dashboard.py`
   - `tarcisio_analyzed_data.csv`
   - `imagemwhats.jpg`
   - `neutral_analysis_results.txt` (opcional)

Pronto! O dashboard estará acessível via link público.