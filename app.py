import streamlit as st
import pandas as pd
import io
from datetime import datetime
from supabase import create_client, Client

# ---------------- CONFIGURAÇÃO DO SUPABASE ----------------
url = "https://nndurpppvlwnozappqhl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uZHVycHBwdmx3bm96YXBwcWhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5OTQxMjIsImV4cCI6MjA3MjU3MDEyMn0.dQsYwTBRbpL0o2wH9Fbs1-8VobLYmizlGy_EvsArp2U"
supabase: Client = create_client(url, key)

st.title("📋Registro de Carros Dedicados")

# ---------------- CONFIGURAÇÃO DE LOGIN ----------------
usuarios = {
    "financeadm": {"senha": "Dcschv2020@", "razao": "TODOS"},
    "SRM2500123": {"senha": "ba7V1sK1fzYAgIGy", "razao": "2AR TRANSPORTES LTDA"},
    "SRM2501082": {"senha": "TbrTNBmm3E2WDi7y", "razao": "NEW EXPRESS BN LTDA."},
    "SRM2500909": {"senha": "sfgzEwAggNPsu43J", "razao": "GETLOG TRANSPORTES LTDA"},
    "janaina.ferreira": {"senha": "JF2025!", "razao": "TODOS"},
    "daniela.conceicao": {"senha": "DC2025!", "razao": "TODOS"},
    "paula.lacerda": {"senha": "PL2025!", "razao": "TODOS"},
    "guilherme.barbosa": {"senha": "GB2025!", "razao": "TODOS"},
    "rafael.reis": {"senha": "RR2025!", "razao": "TODOS"},
    "paula.soares": {"senha": "PS2025!", "razao": "TODOS"},
}

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

if st.session_state["usuario"] is None:
    st.subheader("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            st.session_state["usuario"] = usuario
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos")
    st.stop()

usuario_logado = st.session_state["usuario"]
razao_permitida = usuarios[usuario_logado]["razao"]

st.sidebar.success(f"👤 Usuário logado: {usuario_logado} ({razao_permitida})")
if st.sidebar.button("Sair"):
    st.session_state["usuario"] = None
    st.rerun()

# ---------------- CONFIGURAÇÃO DA APLICAÇÃO ----------------
razoes_sociais = [
    "2AR TRANSPORTES LTDA","ACC SILVA MINIMERCADO","ARMARINHOS MEGA VARIEDADES LTDA","ATHLANTA LOGISTICA LTDA",
    "CESTLAVIE LTDA","CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA","DONALDO TRANSPORTES E LOGISTICA LTDA",
    "DUDU BABY LTDA","EASY CARGO SOLUCOES","ETTORE BABY COMERCIO DE CONFECCOES LTDA","EVZEN LOGISTICA LTDA",
    "FORTH TRANSPORTES LTDA","GABRIATO EMPORIO LTDA","GETLOG TRANSPORTES LTDA","GREEN LOG SERVICOS LOGISTICOS SUSTENTAVEIS E COMERCIO DE SUPRIMENTOS LTDA",
    "GOOD ASSESSORIA POSTAL EMBALAGENS E LOGISTICA LTDA","HBK COMERCIO E ENVIOS DE ENCOMENDAS LTDA","H&L EXPRESSO LTDA",
    "IMILE - ANDRE LUIZ DE SOUZA","IMILE - EMERSON DE SOUZA VELOSO","IMILE - GABRIELLA JOVINA MONTEIRO",
    "IMILE - JOÃO VICTOR CONCEIÇÃO LOPES","IMILE - RODRIGO FREITAS CIRICO","KIM MAGAZINE LTDA","LOJAS MIUK LTDA",
    "MOVIDOS MODA FASHION LTDA","NET CONECT CABOS E ACESSORIOS LTDA","NEW EXPRESS BN LTDA.","NOVALINK MT COMERCIAL LTDA",
    "PREST SERVI APOIO AO E-COMMERCE LTDA","QR PHONE ASSISTENCIA TECNICA LTDA","RESENSERV-RESENDE SERVICOS LTDA",
    "RF TRANSPORTES LTDA","RIVILOG LTDA","ROHNES TRANSPORTE E LOGISTICA EIRELI","TEC SERVICE TRANSPORTES LTDA",
    "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA","WF FINGER TRANSPORTE E LOGISTICA LTDA"
]

tipos_veiculos = ["AJUDANTE", "MOTO", "CARRO UTILITÁRIO", "FIORINO", "VAN", "VUC"]
operacoes = ["SHEIN", "SHEIN - D2D","TIKTOK", "NUVEMSHOP", "BENNET JEANS"]

# ---------------- ABAS ----------------
usuarios_aprovacao_somente = {
    "janaina.ferreira",
    "daniela.conceicao",
    "paula.lacerda",
    "guilherme.barbosa",
    "rafael.reis",
    "paula.soares",
}
if usuario_logado in usuarios_aprovacao_somente:
    abas = ["Aprovação"]
elif usuarios[usuario_logado]["razao"] == "TODOS":
    abas = ["Registro", "Relatório", "Fluxo de Aprovação", "Aprovação"]
else:
    abas = ["Registro", "Relatório", "Fluxo de Aprovação"]

abas_objs = st.tabs(abas)
tab_dict = {nome: abas_objs[i] for i, nome in enumerate(abas)}

# ---------------- Aba Registro ----------------
if "Registro" in tab_dict:
    with tab_dict["Registro"]:
        st.header("📌 Registro de Veículos")

        if razao_permitida != "TODOS":
            razao_social = razao_permitida
            st.info(f"🔒 Você só pode registrar para: **{razao_social}**")
        else:
            razao_social = st.selectbox("Razão Social", razoes_sociais)

        ano = st.number_input("Ano", min_value=2000, max_value=2100, step=1)
        quinzena = st.selectbox("Quinzena", ["1ª Quinzena", "2ª Quinzena"])
        mes = st.selectbox("Mês", [
            "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
            "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
        ])
        operacao = st.selectbox("Operação", operacoes)

        quantidades = {}
        st.subheader("Quantidade de Veículos")
        for veiculo in tipos_veiculos:
            col1, col2 = st.columns([3, 1])
            col1.write(veiculo)
            quantidades[veiculo] = col2.number_input(f"Qtd {veiculo}", min_value=0, step=1, key=f"{veiculo}_qtd")

        observacoes = st.text_area("Observações (opcional)")

        if st.button("Submeter para aprovação"):
            for veiculo, quantidade in quantidades.items():
                if quantidade > 0:
                    supabase.table("registros").insert({
                        "RAZAO_SOCI": razao_social,
                        "ANO": ano,
                        "QUINZENA": quinzena,
                        "MES": mes,
                        "OPERACAO": operacao,
                        "TIPO_VEICUL": veiculo,
                        "QUANTIDADE": quantidade,
                        "OBSERVACAO": observacoes,
                        "DATA_SUBMI": datetime.now().strftime("%Y-%m-%d"),
                        "STATUS": "Pendente",
                        "APROVADOR": "",
                        "DATA_DECIS": None,
                        "MOTIVO_REJ": ""
                    }).execute()
            st.success("✅ Registro submetido para aprovação!")

# ---------------- Aba Relatório ----------------
if "Relatório" in tab_dict:
    with tab_dict["Relatório"]:
        st.header("📊 Relatório e Exportação")

        data = supabase.table("registros").select("*").eq("STATUS", "Aprovado").execute()
        df = pd.DataFrame(data.data)

        if not df.empty:
            if razao_permitida != "TODOS":
                df = df[df["RAZAO_SOCI"] == razao_permitida]

            if razao_permitida == "TODOS":
                filtro_razao = st.selectbox("Filtrar por Razão Social", ["Todas"] + razoes_sociais)
                if filtro_razao != "Todas":
                    df = df[df["RAZAO_SOCI"] == filtro_razao]

            filtro_quinzena = st.selectbox("Filtrar por Quinzena", ["Todas", "1ª Quinzena", "2ª Quinzena"])
            filtro_mes = st.selectbox("Filtrar por Mês", ["Todos"] + [
                "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
            ])

            if filtro_quinzena != "Todas":
                df = df[df["QUINZENA"] == filtro_quinzena]
            if filtro_mes != "Todos":
                df = df[df["MES"] == filtro_mes]

            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Relatório")
            st.download_button(
                label="📥 Exportar Excel",
                data=output.getvalue(),
                file_name="relatorio_filtrado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Nenhum registro aprovado encontrado.")

























