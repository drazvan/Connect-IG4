from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import os
from datetime import datetime, timedelta

template_path = os.path.join(os.path.dirname(__file__), 'templates/')
"""Path to the templates directory"""

from game import Player

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
        
        for player in Player.all().order("name"):
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


class APIRequest(webapp.RequestHandler):
    """Register request"""
        
    def post(self):
        # extract parameters      
        command = self.request.get("command")
        
        # put server's response between --- and ---
        self.response.out.write("---\n")
        
        # analyze commands
        if command == "register":  
            name = self.request.get("name")
            ip_address = self.request.get("ip")
            listen_port = self.request.get("port")
            
            # check if the player already exists
            existing = Player.all().filter("name = ", name)
            
            # If there's an existing player with the same name but different IP/Port
            # Shouldn't we just send back a FAIL?
            
            player = Player(name=name)
            
            for p in existing:
                player = p
            
            # set new properties    
            player.ip_address = ip_address
            player.listen_port = listen_port
            player.last_online = datetime.now()
            
            # save
            player.put()    
            
            self.response.out.write("OK")

        elif command == "ping":  
            name = self.request.get("name")
            
            # check if the player already exists
            existing = Player.all().filter("name = ", name)
            
            player = None
            
            for p in existing:
                player = p

            if p == None:
                self.response.out.write("UNKNOWN USER")
            else:            
                # set new properties    
                player.last_online = datetime.now()
                
                # save
                player.put()    
            
                self.response.out.write("OK")
            
        elif command == "list":
            """List all users"""
            
            self.response.out.write("OK\n")
            for player in Player.all().order("name"):
                self.response.out.write("%s, %s, %s\n" % 
                        (player.name, player.ip_address, player.listen_port))
                 
        else:
            self.response.out.write("UNKNOWN COMMAND")  
        
        self.response.out.write("---\n")


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
