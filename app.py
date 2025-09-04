import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

st.set_page_config(layout="wide")
st.title("📋 Registro de Carros Dedicados")

# ---------------- CONEXÃO COM SUPABASE ----------------
url = "https://nndurpppvlwnozappqhl.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uZHVycHBwdmx3bm96YXBwcWhsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Njk5NDEyMiwiZXhwIjoyMDcyNTcwMTIyfQ.HSurs6kpKXCTRwR9eJE-GbZHYr0IZCQoWIaCODNHiT8"
supabase = create_client(url, key)

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
    "rafael.reis": {"senha": "RR2025!", "razao": "TODOS"}
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
    "IMILE - JOAO VICTOR CONCEICAO LOPES","IMILE - RODRIGO FREITAS CIRICO","KIM MAGAZINE LTDA","LOJAS MIUK LTDA",
    "MOVIDOS MODA FASHION LTDA","NET CONECT CABOS E ACESSORIOS LTDA","NEW EXPRESS BN LTDA.","NOVALINK MT COMERCIAL LTDA",
    "PREST SERVI APOIO AO E-COMMERCE LTDA","QR PHONE ASSISTENCIA TECNICA LTDA","RESENSERV-RESENDE SERVICOS LTDA",
    "RF TRANSPORTES LTDA","RIVILOG LTDA","ROHNES TRANSPORTE E LOGISTICA EIRELI","TEC SERVICE TRANSPORTES LTDA",
    "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA","WF FINGER TRANSPORTE E LOGISTICA LTDA"
]

tipos_veiculos = ["AJUDANTE", "MOTO", "CARRO UTILITARIO", "FIORINO", "VAN", "VUC"]
operacoes = ["SHEIN", "SHEIN - D2D","TIKTOK", "NUVEMSHOP", "BENNET JEANS"]

# ---------------- MAPA DE COLUNAS (SEM ACENTOS) ----------------
colunas_map = {
    "Razao Social": "Razao_Social",
    "Ano": "Ano",
    "Quinzena": "Quinzena",
    "Mes": "Mes",
    "Operacao": "Operacao",
    "Tipo de Veiculo": "Tipo_de_Veiculo",
    "Quantidade": "Quantidade",
    "Observacoes": "Observacoes",
    "Data de Submissao": "Data_de_Submissao",
    "Status": "Status",
    "Aprovador": "Aprovador",
    "Data da Decisao": "Data_da_Decisao",
    "Motivo Rejeicao": "Motivo_Rejeicao"
}

# ---------------- ABAS ----------------
usuarios_aprovacao_somente = {
    "janaina.ferreira",
    "daniela.conceicao",
    "paula.lacerda",
    "guilherme.barbosa",
    "rafael.reis",
}

if usuario_logado in usuarios_aprovacao_somente:
    abas = ["Aprovacao"]
elif usuarios[usuario_logado]["razao"] == "TODOS":
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao", "Aprovacao"]
else:
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao"]

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
            col1, col2 = st.columns([3,1])
            col1.write(veiculo)
            quantidades[veiculo] = col2.number_input(f"Qtd {veiculo}", min_value=0, step=1, key=f"{veiculo}_qtd")

        observacoes = st.text_area("Observações (opcional)")

        if st.button("Submeter para aprovação"):
            registros = []
            for veiculo, quantidade in quantidades.items():
                if quantidade > 0:
                    registro = {
                        colunas_map["Razão Social"]: razao_social,
                        colunas_map["Ano"]: int(ano),
                        colunas_map["Quinzena"]: 1 if quinzena == "1ª Quinzena" else 2,
                        colunas_map["Mes"]: ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                                             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1,
                        colunas_map["Operação"]: operacao,
                        colunas_map["Tipo_de_Veiculo"]: veiculo,
                        colunas_map["Quantidade"]: int(quantidade),
                        colunas_map["Observacoes"]: observacoes,
                        colunas_map["Data_de_Submissao"]: datetime.now(),
                        colunas_map["Status"]: "Pendente",
                        colunas_map["Aprovador"]: None,
                        colunas_map["Data_da_Decisao"]: None,
                        colunas_map["Motivo_Rejeicao"]: None
                    }
                    registros.append(registro)

            if registros:
                for registro in registros:
                    response = supabase.table("registros_diarios").insert(registro).execute()
                    if response.error:
                        st.error(f"Erro ao enviar registro: {response.error.message}")
                        break
                else:
                    st.success("✅ Registro submetido para aprovação no banco!")
                    st.dataframe(pd.DataFrame(registros))
            else:
                st.warning("⚠️ Nenhuma quantidade informada.")

# ---------------- Aba Aprovação ----------------
if "Aprovação" in tab_dict:
    with tab_dict["Aprovação"]:
        st.header("✅ Aprovação de Registros")
        data = supabase.table("registros_diarios").select("*").execute().data
        if data:
            df_fluxo = pd.DataFrame(data)
            df_pendentes = df_fluxo[df_fluxo["Status"] == "Pendente"]
            if not df_pendentes.empty:
                for i, row in df_pendentes.iterrows():
                    with st.expander(f"{row['Razao_Social']} - {row['Operacao']} - {row['Mes']} {row['Ano']}"):
                        st.write(row)
                        motivo = st.text_input("Motivo da rejeição (se rejeitar)", key=f"motivo_{i}")
                        col1, col2 = st.columns(2)

                        if col1.button("✔️ Aprovar", key=f"aprovar_{i}"):
                            response = supabase.table("registros_diarios").update({
                                "Status": "Aprovado",
                                "Aprovador": usuario_logado,
                                "Data_da_Decisao": datetime.now()
                            }).eq("id", row["id"]).execute()
                            if response.error:
                                st.error(f"Erro ao aprovar registro: {response.error.message}")
                            else:
                                st.success("Registro aprovado!")
                                st.rerun()

                        if col2.button("❌ Rejeitar", key=f"rejeitar_{i}"):
                            response = supabase.table("registros_diarios").update({
                                "Status": "Rejeitado",
                                "Aprovador": usuario_logado,
                                "Data_da_Decisao": datetime.now(),
                                "Motivo_Rejeicao": motivo
                            }).eq("id", row["id"]).execute()
                            if response.error:
                                st.error(f"Erro ao rejeitar registro: {response.error.message}")
                            else:
                                st.warning("Registro rejeitado!")
                                st.rerun()
            else:
                st.info("Nenhum registro pendente.")
        else:
            st.info("Nenhum registro pendente.")






































