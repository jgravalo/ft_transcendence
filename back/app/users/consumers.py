import json
import time
from channels.generic.websocket import WebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync

#User = get_user_model()  # 👈 Esto obtiene tu modelo personalizado

class Connection(WebsocketConsumer):
	def connect(self):
		# Aceptar la conexión WebSocket
		# username = request.GET.get('user', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
		print('llego a WebSocket Connect')
		user = self.scope['user']
		print("username from ws:", user.username)
		self.accept()
		print('llego a accept')

		# Solo guardar si el usuario está autenticado
		if user.is_authenticated:
			user.is_online = True
			user.save()

		self.room_group_name = user.username
		print(f'room_group_name for user = {self.room_group_name}')
		# self.channel_layer.group_add(self.room_group_name, self.channel_name)
		async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
		"""
		self.send(text_data=json.dumps({
			"message": "Conexión WebSocket exitosa from Django",
			"status": user.is_online if user.is_authenticated else False,
			"content": render_to_string("close_login.html")
		}))
		"""

	def disconnect(self, close_code):
		print('desconexion desde el front')
		user = self.scope['user']
		if user.is_authenticated:
			user.is_online = False
			user.save()
		# logout(request)
		async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)
		# await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
		self.close()
		# pass

	def receive(self, text_data):
		# Recibir un mensaje desde el WebSocket
		text_data_json = json.loads(text_data)
		try:
			# message = text_data_json['message']
			# Enviar un mensaje de vuelta al WebSocket
			self.send(text_data=json.dumps({
			}))
		except:
			self.send(text_data=json.dumps({
				'message': 'error'
			}))

	def warn_player(self, event):
		context = {
			"link": event["link"],
			"user": event["user"]
		}
		self.send(text_data=json.dumps({
			"message": event["message"],
			"element": 'modalContainer',
			"content": render_to_string('invite.html', context)
		}))