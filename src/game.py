'''
Data model for the Connect-IG4 game. 
'''

from google.appengine.ext import db

class Player(db.Model):
    """A player in the connect4 game."""
    
    nickname = db.StringProperty(required=True)
    password = db.StringProperty()
    ip_address = db.StringProperty()
    listen_port = db.StringProperty()
    last_online = db.DateTimeProperty()
    online = db.BooleanProperty()
    
    # statistics
    won = db.IntegerProperty()
    lost = db.IntegerProperty()
    score = db.IntegerProperty()
    
    
class Game(db.Model):
    """A game in the connect4 game."""
    
    id = db.IntegerProperty(required=True)    
    
    creator = db.ReferenceProperty(Player, 'creator', 'own_games')
    opponent = db.ReferenceProperty(Player, 'opponent', 'other_games')
    
    status = db.StringProperty()
    """Must be one of the following:
        - 'WAITING'
        - 'PLAYING'
        - 'FINISHED'
        - 'ABANDONNED'
    """
    
    # We hold explicitly the winner and the looser for easier access
    winner = db.ReferenceProperty(Player, 'winner', 'won_games')
    looser = db.ReferenceProperty(Player, 'looser', 'lost_games')
    
    board = db.StringProperty()
    """ A string representation of the board """
    
    
class Config(db.Model):
    """Holds different configuration options"""
    
    current_game_id = db.IntegerProperty()
    