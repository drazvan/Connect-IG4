import time, urllib, sys

#API_URL = 'http://connectig4.appspot.com/api'
API_URL = 'http://localhost:8080/api'

def getStatus(answer):
    """ The status of the answer returned by the API is in the 2nd line"""
    return answer.splitlines()[1]

def connect(nickname, password, ip, port):
    """ Connect the client to the server
        Return the status of the connection, either OK or FAIL
    """
    
    data = {'command' : 'connect', 'nickname': nickname, 'password': password, 'ip': ip, 'port': port}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))
    
    return getStatus(handler.read())
    
def ping(nickname, password):
    """ Pings the server to say that we are ALIVE """
    
    data = {'command' : 'ping', 'nickname': nickname, 'password': password}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))
    
    return getStatus(handler.read())
    
def disconnect(nickname, password):
    """ Pings the server to say that we are ALIVE """

    data = {'command' : 'disconnect', 'nickname': nickname, 'password': password}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))

    return getStatus(handler.read())
    
def create(nickname, password):
    """ Create a new game for the player """
    
    data = {'command' : 'create', 'nickname': nickname, 'password': password}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))
    answer = handler.read()
    
    return {'status' : getStatus(answer), 'game' : answer}
    
def join(nickname, password, opponent):
    """ Joins the game started by opponent """
    
    data = {'command' : 'join', 'nickname': nickname, 'password': password, 'opponent': opponent}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))
    answer = handler.read()
    
    return {'status' : getStatus(answer), 'data' : answer}
    
def listPlayers():
    """ List all the waiting players """
    
    data = {'command' : 'list'}
    handler = urllib.urlopen(API_URL, urllib.urlencode(data))
    answer = handler.read()
    
    return {'status' : getStatus(answer), 'data' : answer}
    

if __name__ == "__main__":
        
    if len(sys.argv) == 5:
            nickname = sys.argv[1]
            password = sys.argv[2]
            ip = sys.argv[3]
            port = sys.argv[4]
            
            connection = connect(nickname, password, ip, port)
            print connection
    else:
        connection = "FAIL"

    # Loop until the user is connected
    while (connection.startswith("FAIL")):
        print "Please connect yourself to the server."
        nickname = raw_input("Enter your nickname : ")
        password = raw_input("Enter your password : ")
        ip = raw_input("Enter your network IP : ")
        port = raw_input("Enter the port : ")

        connection = connect(nickname, password, ip, port)

    # Set the last time we pinged at the return of the request
    last_ping = time.time()

    # connection is OK, we need to stay alive until the user decides to leave the loop
    while (connection == "OK"):
        # If the last ping is more than 10 seconds ago, we way to the server that we are still here, waiting.
        if ((time.time()-last_ping) > 10):
            # This is a bit useless as the connection will still be alive if we use the same credentials. Just in case the server is down.
            connection = ping(nickname, password)  
            last_ping = time.time()
            print "\nPING!\n"
    
        # Ask the user what he wants to do now
        choice = 0
    
        while (choice == 0):
            print "1 - Create"
            print "2 - Join"
            print "3 - List"
            print "42 - Quit"
        
            choice = raw_input("What do you want to do ? : ")
    
            if (int(choice) == 1):
                answer = create(nickname, password)
                connection = answer['status']
                print 'Game id : ' + answer['game']
        
            elif (int(choice) == 2):
                opponent = "FAIL"
                while (opponent.startswith("FAIL")):
                    opponent = raw_input("Enter your oppenent's name : ")
                    answer = join(nickname, password, oppenent)
                    opponent = answer['status']
            
                print "Answer : " + answer['data']
            
            elif (int(choice) == 3):
                answer = listPlayers()
                print answer['data']
        
            elif (int(choice) == 42):
                print disconnect(nickname, password)
                connection = "FAIL"
    
    print "Disconnected"