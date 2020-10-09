import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Game, Player, Profile, Roast
import time
from django.utils import timezone
from datetime import timedelta

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
        print(type(self.channel_name))
        print(self.channel_name)
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
                player = Player(user= profile, state= 0, game= game, score = 0, channel_name = self.channel_name, admin=True)
            else:
                player = Player(user= profile, state= 0, game= game, score = 0, channel_name = self.channel_name)
            player.save()
            self.accept()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'game_data': game.json_data(),
                    'scroll': False
                }
            )
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'image_update',
                    'player': player.user.username,
                    "src": "../../../" + str(player.user.image)
                }
            )
            for p in game.player.all().exclude(pk=player.pk):
                json_data = {
                    "action": "image_update",
                    "player": p.user.username,
                    "src": "../../../" + str(p.user.image)
                }
                self.send(text_data=json.dumps(json_data))
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
        if game.empty():
            game.delete()
            return 
 
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_data': game.json_data(),
                'scroll': False
            }
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data)
        # message = text_data_json['message']
        game = self.get_game()
        player = self.get_player()
        if text_data_json['action'] == "startGame":
            if not player.admin or game.state != 0:
                return
            game.shuffle()
        elif text_data_json['action'] == 'roast':
            if player.state != 0 or game.state != 1 or player.submitted:
                return
            content = text_data_json['message']
            if len(content) > 400:
                return
            player.check_submission()
            roast = Roast(game=game, player=player, roast=content)
            roast.save()
        
            if game.roast_complete():
                game.clear_submissions()
                game.change_state(2)
            else:
                return
        elif text_data_json["action"] == "judge":
            if player.state != 2 or game.state != 2:
                return
            try:
                username = text_data_json["player"]
                profile = Profile.objects.get(username=username)
                winner = game.player.get(user=profile)
                winner.add_score()
                winning_roast = winner.roast.get()
                winning_roast.select()
            except Exception as e:
                print(e)
                return
            
            game.change_state(3)
            game_data = game.json_data()
            self.game_update({'game_data': game_data, 'scroll': True})
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_update',
                    'game_data': game_data,
                    'scroll': True
                }
            )
            time.sleep(5)
            if game.winner():
                game.change_state(4)
                game_data = game.json_data()
                self.game_update({'game_data': game_data, 'scroll': True})
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'game_update',
                        'game_data': game_data,
                        'scroll': True
                    }
                )
                time.sleep(3)
                game.shuffle()
                game.change_state(0)
            else:
                game.next_round(winner)
        elif text_data_json["action"] == "skip":
            if not player.admin or game.state in [0, 3, 4]:
                return
            game.skip()
        elif text_data_json["action"] == "time_out":
            if not player.admin or game.state in [0, 3, 4]:
                return
            if timezone.now() - game.time < timedelta(seconds=game.round_length):
                return
            for p in game.player.filter(submitted=False):
                if game.state == 1:
                    if p.state == 0:
                        print(f"admin kicks {p.user.username}")
                        if p.kickable:
                            print(f"kicked {p.user.username}")
                            async_to_sync(self.channel_layer.send)(
                                p.channel_name,
                                {
                                    'type': 'kick'
                                }
                            )
                        elif timezone.now() - p.joined <= timedelta(seconds=game.round_length):
                            pass
                        else:
                            p.kickable = True
                            p.save()

                elif game.state == 2:
                    if p.state ==2:
                        print(f"admin kicks {p.user.username}")
                        if p.kickable:
                            print(f"kicked {player.user.username}")
                            async_to_sync(self.channel_layer.send)(
                                p.channel_name,
                                {
                                    'type': 'kick'
                                }
                            )
                        elif timezone.now() - p.joined <= timedelta(seconds=game.round_length):
                            pass
                        else:
                            p.kickable = True
                            p.save()
            game.skip()
        # Send message to room group
        print("update")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_data': game.json_data(),
                'scroll': True
            }
        )

    # Receive message from room group
    def game_update(self, event):
        player = self.get_player()
        json_data = {
            "action": "game_update",
            "game": event["game_data"],
            "player": player.player_info(),
            "scroll": event["scroll"]
        }
        # Send message to WebSocket
        self.send(text_data=json.dumps(json_data))

    def image_update(self, event):
        json_data = {
            "action": "image_update",
            "player": event["player"],
            "src": event["src"]
        }
        self.send(text_data=json.dumps(json_data))

    def kick(self, event):
        self.send(text_data=json.dumps({"action": "exit"}))
        game = self.get_game()
        print("update")
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'game_update',
                'game_data': game.json_data(),
                'scroll': False
            }
        )