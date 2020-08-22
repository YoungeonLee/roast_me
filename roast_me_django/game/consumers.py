import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Game, Player, Profile
# from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound

class GameConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name
        #self.scope["session"].save()
        print(self.scope["session"].session_key)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.game = Game.objects.get(name=self.room_name)
        if not self.game.full():
            self.profile = Profile.objects.get(user_id=self.scope["session"].session_key)
            self.player = Player(user= self.profile, state= 0, game= self.game, score = 0)
            self.player.save()
            self.accept()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_update',
                }
            )
        else:
            self.close()
        

    def disconnect(self, close_code):
        # Leave room group
        self.player.delete()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_update',
            }
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        #message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_message',
                'message':self.channel_name
            }
        )

    # Receive message from room group
    def game_update(self, event):
        json_data = self.game.json_data()
        # Send message to WebSocket
        self.send(text_data=json.dumps(json_data))