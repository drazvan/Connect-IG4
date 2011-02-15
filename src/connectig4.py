import os
from datetime import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from game import Player
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
        
class GamesPage(webapp.RequestHandler):
    """Games page"""
        
    def get(self):
        self.response.out.write(template.render(template_path + 'games.html', 
                                                { 'Games' : 'active'
                                                       }))


class ScoresPage(webapp.RequestHandler):
    """Scores page"""
        
    def get(self):
        self.response.out.write(template.render(template_path + 'scores.html', 
                                                { 'Scores' : 'active'
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
                                      ('/scores', ScoresPage),
                                      ('/about', AboutPage),
                                      ('/api', APIRequest)
                                      ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
