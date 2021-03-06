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
nameChatOrGroup = ['name_group_1', 'NAME_CHANNEL'] #defina uma lista de nomes de grupos, canais ou remetentes para filtrar a busca
delay = 5 #defina em segundos o tempo de espera entre uma execução e outra das buscas por novas mensagens
listIdChat = []#defina uma lista com os ID's dos grupos e canais que aceitará gravar as mensagens ou deixe a lista vazia
conexao = pymysql.connect(db='telagram_mensagens', user='root', passwd='test') #dados conexão com o BD
queryInsert = 'INSERT INTO telegram_message (IDMESSAGE, TXTMESSAGE, DATEINSERT, IDCHAT, TITLECHAT, IDCHATGROUP, SENDERID, SENDERFIRSTNAME, IDMIDIA) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)' #query para insert de dados
querySelect = 'SELECT IDMESSAGE FROM telagram_mensagens.telegram_message' #query para consultar ids já cadastrados no BD
directory = 'nome_da_pasta' #informe o nome da pasta onde salvará as midias. IMPORTANTE: a pasta deve estar localizada dentro da pasta onde localizar o script.


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

while(True):
    numSearch = len(txtSearch)
    while(countSearch < numSearch):
        for message in client.get_messages(entity=chatOrGroup, search=txtSearch[countSearch], limit=numLimit):
            if str(message.chat.title) in nameChatOrGroup:
                try:
                    message.download_media( directory + '/' + str(message.photo.id))
                    idMidia = message.photo.id
                except:
                    otherName = str(message.date)
                    otherName = otherName.replace('-','')
                    otherName = otherName.replace(':','')
                    otherName = otherName.replace('+','')
                    otherName = otherName.replace(' ','')
                    message.download_media( directory + '/foto' + otherName + str(numRegistros) )
                    idMidia = 0
                    continue
                txtMessage = message.message
                idMessage = message.id
                idChat = message.peer_id
                dateMsg = message.date
                titleChat = message.chat.title
                idChatGroup = message.chat_id
                senderId = message.sender.id
                senderFirstName = message.sender.first_name
                if (idMessage not in idTemp) and (idMessage not in listBD):
                    if len(listIdChat) > 0:
                        if idChat in listIdChat:
                            sqlDados = (idMessage, txtMessage, dateMsg, idChat, titleChat, idChatGroup, senderId, senderFirstName, idMidia)
                            conexao.ping(reconnect=True)
                            cursor.execute(queryInsert, sqlDados)
                            conexao.commit()
                            conexao.close()
                            numRegistros += 1
                            idTemp.append(idMessage)
                            print('Total de registros inseridos -> ', numRegistros,'\n')
                    elif len(listIdChat) == 0:
                        sqlDados = (idMessage, txtMessage, dateMsg, idChat, titleChat, idChatGroup, senderId, senderFirstName, idMidia)
                        conexao.ping(reconnect=True)
                        cursor.execute(queryInsert, sqlDados)
                        conexao.commit()
                        conexao.close()
                        numRegistros += 1
                        idTemp.append(idMessage)
                        print('Total de registros inseridos -> ', numRegistros,'\n')
        countSearch+=1
    print('Script em execução....', datetime.now())
    time.sleep(delay)
