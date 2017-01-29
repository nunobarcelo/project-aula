"""`main` is the top level module for your Bottle application."""

# import the Bottle framework
from bottle import Bottle, debug, template, request, redirect
from google.appengine.ext import ndb
debug(True)
# Create the Bottle WSGI application.
import json
import urllib2
import time
from datetime import datetime


bottle = Bottle()
	
@bottle.route('/inicio')
def mainpage():
	return """<form action="/inicio/" method="post">
			Username: <input type="text" name="username">  <br/>
			<input type="submit" value="Login" />
		</form>"""

@bottle.route('/inicio/', method='post')
def do_login():
	username = request.forms.get('username')
	if username == '0':
		redirect('/admin')
	else:
		redirect('/user/'+username)

@bottle.route('/admin')
def administrador():
	return """<form action="/admin/" method="post">
	<button name="subject" type="submit" value="Ver Todas as Salas">Ver Todas as Salas</button></br>
	<button name="subject" type="submit" value="Ver Salas Abertas">Ver Salas Abertas</button></br></br>
	<button name="subject" type="submit" value="Logout">Logout</button>
	</form>"""

@bottle.route('/admin/', method='post')
def adminaction():
	valor = request.forms.get('subject')
	adm =admin()
	if valor == "Ver Todas as Salas":
		return adm.list_all_rooms()
	elif valor == "Ver Salas Abertas":
		redirect('/available_rooms')
	else:
		redirect('/inicio')
		
@bottle.route('/admin/salasabertas')
def slas_abertas():
	adm =admin()
	return adm.list_open_rooms()

@bottle.route('/admin/space/<idSpace>/<name>')
def correr(idSpace, name):
	adm =admin()
	return adm.list_next(idSpace, name)
	
@bottle.route('/admin/available_rooms/<idSpace>/<name>')
def apresenta(idSpace,name):
	t = available_rooms(IDsala = idSpace, namesala = name)
	key = t.put()
	redirect('/admin')

@bottle.route('/available_rooms')
def apresentar_salas():
	ret = ""
	msgs = available_rooms.query()
	temp ="""%for item in list:
	<p> <a href="/check_in/alunosnasala/{{item.IDsala}}"> {{item.namesala}} </a></p>
	%end"""
	return template(temp, list = msgs)
	
@bottle.route('/user/<nomeuser>')
def utilizador(nomeuser):
	n_user = str(time.mktime(datetime.now().timetuple()))
	t = student(IDuser = n_user, NameUser = nomeuser)
	key = t.put()
	redirect('available_rooms/'+n_user+'/'+nomeuser)

@bottle.route('/user/available_rooms/<userid>/<nomeuser>')
def utilizador(userid,nomeuser):
	ret = ""
	msgs = available_rooms.query()
	Templateopenrooms = """%for item in list:
	<p> <a href="{{item.IDsala}}/sala"> {{item.namesala}} </a></p>
	%end"""
	return template(Templateopenrooms, list = msgs)

@bottle.route('/user/available_rooms/<userid>/<salaid>/sala')
def entrarounao(userid, salaid):
	Tempcheck = """<p> <a href="/check_in/{{iduser}}/{{idsala}}">check_in </a></p>
	<p> <a href="/check_in/alunosnasala/{{idsala}}">Alunos na sala </a></p>
	"""
	return template(Tempcheck, iduser = userid, idsala = salaid)
	
@bottle.route('/check_in/alunosnasala/<salaid>')
def apresentar_check(salaid):
	nome = ""
	msgs = check_in.query(check_in.IDsala == salaid)
	for m in msgs:
		t = student.query(student.IDuser == m.IDuser)
		if t != None:
			for r in t:
				nome +=   r.NameUser + "<br>"
	return nome

@bottle.route('/check_in/<userid>/<idsala>')
def checks(userid, idsala):
	ret = ""
	msgs = check_in.query(check_in.IDuser == userid)
	for m in msgs:
		ret += m.IDuser + "<br>"
	if ret == "":
		t = check_in(IDuser = userid, IDsala = idsala)
		key = t.put()
		return "Entrou na sala"
	else: 
		m.key.delete()
		t = check_in(IDuser = userid, IDsala = idsala)
		key = t.put()
		return "Saiu da sala anterior e encontra-se nesta sala"

@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'
	
class admin:

	def list_open_rooms(self):
		avl_room=available_rooms()
		return avl_room.apresentar_salas()

	def list_all_rooms(self):
		response = urllib2.urlopen("https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces").read()
		jsonobj = json.loads(response)
		TemplateAllRooms = """%for item in list:
		<p> <a href="/admin/space/{{item['id']}}/{{item['name']}}"> {{item['name']}} </a></p>
		%end"""
		return template(TemplateAllRooms, list = jsonobj)
	
	def list_next(self, idSpace, name):
		url = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/' + idSpace
		response2 = urllib2.urlopen(url).read()
		jsonobj2 = json.loads(response2)
		if len(jsonobj2) == 9:
			Templateaddroom = """<p> <a href="/admin/available_rooms/{{id}}/{{name}}">
			ADD ROOM </a></p>"""
			return template(Templateaddroom, id = idSpace , name = name)
		TemplateRooms = """%for item in list:
		<p> <a href="/admin/space/{{item['id']}}/{{item['name']}}"> {{item['name']}} </a></p>
		%end"""
		return template(TemplateRooms, list = jsonobj2["containedSpaces"])
		
class student(ndb.Model):
	IDuser = ndb.StringProperty()
	NameUser = ndb.StringProperty()
		
class available_rooms(ndb.Model):
	IDsala = ndb.StringProperty()
	namesala = ndb.StringProperty()
	
class check_in(ndb.Model):
	IDuser = ndb.StringProperty()
	IDsala = ndb.StringProperty()
			

