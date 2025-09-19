import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Dashboard de Metas", layout="wide", page_icon="📊")

# URL do Google Sheets
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSlQ9u5x09qR0dAKJsMC-fXTvJWRWPzMrXpaGaojOPblRrJYbx4Q-xalzh2hmf2WtwHRoLVIBOdL_HC/pub?output=csv"

# --- DEFINIÇÃO DAS METAS E CRITÉRIOS DE COR ---
# Mapeamento de nomes para padronização
NOME_MAPPING = {
    'Werbet': 'Werbet', 'Werker Alencar': 'Werbet', 'Werbet Alencar': 'Werbet',
    'Pamela': 'Pamela', 'Pamela Crédita': 'Pamela', 'Pamela Cri': 'Pamela', 'Pamela Cristina': 'Pamela',
    'Ana Clara': 'Ana Clara', 'Ana Clara Souza': 'Ana Clara',
    'Danilo': 'Danilo', 'Danilo Neder': 'Danilo',
    'Natalie': 'Natalie', 'Natalie Lopes': 'Natalie',
    'Andressa': 'Andressa',
    'Rafael': 'Rafael', 'Rafael Miguel': 'Rafael',
    'Thaís': 'Thaís', 'Thais Mendonca': 'Thaís', 'Thais': 'Thaís', 'Thaki': 'Thaís'
}

META_1 = ["Andressa", "Thaís", "Rafael"]  # 1 produto/dia útil
META_2 = ["Danilo", "Natalie", "Pamela", "Ana Clara", "Werbet"]  # 2 produtos/dia útil

# Dicionário com dias úteis por mês
DIAS_UTEIS_POR_MES = {
    "Junho": 21,
    "Julho": 23,
    "Agosto": 21,
    "Setembro": 22
}

# Metas mensais específicas por comercial (usando nomes padronizados)
META_MENSAL_POR_COMERCIAL = {
    "Junho": {"Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42},
    "Julho": {"Andressa": 23, "Rafael": 23, "Thaís": 23, "Ana Clara": 46, "Danilo": 46, "Pamela": 46, "Natalie": 46, "Werbet": 46},
    "Agosto": {"Andressa": 21, "Rafael": 21, "Thaís": 21, "Ana Clara": 42, "Danilo": 42, "Pamela": 42, "Natalie": 42, "Werbet": 42},
    "Setembro": {"Andressa": 22, "Rafael": 22, "Thaís": 22, "Ana Clara": 44, "Danilo": 44, "Pamela": 44, "Natalie": 44, "Werbet": 44}
}

# Metas mensais totais por mês
META_TOTAL_POR_MES = {
    "Junho": 63,
    "Julho": 69,
    "Agosto": 63,
    "Setembro": 66
}

# --- FUNÇÃO PARA CARREGAR DADOS ---
@st.cache_data
def load_data():
    df = pd.read_csv(URL)
    df['Data de Conclusão'] = pd.to_datetime(df['Data de Conclusão'], dayfirst=True, errors='coerce')
    df.dropna(subset=['Data de Conclusão'], inplace=True)
    df['Ano'] = df['Data de Conclusão'].dt.year
    df['Mês'] = df['Data de Conclusão'].dt.strftime('%B')

    # Converter nomes dos meses para português
    meses_traducao = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março', 'April': 'Abril',
        'May': 'Maio', 'June': 'Junho', 'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    df['Mês'] = df['Mês'].map(meses_traducao).fillna(df['Mês'])
    df['Dia'] = df['Data de Conclusão'].dt.day

    # Padronizar nomes dos comerciais
    df['Comercial_Padronizado'] = df['Comercial/Capitão']
    for nome_original, nome_padrao in NOME_MAPPING.items():
        df.loc[df['Comercial/Capitão'].str.contains(nome_original, case=False, na=False), 'Comercial_Padronizado'] = nome_padrao

    return df

df = load_data()

# --- ESTILOS CSS ---
st.markdown("""
<style>
.main-header {font-size: 2.5rem !important; color: #2E86AB !important; text-align: center; margin-bottom: 1rem;}
.sub-header {font-size: 1.5rem !important; color: #2E86AB !important; border-bottom: 2px solid #2E86AB; padding-bottom: 0.5rem; margin-top: 2rem;}
.metric-card {background-color: #f8f9fa; border-radius: 10px; padding: 1rem; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);}
.success-text {color: #28a745; font-weight: bold;}
.danger-text {color: #dc3545; font-weight: bold;}
.stDataFrame {border-radius: 10px; overflow: hidden;}
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
st.markdown("<h1 class='main-header'>📊 Dashboard de Performance Comercial</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#6c757d;'>Acompanhamento de metas e performance da equipe comercial</p>", unsafe_allow_html=True)
st.markdown("---")

# --- FILTROS ---
st.markdown("### 🔍 Filtros")
col1, col2, col3 = st.columns([1, 1, 2])
anos = sorted(df['Ano'].unique())
meses = sorted(df['Mês'].unique())

ano_sel = col1.selectbox("**Ano**", anos, key="ano_filter")
mes_sel = col2.multiselect("**Mês**", meses, default=meses, key="mes_filter")
comercial_sel = col3.selectbox("**Comercial**", ["Todos"] + sorted(df['Comercial_Padronizado'].unique()), key="comercial_filter")

# --- FILTRANDO POR MÊS E ANO ---
df_filtered = df[(df['Ano'] == ano_sel) & (df['Mês'].isin(mes_sel))]

# --- CALCULAR DIAS ÚTEIS DO PERÍODO ---
qtd_dias_uteis = sum(DIAS_UTEIS_POR_MES.get(m, 0) for m in mes_sel)
if qtd_dias_uteis > 0:
    st.info(f"**📅 Dias úteis no período selecionado: {qtd_dias_uteis}**")
else:
    st.warning("⚠️ Nenhum dado encontrado para o período selecionado")

# --- FILTRO POR INTERVALO DE DATAS ---
if not df_filtered.empty:
    min_date = df_filtered['Data de Conclusão'].min()
    max_date = df_filtered['Data de Conclusão'].max()
    date_range = st.date_input("**Intervalo de datas:**", value=(min_date, max_date), min_value=min_date, max_value=max_date, key="date_filter")
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['Data de Conclusão'] >= pd.to_datetime(start_date)) &
            (df_filtered['Data de Conclusão'] <= pd.to_datetime(end_date))
        ]

# --- FILTRAR POR COMERCIAL ESPECÍFICO ---
if comercial_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Comercial_Padronizado'] == comercial_sel]

# --- FUNÇÕES DE META ---
def meta_diaria(nome):
    return 1 if nome in META_1 else 2 if nome in META_2 else 0

def meta_mensal(nome, meses_selecionados):
    total_meta = 0
    for mes in meses_selecionados:
        if mes in META_MENSAL_POR_COMERCIAL and nome in META_MENSAL_POR_COMERCIAL[mes]:
            total_meta += META_MENSAL_POR_COMERCIAL[mes][nome]
        else:
            dias_uteis = DIAS_UTEIS_POR_MES.get(mes, 0)
            if nome in META_1:
                total_meta += dias_uteis
            elif nome in META_2:
                total_meta += dias_uteis * 2
    return total_meta

def meta_total_mensal(meses_selecionados):
    return sum(META_TOTAL_POR_MES.get(m, 0) for m in meses_selecionados)

# --- RESUMO DAS METAS ---
if not df_filtered.empty:
    st.markdown("---")
    st.markdown("<h2 class='sub-header'>📈 Resumo Geral</h2>", unsafe_allow_html=True)

    total_meta = meta_total_mensal(mes_sel)
    total_realizado = df_filtered.shape[0]
    percentual_atingido = (total_realizado / total_meta * 100) if total_meta > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Meta Total", f"{total_meta:.0f}")
    col2.metric("Realizado", f"{total_realizado:.0f}")
    col3.metric("Atingimento", f"{percentual_atingido:.1f}%")
    col4.metric("Dias Úteis", f"{qtd_dias_uteis}")

    # Gráfico de pizza simplificado
    fig_pizza = px.pie(
        values=[total_realizado, max(0, total_meta - total_realizado)],
        names=['Atingido', 'Restante'],
        title="Status da Meta Geral",
        color_discrete_sequence=['#28a745', '#dc3545'],
        hole=0.4
    )
    fig_pizza.update_traces(textinfo='percent+label', textfont_size=14)
    fig_pizza.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig_pizza, use_container_width=True)

    # --- DESEMPENHO POR COMERCIAL ---
    st.markdown("---")
    st.markdown("<h2 class='sub-header'>👥 Desempenho por Comercial</h2>", unsafe_allow_html=True)

    desempenho_comerciais = df_filtered.groupby('Comercial_Padronizado').size().reset_index(name='Realizado')
    desempenho_comerciais['Meta'] = desempenho_comerciais['Comercial_Padronizado'].apply(lambda x: meta_mensal(x, mes_sel))
    desempenho_comerciais['Atingimento'] = (desempenho_comerciais['Realizado'] / desempenho_comerciais['Meta'] * 100).round(1)
    desempenho_comerciais['Status'] = desempenho_comerciais.apply(lambda x: '✅' if x['Realizado'] >= x['Meta'] else '❌', axis=1)

    # Gráfico de barras
    fig = px.bar(
        desempenho_comerciais,
        x='Comercial_Padronizado',
        y='Realizado',
        color='Status',
        text='Realizado',
        title='Produtos Vendidos por Comercial',
        color_discrete_map={'✅': '#28a745', '❌': '#dc3545'}
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DETALHADA COM CORES ---
    st.markdown("**📋 Detalhamento por Comercial**")
    tabela_display = desempenho_comerciais[['Comercial_Padronizado', 'Realizado', 'Meta', 'Atingimento', 'Status']].copy()
    tabela_display['Atingimento'] = tabela_display['Atingimento'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "0%")
    tabela_display.columns = ['Comercial', 'Realizado', 'Meta', 'Atingimento', 'Status']

    def colorize_status(val):
        return 'background-color: #d4edda; color: #155724; font-weight: bold;' if val == '✅' else 'background-color: #f8d7da; color: #721c24; font-weight: bold;'

    def colorize_atingimento(val):
        try:
            percent = float(val.replace('%', ''))
            if percent >= 100:
                return 'background-color: #d4edda; color: #155724; font-weight: bold;'
            elif percent >= 80:
                return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
            else:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        except:
            return ''

    styled_table = tabela_display.style \
        .map(colorize_status, subset=['Status']) \
        .map(colorize_atingimento, subset=['Atingimento']) \
        .format({'Realizado': '{:.0f}', 'Meta': '{:.0f}'}) \
        .set_properties(**{'text-align': 'center', 'border': '1px solid #dee2e6'}) \
        .set_table_styles([{'selector': 'th', 'props': [('background-color', '#2E86AB'), ('color', 'white'), ('text-align', 'center')]}])

    st.dataframe(styled_table, use_container_width=True, height=400)

else:
    st.warning("⚠️ **Nenhum dado disponível para os filtros selecionados**")

# --- LEGENDA ---
st.markdown("---")
st.markdown("**📖 Legenda:**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- 🟢 **Verde**: Meta atingida ou superada")
    st.markdown("- ✅ **Check**: Meta diária/mensal cumprida")
with col2:
    st.markdown("- 🔴 **Vermelho**: Meta não atingida")
    st.markdown("- ❌ **X**: Meta diária/mensal não cumprida")
