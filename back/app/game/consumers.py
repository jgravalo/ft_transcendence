import json
import time
from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

async def do_match():
    print("from match")
    time.sleep(1)
    print("from match")

class AsyncMatch(AsyncWebsocketConsumer):
    async def connect(self):
        # Aceptar la conexión WebSocket
        await self.accept()
        await do_match()
        print("form connect")
        await self.send(text_data=json.dumps({"message": "Conexión Async WebSocket exitosa from Django"}))

    def disconnect(self, close_code):
        # Desconectar el WebSocket
        pass

    async def receive(self, text_data):
        # Recibir un mensaje desde el WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send(text_data=json.dumps({
                'message': message
            }))


class Match(WebsocketConsumer):
    def connect(self):
        # Aceptar la conexión WebSocket
        self.accept()
        self.send(text_data=json.dumps({"message": "Conexión WebSocket exitosa from Django"}))

    def disconnect(self, close_code):
        # Desconectar el WebSocket
        pass

    def receive(self, text_data):
        # Recibir un mensaje desde el WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        try:
            player1 = text_data_json['player1']
            player2 = text_data_json['player2']
            ballLeft = text_data_json['ballLeft']
            ballTop = text_data_json['ballTop']
            print("player1:", text_data_json['player1'])
            print("player2:", text_data_json['player2'])
            # Enviar un mensaje de vuelta al WebSocket
            self.send(text_data=json.dumps({
                'message': 'exito',
                'player1': player1,
                'player2': player2,
                'ballLeft': ballLeft,
                'ballTop': ballTop
            }))
        except:
            self.send(text_data=json.dumps({
                'message': 'error'
            }))
        
