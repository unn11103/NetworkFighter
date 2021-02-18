import PodSixNet.Channel
import PodSixNet.Server
from time import sleep


class ClientChannel(PodSixNet.Channel.Channel):

    #Create a function that will respond to a request to move a player
    def Network_move(self, data):

        #Fetch the data top help us identify which game needs to update
        gameID = data['gameID']
        player = data['player']
        x = data['x']
        y = data['y']

        #Call the move function of the server to update this game
        self._server.move_player(x, y, gameID, player)

    def Network_doingHit(self,data):
        gameID = data['gameID']
        player = data['player']
        self._server.player_doingHit(gameID,player)

    def Network_isBlock(self,data):

        gameID = data['gameID']
        player = data['player']
        self._server.player_isBlock(gameID,player)

    def Network_restart(self,data):
        print("doing restart")
        gameID = data['gameID']
        self._server.restart_game(gameID)

class MyServer(PodSixNet.Server.Server) :
    channelClass = ClientChannel

    def __init__(self, *args, **kwargs):
        PodSixNet.Server.Server.__init__(self, *args, **kwargs)

        self.games = []
        self.queue = None
        self.gameIndex = 0
        self.restartCount = 0
        self.velocity = 8



    def Connected(self,channel,addr):
        print('New Connection : ', channel)

        if self.queue == None :
            channel.gameID = self.gameIndex
            self.queue = Game(channel,self.gameIndex)
        else :
            channel.gameID = self.gameIndex
            self.queue.player_channels.append(channel)

            for i in range(0,len(self.queue.player_channels)):
                self.queue.player_channels[i].Send({"action":"startgame","player":i,"gameID":self.queue.gameID,"velocity":self.velocity})

            #creating player list
            self.games.append(self.queue)

            self.queue = None

            self.gameIndex +=1

    def move_player(self,x,y,gameID,player):
        g = self.games[gameID]

        g.players[player].move(x,y)

        for i in range(0,len(g.player_channels)):
            if not i == player :
                g.player_channels[i].Send({"action":"position","player":player,"x":g.players[player].x,"y":g.players[player].y})

    def player_doingHit(self,gameID,player):
        g = self.games[gameID]
        for i in range(0,len(g.player_channels)):
            if not i == player :
                g.player_channels[i].Send({"action":"checkHit","player":player})

    def player_isBlock(self,gameID,player):
        g = self.games[gameID]

        for i in range(0,len(g.player_channels)):
            if not i == player :
                g.player_channels[i].Send({"action":"checkBlock","player":player})

    def restart_game(self,gameID):
        g = self.games[gameID]
        print("restarting...")
        g.players[0].x = 0
        g.players[1].x = 936
        for i in range(0,len(g.player_channels)):
            g.player_channels[i].Send({"action":"doRestart"})





class Game(object):

    #Constructor
    def __init__(self, player, gameIndex):

        #Create a list of players
        self.players = []
        self.players.append(Player(0, 400))
        self.players.append(Player(936, 400))

        #Store the network channel of the first client
        self.player_channels = [player]

        #Set the game id
        self.gameID = gameIndex



#Create a player class to hold all of our information about a single player
class Player(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def move(self,x,y):
        self.x +=x
        self.y +=y



#connection
address=input("Host:Port (localhost:8000): ")
if not address:
    host, port="localhost", 8000
else:
    host,port=address.split(":")

myServer = MyServer(localaddr=(host, int(port)))

print("Starting Server ")
while 1 :
    myServer.Pump()
    sleep(0.01)


