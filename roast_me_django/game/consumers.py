import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Game, Player, Profile, Roast
import time
# from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
# docker run -p 6379:6379 -d redis:5

class GameConsumer(WebsocketConsumer):
    def get_game(self):
        return Game.objects.get(name=self.room_name)

    def get_profile(self):
        return Profile.objects.get(user_id=self.scope["session"].session_key)

    def get_player(self):
        profile = self.get_profile()
        game = self.get_game()
        return Player.objects.get(user=profile, game=game)

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
        game = self.get_game()
        if not game.full():
            profile = self.get_profile()
            if game.empty():
                player = Player(user= profile, state= 0, game= game, score = 0, admin=True)
            else:
                player = Player(user= profile, state= 0, game= game, score = 0)
            player.save()
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
        game = self.get_game()
        player = self.get_player()
        player_state = player.state

        if player.admin:
            print("admin left")
            player.delete()
            game.make_admin()
        else:
            print("player left")
            player.delete()

        if game.num_of_players() < 4:
            game.change_state(0)
        elif player_state != 0:
            game.shuffle()
        else:
            if game.roast_complete():
                game.clear_submissions()
                game.change_state(2)
            
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
        print(text_data)
        # message = text_data_json['message']
        game = self.get_game()
        if text_data_json['action'] == "startGame":
            game.shuffle()
        elif text_data_json['action'] == 'roast':
            content = text_data_json['message']
            player = self.get_player()
            player.check_submission()
            roast = Roast(game=game, player=player, roast=content)
            roast.save()
        
            if game.roast_complete():
                game.clear_submissions()
                game.change_state(2)
        elif text_data_json["action"] == "judge":
            username = text_data_json["player"]
            profile = Profile.objects.get(username=username)
            winner = game.player.get(user=profile)
            winner.add_score()
            winning_roast = winner.roast.get()
            winning_roast.select()
            if game.winner():
                game.change_state(4)
            else:
                game.change_state(3)
                self.game_update(None)
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_update',
                    }
                )
                time.sleep(5)
                game.next_round(winner)
        elif text_data_json["action"] == "skip":
            game.skip()
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_update',
            }
        )

    # Receive message from room group
    def game_update(self, event):
        player = self.get_player()
        game = self.get_game()
        json_data = {
            "game": game.json_data(),
            "player": player.player_info()
        }
        # Send message to WebSocket
        self.send(text_data=json.dumps(json_data))