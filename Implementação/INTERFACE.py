import pandas as pd 
import streamlit as st
import numpy as np
from PIL import Image
import VERIFICACOES as vf
import APLICACAO as ap

####### MENU LATERAL #############
st.sidebar.title("Menu",anchor=None)
op =  st.sidebar.selectbox('Selecione a Pagina', ['Página Inicial','Sobre Indicadores','Laboratório'])
st.sidebar.header('Autor')
st.sidebar.write('Esta plataforma foi desenvolvido por Leonardo de Souza Mateus como projeto de TCC para a conclusão do curso de Engenharia da Computação na Universidade Federal do Paraná')
st.sidebar.header('Contato')


if op == 'Página Inicial':
    #### INTERFACE DE APRESENTAÇÃO DO PROJETO #############
    cini = st.container()
    cini.title('Bem-vindo ao Lab Stock Market',anchor=None)
    cini.subheader('Plataforma que te ajuda analisar a performance dos principais indicadores da Análise Técnica sobre o mercado de ações brasileiro',anchor=None)
    cini.image(Image.open('C:/Users/leona/Documents/Untitled Folder/foto_inicial.png'))
elif op == 'Sobre Indicadores':
    #### INTERFACE DE APRESENTAÇÃO DOS INDICADORES #############
    st.title('Indicadores da Análise Técnica',anchor=None)
elif op == 'Laboratório':
    #### CONTANEIR DE OPÇÕES #############
     coption = st.container()
     coption.title('Faça suas Análises')
     col1,col2,col3 = coption.columns(3)
     ativo = col1.selectbox("Escolha um Ativo",[
                                    'ABEV3',
                                    'BBAS3',
                                    'BBDC4',
                                    'BOVA11',
                                    'ELET3',
                                    'ITSA4',
                                    'ITUB4',
                                    'MGLU3',
                                    'PETR4',
                                    'VALE3',
                                    'VIVT3',
                                    'WEGE3']
                )
     ativo = ativo+'.SA'
     data_ini = col2.date_input("Escolha uma data inicial")
     data_fim = col3.date_input("Escolha uma data final")
     ##### SEGUNDA LINHA #########
     col4, col5 = coption.columns(2)
     padrao = col4.radio("Escolha um padrão",['Nenhum','Topo-Duplo','Fundo-Duplo'])
     indicador = str()
     if padrao == 'Nenhum':
         
         indicador = col5.selectbox('Escolha os indicadores', ['Médias Móveis','Resistência','Suporte'])
         if indicador == 'Médias Móveis':
            col6, col7 = coption.columns(2)
            media_curta = col6.slider('Informe o período da Média Curta')
            media_longa = col7.slider('Informe o período da Média Longa')
            media = vf.verifica_medias_moveis(media_curta,media_longa)
     

     botao = coption.button('ANALISAR')
     if botao:
         data = vf.verifica_data(data_ini,data_fim)

         if data != 'data correta': coption.error(data)
         elif padrao == 'Nenhum' and indicador == 'Médias Móveis' and media != 'media correta': coption.error(media)
         else:
             coption.success('Dados inseridos corretamente, Aguarde a saída métricas !!')
             
             ##### SOBRE O ATIVO ########
             cativo = st.container() 
             cativo.header("Ativo escolhido: "+ativo)
             dicionario_ativo = ap.get_dicionario()
             cativo.write(dicionario_ativo[ativo])

             ###### SOBRE OS DADOS ########
             df = ap.get_dataframe(ativo,data_ini,data_fim)
             col2,col3,col4 = cativo.columns(3)
             col2.metric(label="Período de Análise", value= ap.get_periodo_analise(data_ini,data_fim))
             col3.metric(label="Conjunto de Dados", value= ap.get_tamanho_df(df))
             if padrao == 'Nenhum':
                col4.metric(label="Estrátegia", value=indicador)
             else:
                col4.metric(label="Estrátegia", value=padrao)

             ##### BACKTEST E DASHBOARD ###########
             cbacktest = st.container()
             col1 = cbacktest.columns(1)
             if indicador == 'Médias Móveis':
                 grafico_medias =  ap.medias_moveis(ativo,data_ini,data_fim,media_curta,media_longa)
                 cbacktest.write(grafico_medias)
                 #### DASH SEGUNDA LINHA ##########
                 df_medias_moveis = ap.get_bkt_medias_moveis()
                 col2, col3,col4, col5 = cbacktest.columns(4)
                 col2.metric(label="Qtd. Sinais de Venda", value=df_medias_moveis['N Sinais Venda'][0])
                 col3.metric(label="Qtd. Sinais de Compra", value=df_medias_moveis['N Sinais Compra'][0])
                 col4.metric(label="Qtd. Total  de Sinais", value=df_medias_moveis['N Sinais'][0])
                 col5.metric(label="Qtd. de Sinais por Ano", value=df_medias_moveis['N Sinais Ano'][0])
                 #### DASH TERCEIRA LINHA ##########
                 col6, col7,col8 = cbacktest.columns(3)
                 col6.metric(label="Taxa de Acerto", value=df_medias_moveis['Taxa Acerto'][0])
                 col7.metric(label="Média de Ganhos R$", value=df_medias_moveis['Media Ganho'][0])
                 col8.metric(label="Média de Perdas R$", value=df_medias_moveis['Media Perda'][0])
                 #### DASH QUARTA LINHA ##########
                 col9, col10,col11 = cbacktest.columns(3)
                 col9.metric(label="Payoff", value=df_medias_moveis['Payoff'][0])
                 col10.metric(label="Lucro R$", value=df_medias_moveis['Lucro Final'][0])
                 col11.metric(label="Rentabilidade", value=df_medias_moveis['Rentabilidade Final'][0])
             elif indicador == 'Resistência':
                 resistencia = ap.get_resistencia(ativo,data_ini,data_fim)
                 cbacktest.write(resistencia)
             elif indicador == 'Suporte':
                 suporte = ap.get_suporte(ativo,data_ini,data_fim)
                 cbacktest.write(suporte)

             