from channels.generic.websocket import AsyncWebsocketConsumer
import json
#from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.apps import apps
from urllib.parse import parse_qs

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
        print('user =', self.scope['user'])
        self.user1 = self.scope['user'].id  # Usuario actual
        # self.user2 = self.scope['url_route']['kwargs']['other_user_id']  # ID del otro usuario
        # User = apps.get_model('users', 'User')
        self.user2 = parse_qs(self.scope["query_string"].decode()).get("user", [None])[0]
        # self.user2 = await sync_to_async(User.objects.get)(id=self.user2)

        print('user1:', self.user1)
        print('user2:', self.user2)

        self.user1 = int(self.user1)
        self.user2 = int(self.user2)

        # Asegurar que el ID más bajo siempre va primero para que la sala sea única
        self.room_name = f'chat_{min(self.user1, self.user2)}_{max(self.user1, self.user2)}'
        self.room_group_name = f'private_{self.room_name}'
        print(f"🔗 Conectando a la sala {self.room_group_name}")

        # Unir el canal WebSocket del usuario al grupo en Redis
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ Conexión aceptada para {self.channel_name}")

        try:
            # Obtener modelos dinámicamente
            print('obteniendo modelos')
            Group = apps.get_model('chat', 'Group')
            Message = apps.get_model('chat', 'Message')

            # Buscar o crear la sala de chat
            print('instanciando grupo')
            from django.core.exceptions import ObjectDoesNotExist
            try:
                group = await sync_to_async(Group.objects.get)(room=self.room_group_name)
            except ObjectDoesNotExist:
                group = await sync_to_async(Group.objects.create)(room=self.room_group_name)

            print('instanciando lista de mensajes')
            # Obtener los mensajes de la sala
            messages = await sync_to_async(lambda: list(group.history.all()))()

            print('instanciando bucle de mensajes')
            # Enviar los mensajes anteriores al usuario
            for msg in messages:
                print('es el message')
                message = msg.message
                print('es el username')
                sender = await sync_to_async(lambda: msg.user.username)()
                print('es el role')
                role = 'me' if sender == self.scope['user'].username else 'sender'
                print('old message: >>>', message)
                await self.send(text_data=json.dumps({
                    'message': message,
                    'sender': sender,
                    'role': role
                }))
            print('✅chat recuperado')
        except Exception as e:
            print("❌ Error al obtener mensajes:", e)

    async def disconnect(self, close_code):
        """
        Se ejecuta cuando un usuario se desconecta.
        - Se elimina del grupo de chat en Redis.
        """
        print(f"❌ Desconectando de {self.room_group_name}")
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

        # Guardar mensaje en la base de datos de forma asíncrona
        try:
            Group = apps.get_model('chat', 'Group')
            Message = apps.get_model('chat', 'Message')
            print('modelos extraidos')

            # Usar sync_to_async para consultas a la base de datos
            group = await sync_to_async(Group.objects.get)(room=self.room_group_name)
            chat = await sync_to_async(Message.objects.create)(user=self.scope['user'], message=message)
            print('modelos guardados')

            # Relación ManyToMany hay que usar `.add()` dentro de `sync_to_async`
            await sync_to_async(group.history.add)(chat)

            print('✅chat guardado')
        except Exception as e:
            print("❌ Error al obtener mensajes:", e)

        # Enviar el mensaje a la otra persona en el chat
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender
            }
        )
        print(f"📤 Mensaje enviado al grupo {self.room_group_name}")

    async def chat_message(self, event):
        """
        Se ejecuta cuando un mensaje llega desde el grupo en Redis.
        - Envía el mensaje al frontend.
        """
        print(f"📬 Mensaje recibido en grupo: {event}")
        message = event['message']
        sender = event['sender']
        if sender == self.scope['user'].username:
            role = 'me'
        else:
            role = 'sender'
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'role': role
        }))
        print(f"➡️ Mensaje enviado a cliente WebSocket")
