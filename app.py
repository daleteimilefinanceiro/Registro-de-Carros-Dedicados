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

# ---------------- MAPA DE COLUNAS ----------------
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
elif razao_permitida == "TODOS":
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao", "Aprovacao"]
else:
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao"]

abas_objs = st.tabs(abas)
tab_dict = {nome: abas_objs[i] for i, nome in enumerate(abas)}

# ---------------- Aba Registro ----------------
if "Registro" in tab_dict:
    with tab_dict["Registro"]:
        st.header("📌 Registro de Veículos")
        
        # Razão Social
        if razao_permitida != "TODOS":
            razao_social = razao_permitida
            st.info(f"🔒 Você só pode registrar para: **{razao_social}**")
        else:
            razao_social = st.selectbox("Razão Social", razoes_sociais)

        # Ano, Quinzena e Mês
        ano = st.number_input("Ano", min_value=2000, max_value=2100, step=1)
        quinzena = st.selectbox("Quinzena", ["1ª Quinzena", "2ª Quinzena"])
        mes = st.selectbox("Mês", [
            "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
            "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
        ])

        # Operação
        operacao = st.selectbox("Operação", operacoes)

        # Quantidade de veículos
        quantidades = {}
        st.subheader("Quantidade de Veículos")
        for veiculo in tipos_veiculos:
            col1, col2 = st.columns([3,1])
            col1.write(veiculo)
            quantidades[veiculo] = col2.number_input(
                f"Qtd {veiculo}", min_value=0, step=1, key=f"{veiculo}_qtd"
            )

        # Observações
        observacoes = st.text_area("Observações (opcional)")

        # Botão de submissão
        if st.button("Submeter para aprovação"):
            registros = []
            for veiculo, quantidade in quantidades.items():
                if quantidade > 0:
                    registro = {
                        "Razao_Social": razao_social,
                        "Ano": int(ano),
                        "Quinzena": 1 if quinzena == "1ª Quinzena" else 2,
                        "Mes": ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"].index(mes) + 1,
                        "Operacao": operacao,
                        "Tipo_de_Veiculo": veiculo,
                        "Quantidade": int(quantidade),
                        "Observacoes": observacoes if observacoes else None,
                        "Data_de_Submissao": datetime.now().isoformat(),  # <- CORREÇÃO AQUI
                        "Status": "Pendente",
                        "Aprovador": "Pendente",
                        "Data_da_Decisao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Motivo_Rejeicao": "Pendente"
                    }
                    registros.append(registro)

            if registros:
                try:
                    response = supabase.table("registros_diarios").insert(registros).execute()
                    if hasattr(response, "error") and response.error:
                        st.error(f"Erro ao enviar registro: {response.error.message}")
                    else:
                        st.success("✅ Registro submetido para aprovação no banco!")
                        st.dataframe(pd.DataFrame(registros))
                except Exception as e:
                    st.error(f"Erro ao enviar para o Supabase: {e}")
            else:
                st.warning("⚠️ Nenhuma quantidade informada.")

# ---------------- Aba Aprovação ----------------
if "Aprovação" in tab_dict:
    with tab_dict["Aprovação"]:
        st.header("✅ Aprovação de Registros")
        
        # Pega todos os registros
        result = supabase.table("registros_diarios").select("*").execute()
        data = result.data

        if data:
            df_fluxo = pd.DataFrame(data)
            df_pendentes = df_fluxo[df_fluxo["Status"] == "Pendente"]

            if not df_pendentes.empty:
                for i, row in df_pendentes.iterrows():
                    with st.expander(f"{row['Razao_Social']} - {row['Operacao']} - {row['Mes']} {row['Ano']}"):
                        st.write(row)
                        motivo = st.text_input("Motivo da rejeição (se rejeitar)", key=f"motivo_{i}")
                        col1, col2 = st.columns(2)

                        # Aprovar registro
                        if col1.button("✔️ Aprovar", key=f"aprovar_{i}"):
                            update_result = supabase.table("registros_diarios").update({
                                "Status": "Aprovado",
                                "Aprovador": usuario_logado,
                                "Data_da_Decisao": datetime.now()
                            }).eq("id", row["id"]).execute()

                            if update_result.data:  # Se retornou dados, consideramos sucesso
                                st.success("Registro aprovado!")
                                st.experimental_rerun()
                            else:
                                st.error("Erro ao aprovar registro!")

                        # Rejeitar registro
                        if col2.button("❌ Rejeitar", key=f"rejeitar_{i}"):
                            update_result = supabase.table("registros_diarios").update({
                                "Status": "Rejeitado",
                                "Aprovador": usuario_logado,
                                "Data_da_Decisao": datetime.now(),
                                "Motivo_Rejeicao": motivo
                            }).eq("id", row["id"]).execute()

                            if update_result.data:
                                st.warning("Registro rejeitado!")
                                st.experimental_rerun()
                            else:
                                st.error("Erro ao rejeitar registro!")
            else:
                st.info("Nenhum registro pendente.")
        else:
            st.info("Nenhum registro pendente.")
            # ---------------- Aba Fluxo de Aprovação ----------------
# ---------------- Aba Fluxo de Aprovação ----------------
if "Fluxo de Aprovacao" in tab_dict:
    with tab_dict["Fluxo de Aprovacao"]:
        st.header("📊 Fluxo de Aprovação")

        # Pega todos os registros
        result = supabase.table("registros_diarios").select("*").execute()
        data = result.data

        if data:
            df_fluxo = pd.DataFrame(data)

            # FILTRO DE PARCEIRO (apenas registros do parceiro logado)
            if razao_permitida != "TODOS":
                df_fluxo = df_fluxo[df_fluxo["Razao_Social"] == razao_permitida]

            # FILTRO DE MÊS, QUINZENA E STATUS
            meses = [
                "Todos","Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
            ]
            mes_filtro = st.selectbox("Filtrar por mês", meses)
            quinzena_filtro = st.selectbox("Filtrar por quinzena", ["Todos", "1ª Quinzena", "2ª Quinzena"])
            status_filtro = st.selectbox("Filtrar por status", ["Todos", "Pendente", "Aprovado", "Rejeitado"])

            df_filtrado = df_fluxo.copy()

            if mes_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Mes"] == meses.index(mes_filtro)]
            if quinzena_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Quinzena"] == (1 if quinzena_filtro == "1ª Quinzena" else 2)]
            if status_filtro != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Status"] == status_filtro]

            if not df_filtrado.empty:
                st.dataframe(df_filtrado)

                # BOTÃO PARA BAIXAR RELATÓRIO
                df_filtrado_excel = df_filtrado.copy()
                df_filtrado_excel["Data_de_Submissao"] = pd.to_datetime(df_filtrado_excel["Data_de_Submissao"])
                df_filtrado_excel["Data_da_Decisao"] = pd.to_datetime(df_filtrado_excel["Data_da_Decisao"], errors='coerce')

                csv = df_filtrado_excel.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Baixar relatório filtrado",
                    data=csv,
                    file_name=f"relatorio_{usuario_logado}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum registro encontrado para este filtro.")
        else:
            st.info("Nenhum registro cadastrado.")
# ---------------- Aba Aprovação ----------------
if "Aprovacao" in tab_dict and usuario_logado in usuarios_aprovacao_somente:
    with tab_dict["Aprovacao"]:
        st.header("✅ Aprovação de Registros")

        # Pega todos os registros pendentes
        result = supabase.table("registros_diarios").select("*").eq("Status", "Pendente").execute()
        data = result.data

        if data:
            df_pendentes = pd.DataFrame(data)

            if not df_pendentes.empty:
                for i, row in df_pendentes.iterrows():
                    with st.expander(f"{row['Razao_Social']} - {row['Operacao']} - {row['Mes']}/{row['Ano']} - {row['Tipo_de_Veiculo']}"):
                        st.write(row)

                        motivo = st.text_input("Motivo da rejeição (se rejeitar)", key=f"motivo_{i}")
                        col1, col2 = st.columns(2)

                        # Botão Aprovar
                        if col1.button("✔️ Aprovar", key=f"aprovar_{i}"):
                            update_result = supabase.table("registros_diarios").update({
                                "Status": "Aprovado",
                                "Aprovador": usuario_logado,
                                "Data_da_Decisao": datetime.now().isoformat(),
                                "Motivo_Rejeicao": "N/A"
                            }).eq("id", row["id"]).execute()

                            if hasattr(update_result, "error") and update_result.error:
                                st.error(f"Erro ao aprovar: {update_result.error.message}")
                            else:
                                st.success("Registro aprovado!")
                                st.experimental_rerun()

                        # Botão Rejeitar
                        if col2.button("❌ Rejeitar", key=f"rejeitar_{i}"):
                            if not motivo:
                                st.warning("Digite o motivo da rejeição antes de rejeitar!")
                            else:
                                update_result = supabase.table("registros_diarios").update({
                                    "Status": "Rejeitado",
                                    "Aprovador": usuario_logado,
                                    "Data_da_Decisao": datetime.now().isoformat(),
                                    "Motivo_Rejeicao": motivo
                                }).eq("id", row["id"]).execute()

                                if hasattr(update_result, "error") and update_result.error:
                                    st.error(f"Erro ao rejeitar: {update_result.error.message}")
                                else:
                                    st.warning("Registro rejeitado!")
                                    st.experimental_rerun()
            else:
                st.info("Nenhum registro pendente para aprovação.")
        else:
            st.info("Nenhum registro pendente.")
































































