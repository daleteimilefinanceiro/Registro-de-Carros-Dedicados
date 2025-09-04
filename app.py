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










































