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
    "2AR TRANSPORTES LTDA",
    "ACC SILVA MINIMERCADO",
    "ARMARINHOS MEGA VARIEDADES LTDA",
    "ATHLANTA LOGISTICA LTDA",
    "CESTLAVIE LTDA",
    "CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA",
    "DONALDO TRANSPORTES E LOGISTICA LTDA",
    "DUDU BABY LTDA",
    "EASY CARGO SOLUCOES",
    "ETTORE BABY COMERCIO DE CONFECCOES LTDA",
    "EVZEN LOGISTICA LTDA",
    "FORTH TRANSPORTES LTDA",
    "GABRIATO EMPORIO LTDA",
    "GETLOG TRANSPORTES LTDA",
    "GREEN LOG SERVICOS LOGISTICOS SUSTENTAVEIS E COMERCIO DE SUPRIMENTOS LTDA",
    "GOOD ASSESSORIA POSTAL EMBALAGENS E LOGISTICA LTDA",
    "HBK COMERCIO E ENVIOS DE ENCOMENDAS LTDA",
    "H&L EXPRESSO LTDA",
    "IMILE - ANDRE LUIZ DE SOUZA",
    "IMILE - EMERSON DE SOUZA VELOSO",
    "IMILE - GABRIELLA JOVINA MONTEIRO",
    "IMILE - JOÃO VICTOR CONCEIÇÃO LOPES",
    "IMILE - RODRIGO FREITAS CIRICO",
    "KIM MAGAZINE LTDA",
    "LOJAS MIUK LTDA",
    "MOVIDOS MODA FASHION LTDA",
    "NET CONECT CABOS E ACESSORIOS LTDA",
    "NEW EXPRESS BN LTDA.",
    "NOVALINK MT COMERCIAL LTDA",
    "PREST SERVI APOIO AO E-COMMERCE LTDA",
    "QR PHONE ASSISTENCIA TECNICA LTDA",
    "RESENSERV-RESENDE SERVICOS LTDA",
    "RF TRANSPORTES LTDA",
    "RIVILOG LTDA",
    "ROHNES TRANSPORTE E LOGISTICA EIRELI",
    "TEC SERVICE TRANSPORTES LTDA",
    "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA",
    "WF FINGER TRANSPORTE E LOGISTICA LTDA"
]

tipos_veiculos = ["Carro HR", "Fiorino", "Moto", "Caminhão", "Ajudante", "VUC"]
operacoes = ["TIKTOK", "SHEIN - D2D"]
arquivo_excel = "registros.xlsx"

tab1, tab2 = st.tabs(["Registro", "Relatório"])

# ---------------- Aba Registro ----------------
with tab1:
    st.header("📌 Registro de Veículos")

    # Se for transportadora, trava a razão social
    if razao_permitida != "TODOS":
        razao_social = razao_permitida
        st.info(f"🔒 Você só pode registrar para: **{razao_social}**")
    else:
        razao_social = st.selectbox("Razão Social", razoes_sociais)

    ano = st.number_input("Ano", min_value=2000, max_value=2100, step=1)
    quinzena = st.selectbox("Quinzena", ["1ª Quinzena", "2ª Quinzena"])
    mes = st.selectbox("Mês", [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ])
    operacao = st.selectbox("Operação", operacoes)

    # Veículos fixos com campo de quantidade ao lado
    veiculos_fixos = tipos_veiculos
    quantidades = {}

    st.subheader("Quantidade de Veículos")
    for veiculo in veiculos_fixos:
        col1, col2 = st.columns([3, 1])
        col1.write(veiculo)
        quantidades[veiculo] = col2.number_input(
            f"Qtd {veiculo}", min_value=0, step=1, key=f"{veiculo}_qtd"
        )

    observacoes = st.text_area("Observações (opcional)")

    if st.button("Registrar"):
        registros = []
        for veiculo, quantidade in quantidades.items():
            if quantidade > 0:  # só registra se quantidade > 0
                registros.append({
                    "Razão Social": razao_social,
                    "Ano": ano,
                    "Quinzena": quinzena,
                    "Mês": mes,
                    "Operação": operacao,
                    "Tipo de Veículo": veiculo,
                    "Quantidade": quantidade,
                    "Observações": observacoes,
                    "Data de Registro": datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # data automática
                })

        if registros:
            df_novo = pd.DataFrame(registros)

            if os.path.exists(arquivo_excel):
                df_existente = pd.read_excel(arquivo_excel)
                df_final = pd.concat([df_existente, df_novo], ignore_index=True)
            else:
                df_final = df_novo

            df_final.to_excel(arquivo_excel, index=False)

            st.success("✅ Registro(s) salvo(s) com sucesso!")
            st.dataframe(df_novo)
        else:
            st.warning("⚠️ Nenhuma quantidade informada para registrar.")

# ---------------- Aba Relatório ----------------
with tab2:
    st.header("📊 Relatório e Exportação")

    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)

        # Se não for admin, filtra automaticamente
        if razao_permitida != "TODOS":
            df = df[df["Razão Social"] == razao_permitida]

        # Admin pode filtrar manualmente
        if razao_permitida == "TODOS":
            filtro_razao = st.selectbox("Filtrar por Razão Social", ["Todas"] + razoes_sociais)
            if filtro_razao != "Todas":
                df = df[df["Razão Social"] == filtro_razao]

        filtro_quinzena = st.selectbox("Filtrar por Quinzena", ["Todas", "1ª Quinzena", "2ª Quinzena"])
        filtro_mes = st.selectbox("Filtrar por Mês", ["Todos",
                                                      "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])

        if filtro_quinzena != "Todas":
            df = df[df["Quinzena"] == filtro_quinzena]
        if filtro_mes != "Todos":
            df = df[df["Mês"] == filtro_mes]

        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Relatório")
        processed_data = output.getvalue()

        st.download_button(
            label="📥 Exportar Excel",
            data=processed_data,
            file_name="relatorio_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ Nenhum registro encontrado. Comece adicionando registros na aba Registro.")













