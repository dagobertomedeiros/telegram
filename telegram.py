from telethon import TelegramClient, events, sync
import re, pymysql
import time, datetime
from datetime import datetime


#Parametros
api_id = 0000 #dados fornecidos pelo telegram
api_hash = 'xxxxxx' #dados fornecidos pelo telegram
txtSearch = 'minutinhos  ' #defina um conjunto chave de caracteres que devem ser buscados entre as mensagens
numLimit = 1 #Sempre utilizar 1, evita retrabalho com mensagens duplicadas, assim a coleta será sempre da ultima mensagem
chatOrGroup = 'INF016-2021.1' #coloca o nome do grupo ou chat_id do grupo
delay = 5 #defina em segundos o tempo de espera entre uma execução e outra das buscas por novas mensagens
conexao = pymysql.connect(db='telagram_mensagens', user='root', passwd='1234') #dados conexão com o BD
queryInsert = 'INSERT INTO TELEGRAM_MESSAGE (IDMESSAGE, TXTMESSAGE, DATEINSERT) VALUES (%s, %s, %s)' #query para insert de dados
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
idTemp = None
while(True):
    message = client.get_messages(entity=chatOrGroup, search=txtSearch, limit=numLimit)
    strMessage = str(message)
    txtMessage = strMessage.split('message=')
    idMessage = strMessage.split('Message(id=')
    idMessage = idMessage[1][0:4]
    txtMessage = txtMessage[1].split(', out=')
    txtMessage = txtMessage[0]
    if idTemp != idMessage and idMessage not in listBD:
        now = datetime.now()
        sqlDados = (idMessage, txtMessage, now)
        cursor.execute(queryInsert, sqlDados)
        conexao.commit()
        conexao.close()
        numRegistros += 1
        print('Total de registros inseridos - ', numRegistros,'\n')
    idTemp = idMessage
    time.sleep(delay)