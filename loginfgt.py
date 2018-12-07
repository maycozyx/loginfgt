# Autor: mayco.zyx@gmail.com Data: 07/12/2018
# -*- coding: utf-8 -*-
# Use o parâmetro -d na linha de comando para ativar o modo debug

import requests, time, sys

debug = False # controla o modo debug que pode ser ativado passando na linha de comando o parâmetro -d
TCONNA = 5 # tempo que espera para tentar conectar novamente caso haja falha com o adaptador de rede
TCONNF = 60 # tempo que espera para tentar conectar novamente caso já esteja conectado no Fortgate
TCONNSE = 30 # tempo que espera para tentar novamente caso o usuário e senha do Fortgate estejam incorretos
URL = 'http://www.google.com/' # URL para se testar se há conexão com a internet. Tem que usar / no final da URL e seguir este padrão 'http://www.google.com/'. Nãoo pode ser 'https'.
UFGT = '' # preencha com o usuário do Fortgate
SFGT = '' # preencha com a senha do Fortgate

# FUNÇÕES

# verifica se foi passado algum parâmetro na linha de comando
def verifica_parametros():
	global debug
	for parametro in sys.argv:
		if ( parametro == '-d' ): # se foi utilizado na linha de comando o parâmetro -d então ativa o modo debug
			debug = True

# mostra mensagens para depuração
def db( mensagem ):
	if ( debug ):
		print( mensagem )

# verifica se o requests retornou a página do Fortgate
def epf( url ): # é a página do Fortgate que foi recebida?
	if ( url[0:32] == 'http://192.168.0.1:1000/fgtauth?' ):
		return True
	else:
		return False

# envia dados de login
def edados( magic, urlf ): # magic = número magic; urlf = URL do Fortgate
	db('11 - Preparando a carga POST de dados do formulário.')
	payload = { '4Tredir': URL, 'magic': magic, 'username': UFGT, 'password': SFGT } # carga a ser enviada com os dados do formulário de conexão do Fortgate
	db('12 - Tentando enviar os dados do formulário.')
	try:
		r = requests.post(urlf, data=payload)
		db('13 - Dados do formulário enviados com sucesso.')
		if ( epf( r.url ) ): # recebeu uma página do Fortgate novamente
			if  ( r.text.find( 'window.location="' + URL ) != -1 ): # se foi recebido a página de redirecionamento, significa que login foi bem sucedido
				db('14 - Página de redirecionamento recebida. Login no Fortgate foi bem sucedido!')
			elif ( r.text.find( 'Falhou!' ) != -1 ):
				db('15 - Usuário ou senha incorretos. Autenticação falhou.')
			else:
				db('16 - Foi recebido do Fortgate uma página não conhecida. Provavelmente a autenticação falhou.')
				if ( debug ):
					print( r.text ) # mostra o conteúdo da página desconhecida
		else:
			db('17 - Foi recebido uma página não conhecida. Provavelmente a autenticação falhou.')
			if ( debug ):
				print( r.text ) # mostra o conteúdo da página desconhecida
	except requests.ConnectionError:
		db('18 - Não foi possível utilizar o Adaptador de Rede na tentativa de enviar os dados de login, verifique os cabos e se sua placa de rede está ativada.')
	time.sleep( TCONNSE ) # aguarda um pouco para caso necessite tentar novamente

# verifica se encontra o input name magic, caso encontre então significa que está sem conexão com a internet 
#  o numero magic caso encontre
def nmagic( r ): 
	db('8 - Procurando o número magic.')
	if ( r.text.find( 'magic' ) != -1 ): # se encontrou a tag <input name="magic">
		db('9 - Encontrado o número magic.')
		magicpos = r.text.find( 'magic' ) # posição onde foi encontrado o magic
		magic = ( r.text[magicpos+14:magicpos+30] ) # separa o número magic
		edados( magic, r.url )
	else:
		db('10 - Não foi encontrado o número magic. Provavelmente a estrutura HTML da página de login do Fortgate foi alterada.')

# verifica se é a página de login do Fortgate
def pgfgt( r ):
	db('5 - Verificando se a página recebida é oriunda do Fortgate.')
	if ( epf( r.url ) ): # verifica se veio a página de login do Fortgate
		db('6 - Recebido a página de login do Fortgate, pois não há acesso a internet.')
		nmagic( r ) # tenta realizar o login no Fortgate
	else:
		db('5b - A página recebida não é oriunda do Fortgate.')
		if ( r.url == URL ): # a página solicitada é a página recebida, então há acesso a internet
			db('7 - Está tudo bem, há conexão com a internet!')
		else:
			if ( debug ): # para verificar se as URLs estão coincidindo 
				print('As duas URLs abaixo devem ser iguais:')
				print(r.url)
				print(URL)
				print('Verifique se você utilizou o padrão correto na URL requisitada.')
				print('7b - Há conexão com a internet.')
		time.sleep( TCONNF ) # espera um minuto até testar novamente a conexão 

# testa está sem conexão com a internet 
def trequest():
	db('2 - Tentando usar o Adaptador de rede.')
	try:
		r = requests.get( URL )
		db('3 - Requisição enviada para: ' + URL)
		pgfgt( r )
	except requests.ConnectionError: # sem conexão com o adaptador de rede
		db('4 - Não foi possível utilizar o Adaptador de Rede, verifique os cabos da rede e se sua placa de rede está ativada.')
		time.sleep( TCONNA ) 

# PROGRAMA PRINCIPAL

db('0 - Foi dada a largada!')
iniciando = True

verifica_parametros()

# fica verificando infinitamente para saber se há conexão com a internet
while True:
	db('1 - Iniciando a verificação de conexão com a internet.') if iniciando else db('\n1 - Reiniciando a verificação de conexão com a internet.')
	if ( iniciando ):
		iniciando = False
	trequest()
