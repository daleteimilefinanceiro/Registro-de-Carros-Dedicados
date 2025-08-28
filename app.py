import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

st.title("📋Registro de Carros Dedicados")

# ---------------- CONFIGURAÇÃO DE LOGIN ----------------
usuarios = {
    "financeadm": {"senha": "Dcschv2020@", "razao": "TODOS"},
    "SRM2500123": {"senha": "ba7V1sK1fzYAgIGy", "razao": "2AR TRANSPORTES LTDA"},
    "SRM2501082": {"senha": "TbrTNBmm3E2WDi7y", "razao": "NEW EXPRESS BN LTDA."},
    "SRM2500909": {"senha": "sfgzEwAggNPsu43J", "razao": "GETLOG TRANSPORTES LTDA"},
    "janaina.ferreira": {"senha": "1234", "razao": "TODOS"}
    # Adicione os outros aqui...
}

# Estado de login
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

arquivo_fluxo = "fluxo.xlsx"

# ---------------- ABAS ----------------
if usuario_logado == "financeadm":
    abas = ["Registro", "Relatório", "Fluxo de Aprovação", "Aprovação"]
elif usuario_logado == "janaina.ferreira":
    abas = ["Aprovação"]
else:
    abas = ["Registro", "Fluxo de Aprovação"]

abas_objs = st.tabs(abas)

# Mapeando abas dinamicamente
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
            registros = []
            for veiculo, quantidade in quantidades.items():
                if quantidade > 0:
                    registros.append({
                        "Razão Social": razao_social,
                        "Ano": ano,
                        "Quinzena": quinzena,
                        "Mês": mes,
                        "Operação": operacao,
                        "Tipo de Veículo": veiculo,
                        "Quantidade": quantidade,
                        "Observações": observacoes,
                        "Data de Submissão": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Status": "Pendente",
                        "Aprovador": "",
                        "Data da Decisão": "",
                        "Motivo Rejeição": ""
                    })

            if registros:
                df_novo = pd.DataFrame(registros)
                if os.path.exists(arquivo_fluxo):
                    df_existente = pd.read_excel(arquivo_fluxo)
                    df_final = pd.concat([df_existente, df_novo], ignore_index=True)
                else:
                    df_final = df_novo
                df_final.to_excel(arquivo_fluxo, index=False)
                st.success("✅ Registro submetido para aprovação!")
                st.dataframe(df_novo)
            else:
                st.warning("⚠️ Nenhuma quantidade informada.")

# ---------------- Aba Relatório ----------------
if "Relatório" in tab_dict:
    with tab_dict["Relatório"]:
        st.header("📊 Relatório e Exportação")

        if os.path.exists(arquivo_fluxo):
            df = pd.read_excel(arquivo_fluxo)
            df = df[df["Status"] == "Aprovado"]  # só mostra aprovados

            if razao_permitida != "TODOS":
                df = df[df["Razão Social"] == razao_permitida]

            if razao_permitida == "TODOS":
                filtro_razao = st.selectbox("Filtrar por Razão Social", ["Todas"] + razoes_sociais)
                if filtro_razao != "Todas":
                    df = df[df["Razão Social"] == filtro_razao]

            filtro_quinzena = st.selectbox("Filtrar por Quinzena", ["Todas", "1ª Quinzena", "2ª Quinzena"])
            filtro_mes = st.selectbox("Filtrar por Mês", ["Todos"] + [
                "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"
            ])

            if filtro_quinzena != "Todas":
                df = df[df["Quinzena"] == filtro_quinzena]
            if filtro_mes != "Todos":
                df = df[df["Mês"] == filtro_mes]

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

# ---------------- Aba Fluxo de Aprovação ----------------
if "Fluxo de Aprovação" in tab_dict:
    with tab_dict["Fluxo de Aprovação"]:
        st.header("🔎 Fluxo de Aprovação")

        if os.path.exists(arquivo_fluxo):
            df = pd.read_excel(arquivo_fluxo)

            if razao_permitida != "TODOS":
                df = df[df["Razão Social"] == razao_permitida]

            st.dataframe(df)
        else:
            st.info("Nenhum registro encontrado no fluxo.")

# ---------------- Aba Aprovação ----------------
if "Aprovação" in tab_dict:
    with tab_dict["Aprovação"]:
        st.header("✅ Aprovação de Registros")

        if os.path.exists(arquivo_fluxo):
            df_fluxo = pd.read_excel(arquivo_fluxo)
            df_pendentes = df_fluxo[df_fluxo["Status"] == "Pendente"]

            if not df_pendentes.empty:
                for i, row in df_pendentes.iterrows():
                    with st.expander(f"{row['Razão Social']} - {row['Operação']} - {row['Mês']} {row['Ano']}"):
                        st.write(row)

                        motivo = st.text_input("Motivo da rejeição (se rejeitar)", key=f"motivo_{i}")
                        col1, col2 = st.columns(2)

                        if col1.button("✔️ Aprovar", key=f"aprovar_{i}"):
                            df_fluxo.loc[i, "Status"] = "Aprovado"
                            df_fluxo.loc[i, "Aprovador"] = usuario_logado
                            df_fluxo.loc[i, "Data da Decisão"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            df_fluxo.to_excel(arquivo_fluxo, index=False)
                            st.success("Registro aprovado!")
                            st.rerun()

                        if col2.button("❌ Rejeitar", key=f"rejeitar_{i}"):
                            df_fluxo.loc[i, "Status"] = "Rejeitado"
                            df_fluxo.loc[i, "Aprovador"] = usuario_logado
                            df_fluxo.loc[i, "Data da Decisão"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            df_fluxo.loc[i, "Motivo Rejeição"] = motivo
                            df_fluxo.to_excel(arquivo_fluxo, index=False)
                            st.warning("Registro rejeitado!")
                            st.rerun()
            else:
                st.info("Nenhum registro pendente.")
        else:
            st.info("Nenhum registro pendente.")















