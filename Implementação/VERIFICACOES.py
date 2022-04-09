
def verifica_data(data_ini, data_fim):
    if data_ini < data_fim:
        return 'data correta'
    elif data_ini == data_fim:
        return 'Data Inicial não pode ser igual a Data Final'
    else:
        return 'Data Inicial deve ser menor que a Data Final'
    return 'nada'

def verifica_medias_moveis(media_curta,media_longa):
    if media_curta != 0 and media_curta < media_longa:
        return 'media correta'
    elif media_curta > media_longa:
        return 'O período da Média Curta não pode ser maior que o período da Média Longa'
    elif media_curta == 0 and media_longa == 0:
        return 'Informe o período das Médias'
    elif media_curta == 0 or media_longa == 0:
        return 'O período das Médias não podem ser iguais a ZERO'
    else:
        return 'O período das Médias não podem ser iguais'
    