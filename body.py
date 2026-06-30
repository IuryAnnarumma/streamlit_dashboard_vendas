import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import urllib3
from functions import formatar_numero

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def renderizar_body():
    st.title('DASHBOARD DE VENDAS: :shopping_cart: ')

    st.sidebar.title('Filtros')
    regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
    regiao = st.sidebar.selectbox('Região', regioes)

    if regiao == 'Brasil':
        regiao = ''

    todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
    if todos_anos:
        ano = ''
    else:
        ano = st.sidebar.slider('Ano', 2020, 2023)

    query_string = {'regiao': regiao.lower(), 'ano': ano}

    # --- REQUISIÇÃO DOS DADOS EXCLUSIVA DO DASHBOARD ---
    url = 'https://labdados.com/produtos'
    response = requests.get(url, verify=False, params=query_string)
    
    data = pd.DataFrame.from_dict(response.json())
    data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')


    ### ----- Filtros -----

    filtro_vendedores = st.sidebar.multiselect('Vendedores', data['Vendedor'].unique())
    if filtro_vendedores:
        data = data[data['Vendedor'].isin(filtro_vendedores)]

    ### ----- Criação/Manipulação de TABELAS -----
    ### I - Tabelas de Receita
    receita_por_estado = data.groupby('Local da compra')['Preço'].sum()
    receita_por_estado = data.drop_duplicates(
        subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(
                receita_por_estado, left_on = 'Local da compra', right_index=True).sort_values('Preço')

    receita_mensal = data.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].sum().reset_index()
    receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
    receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

    receita_categoria = data.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending = False)

    ### II - Tabelas de Quantidade de Vendas
    vendas_por_estado = pd.DataFrame(data.groupby('Local da compra')['Preço'].count())
    vendas_por_estado = data.drop_duplicates(
        subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(
            vendas_por_estado, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)
    vendas_mensal = pd.DataFrame(data.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count().reset_index())
    vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
    vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()
    vendas_categorias = pd.DataFrame(data.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))

    ### III - Tabelas de Vendedores
    vendedores = pd.DataFrame(data.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

    ### ---- Criação de GRÁFICOS ---------
    ### I - Gráficos de Receita
    fig_mapa_receita = px.scatter_geo(receita_por_estado,
                                    lat = 'lat',
                                    lon = 'lon',
                                    scope = 'south america',
                                    size = 'Preço',
                                    template = 'seaborn',
                                    hover_name = 'Local da compra', hover_data = {'lat': False, 'lon': False},
                                    title = 'Receita por Estado')

    fig_receita_mensal = px.line(receita_mensal,
                                x = 'Mes',
                                y = 'Preço',
                                markers = True,
                                range_y = (0,receita_mensal.max()),
                                color = 'Ano',
                                line_dash = 'Ano',
                                title = 'Receita Mensal')
    fig_receita_mensal.update_layout(yaxis_title = 'Receita')

    fig_receita_estados = px.bar(receita_por_estado.head(),
                                x = 'Local da compra',
                                y = 'Preço',
                                text_auto = True,
                                title = 'Top estados (Receita)')
    fig_receita_estados.update_layout(yaxis_title = 'Receita')

    fig_receita_categorias = px.bar(receita_categoria,
                                    text_auto = True,
                                    title = 'Receita por Categoria')
    fig_receita_categorias.update_layout(yaxis_title = 'Receita')


    ### II - Gráficos de Quantidade de Vendas
    fig_mapa_vendas = px.scatter_geo(vendas_por_estado,
                                     lat = 'lat',
                                     lon = 'lon',
                                     scope = 'south america',
                                     fitbounds = 'locations',
                                     template = 'seaborn',
                                     size = 'Preço',
                                     hover_name = 'Local da compra',
                                     hover_data = {'lat': False, 'lon': False},
                                     title = 'Vendas por Estado'
                                     )
    fig_vendas_mensal = px.line(vendas_mensal,
                                x = 'Mes',
                                y = 'Preço',
                                markers = True,
                                range_y = (0, vendas_mensal.max()),
                                color = 'Ano',
                                line_dash = 'Ano',
                                title = 'Quantidade de Vendas Mensal')
                                
    fig_vendas_mensal.update_layout(yaxis_title = 'Quantidade de Vendas')

    fig_vendas_por_estado = px.bar(vendas_por_estado.head(),
                                   x = 'Local da compra',
                                   y = 'Preço',
                                   text_auto = 'True',
                                   title = 'Top 5 Estados')
    
    fig_vendas_por_estado.update_layout(yaxis_title = 'Quantidade de Vendas')

    fig_vendas_categorias = px.bar(vendas_categorias,
                                   text_auto = True,
                                   title = 'Vendas por Categoria')
    
    fig_vendas_categorias.update_layout(showlegend = False,
                                        yaxis_title = 'Quantidade de Vendas')

# ----- Renderização na Tela -----
    # Abas
    aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

    # Aba Receita
    with aba1:
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.metric('Receita', formatar_numero(data['Preço'].sum(), 'R$'))
            st.plotly_chart(fig_mapa_receita, width = 'stretch')
            st.plotly_chart(fig_receita_estados, width = 'stretch')
        with coluna2:
            st.metric('Quantidade de vendas', formatar_numero(data.shape[0]))
            st.plotly_chart(fig_receita_mensal, width = 'stretch')
            st.plotly_chart(fig_receita_categorias, width = 'stretch')

    # Aba Quantidade de Vendas
    with aba2:
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.metric('Receita', formatar_numero(data['Preço'].sum(), 'R$'))
            st.plotly_chart(fig_mapa_vendas, width = 'stretch')
            st.plotly_chart(fig_vendas_por_estado, width = 'stretch')

        with coluna2:
            st.metric('Quantidade de vendas', formatar_numero(data.shape[0]))
            st.plotly_chart(fig_vendas_mensal, width = 'stretch')
            st.plotly_chart(fig_vendas_categorias, width = 'stretch')

    # Aba Vendedores
    with aba3:
        qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.metric('Receita', formatar_numero(data['Preço'].sum(), 'R$'))
            fig_receita_vendedores = px.bar(vendedores['sum'].sort_values(ascending = False).head(qtd_vendedores),
                                            x = 'sum',
                                            y = vendedores['sum'].sort_values(ascending = False).head(qtd_vendedores).index,
                                            text_auto = True,
                                            title = f'Top {qtd_vendedores} vendedores (Receita)')
            fig_receita_vendedores.update_layout(yaxis_title = '')
            st.plotly_chart(fig_receita_vendedores)

        with coluna2:
            st.metric('Quantidade de vendas', formatar_numero(data.shape[0]))
            fig_vendas_vendedores = px.bar(vendedores['count'].sort_values(ascending = False).head(qtd_vendedores),
                                            x = 'count',
                                            y = vendedores['count'].sort_values(ascending = False).head(qtd_vendedores).index,
                                            text_auto = True,
                                            title = f'Top {qtd_vendedores} vendedores (Quantidade de Vendas)')
            fig_vendas_vendedores.update_layout(yaxis_title = '')
            st.plotly_chart(fig_vendas_vendedores)

    