import streamlit as st
import pandas as pd
import os

st.title("📋Registro de Carros Dedicados")

# Lista de Razões Sociais
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

# Lista de Tipos de Veículo
tipos_veiculos = ["Carro HR", "Fiorino", "Moto", "Caminhão", "Ajudante", "VUC"]

# Lista de Operações
operacoes = ["TIKTOK", "SHEIN - D2D"]

# Caminho do arquivo Excel
arquivo_excel = "registros.xlsx"

# Criando abas
tab1, tab2 = st.tabs(["Registro", "Relatório"])

# ---------------- Aba Registro ----------------
with tab1:
    st.header("📌 Registro de Veículos")

    razao_social = st.selectbox("Razão Social", razoes_sociais)
    ano = st.number_input("Ano", min_value=2000, max_value=2100, step=1)
    quinzena = st.selectbox("Quinzena", ["1ª Quinzena", "2ª Quinzena"])
    mes = st.selectbox("Mês", [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ])
    operacao = st.selectbox("Operação", operacoes)

    veiculos_selecionados = st.multiselect("Tipo de Veículo", tipos_veiculos)

    # Quantidades dinâmicas
    quantidades = {}
    for veiculo in veiculos_selecionados:
        quantidades[veiculo] = st.number_input(f"Quantidade de {veiculo}", min_value=0, step=1)

    # Botão Registrar
    if st.button("Registrar"):
        registros = []
        for veiculo, quantidade in quantidades.items():
            registros.append({
                "Razão Social": razao_social,
                "Ano": ano,
                "Quinzena": quinzena,
                "Mês": mes,
                "Operação": operacao,
                "Tipo de Veículo": veiculo,
                "Quantidade": quantidade
            })

        df_novo = pd.DataFrame(registros)

        # Salvar no Excel
        if os.path.exists(arquivo_excel):
            df_existente = pd.read_excel(arquivo_excel)
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        else:
            df_final = df_novo

        df_final.to_excel(arquivo_excel, index=False)

        st.success("✅ Registro(s) salvo(s) com sucesso!")
        st.dataframe(df_novo)

import io

# ---------------- Aba Relatório ----------------
with tab2:
    st.header("📊 Relatório e Exportação")

    if os.path.exists(arquivo_excel):
        df = pd.read_excel(arquivo_excel)

        # Filtros
        filtro_razao = st.selectbox("Filtrar por Razão Social", ["Todas"] + razoes_sociais)
        filtro_quinzena = st.selectbox("Filtrar por Quinzena", ["Todas", "1ª Quinzena", "2ª Quinzena"])
        filtro_mes = st.selectbox("Filtrar por Mês", ["Todos",
                                                      "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])

        df_filtrado = df.copy()

        if filtro_razao != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Razão Social"] == filtro_razao]
        if filtro_quinzena != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Quinzena"] == filtro_quinzena]
        if filtro_mes != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Mês"] == filtro_mes]

        st.dataframe(df_filtrado)

        # Botão de download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name="Relatório")
        processed_data = output.getvalue()

        st.download_button(
            label="📥 Exportar Excel",
            data=processed_data,
            file_name="relatorio_filtrado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ Nenhum registro encontrado. Comece adicionando registros na aba Registro.")









