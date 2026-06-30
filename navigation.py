import streamlit as st
import body

def iniciar_navegacao():
    def carregar_dashboard():
        body.renderizar_body()

    def pagina_dados_brutos():
        from pages import dados_brutos
        dados_brutos.renderizar_dados_brutos()


    page_1 = st.Page(carregar_dashboard, title="Dashboard", default=True)
    page_2 = st.Page(pagina_dados_brutos, title="Dados Brutos")


    pg = st.navigation([page_1, page_2])
    return pg