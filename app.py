import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
    "leticia.lima": {"senha": "LL2025!", "razao": "TODOS"},
    "daniela.conceicao": {"senha": "DC2025!", "razao": "TODOS"},
    "paula.lacerda": {"senha": "PL2025!", "razao": "TODOS"},
    "guilherme.barbosa": {"senha": "GB2025!", "razao": "TODOS"},
    "rafael.reis": {"senha": "RR2025!", "razao": "TODOS"},
    "paula.soares": {"senha": "PS2025!", "razao": "TODOS"},
    "SRM2404167": {"senha": "bcNL6gY37UAKBG62", "razao": "WF FINGER TRANSPORTE E LOGISTICA LTDA"}
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
    "2AR TRANSPORTES LTDA","ACC SILVA MINIMERCADO","ARMARINHOS MEGA VARIEDADES LTDA",
    "ATHLANTA LOGISTICA LTDA","CESTLAVIE LTDA","CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA",
    "DONALDO TRANSPORTES E LOGISTICA LTDA","DUDU BABY LTDA","EASY CARGO SOLUCOES",
    "ETTORE BABY COMERCIO DE CONFECCOES LTDA","EVZEN LOGISTICA LTDA","FORTH TRANSPORTES LTDA",
    "GABRIATO EMPORIO LTDA","GETLOG TRANSPORTES LTDA","GREEN LOG SERVICOS LOGISTICOS SUSTENTAVEIS E COMERCIO DE SUPRIMENTOS LTDA",
    "GOOD ASSESSORIA POSTAL EMBALAGENS E LOGISTICA LTDA","HBK COMERCIO E ENVIOS DE ENCOMENDAS LTDA",
    "H&L EXPRESSO LTDA","IMILE - ANDRE LUIZ DE SOUZA","IMILE - EMERSON DE SOUZA VELOSO",
    "IMILE - GABRIELLA JOVINA MONTEIRO","IMILE - JOAO VICTOR CONCEICAO LOPES",
    "IMILE - RODRIGO FREITAS CIRICO","KIM MAGAZINE LTDA","LOJAS MIUK LTDA",
    "MOVIDOS MODA FASHION LTDA","NET CONECT CABOS E ACESSORIOS LTDA","NEW EXPRESS BN LTDA.",
    "NOVALINK MT COMERCIAL LTDA","PREST SERVI APOIO AO E-COMMERCE LTDA","QR PHONE ASSISTENCIA TECNICA LTDA",
    "RESENSERV-RESENDE SERVICOS LTDA","RF TRANSPORTES LTDA","RIVILOG LTDA",
    "ROHNES TRANSPORTE E LOGISTICA EIRELI","TEC SERVICE TRANSPORTES LTDA",
    "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA","WF FINGER TRANSPORTE E LOGISTICA LTDA"
]

tipos_veiculos = ["FIORINO", "VAN", "VUC", "CARRO UTILITARIO", "AJUDANTE", "MOTO"]
operacoes = ["TIKTOK", "BENNET JEANS", "SHEIN", "NUVEMSHOP"]

# ---------------- CONFIGURAÇÃO DAS ABAS ----------------
usuarios_aprovacao_somente = {
    "leticia.lima", "daniela.conceicao", "paula.lacerda", "guilherme.barbosa",
    "rafael.reis", "paula.soares",
}

if usuario_logado in usuarios_aprovacao_somente:
    abas = ["Aprovacao", "Relatorio"]
elif razao_permitida == "TODOS":
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao", "Aprovacao"]
else:
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao"]

abas_objs = st.tabs(abas)
tab_dict = {nome: abas_objs[i] for i, nome in enumerate(abas)}

# ---------------- Helpers Supabase ----------------
def registros_existem_para(razao, data_oficial):
    """Retorna True/False e lista de registros existentes (tenta colunas maiúsculas e camelcase)."""
    # Tenta consulta nas duas possíveis convenções de colunas
    try:
        res = supabase.table("registro_veiculos_calendario").select("*")\
            .eq("RAZAO_SOCIAL", razao).eq("DATA_OFICIAL", data_oficial).execute()
        if res.data:
            return True, res.data
    except Exception:
        pass
    try:
        res2 = supabase.table("registro_veiculos_calendario").select("*")\
            .eq("Razao_Social", razao).eq("Data_Oficial", data_oficial).execute()
        if res2.data:
            return True, res2.data
    except Exception:
        pass
    return False, []

def inserir_registro_linhas(razao, data_oficial, quantidades_dict, operacao, usuario):
    """Insere uma linha por modalidade (MODALIDADE) com QUANTIDADE correspondente.
       Colunas em maiúsculo conforme solicitado. Define STATUS='Pendente' por padrão."""
    data_de_registro = datetime.now().isoformat()
    inserir = []
    for modalidade, qtd in quantidades_dict.items():
        # Se qtd == 0 pulamos para evitar linhas vazias (alterável)
        if qtd is None:
            qtd = 0
        inserir.append({
            "RAZAO_SOCIAL": razao,
            "DATA_OFICIAL": data_oficial,
            "DATA_DE_REGISTRO": data_de_registro,
            "QUANTIDADE": int(qtd),
            "MODALIDADE": modalidade,
            "OPERACAO": operacao,
            "APROVADOR": None,
            "DATA_DA_APROVACAO": None,
            "STATUS": "Pendente",
            "MOTIVO_REJEICAO": None,
            "USUARIO_REGISTRANTE": usuario
        })
    # Inserção em lote
    supabase.table("registro_veiculos_calendario").insert(inserir).execute()

# ---------------- ABA REGISTRO ----------------
if "Registro" in tab_dict:
    with tab_dict["Registro"]:
        st.title("📅 CALENDÁRIO")

        # ---------- Estado inicial do calendário e do formulário ----------
        hoje = datetime.now()
        # Inicializa ano/mes do calendário (chaves únicas e constantes)
        if "cal_ano" not in st.session_state:
            st.session_state["cal_ano"] = max(2025, min(hoje.year, 2030))
        if "cal_mes" not in st.session_state:
            st.session_state["cal_mes"] = hoje.month

        if "data_selecionada" not in st.session_state:
            st.session_state["data_selecionada"] = None
        if "form_aberto" not in st.session_state:
            st.session_state["form_aberto"] = False

        # ---------- Cabeçalho com navegação de mês ----------
        col_left, col_center, col_right = st.columns([1, 6, 1])
        with col_left:
            if st.button("⬅️", key="btn_prev_month"):
                # volta um mês dentro do intervalo 2025-2030
                ano = st.session_state["cal_ano"]
                mes = st.session_state["cal_mes"]
                prev = (datetime(ano, mes, 1) - timedelta(days=1))
                if 2025 <= prev.year <= 2030:
                    st.session_state["cal_ano"] = prev.year
                    st.session_state["cal_mes"] = prev.month
        with col_center:
            mes_nome = datetime(st.session_state["cal_ano"], st.session_state["cal_mes"], 1).strftime("%B %Y")
            st.markdown(f"### {mes_nome}")
        with col_right:
            if st.button("➡️", key="btn_next_month"):
                ano = st.session_state["cal_ano"]
                mes = st.session_state["cal_mes"]
                # avança ao próximo mês (maneira segura)
                next_month = (datetime(ano, mes, 28) + timedelta(days=4)).replace(day=1)
                if 2025 <= next_month.year <= 2030:
                    st.session_state["cal_ano"] = next_month.year
                    st.session_state["cal_mes"] = next_month.month

        # ---------- Geração dos dias do mês ----------
        ano_atual = st.session_state["cal_ano"]
        mes_atual = st.session_state["cal_mes"]
        primeiro_dia = datetime(ano_atual, mes_atual, 1)
        # calcula último dia do mês
        if mes_atual == 12:
            ultimo_dia = datetime(ano_atual, 12, 31)
        else:
            ultimo_dia = datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
        dias_mes = pd.date_range(primeiro_dia, ultimo_dia)

        # ---------- Cabeçalho dias da semana ----------
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        cols = st.columns(7)
        for i, dia in enumerate(dias_semana):
            cols[i].markdown(f"**{dia}**", unsafe_allow_html=True)

        # ---------- Monta calendário em linhas de 7 ----------
        calendario = []
        linha = []
        primeira_semana_vazia = (primeiro_dia.weekday() + 1) % 7
        for _ in range(primeira_semana_vazia):
            linha.append(" ")
        for dia in dias_mes:
            linha.append(f"{dia.day:02d}")
            if len(linha) == 7:
                calendario.append(linha)
                linha = []
        if linha:
            while len(linha) < 7:
                linha.append(" ")
            calendario.append(linha)

        # ---------- Exibe o calendário (botoes) ----------
        for semana in calendario:
            cols = st.columns(7)
            for i, dia_label in enumerate(semana):
                if dia_label.strip() == "":
                    cols[i].write(" ")
                    continue
                dia_int = int(dia_label)
                dia_str = f"{ano_atual}-{mes_atual:02d}-{dia_int:02d}"

                # Consulta registros existentes para a data
                try:
                    res = supabase.table("registro_veiculos_calendario").select(
                        "STATUS, MODALIDADE, QUANTIDADE, OPERACAO") \
                        .eq("RAZAO_SOCIAL", razao_permitida).eq("DATA_OFICIAL", dia_str).execute()
                    registros_existentes = res.data or []
                except Exception:
                    registros_existentes = []

                # Determina status e símbolo
                is_blocked = False
                symbol = ""
                if registros_existentes:
                    # Se todos registros rejeitados, desbloqueia para correção
                    todos_rejeitados = all(
                        (r.get("STATUS") or r.get("Status") or "").lower() == "rejeitado"
                        for r in registros_existentes
                    )
                    if todos_rejeitados:
                        is_blocked = False  # desbloqueado
                        symbol = "❌"
                    else:
                        is_blocked = True  # bloqueia datas com registro aprovado ou pendente
                        # prioriza exibir pendente se houver algum pendente
                        status_val = [r.get("STATUS") or r.get("Status") for r in registros_existentes if
                                      r.get("STATUS") or r.get("Status")]
                        if any(s.lower() == "pendente" for s in status_val):
                            symbol = "⏳"
                        else:
                            symbol = "✅"

                # Botão do dia
                if cols[i].button(f"{symbol} {dia_label}", disabled=is_blocked and symbol != "❌", key=f"btn_{dia_str}"):
                    # Se desbloqueado ou rejeitado, abre formulário para ajustes
                    st.session_state["data_selecionada"] = dia_str
                    st.session_state["form_aberto"] = True

                    if registros_existentes and symbol != "❌":
                        # mostra prévia se não desbloqueado (aprovado ou pendente)
                        st.subheader(f"📄 Registro(s) de {dia_str}")
                        for reg in registros_existentes:
                            st.markdown(
                                f"- **Veículo:** {reg.get('MODALIDADE', '—')}, **Qtd:** {reg.get('QUANTIDADE', '—')}, "
                                f"**Operação:** {reg.get('OPERACAO', '—')}, **Status:** {reg.get('STATUS', '—')}"
                            )
        # ---------- Formulário persistente (não fecha ao interagir) ----------
        if st.session_state.get("form_aberto") and st.session_state.get("data_selecionada"):
            dia_str = st.session_state["data_selecionada"]
            st.divider()
            st.subheader(f"📝 Registrar uso de veículos — {dia_str}")

            col1, col2 = st.columns(2)
            if razao_permitida != "TODOS":
                col1.info(f"🔒 Razão Social: **{razao_permitida}**")
                razao_social = razao_permitida
            else:
                razao_social = col1.selectbox("Razão Social", razoes_sociais, key=f"razao_{dia_str}")
            operacao = col2.selectbox("Operação", ["TIKTOK", "BENNET JEANS", "SHEIN", "NUVEM SHOP"], key=f"oper_{dia_str}")

            # Quantidade de veículos
            st.markdown("**Quantidade de Veículos**")
            tipos_veiculos = ["FIORINO", "VAN", "VUC", "CARRO UTILITÁRIO", "AJUDANTE", "MOTO"]
            quantidades = {}
            for i in range(0, len(tipos_veiculos), 3):
                cols_q = st.columns(3)
                for j, veiculo in enumerate(tipos_veiculos[i:i + 3]):
                    quantidades[veiculo] = cols_q[j].number_input(
                        veiculo, min_value=0, step=1, key=f"{veiculo}_{dia_str}"
                    )

            observacoes = st.text_area("Observações (opcional)", key=f"obs_{dia_str}")

            if st.button("Registrar", key=f"submeter_{dia_str}"):
                # Insere somente modalidades com quantidade > 0
                for veiculo, qtd in quantidades.items():
                    if qtd and qtd > 0:
                        registro = {
                            "RAZAO_SOCIAL": razao_social,
                            "DATA_OFICIAL": dia_str,
                            "DATA_DE_REGISTRO": datetime.now().strftime("%d/%m/%Y"),
                            "MODALIDADE": veiculo,
                            "QUANTIDADE": int(qtd),
                            "OPERACAO": operacao,
                            "STATUS": "Pendente",
                            "APROVADOR": None,
                            "DATA_DA_APROVACAO": None,
                            "MOTIVO_REJEICAO": "",
                            "OBSERVACOES": observacoes,
                            "USUARIO_REGISTRANTE": usuario_logado
                        }
                        supabase.table("registro_veiculos_calendario").insert(registro).execute()

                st.success(f"✅ Registro de {dia_str} submetido com sucesso!")
                # fecha o form mantendo mês/ano
                st.session_state["form_aberto"] = False
                st.session_state["data_selecionada"] = None
                # não forçamos rerun imediato — deixar usuário continuar no mesmo mês

# ---------------- ABA RELATÓRIO ----------------
if "Relatorio" in tab_dict:
    with tab_dict["Relatorio"]:
        st.title("📊 Relatório de Registros")

        # ---------- Filtro por período ----------
        st.markdown("**Selecione o período desejado:**")
        hoje = datetime.now()
        default_start = hoje.replace(day=1)
        default_end = hoje.replace(day=15)  # Sugestão: primeira quinzena do mês
        periodo = st.date_input(
            "Período",
            value=(default_start, default_end),
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2030, 12, 31),
            help="Selecione a data inicial e final do período"
        )

        if isinstance(periodo, tuple) and len(periodo) == 2:
            data_inicio, data_fim = periodo
            if data_inicio > data_fim:
                st.error("❌ A data inicial não pode ser maior que a final.")
            else:
                # ---------- Consulta Supabase ----------
                query = supabase.table("registro_veiculos_calendario").select("*")
                # Filtra por razão social do usuário, se não for TODOS
                if razao_permitida != "TODOS":
                    query = query.eq("RAZAO_SOCIAL", razao_permitida)
                # Filtra pelo período selecionado (DATA_OFICIAL)
                query = query.gte("DATA_OFICIAL", data_inicio.isoformat()) \
                             .lte("DATA_OFICIAL", data_fim.isoformat())
                query = query.eq("STATUS", "Aprovado")

                try:
                    res = query.execute()
                    registros = res.data
                except Exception:
                    registros = []

                if registros:
                    df = pd.DataFrame(registros)
                    st.success(f"✅ {len(df)} registros encontrados!")
                    st.dataframe(df)

                    # ---------- Download do Excel ----------
                    import io  # colocar no topo do script junto com outros imports


                    # ---------- Download do Excel ----------
                    @st.cache_data
                    def convert_df_to_excel(df):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False)
                        processed_data = output.getvalue()
                        return processed_data


                    excel_bytes = convert_df_to_excel(df)
                    st.download_button(
                        label="⬇️ Baixar relatório em Excel",
                        data=excel_bytes,
                        file_name=f"relatorio_{data_inicio}_{data_fim}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# ---------------- ABA FLUXO DE APROVACAO ----------------
if "Fluxo de Aprovacao" in tab_dict:
    with tab_dict["Fluxo de Aprovacao"]:
        st.title("📋 Fluxo de Registros")

        # Filtros
        st.markdown("**Filtrar por período e status:**")
        hoje = datetime.now()
        periodo = st.date_input(
            "Período",
            value=(hoje.replace(day=1), hoje),
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2030, 12, 31)
        )
        data_inicio, data_fim = periodo

        status_filtro = st.selectbox("Status", ["Todos", "Pendente", "Aprovado", "Rejeitado"])

        query = supabase.table("registro_veiculos_calendario").select("*") \
                        .gte("DATA_OFICIAL", data_inicio.isoformat()) \
                        .lte("DATA_OFICIAL", data_fim.isoformat())
        if razao_permitida != "TODOS":
            query = query.eq("RAZAO_SOCIAL", razao_permitida)
        if status_filtro != "Todos":
            query = query.eq("STATUS", status_filtro)
        registros = query.execute().data or []

        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df)
        else:
            st.info("ℹ️ Nenhum registro encontrado para o filtro selecionado")

# ---------------- ABA APROVACAO ----------------
if "Aprovacao" in tab_dict:
    if usuario_logado in usuarios_aprovacao_somente:
        with tab_dict["Aprovacao"]:
            st.title("🛠 Aprovação de Registros")

            # Filtro de período
            hoje = datetime.now()
            periodo = st.date_input(
                "Período",
                value=(hoje.replace(day=1), hoje),
                min_value=datetime(2025, 1, 1),
                max_value=datetime(2030, 12, 31)
            )
            data_inicio, data_fim = periodo

            # Consulta registros pendentes
            query = supabase.table("registro_veiculos_calendario").select("*") \
                .eq("STATUS", "Pendente") \
                .gte("DATA_OFICIAL", data_inicio.isoformat()) \
                .lte("DATA_OFICIAL", data_fim.isoformat())
            registros = query.execute().data or []

            if registros:
                st.success(f"✅ {len(registros)} registros pendentes")
                for i, registro in enumerate(registros):
                    with st.expander(
                            f"{registro['RAZAO_SOCIAL']} - {registro['DATA_OFICIAL']} - {registro['MODALIDADE']}"):
                        st.markdown(f"**Operação:** {registro['OPERACAO']}")
                        st.markdown(f"**Quantidade:** {registro['QUANTIDADE']}")
                        st.markdown(f"**Usuário Registrante:** {registro.get('USUARIO_REGISTRANTE', '—')}")
                        obs = registro.get("OBSERVACOES") or registro.get("Observacoes")
                        if obs:
                            st.markdown(f"**Observações:** {obs}")

                        # Aprovar / Rejeitar
                        col1, col2, col3 = st.columns([1, 1, 3])
                        aprovar, rejeitar, motivo_rejeicao = False, False, None
                        with col1:
                            aprovar = st.button("✅ Aprovar", key=f"aprovar_{i}")
                        with col2:
                            rejeitar = st.button("❌ Rejeitar", key=f"rejeitar_{i}")
                        if rejeitar:
                            # Atualiza imediatamente o STATUS para Rejeitado
                            supabase.table("registro_veiculos_calendario").update({
                                "STATUS": "Rejeitado",
                                "APROVADOR": usuario_logado,
                                "DATA_DA_APROVACAO": None
                            }).eq("id", registro["id"]).execute()
                            st.success("❌ Registro marcado como rejeitado (pendente de motivo)")

                            # Agora permite inserir/editar motivo
                            motivo_rejeicao = st.text_area("Motivo da rejeição", key=f"motivo_{i}",
                                                           value=registro.get("MOTIVO_REJEICAO") or "")
                            if st.button("Registrar/Atualizar Rejeição", key=f"registrar_rej_{i}"):
                                supabase.table("registro_veiculos_calendario").update({
                                    "MOTIVO_REJEICAO": motivo_rejeicao
                                }).eq("id", registro["id"]).execute()
                                st.success("✅ Motivo da rejeição registrado!")
                                st.experimental_rerun()
                        if aprovar:
                            supabase.table("registro_veiculos_calendario").update({
                                "STATUS": "Aprovado",
                                "APROVADOR": usuario_logado,
                                "DATA_DA_APROVACAO": datetime.now().isoformat(),
                                "MOTIVO_REJEICAO": None
                            }).eq("id", registro["id"]).execute()

                            # Remove o registro da lista local para sumir imediatamente
                            registros.pop(i)
                            st.success("✅ Registro aprovado!")
            else:
                st.info("ℹ️ Nenhum registro pendente encontrado")
    else:
        with tab_dict["Aprovacao"]:
            st.warning("⚠️ Você não tem permissão para acessar esta aba")































































































