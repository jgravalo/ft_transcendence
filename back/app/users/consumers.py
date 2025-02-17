import json
import time
from channels.generic.websocket import WebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

#User = get_user_model()  # 👈 Esto obtiene tu modelo personalizado

class Connection(WebsocketConsumer):
    def connect(self):
        # Aceptar la conexión WebSocket
        # username = request.GET.get('user', '')  # 'q' es el parámetro, '' es el valor por defecto si no existe
        user = self.scope['user']
        print("username from ws:", user.username)
        self.accept()
        self.send(text_data=json.dumps({
            "message": "Conexión WebSocket exitosa from Django",
            "content": render_to_string("close_login.html");
            }))

    def disconnect(self, close_code):
        user = self.scope['user']
        user.is_active=False
        user.save()
        # logout(request)
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