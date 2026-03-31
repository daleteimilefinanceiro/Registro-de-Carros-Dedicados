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
import streamlit as st
from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ---------------- CONFIGURAÇÃO DE LOGIN ----------------
usuarios = {
    "financeadm": {"senha": "Dcschv2020@", "razao": "TODOS"},
    "SRM2500123": {"senha": "ba7V1sK1fzYAgIGy", "razao": "2AR TRANSPORTES LTDA"},
    "SRM2503544": {"senha": "eHjjfGrWHyMayCxI", "razao": "LT WAY TRANSPORTES LTDA"},
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
    "SRM2402510": {"senha": "RF7FyZsnYvgxHqXO", "razao": "CLIPE LOG LOGISTICA E TRANSPORTE DE CARGAS LTDA"},
    "SRM2600051": {"senha": "X3KPe1WVuebuoVFp", "razao": "WJK ENTREGAS RAPIDAS LIMEIRA LTDA"},
    "SRM2402980": {"senha": "w5jCqDC5Osbb72Fc", "razao": "LIMINAR LOG TRANSPORTES E LOGISTICA LTDA"},
    "SRM2301489": {"senha": "PcUKjJ9prl2D8ySn", "razao": "L A ZAMBELLO EIRELI"},
    "SRM2301330": {"senha": "UMmFCMUXzgUeMBIE", "razao": "AST TRANSPORTE EXPRESS"},
    "SRM2503450": {"senha": "zXWsSFRYkCXovT3O", "razao": "LFB TRANSPORTES LTDA"},
    "SRM2503189": {"senha": "VcfIVZkLzGaKGInV", "razao": "ONLINE SOLUCOES E LOGISTICAS LTDA"},
    "SRM2501542": {"senha": "oyNGVBvdWIBghah2", "razao": "AVISTA LOGISTICA EXPRESS LTDA"},
    "SRM2504004": {"senha": "EDISY3PWq0iQiq1Z", "razao": "JUCIMARA QUITERIA RIBEIRO LOPES - TRANSPORTES"},
    "SRM2400717": {"senha": "rXMzaY7AwmGhkukB", "razao": "FLAVIO PEREIRA"},
    "SRM2301691": {"senha": "QfsL4ozXdOrXyF9N", "razao": "DONALDO TRANSPORTES E LOGISTICA LTDA"},
    "SRM2600372": {"senha": "5nfklhZNTC2E4R3y", "razao": "VIEIRA LOPES LOGISTICA LTDA"},
    "michael.liu": {"senha": "ML2026!", "razao": "TODOS"},
    "SRM2302082": {"senha": "oOEezeC5Te6pPAYo", "razao": "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA"},
    "SRM2403127":{"senha":"DM5rWLSDSUSDFEWf","razao":"LMC LOGISTICA E DISTRIBUICAO E ENTREGAS RAPIDAS LTDA"}

# ---------------- FUNÇÕES AUXILIARES ----------------
def verificar_duplicata(razao, data, operacao, cidade):
    """
    Verifica se já existe registro ativo (não rejeitado) para evitar duplicatas.
    Considera: razão social, data, operação E cidade.
    Retorna: (bool: existe_duplicata, list: registros_encontrados)
    """
    try:
        query = supabase.table("registro_veiculos_calendario").select("*") \
            .eq("RAZAO_SOCIAL", razao) \
            .eq("DATA_OFICIAL", data) \
            .eq("OPERACAO", operacao) \
            .eq("CIDADE", cidade) \
            .neq("STATUS", "Rejeitado")
        registros = query.execute().data or []
        return len(registros) > 0, registros
    except Exception as e:
        logger.error(f"Erro ao verificar duplicatas: {e}")
        st.error(f"❌ Erro ao verificar duplicatas: {e}")
        return False, []

def buscar_registros_mes(razao, primeiro_dia, ultimo_dia):
    """
    Busca todos os registros de um mês de uma vez (otimização de performance).
    Retorna um dicionário organizado por data com as operações registradas.
    """
    try:
        query = supabase.table("registro_veiculos_calendario").select("*") \
            .eq("RAZAO_SOCIAL", razao) \
            .gte("DATA_OFICIAL", primeiro_dia.strftime("%Y-%m-%d")) \
            .lte("DATA_OFICIAL", ultimo_dia.strftime("%Y-%m-%d"))
        registros = query.execute().data or []
        
        # Organizar por data e operação para lookup rápido
        registros_por_dia = {}
        for reg in registros:
            data = reg.get("DATA_OFICIAL")
            if data not in registros_por_dia:
                registros_por_dia[data] = []
            registros_por_dia[data].append(reg)
        
        return registros_por_dia
    except Exception as e:
        logger.error(f"Erro ao buscar registros do mês: {e}")
        return {}

def validar_quantidades(quantidades):
    """
    Valida se pelo menos um veículo foi registrado.
    """
    total = sum(q for q in quantidades.values() if q and q > 0)
    if total == 0:
        return False, "⚠️ Registre pelo menos um veículo!"
    return True, ""

def inserir_registros_batch(registros_lista):
    """
    Insere múltiplos registros de uma vez (batch insert).
    """
    try:
        if not registros_lista:
            return False, "Nenhum registro para inserir"
        
        supabase.table("registro_veiculos_calendario").insert(registros_lista).execute()
        return True, f"✅ {len(registros_lista)} registro(s) inserido(s) com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao inserir registros: {e}")
        erro_str = str(e)
        if "duplicate" in erro_str.lower() or "unique" in erro_str.lower():
            return False, "❌ Registro duplicado detectado!"
        else:
            return False, f"❌ Erro ao registrar: {erro_str}"

# ---------------- AUTENTICAÇÃO ----------------
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

st.sidebar.success(f"👤 Usuário: {usuario_logado}\n🏢 Razão: {razao_permitida}")
if st.sidebar.button("🚪 Sair"):
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
    "IMILE - JOAO VICTOR CONCEICAO LOPES",
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
    "NAPORTA TECNOLOGIA LOGISTICA LTDA",
    "TEREZINHA APARECIDA PATEL SERVICOS DE LOGISTICA LTDA",
    "WF FINGER TRANSPORTE E LOGISTICA LTDA",
    "LT WAY TRANSPORTES LTDA",
    "OSEAS PORTO TRANSPORTES LTDA",
    "WJK ENTREGAS RAPIDAS LIMEIRA LTDA",
    "LIMINAR LOG TRANSPORTES E LOGISTICA LTDA",
    "L A ZAMBELLO EIRELI",
    "AST TRANSPORTE EXPRESS",
    "LFB TRANSPORTES LTDA",
    "ONLINE SOLUCOES E LOGISTICAS LTDA",
    "AVISTA LOGISTICA EXPRESS LTDA",
    "JUCIMARA QUITERIA RIBEIRO LOPES - TRANSPORTES",
    "FLAVIO PEREIRA",
    "VIEIRA LOPES LOGISTICA LTDA",
    "LMC LOGISTICA E DISTRIBUICAO E ENTREGAS RAPIDAS LTDA"
    
]

tipos_veiculos = ["FIORINO", "VAN", "VUC", "CARRO UTILITARIO", "AJUDANTE", "MOTO", "3/4"]
operacoes = ["TIKTOK", "BENNET JEANS", "SHEIN", "NUVEMSHOP", "SHOP FOCO","BITHOME","CUBBO","CANIAO","ESTOCA","EXPRESSIO","FM TRANSPORTES","FRENET","KWAI","LADO ROSA","MAGAZORD","MERCADO LIVRE","MEU RODAPÉ","SATELITAL","ZENATUR"]

# NOVO: Lista de cidades
cidades = [
    "CAMPINAS",
    "SUMARÉ",
    "JUNDIAÍ",
    "CAMPO LIMPO PAULISTA",
    "LIMEIRA",
    "PEDREIRA",
    "SÃO JOSE DOS CAMPOS",
    "GARÇA",
    "VOTORANTIM",
    "AMERICANA",
    "RIBEIRÃO PRETO",
    "SÃO JOSE DO RIO PRETO",
    "MATÃO",
    "SOROCABA",
    "ATIBAIA",
    "EXTREMA",
    "NOVA SERRANA",
    "SÃO PAULO",
    "PALHOÇA",
    "SANTA CATARINA",
    "CURITIBA",
    "RIO DE JANEIRO",
    "PETRÓPOLIS",
    "ARARAQUARA",
    "ARAÇATUBA",
    "DIADEMA",
    "VOTUPORANGA",
    "DOIS CORREGOS",
    "PORTO FELIZ",
    "MOGI MIRIM",
    "MOGI GUAÇU",
    "BEBEDOURO",
    "POA",
    "GUARATINGUETA",
    "CAÇAPAVA",
    "TAUBATÉ",
    "TREMEMBÉ",
    "PINDAMONHANGABA",
    "ROSEIRA",
    "APARECIDA",
    "BRUSQUE",
    "ITAJAÍ",
    "ITAPEMA",
    "BALNEÁRIO CAMBORIÚ",
    "CAMBORIÚ",
    "NAVEGANTES",
    "PORTO BELO",
    "BALNEÁRIO PICARRAS",
    "GUABIRUBA",
    "BLUMENAU",
    "INDAIAL",
    "TIMBÓ",
    "POMERODE",
    "BENEDITO NOVO",
    "DOUTOR PEDRINHO",
    "GASPAR",
    "ILHOTA",
    "MARÍLIA",
    "SÃO CARLOS",
    "CATANDUVA",
    "URUPES",
    "SANTOS",
    "MIRASSOL",
    "JAU",
    "PIRACICABA",
    "AURIFLAMA",
    "DUQUE DE CAXIAS",
    "GOIÂNIA",
    "APARECIDA DE GOIÂNIA"

]

# ---------------- CONFIGURAÇÃO DAS ABAS ----------------
usuarios_aprovacao_somente = {
    "leticia.lima", "river.zhou", "isabel.liu", 
    "lijun.zeng", "rafael.reis", "paula.soares",
}
usuarios_relatorio_somente = {
    "michael.liu"
}

if usuario_logado in usuarios_aprovacao_somente:
    abas = ["Aprovacao", "Relatorio"]
elif usuario_logado in usuarios_relatorio_somente:
    abas = ["Relatorio", "Fluxo de Aprovacao"]
elif razao_permitida == "TODOS":
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao", "Aprovacao"]
else:
    abas = ["Registro", "Relatorio", "Fluxo de Aprovacao"]
abas_objs = st.tabs(abas)
tab_dict = {nome: abas_objs[i] for i, nome in enumerate(abas)}

# ---------------- ABA REGISTRO ----------------
if "Registro" in tab_dict:
    with tab_dict["Registro"]:
        st.title("📅 CALENDÁRIO DE REGISTROS")
        
        # Estado inicial do calendário
        hoje = datetime.now()
        if "cal_ano" not in st.session_state:
            st.session_state["cal_ano"] = max(2025, min(hoje.year, 2030))
        if "cal_mes" not in st.session_state:
            st.session_state["cal_mes"] = hoje.month
        if "data_selecionada" not in st.session_state:
            st.session_state["data_selecionada"] = None
        if "form_aberto" not in st.session_state:
            st.session_state["form_aberto"] = False
        
        # Cabeçalho com navegação de mês
        col_left, col_center, col_right = st.columns([1, 6, 1])
        
        with col_left:
            if st.button("◀️ Anterior", key="btn_prev_month"):
                ano = st.session_state["cal_ano"]
                mes = st.session_state["cal_mes"]
                prev = (datetime(ano, mes, 1) - timedelta(days=1))
                if 2025 <= prev.year <= 2030:
                    st.session_state["cal_ano"] = prev.year
                    st.session_state["cal_mes"] = prev.month
                    st.rerun()
        
        with col_center:
            mes_nome = datetime(st.session_state["cal_ano"], st.session_state["cal_mes"], 1).strftime("%B %Y")
            st.markdown(f"### {mes_nome.upper()}")
        
        with col_right:
            if st.button("Próximo ▶️", key="btn_next_month"):
                ano = st.session_state["cal_ano"]
                mes = st.session_state["cal_mes"]
                next_month = (datetime(ano, mes, 28) + timedelta(days=4)).replace(day=1)
                if 2025 <= next_month.year <= 2030:
                    st.session_state["cal_ano"] = next_month.year
                    st.session_state["cal_mes"] = next_month.month
                    st.rerun()
        
        # Geração dos dias do mês
        ano_atual = st.session_state["cal_ano"]
        mes_atual = st.session_state["cal_mes"]
        primeiro_dia = datetime(ano_atual, mes_atual, 1)
        
        if mes_atual == 12:
            ultimo_dia = datetime(ano_atual, 12, 31)
        else:
            ultimo_dia = datetime(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
        
        dias_mes = pd.date_range(primeiro_dia, ultimo_dia)
        
        # OTIMIZAÇÃO: Buscar todos registros do mês de uma vez
        if razao_permitida != "TODOS":
            registros_mes = buscar_registros_mes(razao_permitida, primeiro_dia, ultimo_dia)
        else:
            registros_mes = {}
        
        # Cabeçalho dias da semana
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        cols = st.columns(7)
        for i, dia in enumerate(dias_semana):
            cols[i].markdown(f"**{dia}**")
        
        # Monta calendário em linhas de 7
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
        
        # Exibe o calendário
        for semana in calendario:
            cols = st.columns(7)
            for i, dia_label in enumerate(semana):
                if dia_label.strip() == "":
                    cols[i].write(" ")
                    continue
                
                dia_int = int(dia_label)
                dia_str = f"{ano_atual}-{mes_atual:02d}-{dia_int:02d}"
                
                # OTIMIZAÇÃO: Lookup direto no dicionário
                registros_existentes = registros_mes.get(dia_str, [])
                
                # Determina status e símbolo
                symbol = ""
                if registros_existentes:
                    registros_ativos = [r for r in registros_existentes 
                                      if (r.get("STATUS") or "").lower() != "rejeitado"]
                    if registros_ativos:
                        status_val = [r.get("STATUS") for r in registros_ativos if r.get("STATUS")]
                        if any(s.lower() == "pendente" for s in status_val):
                            symbol = "⏳"
                        else:
                            symbol = "✅"
                    else:
                        symbol = "❌"
                
                # Botão do dia - NUNCA desabilitado
                if cols[i].button(f"{symbol} {dia_label}", key=f"btn_{dia_str}"):
                    st.session_state["data_selecionada"] = dia_str
                    st.session_state["form_aberto"] = True
                    if "operacao_selecionada" in st.session_state:
                        del st.session_state["operacao_selecionada"]
        
        # Formulário de registro
        if st.session_state.get("form_aberto") and st.session_state.get("data_selecionada"):
            dia_str = st.session_state["data_selecionada"]
            st.divider()
            st.subheader(f"📝 Registrar veículos — {dia_str}")
            
            col1, col2, col3 = st.columns(3)
            
            if razao_permitida != "TODOS":
                col1.info(f"🏢 Razão Social: **{razao_permitida}**")
                razao_social = razao_permitida
            else:
                razao_social = col1.selectbox("Razão Social", razoes_sociais, key=f"razao_{dia_str}")
            
            operacao = col2.selectbox("Operação", operacoes, key=f"oper_{dia_str}")
            
            # NOVO: Campo de Cidade
            cidade = col3.selectbox("🏙️ Cidade", cidades, key=f"cidade_{dia_str}")
            
            # VERIFICAÇÃO DE DUPLICATA
            tem_duplicata, registros_dup = verificar_duplicata(razao_social, dia_str, operacao, cidade)
            
            if tem_duplicata:
                st.warning(f"⚠️ Já existe registro **{operacao}** para **{cidade}** nesta data:")
                with st.expander("👁️ Ver registros existentes"):
                    for reg in registros_dup:
                        status_emoji = {"Pendente": "⏳", "Aprovado": "✅", "Rejeitado": "❌"}.get(reg.get("STATUS"), "")
                        cidade_reg = reg.get('CIDADE', '—')
                        st.markdown(
                            f"{status_emoji} **{reg.get('MODALIDADE')}**: {reg.get('QUANTIDADE')} unidades - Cidade: {cidade_reg} - Status: {reg.get('STATUS')}")
                st.info("💡 Selecione outra operação/cidade ou solicite a rejeição do registro existente.")
                st.stop()
            
            # Quantidade de veículos
            st.markdown("**Quantidade de Veículos**")
            quantidades = {}
            for i in range(0, len(tipos_veiculos), 3):
                cols_q = st.columns(3)
                for j, veiculo in enumerate(tipos_veiculos[i:i + 3]):
                    quantidades[veiculo] = cols_q[j].number_input(
                        veiculo, min_value=0, step=1, key=f"{veiculo}_{dia_str}_{operacao}"
                    )
            
            observacoes = st.text_area("📋 Observações (opcional)", key=f"obs_{dia_str}_{operacao}")
            
            if st.button("✅ Registrar", key=f"submeter_{dia_str}_{operacao}"):
                # Validar quantidades
                valido, msg_erro = validar_quantidades(quantidades)
                if not valido:
                    st.error(msg_erro)
                    st.stop()
                
                # Preparar registros
                registros_para_inserir = []
                data_registro = datetime.now().isoformat()
                
                for veiculo, qtd in quantidades.items():
                    if qtd and qtd > 0:
                        registros_para_inserir.append({
                            "RAZAO_SOCIAL": razao_social,
                            "DATA_OFICIAL": dia_str,
                            "DATA_DE_REGISTRO": data_registro,
                            "MODALIDADE": veiculo,
                            "QUANTIDADE": int(qtd),
                            "OPERACAO": operacao,
                            "CIDADE": cidade,  # NOVO CAMPO
                            "STATUS": "Pendente",
                            "APROVADOR": None,
                            "DATA_DA_APROVACAO": None,
                            "MOTIVO_REJEICAO": None,
                            "OBSERVACOES": observacoes,
                            "USUARIO_REGISTRANTE": usuario_logado
                        })
                
                # Inserir em batch
                sucesso, mensagem = inserir_registros_batch(registros_para_inserir)
                
                if sucesso:
                    st.success(mensagem)
                    st.session_state["form_aberto"] = False
                    st.session_state["data_selecionada"] = None
                    st.balloons()
                    st.rerun()
                else:
                    st.error(mensagem)

# ---------------- ABA RELATÓRIO ----------------
if "Relatorio" in tab_dict:
    with tab_dict["Relatorio"]:
        st.title("📊 Relatório de Registros")
        
        st.markdown("**Selecione o período desejado:**")
        hoje = datetime.now()
        default_start = hoje.replace(day=1)
        default_end = hoje
        
        periodo = st.date_input(
            "📅 Período",
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
                query = supabase.table("registro_veiculos_calendario").select("*")
                
                if razao_permitida != "TODOS":
                    query = query.eq("RAZAO_SOCIAL", razao_permitida)
                
                query = query.gte("DATA_OFICIAL", data_inicio.isoformat()) \
                    .lte("DATA_OFICIAL", data_fim.isoformat()) \
                    .eq("STATUS", "Aprovado")
                
                try:
                    res = query.execute()
                    registros = res.data
                except Exception as e:
                    logger.error(f"Erro ao buscar relatório: {e}")
                    st.error(f"❌ Erro ao buscar dados: {e}")
                    registros = []
                
                if registros:
                    df = pd.DataFrame(registros)
                    st.success(f"✅ {len(df)} registros encontrados!")
                    
                    # Métricas resumidas
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("📦 Total de Veículos", df["QUANTIDADE"].sum())
                    col2.metric("🏢 Razões Sociais", df["RAZAO_SOCIAL"].nunique())
                    col3.metric("📅 Dias com Registro", df["DATA_OFICIAL"].nunique())
                    
                    # NOVO: Métrica de cidades (se disponível)
                    if "CIDADE" in df.columns:
                        col4.metric("🏙️ Cidades", df["CIDADE"].nunique())
                    
                    st.dataframe(df, use_container_width=True)
                    
                    @st.cache_data
                    def convert_df_to_excel(dataframe):
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            dataframe.to_excel(writer, index=False, sheet_name='Registros')
                        return output.getvalue()
                    
                    excel_bytes = convert_df_to_excel(df)
                    
                    st.download_button(
                        label="📥 Baixar relatório em Excel",
                        data=excel_bytes,
                        file_name=f"relatorio_{data_inicio}_{data_fim}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.info("ℹ️ Nenhum registro aprovado encontrado para o período selecionado.")

# ---------------- ABA FLUXO DE APROVACAO ----------------
if "Fluxo de Aprovacao" in tab_dict:
    with tab_dict["Fluxo de Aprovacao"]:
        st.title("🔄 Fluxo de Registros")
        
        st.markdown("**Filtrar por período e status:**")
        hoje = datetime.now()
        
        periodo = st.date_input(
            "📅 Período",
            value=(hoje.replace(day=1), hoje),
            min_value=datetime(2025, 1, 1),
            max_value=datetime(2030, 12, 31)
        )
        
        if len(periodo) == 2:
            data_inicio, data_fim = periodo
        else:
            data_inicio = data_fim = periodo[0]
        
        status_filtro = st.selectbox("🔍 Status", ["Todos", "Pendente", "Aprovado", "Rejeitado"])
        
        query = supabase.table("registro_veiculos_calendario").select("*") \
            .gte("DATA_OFICIAL", data_inicio.isoformat()) \
            .lte("DATA_OFICIAL", data_fim.isoformat())
        
        if razao_permitida != "TODOS":
            query = query.eq("RAZAO_SOCIAL", razao_permitida)
        
        if status_filtro != "Todos":
            query = query.eq("STATUS", status_filtro)
        
        try:
            registros = query.execute().data or []
        except Exception as e:
            logger.error(f"Erro ao buscar fluxo: {e}")
            st.error(f"❌ Erro: {e}")
            registros = []
        
        if registros:
            df = pd.DataFrame(registros)
            
            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📋 Total", len(df))
            col2.metric("⏳ Pendentes", len(df[df["STATUS"] == "Pendente"]))
            col3.metric("✅ Aprovados", len(df[df["STATUS"] == "Aprovado"]))
            col4.metric("❌ Rejeitados", len(df[df["STATUS"] == "Rejeitado"]))
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum registro encontrado para o filtro selecionado")

# ---------------- ABA APROVACAO ----------------
if "Aprovacao" in tab_dict:
    if usuario_logado in usuarios_aprovacao_somente or razao_permitida == "TODOS":
        with tab_dict["Aprovacao"]:
            st.title("✅ Aprovação de Registros")
            
            hoje = datetime.now()
            periodo = st.date_input(
                "📅 Período",
                value=(hoje.replace(day=1), hoje),
                min_value=datetime(2025, 1, 1),
                max_value=datetime(2030, 12, 31)
            )
            
            if len(periodo) == 2:
                data_inicio, data_fim = periodo
            else:
                data_inicio = data_fim = periodo[0]
            
            query = supabase.table("registro_veiculos_calendario").select("*") \
                .eq("STATUS", "Pendente") \
                .gte("DATA_OFICIAL", data_inicio.isoformat()) \
                .lte("DATA_OFICIAL", data_fim.isoformat()) \
                .order("DATA_OFICIAL", desc=False)
            
            try:
                registros = query.execute().data or []
            except Exception as e:
                logger.error(f"Erro ao buscar aprovações: {e}")
                st.error(f"❌ Erro: {e}")
                registros = []
            
            if registros:
                st.success(f"⏳ {len(registros)} registros pendentes de aprovação")
                
                for i, registro in enumerate(registros):
                    # NOVO: Adicionar cidade no título do expander (se disponível)
                    cidade_info = f" | {registro.get('CIDADE', '—')}" if registro.get('CIDADE') else ""
                    
                    with st.expander(
                        f"📦 {registro['RAZAO_SOCIAL']} | {registro['DATA_OFICIAL']} | {registro['OPERACAO']}{cidade_info} | {registro['MODALIDADE']} | {registro['QUANTIDADE']} unidades"
                    ):
                        col_info1, col_info2 = st.columns(2)
                        col_info1.markdown(f"**🏢 Razão Social:** {registro['RAZAO_SOCIAL']}")
                        col_info1.markdown(f"**📅 Data:** {registro['DATA_OFICIAL']}")
                        col_info1.markdown(f"**🚗 Modalidade:** {registro['MODALIDADE']}")
                        
                        col_info2.markdown(f"**🔢 Quantidade:** {registro['QUANTIDADE']}")
                        col_info2.markdown(f"**⚙️ Operação:** {registro['OPERACAO']}")
                        
                        # NOVO: Mostrar cidade (se disponível)
                        if registro.get('CIDADE'):
                            col_info2.markdown(f"**🏙️ Cidade:** {registro['CIDADE']}")
                        
                        col_info2.markdown(f"**👤 Registrado por:** {registro.get('USUARIO_REGISTRANTE', '—')}")
                        
                        obs = registro.get("OBSERVACOES")
                        if obs:
                            st.info(f"📋 **Observações:** {obs}")
                        
                        st.divider()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✅ Aprovar", key=f"aprovar_{i}", use_container_width=True):
                                try:
                                    supabase.table("registro_veiculos_calendario").update({
                                        "STATUS": "Aprovado",
                                        "APROVADOR": usuario_logado,
                                        "DATA_DA_APROVACAO": datetime.now().isoformat(),
                                        "MOTIVO_REJEICAO": None
                                    }).eq("id", registro["id"]).execute()
                                    
                                    st.success("✅ Registro aprovado com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    logger.error(f"Erro ao aprovar: {e}")
                                    st.error(f"❌ Erro ao aprovar: {e}")
                        
                        with col2:
                            if st.button("❌ Rejeitar", key=f"rejeitar_{i}", use_container_width=True):
                                st.session_state[f"rejeitando_{i}"] = True
                        
                        # Formulário de rejeição
                        if st.session_state.get(f"rejeitando_{i}", False):
                            motivo = st.text_area(
                                "📝 Motivo da rejeição (obrigatório)",
                                key=f"motivo_{i}",
                                placeholder="Descreva o motivo da rejeição..."
                            )
                            
                            col_confirm, col_cancel = st.columns(2)
                            
                            with col_confirm:
                                if st.button("Confirmar Rejeição", key=f"confirmar_rej_{i}", type="primary"):
                                    if not motivo or motivo.strip() == "":
                                        st.error("❌ O motivo da rejeição é obrigatório!")
                                    else:
                                        try:
                                            supabase.table("registro_veiculos_calendario").update({
                                                "STATUS": "Rejeitado",
                                                "APROVADOR": usuario_logado,
                                                "DATA_DA_APROVACAO": datetime.now().isoformat(),
                                                "MOTIVO_REJEICAO": motivo
                                            }).eq("id", registro["id"]).execute()
                                            
                                            st.success("✅ Registro rejeitado com sucesso!")
                                            st.session_state[f"rejeitando_{i}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            logger.error(f"Erro ao rejeitar: {e}")
                                            st.error(f"❌ Erro ao rejeitar: {e}")
                            
                            with col_cancel:
                                if st.button("Cancelar", key=f"cancelar_rej_{i}"):
                                    st.session_state[f"rejeitando_{i}"] = False
                                    st.rerun()
            else:
                st.info("ℹ️ Nenhum registro pendente de aprovação no período selecionado.")










































