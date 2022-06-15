##################################### BIBLIOTECAS #############################
import pandas as pd 
import plotly.graph_objects as go
import pandas_datareader.data as web
from datetime import datetime
from PIL import Image
import tensorflow as tf
##############################################################

############### ENTENDIMENTO DOS DADOS #######################################

def get_dicionario():
    dicionario_ativo = dict()
    dicionario_ativo = {
    'ABEV3.SA': 'A Ambev é uma empresa brasileira dedicada à produção de bebidas, entre as quais cervejas, refrigerantes, energéticos, sucos, chás e água.',
    'BBAS3.SA': 'Banco do Brasil é um banco brasileiro, constituído na forma de sociedade de economia mista, com participação do Governo Federal do Brasil em 50% das ações.',
    'BBDC4.SA': 'Bradesco é um banco brasileiro, constituído na forma de sociedade anônima, com sede em Osasco, em São Paulo.',
    'ELET3.SA': 'A Eletrobras é uma sociedade de economia mista e atua como uma holding, dividida em geração, transmissão e distribuição.',
    'ITSA4.SA': 'A Itaúsa é uma holding brasileira de investimentos de capital aberto com mais de 45 anos de trajetória.',
    'ITUB4.SA': 'Itaú Unibanco, também conhecido como Itaú, é o maior banco brasileiro, com sede na cidade de São Paulo, no estado homônimo.',
    'MGLU3.SA': 'O Magazine Luiza ou Magalu, é uma plataforma digital de varejo brasileira multicanal.',
    'PETR4.SA': 'Petróleo Brasileiro S.A. é uma empresa de capital aberto, cujo acionista majoritário é o Governo do Brasil.',
    'VALE3.SA': 'Vale é uma mineradora multinacional brasileira e uma das maiores operadoras de logística do país.',
    'VIVT3.SA': 'Telefônica Brasil é uma empresa do Grupo Telefónica, um dos principais conglomerados de comunicação do mundo.',
    'WEGE3.SA': 'WEG S.A é uma empresa multinacional brasileira com sede na cidade de Jaraguá do Sul.'
    }
    return dicionario_ativo

def get_dataframe(ativo, data_ini,data_fim):
    df = web.DataReader(ativo,data_source="yahoo",start=data_ini,end=data_fim)
    df.reset_index(level=0, inplace=True)
    df = df.dropna()
    df['Date'] = df['Date'].astype(str)
    df['Date'] = df['Date'].str.replace('T00:00:00', '')
    return df

def get_grafico_ativo(df):
    fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])
    return fig

def get_preco_ativo(ativo):
    data = datetime.now().date().isoformat()
    df = get_dataframe(ativo,data,data)
    preco = df['Close'][0]
    preco = round(preco,2)
    preco = 'R$ '+ str(preco).replace('.',',')
    return preco

def get_periodo_analise(data_ini,data_fim):
    di = datetime.strptime(str(data_ini), '%Y-%m-%d')
    df = datetime.strptime(str(data_fim), '%Y-%m-%d')
    quantidade_dias = str(abs((df - di).days)) +' dias' 
    return quantidade_dias

def get_tamanho_df(df):
    dimensao = df.shape
    tamanho = str(dimensao[1]) + ' x ' + str(dimensao[0])
    return tamanho
    
###################################################################################################################


############ ALGORITMOS DE IDENTIFICAÇÃO ################################

######### CRUZAMENTO DE MÉDIAS MÓVEIS #########
def medias_moveis(ativo,data_ini,data_fim,media_curta,media_longa):
    global df_medias_moveis 
    df_medias_moveis = get_dataframe(ativo,data_ini,data_fim)
    
    #criar sinal de compra e venda
    curta = 'SMA'+str(media_curta)
    longa = 'SMA'+str(media_longa)
    df_medias_moveis[curta] = df_medias_moveis['Close'].rolling(media_curta).mean()
    df_medias_moveis[longa] = df_medias_moveis['Close'].rolling(media_longa).mean()
    
    df_medias_moveis['Anterior'] = df_medias_moveis[curta].shift(1) - df_medias_moveis[longa].shift(1)
    df_medias_moveis['Atual'] = df_medias_moveis[curta] - df_medias_moveis[longa]
    
    df_medias_moveis.loc[(df_medias_moveis['Anterior'] <0)&(df_medias_moveis['Atual'] >0),'Compra'] = df_medias_moveis['Close']
    df_medias_moveis.loc[(df_medias_moveis['Anterior'] >0)&(df_medias_moveis['Atual'] <0),'Venda'] = df_medias_moveis['Close']

    #remove mesma operação consecutiva 
    indices_compra = df_medias_moveis['Compra'].dropna().index
    indices_venda =  df_medias_moveis['Venda'].dropna().index

    if abs(len(indices_compra) - len(indices_venda)) == 2:
        if len(indices_compra) < len(indices_venda):
            for i in range(0,len(indices_compra)):
                if indices_venda[i] < indices_compra[i] and indices_venda[i+1] < indices_compra[i]:
                    df_medias_moveis['Venda'][indices_venda[i+1]] = None
                    break
                if indices_compra[i] < indices_venda[i] and indices_compra[i+1] < indices_venda[i]:
                    df_medias_moveis['Compra'][indices_compra[i+1]] = None
                    break
        else:
            for i in range(0,len(indices_venda)):
                if indices_venda[i] < indices_compra[i] and indices_venda[i+1] < indices_compra[i]:
                    df_medias_moveis['Venda'][indices_venda[i+1]] = None
                    break
                if indices_compra[i] < indices_venda[i] and indices_compra[i+1] < indices_venda[i]:
                    df_medias_moveis['Compra'][indices_compra[i+1]] = None
                    break
    
    fig = grafico_medias_moveis(curta,longa)

    return fig

def grafico_medias_moveis(media_curta,media_longa):
    fig = go.Figure(
                data=[go.Candlestick(
                    x= df_medias_moveis['Date'],
                    open=df_medias_moveis['Open'],
                    high=df_medias_moveis['High'],
                    low=df_medias_moveis['Low'],
                    close=df_medias_moveis['Close'],
                    showlegend=False
                )]
                
            )
    
    longa = media_longa.replace('SMA','MMS')
    fig.add_trace(go.Scatter(
        x= df_medias_moveis['Date'],
        y=df_medias_moveis[media_longa],
        mode="lines",
        line_color="orange",
        name= longa
    ))

    curta = media_curta.replace('SMA','MMS')
    fig.add_trace(go.Scatter(
        x= df_medias_moveis['Date'],
        y=df_medias_moveis[media_curta],
        mode="lines",
        line_color="purple",
        name= curta
    ))

    fig.add_trace(go.Scatter(
        mode='markers',
        name= 'Compra',
        x=df_medias_moveis['Date'],
        y=df_medias_moveis['Compra'],
        marker=dict(
                color='green',
                symbol = 5,
                size=12,
            )
    ))

    fig.add_trace(go.Scatter(
        mode='markers',
        name= 'Venda',
        x=df_medias_moveis['Date'],
        y=df_medias_moveis['Venda'],
        marker=dict(
                color='red',
                symbol = 6,
                size=12
            )
    ))
    return fig

######### SUPORTE E RESISTÊNCIA #########
def support(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.Low[i]>df1.Low[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.Low[i]<df1.Low[i-1]):
            return 0
    return 1


def resistance(df1, l, n1, n2): #n1 n2 before and after candle l
    for i in range(l-n1+1, l+1):
        if(df1.High[i]<df1.High[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df1.High[i]>df1.High[i-1]):
            return 0
    return 1

def get_suporte(ativo,data_ini,data_fim):
    ticker_df = get_dataframe(ativo,data_ini,data_fim)

    ss = []
    rr = []
    n1=2
    n2=2

    for row in range(3, 205): #len(df)-n2
        if support(ticker_df, row, n1, n2):
            ss.append((row,ticker_df.Low[row]))
    s = 0
    e = 200
    dfpl = ticker_df[s:e]
    fig = go.Figure(data=[go.Candlestick(
                x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

    c=0
    while (1):
        if(c>len(ss)-1 ):
            break
        fig.add_shape(type='line', x0=ss[c][0], y0=ss[c][1],
                    x1=e,
                    y1=ss[c][1],
                    line=dict(color="MediumPurple",width=3)
                    )
        c+=1

    c=0
    while (1):
        if(c>len(rr)-1 ):
            break
        fig.add_shape(type='line', x0=rr[c][0], y0=rr[c][1],
                    x1=e,
                    y1=rr[c][1],
                    line=dict(color="RoyalBlue",width=1)
                    )
        c+=1  
    return fig

def get_resistencia(ativo,data_ini,data_fim):
    ticker_df = get_dataframe(ativo,data_ini,data_fim)

    ss = []
    rr = []
    n1=2
    n2=2

    for row in range(3, 205): #len(df)-n2
         if resistance(ticker_df, row, n1, n2):
            rr.append((row,ticker_df.High[row]))
    s = 0
    e = 200
    dfpl = ticker_df[s:e]
    fig = go.Figure(data=[go.Candlestick(
                x=dfpl.index,
                open=dfpl['Open'],
                high=dfpl['High'],
                low=dfpl['Low'],
                close=dfpl['Close'])])

    c=0
    while (1):
        if(c>len(ss)-1 ):
            break
        fig.add_shape(type='line', x0=ss[c][0], y0=ss[c][1],
                    x1=e,
                    y1=ss[c][1],
                    line=dict(color="MediumPurple",width=3)
                    )
        c+=1

    c=0
    while (1):
        if(c>len(rr)-1 ):
            break
        fig.add_shape(type='line', x0=rr[c][0], y0=rr[c][1],
                    x1=e,
                    y1=rr[c][1],
                    line=dict(color="RoyalBlue",width=1)
                    )
        c+=1  
    return fig

######### DETECTOR DE TOPO-DUPLO E FUNDO-DUPLO #########
def predict(image_file:Image.Image):
    model = tf.keras.models.load_model('model')

    image = tf.keras.preprocessing.image.load_img(image_file, target_size = (80,100))
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = tf.expand_dims(image, 0)

    prediction = model.predict(image)[0][0]
    
    return prediction 

###################################################################################################################


############ BACKTEST ################################

def get_bkt_medias_moveis():
    l1 = pd.Series([float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan'),float('nan')])
    df_backtest =  pd.DataFrame([list(l1)], columns = ['Taxa Acerto','Media Ganho', 'Media Perda', 'Payoff', 'N Sinais Compra', 'N Sinais Venda','N Sinais', 'N Sinais Ano', 'Lucro Final', 'Rentabilidade Final'])
    
    acertos, ganhos, perdas = get_ganhos_e_perdas(df_medias_moveis)
    
    df_backtest['Taxa Acerto'][0] =    get_taxa_acerto(acertos)
    df_backtest['Media Ganho'][0] =    get_media_ganho(ganhos)
    df_backtest['Media Perda'][0] =    get_media_perda(perdas)
    df_backtest['Payoff'][0] =         get_payoff(ganhos,perdas)
    df_backtest['N Sinais Compra'][0] = get_sinais_compra(df_medias_moveis)
    df_backtest['N Sinais Venda'][0] = get_sinais_venda(df_medias_moveis)
    df_backtest['N Sinais'][0] =       get_total_sinais(df_medias_moveis)
    df_backtest['N Sinais Ano'][0] =   get_total_sinais_ano(df_medias_moveis)
    df_backtest['Lucro Final'][0] =    get_lucro(ganhos,perdas,1)
    df_backtest['Rentabilidade Final'][0] = get_rentabilidade(ganhos,perdas,1)

    return df_backtest

def get_ganhos_e_perdas(df):
    df = df.reset_index()
    indices_compra = df['Compra'].dropna().index
    indices_venda =  df['Venda'].dropna().index
    acertos = list()
    ganhos = list()
    perdas = list()

    if len(indices_venda) > len(indices_compra):
        for i in range(0,len(indices_venda)):
            if i < len(indices_venda) - 1:
                #a primeira entrada é de venda
                if indices_venda[i] < indices_compra[i]:
                    if abs(indices_venda[i] - indices_compra[i]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                                acertos.append(1.0)
                                ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                    
                    #segundo cruzamento, segunda entrada é de compra
                    if abs(indices_compra[i] - indices_venda[i+1]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                    
                #a primeira entrada é de compra
                else:
                    if abs(indices_compra[i] - indices_venda[i]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        
                    #segundo cruzamento, segunda entrada é de venda
                    if abs(indices_venda[i] - indices_compra[i+1]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
            #último cruzamento e entrada é de venda           
            else:
                if df['Close'].loc[indices_venda[i]] >= df['Close'][len(df)-1]:
                    acertos.append(1.0)
                    ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'][len(df)-1]))
                else:
                    acertos.append(0.0)
                    ganhos.append(0.0)
                    perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'][len(df)-1]))

    elif len(indices_venda) == len(indices_compra):
        for i in range(0,len(indices_venda)):
            if i < len(indices_venda) - 1:
                #a primeira entrada é de venda
                if indices_venda[i] < indices_compra[i]:
                    if abs(indices_venda[i] - indices_compra[i]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                                acertos.append(1.0)
                                ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                    
                    #segundo cruzamento, segunda entrada é de compra
                    if abs(indices_compra[i] - indices_venda[i+1]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                    
                #a primeira entrada é de compra
                else:
                    if abs(indices_compra[i] - indices_venda[i]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        
                    #segundo cruzamento, segunda entrada é de venda
                    if abs(indices_venda[i] - indices_compra[i+1]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
            #dois últimos cruzamento          
            else:
                #penúltima entrada é de venda e a última é de compra
                if indices_venda[-1:][0] < indices_compra[-1:][0]:
                    #penúltima (venda)
                    if abs(indices_venda[i] - indices_compra[i]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                                acertos.append(1.0)
                                ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                            
                    #última entrada (compra)
                    if df['Close'].loc[indices_compra[i]] <= df['Close'][len(df)-1]:
                        acertos.append(1.0)
                        ganhos.append((df['Close'][len(df)-1] - df['Close'].loc[indices_compra[i]]))
                    else:
                        acertos.append(0.0)
                        ganhos.append(0.0)
                        perdas.append((df['Close'][len(df)-1] - df['Close'].loc[indices_compra[i]]))
                
                #penúltima entrada é de compra e a última é de venda
                else:
                    #penúltima (compra)
                    if abs(indices_compra[i] - indices_venda[i]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                    
                    #última entrada (venda)
                    if df['Close'].loc[indices_venda[i]] >= df['Close'][len(df)-1]:
                        acertos.append(1.0)
                        ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'][len(df)-1]))
                    else:
                        acertos.append(0.0)
                        ganhos.append(0.0)
                        perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'][len(df)-1]))
                    
    else:
        for i in range(0,len(indices_compra)):
            if i < len(indices_compra) - 1:
                #a primeira entrada é de venda
                if indices_venda[i] < indices_compra[i]:
                    if abs(indices_venda[i] - indices_compra[i]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                                acertos.append(1.0)
                                ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                    
                    #segundo cruzamento, segunda entrada é de compra
                    if abs(indices_compra[i] - indices_venda[i+1]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i+1]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                    
                #a primeira entrada é de compra
                else:
                    if abs(indices_compra[i] - indices_venda[i]) < 30:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_venda[i]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i]]))
                    else:
                        if df['Close'].loc[indices_compra[i]] < df['Close'].loc[indices_compra[i]+20]:
                            acertos.append(1.0)
                            ganhos.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append(( df['Close'].loc[indices_compra[i]+20] - df['Close'].loc[indices_compra[i]]))
                        
                    #segundo cruzamento, segunda entrada é de venda
                    if abs(indices_venda[i] - indices_compra[i+1]) < 30:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_compra[i+1]]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_compra[i+1]]))
                    else:
                        if df['Close'].loc[indices_venda[i]] > df['Close'].loc[indices_venda[i]+20]:
                            acertos.append(1.0)
                            ganhos.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
                        else:
                            acertos.append(0.0)
                            ganhos.append(0.0)
                            perdas.append((df['Close'].loc[indices_venda[i]] - df['Close'].loc[indices_venda[i]+20]))
            #último cruzamento e entrada é de compra     
            else:
                if df['Close'].loc[indices_compra[i]] <= df['Close'][len(df)-1]:
                    acertos.append(1.0)
                    ganhos.append((df['Close'][len(df)-1] - df['Close'].loc[indices_compra[i]]))
                else:
                    acertos.append(0.0)
                    ganhos.append(0.0)
                    perdas.append((df['Close'][len(df)-1] - df['Close'].loc[indices_compra[i]]))
    
    return acertos, ganhos, perdas

def get_sinais_venda(df):
    df = df.reset_index()
    return len(df['Venda'].dropna())

def get_sinais_compra(df):
    df = df.reset_index()
    return len(df['Compra'].dropna())

def get_total_sinais(df):
    return (get_sinais_compra(df) + get_sinais_venda(df))

def get_total_sinais_ano(df):
    data_ini = str(df['Date'].loc[0]).replace(' 00:00:00','')
    data_fim = str(df['Date'].loc[len(df)-1]).replace(' 00:00:00','')
    data_ini = datetime.strptime(data_ini, '%Y-%m-%d')
    data_fim = datetime.strptime(data_fim, '%Y-%m-%d')
    quantidade_anos = abs((data_fim - data_ini).days) / 365
    return round((get_total_sinais(df) / quantidade_anos),2)

def get_taxa_acerto(acertos):
    if acertos: return str(round((sum(acertos) / len(acertos)*100),2))+' %'
    else: return str(0.0)+' %'

def get_media_ganho(ganhos):
    if ganhos: return round(sum(ganhos) / len(ganhos),2)
    else: return 0.0

def get_media_perda(perdas):
    if perdas: return round(sum(perdas) / len(perdas),2)
    else: return 0.0

def get_payoff(ganhos,perdas):
    if perdas: return  round((get_media_ganho(ganhos) / get_media_perda(perdas)*-1),2)
    else: return 0.0

def get_lucro(ganhos,perdas,valor_entrada=1):
    lucro = list()
    if ganhos or perdas:
        for i in ganhos:
            lucro.append(i * valor_entrada)

        for j in perdas:
            lucro.append(j * valor_entrada)

        return round(sum(lucro),2)
    else:
        return 0.0

def get_rentabilidade(ganhos,perdas,valor_entrada=1):
    if valor_entrada != 0: return str(round((get_lucro(ganhos,perdas,valor_entrada)/valor_entrada* 100),2))+' %'
    else: return str(0.0)+' %'