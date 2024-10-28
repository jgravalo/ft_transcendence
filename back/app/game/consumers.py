import json
from channels.generic.websocket import WebsocketConsumer

class Match(WebsocketConsumer):
    def connect(self):
        # Aceptar la conexión WebSocket
        self.accept()

    def disconnect(self, close_code):
        # Desconectar el WebSocket
        pass

    def receive(self, text_data):
        # Recibir un mensaje desde el WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enviar un mensaje de vuelta al WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
