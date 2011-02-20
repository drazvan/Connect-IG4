import os
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from game import Player
from game import Game
from api import APIRequest

template_path = os.path.join(os.path.dirname(__file__), 'templates/')
"""Path to the templates directory"""


class MainPage(webapp.RequestHandler):
    """Main page"""
        
    def get(self):
        self.response.out.write(template.render(template_path + 'index.html', 
                                                { 'Home' : 'active'
                                                       }))

class PlayersPage(webapp.RequestHandler):
    """Players page"""
    
    def get(self):
        # see who's online now (the last 30 minutes)
        now = datetime.now()
        
        players = []
        
        for player in Player.all().order("nickname"):
            dif = now - player.last_online
            if dif.days * 84000 + dif.seconds > 60:
                player.online = False
            else:
                player.online = True
                
            players.append(player)
        
        self.response.out.write(template.render(template_path + 'players.html', 
                                                { 'Players' : 'active', 
                                                  'players' : players, 
                                                       }))

class GridPage(webapp.RequestHandler):
    """Games page"""
        
    def get(self):
        
        game_id = self.request.get("game")
        board = "------------------------------------------"
        
        games = Game.all().filter("id = ", int(game_id))
        if games.count() > 0:
            game = games[0]
            board = game.board

            # ignore invalid boards            
            if board == None or len(board) < 42:
                board = "------------------------------------------"
                
            self.response.out.write(template.render(template_path + 'grid.html', 
                                                { 'Games' : 'active', 
                                                  'board' : board,
                                                  'game' : game 
                                                       }))

class GridStrPage(webapp.RequestHandler):
    """Games page"""
        
    def get(self):
        
        game_id = self.request.get("game")
        board = "------------------------------------------"
        
        games = Game.all().filter("id = ", int(game_id))
        if games.count() > 0:
            game = games[0]
            board = game.board

            # ignore invalid boards            
            if board == None or len(board) < 42:
                board = "------------------------------------------"
                
        self.response.out.write(board)
        
class GamesPage(webapp.RequestHandler):
    """Games page"""
        
    def get(self):
        
        
        self.response.out.write(template.render(template_path + 'games.html', 
                { 'Games' : 'active',
                 'games_waiting' : Game.all().filter("status =", "WAITING"), 
                 'games_playing' : Game.all().filter("status =", "PLAYING"),
                 'games_finished' : Game.all().filter("status =", "FINISHED"),
                       }))


class ScoresPage(webapp.RequestHandler):
    """Scores page"""
        
    def get(self):
        
        for player in Player.all():
            # avoid NoneType problems
            if not player.won:
                player.won = 0
            if not player.lost:
                player.lost = 0
            if not player.created:
                player.created = 0
            if not player.abandoned:
                player.abandoned = 0
                
            # compute score
            player.score = 10 * player.won - 3 * player.lost
            player.put() 
        
        self.response.out.write(template.render(template_path + 'scores.html', 
                                                { 'Scores' : 'active',
                                                  'players' : Player.all().order("-score")
                                                       }))
          
          
class AboutPage(webapp.RequestHandler):
    """About page"""
        
    def get(self):
        self.response.out.write(template.render(template_path + 'about.html', 
                                                { 'About' : 'active'
                                                       }))       

        
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/players', PlayersPage) ,
                                      ('/games', GamesPage),
                                      ('/grid', GridPage),
                                      ('/gridstr', GridStrPage),
                                      ('/scores', ScoresPage),
                                      ('/about', AboutPage),
                                      ('/api', APIRequest),
                                      ('/purge', APIRequest),
                                      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
