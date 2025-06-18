import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from collections import Counter
import re

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Análise Política Tarcísio de Freitas",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard - Análise Política Tarcísio de Freitas")

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_csv("tarcisio_analyzed_data.csv")

@st.cache_data
def load_neutral_analysis():
    try:
        with open("neutral_analysis_results.txt", "r") as f:
            content = f.read()
        topics_section, words_section = content.split("\n\nPalavras Mais Comuns em Comentários Neutros:\n")
        topics = topics_section.split("\n")
        words = words_section.split(", ")
        return topics, words
    except:
        return [], []

df = load_data()
neutral_topics, neutral_words = load_neutral_analysis()

# Sidebar com filtros
st.sidebar.header("Filtros")

# Filtro por fonte
sources = st.sidebar.multiselect(
    "Selecione as fontes:",
    options=df["source"].unique(),
    default=df["source"].unique()
)

# Filtro por sentimento
sentiments = st.sidebar.multiselect(
    "Selecione os sentimentos:",
    options=df["sentiment"].unique(),
    default=df["sentiment"].unique()
)

# Aplicar filtros
filtered_df = df[
    (df["source"].isin(sources)) & 
    (df["sentiment"].isin(sentiments))
]

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Notícias", len(filtered_df))

with col2:
    alinhadas = len(filtered_df[filtered_df["sentiment"] == "Alinhado"])
    st.metric("Notícias Alinhadas", alinhadas)

with col3:
    oposicao = len(filtered_df[filtered_df["sentiment"] == "Oposição"])
    st.metric("Notícias de Oposição", oposicao)

with col4:
    neutras = len(filtered_df[filtered_df["sentiment"] == "Neutro"])
    st.metric("Notícias Neutras", neutras)

st.divider()

# Layout em duas colunas
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Distribuição por Sentimento")
    
    # Gráfico de pizza para sentimentos
    sentiment_counts = filtered_df["sentiment"].value_counts()
    fig_sentiment = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title="Análise de Sentimento das Notícias"
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

with col2:
    st.subheader("📰 Distribuição por Fonte")
    
    # Gráfico de barras para fontes
    source_counts = filtered_df["source"].value_counts()
    source_df = pd.DataFrame({
        "Fonte": source_counts.index,
        "Número de Notícias": source_counts.values
    })
    fig_source = px.bar(
        source_df,
        x="Fonte",
        y="Número de Notícias",
        title="Número de Notícias por Fonte"
    )
    st.plotly_chart(fig_source, use_container_width=True)

# Seção específica para análise de comentários neutros
st.subheader("🔍 Análise Aprofundada dos Comentários Neutros")
st.write(f"**{neutras} comentários neutros** representam uma oportunidade significativa de engajamento e conversão.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Principais Tópicos Discutidos")
    if neutral_topics:
        for i, topic in enumerate(neutral_topics[:5], 1):
            st.write(f"**{topic}**")
    else:
        st.write("Nenhum tópico identificado.")

with col2:
    st.subheader("🔤 Palavras Mais Frequentes")
    if neutral_words:
        # Criar gráfico de barras para palavras mais frequentes
        words_df = pd.DataFrame({
            "Palavra": neutral_words[:10],
            "Frequência": range(len(neutral_words[:10]), 0, -1)
        })
        fig_words = px.bar(
            words_df,
            x="Frequência",
            y="Palavra",
            orientation="h",
            title="Top 10 Palavras em Comentários Neutros"
        )
        st.plotly_chart(fig_words, use_container_width=True)
    else:
        st.write("Nenhuma palavra identificada.")

# Insights sobre neutros
st.subheader("💡 Insights dos Comentários Neutros")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Potencial de Conversão", f"{neutras} eleitores")
    st.write("Eleitores neutros são mais propensos à conversão com comunicação direcionada.")

with col2:
    st.metric("Temas de Interesse", "Governo, Política")
    st.write("Discussões focam em aspectos práticos da gestão pública.")

with col3:
    st.metric("Oportunidade", "72% do total")
    st.write("Maioria dos comentários são neutros, representando grande oportunidade.")

# Mapa de localização
st.subheader("🗺️ Distribuição Geográfica")

# Preparar dados de localização
location_counts = filtered_df["location"].value_counts()

# Coordenadas aproximadas para algumas localizações brasileiras
location_coords = {
    "SÃO PAULO": [-23.5505, -46.6333],
    "SP": [-23.5505, -46.6333],
    "RIO DE JANEIRO": [-22.9068, -43.1729],
    "RJ": [-22.9068, -43.1729],
    "BELO HORIZONTE": [-19.9167, -43.9345],
    "MG": [-19.9167, -43.9345],
    "SALVADOR": [-12.9714, -38.5014],
    "BA": [-12.9714, -38.5014],
    "BRASÍLIA": [-15.8267, -47.9218],
    "DF": [-15.8267, -47.9218],
    "CURITIBA": [-25.4284, -49.2733],
    "PR": [-25.4284, -49.2733],
    "PORTO ALEGRE": [-30.0346, -51.2177],
    "RS": [-30.0346, -51.2177],
    "FORTALEZA": [-3.7319, -38.5267],
    "CE": [-3.7319, -38.5267],
    "RECIFE": [-8.0476, -34.8770],
    "PE": [-8.0476, -34.8770],
    "MANAUS": [-3.1190, -60.0217],
    "AM": [-3.1190, -60.0217]
}

# Criar mapa
m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

for location, count in location_counts.items():
    if location in location_coords and location != "Desconhecido":
        coords = location_coords[location]
        folium.CircleMarker(
            location=coords,
            radius=min(count * 5, 50),  # Tamanho proporcional ao número de menções
            popup=f"{location}: {count} menções",
            color="blue",
            fill=True,
            fillColor="blue"
        ).add_to(m)

# Exibir mapa
st_folium(m, width=700, height=500)

# Gráfico de barras para localização
location_df = pd.DataFrame({
    "Localização": location_counts.index,
    "Número de Notícias": location_counts.values
})

fig_location = px.bar(
    location_df,
    x="Localização",
    y="Número de Notícias",
    title="Distribuição por Localização"
)
st.plotly_chart(fig_location, use_container_width=True)

# Análise de perfil político
st.subheader("🏛️ Análise de Perfil Político")

# Extrair perfis políticos
political_profiles = []
for profile in filtered_df["political_profile"]:
    if isinstance(profile, str):
        if "(Direita)" in profile:
            political_profiles.append("Direita")
        elif "(Esquerda)" in profile:
            political_profiles.append("Esquerda")
        elif "(Centro)" in profile:
            political_profiles.append("Centro")
        else:
            political_profiles.append("Indefinido")
    else:
        political_profiles.append("Indefinido")

profile_counts = pd.Series(political_profiles).value_counts()

col1, col2 = st.columns(2)

with col1:
    # Gráfico de pizza para perfis políticos
    fig_profile = px.pie(
        values=profile_counts.values,
        names=profile_counts.index,
        title="Distribuição de Perfil Político"
    )
    st.plotly_chart(fig_profile, use_container_width=True)

with col2:
    # Métricas de perfil político
    st.metric("Perfil Direita", profile_counts.get("Direita", 0))
    st.metric("Perfil Esquerda", profile_counts.get("Esquerda", 0))
    st.metric("Perfil Centro", profile_counts.get("Centro", 0))
    st.metric("Perfil Indefinido", profile_counts.get("Indefinido", 0))

# Análise temporal
st.subheader("📅 Análise Temporal")

# Converter datas para datetime
filtered_df_copy = filtered_df.copy()
filtered_df_copy["date_parsed"] = pd.to_datetime(filtered_df_copy["date"], format="%d/%m/%Y", errors="coerce")
filtered_df_copy["year_month"] = filtered_df_copy["date_parsed"].dt.to_period("M")

# Contar notícias por mês
temporal_counts = filtered_df_copy.groupby("year_month").size().reset_index(name="count")
temporal_counts["year_month_str"] = temporal_counts["year_month"].astype(str)

fig_temporal = px.line(
    temporal_counts,
    x="year_month_str",
    y="count",
    title="Evolução Temporal das Notícias",
    labels={"year_month_str": "Período", "count": "Número de Notícias"}
)
st.plotly_chart(fig_temporal, use_container_width=True)

# Seção de captação de leads via WhatsApp
st.subheader("📱 Captação de Leads - WhatsApp")
st.image("imagemwhats.jpg", use_container_width=True, caption="Mapa Mental do fluxo de interação de leads via WhatsApp")

with st.container():
    st.markdown("### 🚀 Como potencializamos a estratégia com IA")
    st.markdown("""
    A estratégia vai além do fluxo de automação: utilizamos **análise de dados em larga escala**, ferramentas de **NLP (Processamento de Linguagem Natural)** e **Inteligência Artificial** para:
    
    - 🧠 **Classificar o perfil político do eleitor** com base em suas mensagens e interações online (incluindo dados do Reddit, X/Twitter, portais de notícias e fóruns).
    - 🔍 **Detectar temas sensíveis**, pautas prioritárias e inclinações ideológicas para **personalizar o conteúdo**.
    - 🧩 **Aplicar análise de sentimento e clusterização** para agrupar eleitores em **tribos digitais** com estratégias distintas.
    - 🎯 **Testar campanhas com IA generativa** e adaptar mensagens para diferentes públicos com base em **engajamento e conversão**.
    - 📊 **Analisar o impacto das campanhas** em tempo real, ajustando estratégias conforme necessário.
                
                
    """)

col1, col2 = st.columns([2, 1])

with col1:
    st.write("**Conecte-se conosco e receba atualizações exclusivas sobre as políticas e ações do Governador Tarcísio de Freitas!**")
    
    # Formulário para captação de leads
    with st.form("lead_form"):
        nome = st.text_input("Nome completo:")
        telefone = st.text_input("Telefone (com DDD):")
        cidade = st.text_input("Cidade:")
        interesse = st.selectbox(
            "Principal interesse:",
            ["Segurança Pública", "Infraestrutura", "Educação", "Saúde", "Economia", "Meio Ambiente", "Outros"]
        )
        
        submitted = st.form_submit_button("📲 Entrar no Grupo WhatsApp")
        
        if submitted:
            if nome and telefone:
                # Criar mensagem para WhatsApp
                mensagem = f"Olá! Sou {nome} de {cidade}. Gostaria de receber atualizações sobre {interesse}. Telefone: {telefone}"
                whatsapp_url = f"https://wa.me/5511999999999?text={mensagem.replace(' ', '%20')}"
                
                st.success("✅ Dados registrados com sucesso!")
                st.markdown(f"[📲 Clique aqui para entrar no grupo WhatsApp]({whatsapp_url})")
                
                # Salvar lead (opcional - para análise posterior)
                lead_data = {
                    "nome": nome,
                    "telefone": telefone,
                    "cidade": cidade,
                    "interesse": interesse,
                    "timestamp": pd.Timestamp.now()
                }
                
                # Salvar em arquivo CSV (pode ser substituído por banco de dados)
                try:
                    leads_df = pd.read_csv("leads_whatsapp.csv")
                    leads_df = pd.concat([leads_df, pd.DataFrame([lead_data])], ignore_index=True)
                except FileNotFoundError:
                    leads_df = pd.DataFrame([lead_data])
                
                leads_df.to_csv("leads_whatsapp.csv", index=False)
            else:
                st.error("❌ Por favor, preencha pelo menos o nome e telefone.")

with col2:
    st.info("""
    **Benefícios de se conectar:**
    
    ✅ Atualizações em primeira mão
    
    ✅ Acesso a eventos exclusivos
    
    ✅ Canal direto com a equipe
    
    ✅ Participação em pesquisas
    
    ✅ Conteúdo exclusivo
    """)

# Tabela de dados filtrados
st.subheader("📋 Dados Detalhados")
st.dataframe(
    filtered_df[["source", "title", "sentiment", "location", "political_profile", "date"]],
    use_container_width=True
)

# Estatísticas adicionais
st.subheader("📊 Estatísticas Adicionais")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Fontes", len(df["source"].unique()))

with col2:
    avg_sentiment_score = len(df[df["sentiment"] == "Alinhado"]) / len(df) * 100
    st.metric("% Sentimento Positivo", f"{avg_sentiment_score:.1f}%")

with col3:
    locations_identified = len(df[df["location"] != "Desconhecido"])
    st.metric("Localizações Identificadas", locations_identified)

# Rodapé
st.divider()
st.write("**Dashboard desenvolvido para análise política e captação de leads - Comitê de Campanha Tarcísio de Freitas**")

