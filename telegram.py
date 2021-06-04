from telethon import TelegramClient, events, sync
import re, pymysql
import time, datetime
from datetime import datetime


#Parametros
api_id = XXXXX #dados fornecidos pelo telegram.
api_hash = 'XXXXXX' #dados fornecidos pelo telegram.
txtSearch = ['closed'] #defina um conjunto chave de expressões que devem ser buscados entre as mensagens. Devem estar em aspas e numa lista ['xxx', 'yyy', 'cccc'].
numLimit = 5 #Este número determina a quantidade de mensagens que serão coletadas a cada consulta ao seu telegram.
chatOrGroup = None #'None' para pesquisar em todos os grupos/chats/contatos ou coloca o nome do grupo ou chat_id do grupo
delay = 5 #defina em segundos o tempo de espera entre uma execução e outra das buscas por novas mensagens
conexao = pymysql.connect(db='telagram_mensagens', user='root', passwd='test') #dados conexão com o BD

queryInsert = 'INSERT INTO telegram_message (IDMESSAGE, TXTMESSAGE, DATEINSERT) VALUES (%s, %s, %s)' #query para insert de dados
querySelect = 'SELECT IDMESSAGE FROM telagram_mensagens.telegram_message' #query para consultar ids já cadastrados no BD


numRegistros = 0
cursor = conexao.cursor()
cursor.execute(querySelect)
exist = cursor.fetchall()
exist = list(exist)
listBD = []
for x in exist:
    item = x
    item = str(item)
    for y in ['(', ',', ')']:
        item = item.replace(y, '')
    listBD.append(item)

client = TelegramClient('test_session', api_id, api_hash)
client.start()
idTemp = []
countChat = 0
countSearch = 0
countLimit = 0
while(True):
    numSearch = len(txtSearch)
    while(countSearch < numSearch):
        message = client.get_messages(entity=chatOrGroup, search=txtSearch[countSearch], limit=numLimit)
        message = list(message)
        while(countLimit<numLimit):
            strMessage = str(message[countLimit])
            txtMessage = strMessage.split('message=')
            idMessage = strMessage.split('Message(id=')
            idMessage = idMessage[1][0:4]
            txtMessage = txtMessage[1].split(', out=')
            txtMessage = txtMessage[0]
            if idMessage not in idTemp and idMessage not in listBD:
                now = datetime.now()
                sqlDados = (idMessage, txtMessage, now)
                cursor.execute(queryInsert, sqlDados)
                conexao.commit()
                conexao.close()
                numRegistros += 1
                countLimit+=1
                idTemp.append(idMessage)
                print('Total de registros inseridos - ', numRegistros,'\n')
        countSearch+=1
    time.sleep(delay)

