import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PrivateChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para un chat privado entre dos usuarios.
    """
    async def connect(self):
        """
        Se ejecuta cuando un usuario se conecta.
        - Se obtiene el nombre único de la sala a partir de los dos usuarios en el chat.
        - Se une al usuario a la sala.
        """
        print('conecta socket')
        self.user1 = self.scope['user'].id  # Usuario actual
        self.user2 = self.scope['url_route']['kwargs']['other_user_id']  # ID del otro usuario

        # Asegurar que el ID más bajo siempre va primero para que la sala sea única
        self.room_name = f'chat_{min(self.user1, self.user2)}_{max(self.user1, self.user2)}'
        self.room_group_name = f'private_{self.room_name}'

        # Unir el canal WebSocket del usuario al grupo en Redis
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """
        Se ejecuta cuando un usuario se desconecta.
        - Se elimina del grupo de chat en Redis.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Se ejecuta cuando el WebSocket recibe un mensaje del usuario.
        - El mensaje se envía a Redis para que lo reciba el otro usuario.
        """
        data = json.loads(text_data)
        message = data['message']
        sender = self.scope['user'].username  # Obtener el nombre del usuario actual

        # Enviar el mensaje a la otra persona en el chat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )

    async def chat_message(self, event):
        """
        Se ejecuta cuando un mensaje llega desde el grupo en Redis.
        - Envía el mensaje al frontend.
        """
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
