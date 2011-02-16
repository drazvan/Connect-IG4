'''
The Connect-IG4 server will be accessible through the API presented below. 
In order to send a command to the server a valid HTTP request must be sent with 
the requested parameters sent as POST data. The requests are sent to the URL 
http://connectig4.appspot.com/api.

Sending a request
-----------------
A request is sent using the HTTP protocol as presented below. An HTTP request is
composed of two parts: header and data. The header is ended by a blank line. 
You will use only three header options as presented below (Host, Content-Type 
and Content-Length). Obviously, the Content-Length value must correspond to the 
length of the data.

    POST /api HTTP/1.1
    Host: connectig4.appspot.com
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 41

    some_data_aaa_bbbb_aaa_bbb

The data part of the HTTP request will be something having the form:
    command=some_command&param1=value1&param2=value2...&param_n=value_n

where some_command is the name of the requested command and param_k represent 
the parameters required by the API call. Be careful not to include spaces inside
the values.

Parsing a response
------------------
Normally the server's response will look like this:

    HTTP/1.1 200 OK
    Content-Type: text/html; charset=utf-8
    Cache-Control: no-cache
    Expires: Fri, 01 Jan 1990 00:00:00 GMT
    Date: Mon, 14 Feb 2011 21:17:24 GMT
    Server: Google Frontend
    Transfer-Encoding: chunked

    a
    ---
    some_response
    ---
    0
    
You will only be interested in what is between "---" and "---" and you will 
ignore the rest of the options/content. Ideally you should make a function that
takes the whole input and returns only the part between "---".
'''

from datetime import datetime, timedelta
from google.appengine.ext import webapp
from game import Player, Game, Config


class APIRequest(webapp.RequestHandler):
    """Register request"""
    
    def _get(self, entity, property, value):
        """A shortcut since the data store does not have a method get."""
        
        entities = entity.all().filter(property, value)
        
        if entities.count() > 0:
            return entities[0]
        
        return None
    
    def _config(self):
        """Returns the configuration instance"""
        
        config = self._get(Config, "current_game_id >=", 0)
        
        if config == None:
            config = Config(current_game_id = 1)
            config.put()
            
        return config
            
    def _authenticate(self, nickname, password):
        """Internal method used for user authentication.
        
        Checks if the password for the given user is correct.
        
        Return value:
            - a Player instance if the user has be authenticated
            - None otherwise
        """
            
        player = self._get(Player, "nickname = ", nickname)
        
        # if it's a new player
        if player == None or password != player.password: 
            return None
        
        return player
        
    def _purge(self):
        """ Purge all dead players (last_online > 90 secs) """

        # Get players who haven't pinged in more than 90secs and who are currently marked as online
        players = Player.all().filter("last_online < ", datetime.now() - timedelta(seconds=90)).filter("online = ", True)
        for player in players:
            player.online = False # Not online anymore
            player.put() # save
        
            # Get his former game
            player_game = Game.all().filter("creator =", player.nickname).filter("status = ", 'PLAYING')
            
            for game in player_game:
                game.status = 'ABANDONNED' # game OVER
                game.put() # save
            
            
    def connect(self):
        """This command must be sent to the server whenever a player connects 
        for the first time. 
        
        If the player with the given nickname does not already exist then it is 
        created with the given password. If it already exists and the password 
        is incorrect FAIL is returned. If he's already online, he won't be connected
        to prevent messing up with the IP and Port

        Parameters
            - nickname : is the name of the player and it must be unique.
            - password: is the password for the given player.
            - ip : is the local IP address of the player. It is a string like 
              192.168.10.104.
            - port : is the port on which the player waits for connections from 
            other players.
            
        Return value
            - OK if everything is ok and the player has been added.
            - FAIL for any other errors (i.e. bad password, bad IP, bad port, etc.)
        """  
        
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        ip_address = self.request.get("ip")
        listen_port = self.request.get("port")
        
        # check if the player already exists
        player = self._get(Player, "nickname = ", nickname)
        
        # if it's a new player
        if player == None:
            player = Player(nickname=nickname, password=password)
        
        # It's a known player
        if password != player.password:
            self.response.out.write("FAIL Incorrect password")
            return 
        elif player.online == True:
            # It will be triggered if the player has left without saying 'disconnect'
            # 90 seconds later, the player will be able to connect himself if someone triggers a purge
            self.response.out.write("FAIL Already connected elsewhere")
            return
        
        # set new properties, user authenticated  
        player.ip_address = ip_address
        player.listen_port = listen_port
        player.last_online = datetime.now()
        player.online = True
        
        # save
        player.put()    
        
        # respond with OK
        self.response.out.write("OK")
      
    def disconnect(self):
        """
            This command needs to be called before leaving the client, it marks the player as offline.
            If the user doesn't disconnect, he'll need to wait 90 seconds to be purged automatically
            
            Parameters
                - nickname : is the name of the player.
                - password : is the password for the given player.
            
            Return value
                - OK if everything is ok and the player has been added.
                - FAIL for any other errors (i.e. bad password, bad IP, bad port, etc.)
        """
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        
        # authenticate        
        player = self._authenticate(nickname, password)
        if player == None:
            self.response.out.write("FAIL Authentication failed")
            return
        
        # Mark as offline
        player.online = False
        
        # Save
        player.put()
        
        # Select his former game
        player_game = Game.all().filter("creator =", player.nickname).filter("status = ", 'PLAYING')
        
        for game in player_game:
            game.status = 'ABANDONNED' # game OVER
            game.put() # Save
         
        # respond with OK
        self.response.out.write("OK")
      
    def ping(self):
        """Must be sent to the server every 15 seconds so that the server knows 
        which players are online and which are offline.

        Parameters
            - nickname : is the name of the player.
            - password : is the password for the given player.
        
        Return value
            - OK if everything is ok.
            - FAIL for any other errors (i.e. bad password, bad nickname, etc.)
        """
        
        nickname = self.request.get("nickname")
        password = self.request.get("password")

        # authenticate        
        player = self._authenticate(nickname, password)
        if player == None:
            self.response.out.write("FAIL Authentication failed")
            return
        
        # set new properties    
        player.last_online = datetime.now()
        player.online = True
        
        # save
        player.put()    
    
        # respond with OK
        self.response.out.write("OK")
  
    def create(self):
        """Indicates that the given player is willing to start a game and is 
        waiting for an opponent.

        Parameters
            - nickname : is the name of the player.
            - password : is the password for the given player.
            
        Return value
            - OK followed by a game id.
            - FAIL for any errors.
        """
        
        nickname = self.request.get("nickname")
        password = self.request.get("password")

        # authenticate        
        player = self._authenticate(nickname, password)
        if player == None:
            self.response.out.write("FAIL Authentication failed")
            return
        
        # check if he's already playing
        game = Game.all().filter("creator =", player.nickname).filter("status = ", 'PLAYING')
        if game != None:
            self.response.out.write("FAIL Already playing")
            return
        
        # create a new game
        config = self._config()
        game = Game(id = config.current_game_id)
        
        # save new config
        config.current_game_id = config.current_game_id + 1
        config.put();
        
        game.creator = player
        game.status = 'WAITING'
        
        # save game
        game.put()
        
        # respond with OK + game id
        self.response.out.write("OK\n%s" % game.id )
        
    def list(self):
        """Gives the list of all online players that have created a game and 
        are waiting for an opponent. It takes no parameters.

        Return value
            - OK followed by the list of players.
            - FAIL for any errors.
        """
        
        # Purge dead players from the list to prevent listing dead clients
        self._purge()
        
        self.response.out.write("OK\n")
        
        for game in Game.all().filter("status = ", "WAITING"):
            self.response.out.write("%s\n" % game.creator.nickname) 
            
        
    def join(self):
        """Indicates that the given player wants to join the game created by 
        some other player.

        Parameters
            - nickname : is the name of the player.
            - password : is the password for the given player.
            - opponent : is the name of the player that has created the game (previously retrieved with the 'list' command)

        Return value
            - OK followed by the IP address and port of the opponent.
            - FAIL for any errors.
        """
        
        # Purge dead players before to prevent trying to connect to a dead client
        self._purge()
        
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        opponent_nickname = self.request.get("opponent")

        # authenticate        
        player = self._authenticate(nickname, password)
        if player == None:
            self.response.out.write("FAIL Authentication failed")
            return
        
        # check existing opponent, the purge before is important here ;)
        opponent = self._get(Player, "nickname = ", opponent_nickname)
        
        if opponent == None:
            self.response.out.write("FAIL No opponent with the given nickname")
            return
        
        # check if ther's any WAITING game by the given nickname
        games = opponent.own_games.filter("status = ", "WAITING")
        if games.count() == 0:
            self.response.out.write("FAIL No game")
            return
        
        game = games[0]
        
        # update game's status
        ### BUT MAYBE THE CREATOR SHOULD UPDATE IT WHEN THE PLAYER ACTUALLY 
        ### CONNECTS TO HIM...
        game.opponent = player
        game.status = 'PLAYING'
        game.put()
        
        # return OK
        self.response.out.write("OK\n%s, %s" % 
                        (game.creator.ip_address, game.creator.listen_port))
        

    def update(self):
        """Update the status of a game. Only the player that created the game 
        can update its status.

        Parameters
            - nickname : is the name of the player.
            - password : is the password for the given player.
            - game : is the id of the game.
            - status: can be 'PLAYING' or 'FINISHED'.
            - winner: can be a nickname or 'NONE' if the game is not finished yet.
            - board: the board configuration or 'NONE'.

        Return value
            OK.
            FAIL for any errors.
        """
        
        # We purge here to launch this as often as possible
        self._purge()
        
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        game_id = self.request.get("game")
        
        # These parameters are optional
        status = self.request.get("status")
        winner = self.request.get("winner")
        board = self.request.get("board")
        
        # authenticate        
        player = self._authenticate(nickname, password)
        if player == None:
            self.response.out.write("FAIL Authentication failed")
            return
        
        # check the game
        game = self._get(Game, "id = ", int(game_id))
        if game == None:
            self.response.out.write("FAIL No game")
            return
        
        # check if it's the owner
        if game.creator.nickname != nickname:
            self.response.out.write("FAIL Not the creator")
            return
        
        if status != None and status != "":
            game.status = status
            
        if winner != None and winner != "":
            if not winner in [game.creator.nickname, game.opponent.nickname]:
                self.response.out.write("FAIL Invalid winner")
                return 
            
            if winner == game.creator.nickname:
                game.winner = game.creator
                game.looser = game.opponent
            else:
                game.winner = game.opponent
                game.looser = game.creator
                
        if board != None and board != "":
            game.board = board
        
        # save the info
        game.put()
        
        # respond with OK
        self.response.out.write("OK")
        
    def post(self):
        # extract parameters      
        command = self.request.get("command")
        
        # put server's response between --- and ---
        self.response.out.write("---\n")
        
        # analyze commands
        if command == "connect":  
            self.connect()

        elif command == "ping":  
            self.ping()
            
        elif command == "create":
            self.create()
            
        elif command == "list":
            self.list()
            
        elif command == "join":
            self.join()
                     
        elif command == "update":
            self.update()
            
        elif command == "disconnect":
            self.disconnect()
            
        else:
            self.response.out.write("FAIL Unknown command")  
        
        self.response.out.write("\n---\n")
