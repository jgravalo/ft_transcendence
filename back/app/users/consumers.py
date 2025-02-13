import json
import time
from channels.generic.websocket import WebsocketConsumer
#from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

#User = get_user_model()  # 👈 Esto obtiene tu modelo personalizado

class Connection(WebsocketConsumer):
    def connect(self):
        # Aceptar la conexión WebSocket
        self.accept()
        self.send(text_data=json.dumps({"message": "Conexión WebSocket exitosa from Django"}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        # Recibir un mensaje desde el WebSocket
        text_data_json = json.loads(text_data)
        # message = text_data_json['message']
        try:
            # player1 = text_data_json['player1']
            # player2 = text_data_json['player2']
            # ballLeft = text_data_json['ballLeft']
            # ballTop = text_data_json['ballTop']
            # print("player1:", text_data_json['player1'])
            # print("player2:", text_data_json['player2'])
            # Enviar un mensaje de vuelta al WebSocket
            self.send(text_data=json.dumps({
            }))
        except:
            self.send(text_data=json.dumps({
                'message': 'error'
            }))
        
