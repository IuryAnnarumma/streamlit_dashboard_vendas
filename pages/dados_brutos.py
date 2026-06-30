import streamlit as st
import pandas as pd
import requests
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@st.cache_data
def converter_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso.')
    time.sleep(5)
    sucesso.empty()


def renderizar_dados_brutos(): 
    # Requisição
    url = 'https://labdados.com/produtos'
    response = requests.get(url, verify=False)
    data = pd.DataFrame.from_dict(response.json())
    data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')

    st.title('DADOS BRUTOS')

    # Seleção de Colunas
    with st.expander('Colunas'):
        colunas = st.multiselect('Selecione as Colunas:', list(data.columns), list(data.columns))

    # Filtros
    st.sidebar.title('Filtros')
    with st.sidebar.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os Produtos:', data['Produto'].unique(), data['Produto'])
    with st.sidebar.expander('Preço do produto'):
        preco = st.slider('Selecione o preço:', 0, 5000, (0,5000))
    with st.sidebar.expander('Data da compra'):
        data_compra = st.date_input('Selecione uma data', (data['Data da Compra'].min(), data['Data da Compra'].max()))
    with st.sidebar.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os produtos', data['Produto'].unique(), data['Produto'].unique())
    with st.sidebar.expander('Categoria do produto'):
        categoria = st.multiselect('Selecione as categorias', data['Categoria do Produto'].unique(), data['Categoria do Produto'].unique())
    with st.sidebar.expander('Preço do produto'):
        preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
    with st.sidebar.expander('Frete da venda'):
        frete = st.slider('Frete', 0,250, (0,250))
    with st.sidebar.expander('Data da compra'):
        data_compra = st.date_input('Selecione a data', (data['Data da Compra'].min(), data['Data da Compra'].max()))
    with st.sidebar.expander('Vendedor'):
        vendedores = st.multiselect('Selecione os vendedores', data['Vendedor'].unique(), data['Vendedor'].unique())
    with st.sidebar.expander('Local da compra'):
        local_compra = st.multiselect('Selecione o local da compra', data['Local da compra'].unique(), data['Local da compra'].unique())
    with st.sidebar.expander('Avaliação da compra'):
        avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
    with st.sidebar.expander('Tipo de pagamento'):
        tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',data['Tipo de pagamento'].unique(), data['Tipo de pagamento'].unique())
    with st.sidebar.expander('Quantidade de parcelas'):
        qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

    query = '''
    Produto in @produtos and \
    `Categoria do Produto` in @categoria and \
    @preco[0] <= Preço <= @preco[1] and \
    @frete[0] <= Frete <= @frete[1] and \
    @data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
    Vendedor in @vendedores and \
    `Local da compra` in @local_compra and \
    @avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
    `Tipo de pagamento` in @tipo_pagamento and \
    @qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
    '''
    dados_filtrados = data.query(query)
    dados_filtrados = dados_filtrados[colunas]

    st.dataframe(dados_filtrados)

    st.markdown(f'A Tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}]')

    st.markdown('Escreva um nome para o arquivo')
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'data')
        nome_arquivo += '.csv'
    with coluna2:
        st.download_button('Baixar a tabela em CSV', data = converter_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
