import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client
import io
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
st.title("🚗 Registro de Carros Dedicados")

# ---------------- CONEXÃO COM SUPABASE ----------------
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ---------------- CONFIGURAÇÃO DE LOGIN ----------------
usuarios = {
    "financeadm": {"senha": "Dcschv2020@", "razao": "TODOS"},
    "SRM2500123": {"senha": "ba7V1sK1fzYAgIGy", "razao": "2AR TRANSPORTES LTDA"},
    "SRM2503544": {"senha": "eHjjfGrWHyMayCxI", "razao": "LT WAY TRANSPORTES LTDA"},
    "SRM2501082": {"senha": "TbrTNBmm3E2WDi7y", "razao": "NEW EXPRESS BN LTDA."},
    "SRM2500909": {"senha": "sfgzEwAggNPsu43J", "razao": "GETLOG TRANSPORTES LTDA"},
    "leticia.lima": {"senha": "LL2025!", "razao": "TODOS"},
    "river.zhou": {"senha": "RZ2026!", "razao": "TODOS"},
    "isabel.liu": {"senha": "IL2026!", "razao": "TODOS"},
    "lijun.zeng": {"senha": "LZ2026!", "razao": "TODOS"},
    "rafael.reis": {"senha": "RR2025!", "razao": "TODOS"},
    "paula.soares": {"senha": "PS2025!", "razao": "TODOS"},
    "SRM2404167": {"senha": "bcNL6gY37UAKBG62", "razao": "WF FINGER TRANSPORTE E LOGISTICA LTDA"},
    "SRM2301839": {"senha": "VDML4iEq2L0aD5rR", "razao": "RF TRANSPORTES LTDA"},
    "SRM2402169": {"senha": "cXH7SpRxW0erQjYh", "razao": "RIVILOG LTDA"},
    "SRM2500247": {"senha": "70FrwixLao8aa3dX", "razao": "OSEAS PORTO TRANSPORTES LTDA"},
    "SRM2402921": {"senha": "zDhi3Nn8c41LzxJC", "razao": "NAPORTA TECNOLOGIA LOGISTICA LTDA"},
    "SRM2404319": {"senha": "PxIRj38soQHjjIQv", "razao": "H&L EXPRESSO LTDA"},
    "SRM2402510": {"senha": "RF7FyZsnYvgxHqXO", "razao": "CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA"}
}

# ---------------- CONFIGURAÇÃO DA APLICAÇÃO ----------------
razoes_sociais = [
    "2AR TRANSPORTES LTDA", "ACC SILVA MINIMERCADO", "ARMARINHOS MEGA VARIEDADES LTDA",
    "ATHLANTA LOGISTICA LTDA", "CESTLAVIE LTDA", "CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA",
    "DONALDO TRANSPORTES E LOGISTICA LTDA", "DUDU BABY LTDA", "EASY CARGO SOLUCOES",
    "ETTORE BABY COMERCIO DE CONFECCOES LTDA", "EVZEN LOGISTICA LTDA", "FORTH TRANSPORTES LTDA",
    "GABRIATO EMPORIO LTDA", "GETLOG TRANSPORTES LTDA",
    "GREEN LOG SERVICOS LOGISTICOS SUSTENTAVEIS E COMERCIO DE SUPRIMENTOS LTDA",
    "GOOD ASSESSORIA POSTAL EMBALAGENS E LOGISTICA LTDA", "HBK COMERCIO E ENVIOS DE ENCOMENDAS LTDA",
    "H&L EXPRESSO LTDA", "IMILE - ANDRE LUIZ DE SOUZA", "IMILE - EMERSON DE SOUZA VELOSO",
    "IMILE - GABRIELLA JOVINA MONTEIRO", "IMILE - JOAO VICTOR CONCEICAO LOPES",
    "IMILE - RODRIGO FREITAS CIRICO", "KIM MAGAZINE LTDA", "LOJAS MIUK LTDA",
    "MOVIDOS MODA FASHION LTDA", "NET CONECT CABOS E ACESSORIOS LTDA", "NEW EXPRESS BN LTDA.",
    "NOVALINK MT COMERCIAL LTDA", "PREST SERVI APOIO AO E-COMMERCE LTDA", "QR PHONE ASSISTENCIA TECNICA LTDA",
    "RESENSERV-RESENDE SERVICOS LTDA", "RF TRANSPORTES LTDA", "RIVILOG LTDA",
    "ROHNES TRANSPORTE E LOGISTICA EIRELI", "TEC SERVICE TRANSPORTES LTDA",
    "NAPORTA TECNOLOGIA LOGISTICA LTDA", "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA",
    "WF FINGER TRANSPORTE E LOGISTICA LTDA", "LT WAY TRANSPORTES LTDA", "OSEAS PORTO TRANSPORTES LTDA"
]

tipos_veiculos = ["FIORINO", "VAN", "VUC", "CARRO UTILITARIO", "AJUDANTE", "MOTO", "3/4"]
operacoes = ["TIKTOK", "BENNET JEANS", "SHEIN", "NUVEMSHOP", "SHOP FOCO"]

# >>> CIDADE (NOVO)
cidades = [
    "CAMPINAS", "SUMARÉ", "JUNDIAÍ", "CAMPO LIMPO PAULISTA", "LIMEIRA",
    "PEDREIRA", "SÃO JOSE DOS CAMPOS", "GARÇA", "VOTORANTIM", "AMERICANA",
    "RIBEIRÃO PRETO", "SÃO JOSE DO RIO PRETO", "MATÃO", "SOROCABA",
    "ATIBAIA", "EXTREMA", "NOVA SERRANA"
]

# ---------------- ABA REGISTRO ----------------
with st.tab("Registro"):
    st.title("📅 CALENDÁRIO DE REGISTROS")

    dia_str = datetime.now().strftime("%Y-%m-%d")

    col1, col2, col3 = st.columns(3)  # >>> CIDADE (NOVO)

    razao_social = col1.selectbox("Razão Social", razoes_sociais)
    operacao = col2.selectbox("Operação", operacoes)

    cidade = col3.selectbox("Cidade", cidades)  # >>> CIDADE (NOVO)

    st.markdown("**Quantidade de Veículos**")
    quantidades = {}
    for veiculo in tipos_veiculos:
        quantidades[veiculo] = st.number_input(veiculo, min_value=0, step=1)

    observacoes = st.text_area("📋 Observações (opcional)")

    if st.button("✅ Registrar"):
        registros_para_inserir = []
        data_registro = datetime.now().isoformat()

        for veiculo, qtd in quantidades.items():
            if qtd > 0:
                registros_para_inserir.append({
                    "RAZAO_SOCIAL": razao_social,
                    "DATA_OFICIAL": dia_str,
                    "DATA_DE_REGISTRO": data_registro,
                    "MODALIDADE": veiculo,
                    "QUANTIDADE": int(qtd),
                    "OPERACAO": operacao,
                    "CIDADE": cidade,  # >>> CIDADE (NOVO)
                    "STATUS": "Pendente",
                    "OBSERVACOES": observacoes
                })

        if registros_para_inserir:
            supabase.table("registro_veiculos_calendario").insert(registros_para_inserir).execute()
            st.success("✅ Registro realizado com sucesso!")
        else:
            st.error("⚠️ Registre pelo menos um veículo!")

# ---------------- ABA RELATÓRIO ----------------
with st.tab("Relatorio"):
    st.title("📊 Relatório de Registros")

    cidade_filtro = st.selectbox("🏙️ Cidade", ["Todas"] + cidades)  # >>> CIDADE (NOVO)

    query = supabase.table("registro_veiculos_calendario").select("*")

    if cidade_filtro != "Todas":
        query = query.eq("CIDADE", cidade_filtro)  # >>> CIDADE (NOVO)

    registros = query.execute().data or []

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("ℹ️ Nenhum registro encontrado")






















