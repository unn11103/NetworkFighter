from PodSixNet.Connection import ConnectionListener,connection
import sys
import pygame
from time import sleep
from pygame.locals import *


class OnlineGame(ConnectionListener):
    def __init__(self):
        pygame.init()
        size = width,height = 1000,600
        self.screen = pygame.display.set_mode(size)

        music = pygame.mixer.music.load('Sprites/Spider.mp3')
        pygame.display.set_caption("Online Game")
        pygame.mixer.music.play(-1)
        player1C = [pygame.image.load('Sprites/r_1.png'),pygame.image.load('Sprites/r_2.png'),
                           pygame.image.load('Sprites/r_3.png'),pygame.image.load('Sprites/r_4.png'),
                           pygame.image.load('Sprites/r_5.png'),pygame.image.load('Sprites/r_6.png'),
                           pygame.image.load('Sprites/r_7.png'),pygame.image.load('Sprites/r_8.png'),
                           pygame.image.load('Sprites/r_9.png')]
        player2C = [pygame.image.load('Sprites/c_1.png'),pygame.image.load('Sprites/c_2.png'),
                           pygame.image.load('Sprites/c_3.png'),pygame.image.load('Sprites/c_4.png'),
                           pygame.image.load('Sprites/c_5.png'),pygame.image.load('Sprites/c_6.png'),
                           pygame.image.load('Sprites/c_7.png'),pygame.image.load('Sprites/c_8.png'),
                           pygame.image.load('Sprites/c_9.png')]

        player1A = [pygame.image.load('Sprites/a_1.png'),pygame.image.load('Sprites/a_2.png'),pygame.image.load('Sprites/a_3.png'),pygame.image.load('Sprites/a_4.png'),
                    pygame.image.load('Sprites/a_5.png'),pygame.image.load('Sprites/a_6.png')]

        player2A = [pygame.image.load('Sprites/b_1.png'),pygame.image.load('Sprites/b_2.png'),pygame.image.load('Sprites/b_3.png'),pygame.image.load('Sprites/b_4.png'),
                    pygame.image.load('Sprites/b_5.png'),pygame.image.load('Sprites/b_6.png')]

        player1B = pygame.image.load('Sprites/r_b.png')
        player2B = pygame.image.load('Sprites/c_b.png')

        self.win1 = pygame.image.load('Sprites/win1.png')

        self.bg = (250,250,250)
        self.bgImg = pygame.image.load("Sprites/bg.jpg")
        self.players = []
        self.players.append(Player(player1C,player1A,player1B))
        self.players.append(Player(player2C,player2A,player2B))


        self.players[1].rect.x = width-self.players[1].rect.width

        print(self.players[1].rect.x)



        #counting frames for walk and attack
        self.walkcount = 0
        self.attackCount = 0
        self.isWalk = False

        self.gameID = None
        self.player = None

        self.clock = pygame.time.Clock()

        self.screen.fill(self.bg)


        address=input("Address of Server: ")
        try:
            if not address:
                host, port="localhost", 8000
            else:
                host,port=address.split(":")

            self.Connect((host, int(port)))
        except:
            print("Error Connecting to Server")
            print ("Usage:", "host:port")
            print ("e.g.", "localhost:31425")
            exit()


        #wait for both connections
        self.running = False

        #if both players not connected
        while not self.running :

            self.check_exit()
            self.Pump()
            connection.Pump()
            sleep(0.01)

        pygame.display.update()

    def check_keys(self):


        keys = pygame.key.get_pressed()
        if self.players[0].alive and self.players[1].alive :
            if keys[pygame.K_RIGHT] :

                if (self.players[0].stuck and self.player==0) :

                    self.players[self.player].isWalk = True
                    self.players[self.player].rect.x += 0
                else :
                    self.players[self.player].isWalk = True
                    self.players[self.player].rect.x += self.velocity
                    self.Send({"action":"move","x":self.velocity,"y":0,"player":self.player,"gameID":self.gameID})


            if keys[pygame.K_LEFT]:

                if(self.players[1].stuck and self.player == 1):
                    self.players[self.player].isWalk = True
                    self.players[self.player].rect.x -= 0

                else :
                    self.players[self.player].isWalk = True
                    self.players[self.player].rect.x -= self.velocity
                    self.Send({"action":"move","x":-self.velocity,"y":0,"player":self.player,"gameID":self.gameID})

            if keys[pygame.K_z] and self.players[self.player].sta >0 :
                self.players[self.player].doingHit = True
                self.Send({"action":"doingHit","player":self.player,"gameID":self.gameID})

            if keys[pygame.K_x] and self.players[self.player].sta >0 :
                self.players[self.player].isBlock = True
                self.Send({"action":"isBlock","player":self.player,"gameID":self.gameID})
        else :
            if keys[pygame.K_r] and (self.players[0].alive == False or  self.players[1].alive == False):
                print("wow dodge")
                self.Send({"action":"restart","gameID":self.gameID})


    def check_exit(self):
        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                pygame.quit()

    def Network_position(self,data):
        p = data['player']
        self.players[p].rect.x = data['x']
        self.players[p].rect.y = data['y']
        self.players[p].isWalk = True

    def Network_startgame(self,data):
        self.gameID = data['gameID']
        self.player = data['player']

        self.running = True

        self.velocity = data['velocity']

    def Network_checkHit(self,data):
        p = data['player']
        self.players[p].doingHit = True
        print("yeet")

    def Network_checkBlock(self,data):
        p = data['player']
        self.players[p].isBlock = True

    def Network_doRestart(self,data):
        print("restarted!")
        for p in self.players :
            p.alive = True
            p.health = 100
            self.players[0].rect.x = 0
            self.players[1].rect.x = 936


    #main loop
    def update(self):
        if not self.players[1].alive :
            self.screen.blit(self.win1,(0,0))
            self.check_keys()
            self.check_exit()
            connection.Pump()
            self.Pump()
        elif not self.players[0].alive :
            self.screen.blit(self.win2,(0,0))
            self.check_keys()
            self.check_exit()
            connection.Pump()
            self.Pump()

        else :
            for p in self.players :
                p.isWalk = False
                p.doingHit = False
                p.isBlock = False
                if p.sta < 100 :
                    p.sta+=2

            connection.Pump()
            self.Pump()
            self.check_exit()
            self.clock.tick(33)


            #initialize the default
            self.check_keys()

            self.screen.fill(self.bg)

            self.screen.blit(self.bgImg,(0,-100))



            #Handling events for players
            for p in self.players :

                if p.health <=0 :
                    p.alive = False

                #decrease player stamina
                if p.doingHit and p.sta >0:
                    p.sta -= 5
                elif p.isBlock and p.sta>0:
                    p.sta -= 3

                self.players[0].punchBox.x = self.players[0].rect.x+25
                self.players[1].punchBox.x = self.players[1].rect.x+15

                p.hitbox.x =p.rect.x+20

                #checking collision
                self.collideP = pygame.Rect.colliderect(self.players[0].hitbox,self.players[1].hitbox)
                self.hit0 = pygame.Rect.colliderect(self.players[0].punchBox,self.players[1].hitbox)
                self.hit1 = pygame.Rect.colliderect(self.players[1].punchBox,self.players[0].hitbox)

                if self.collideP :
                    p.stuck = True
                else :
                    p.stuck = False

                #doing damage
                if self.hit0 and self.players[0].doingHit == True and self.players[0].sta >0 and not self.players[1].isBlock:
                    print("hit0")
                    self.players[1].health -= 0.5
                    print(self.players[1].health)

                if self.hit1 and self.players[1].doingHit == True and self.players[1].sta>0 and not self.players[0].isBlock:
                    print("hit1")
                    self.players[0].health -= 0.5
                    print(self.players[0].health)


                #Drawing Hitboxes
                #pygame.draw.rect(self.screen,(255,0,0),p.hitbox,2)
                #pygame.draw.rect(self.screen,(0,255,0),p.punchBox,2)

                if self.walkcount +1 >=27:
                    self.walkcount = 0
                if self.attackCount +1 >=24:
                    self.attackCount = 0

                if p.isWalk :
                    self.screen.blit( p.img[self.walkcount//5],(p.rect.x,435))
                    self.walkcount +=1

                elif p.doingHit :
                    self.screen.blit(p.attack[self.attackCount//5],(p.rect.x,435))
                    self.attackCount +=1

                elif p.isBlock :
                    self.screen.blit(p.block,(p.rect.x,435))

                else :
                    self.screen.blit(p.img[0],(p.rect.x,435))

                #Drawing Health Bars
                pygame.draw.rect(self.screen,(255,0,0),(0,0,300,50))
                if self.players[0].alive :
                    pygame.draw.rect(self.screen,(0,255,0),(0,0,300-((300/100)*(100-self.players[0].health)),50))

                pygame.draw.rect(self.screen,(255,0,0),(1000-300,0,300,50))
                if self.players[1].alive :
                    pygame.draw.rect(self.screen,(0,255,0),(1000-300,0,300-((300/100)*(100-self.players[1].health)),50))

                #Drawing Stamina Bars
                pygame.draw.rect(self.screen,(255,0,0),(0,50,300,50))
                if self.players[0].sta >0 :
                    pygame.draw.rect(self.screen,(0,0,255),(0,50,300-((300/100)*(100-self.players[0].sta)),50))

                pygame.draw.rect(self.screen,(255,0,0),(1000-300,50,300,50))
                if self.players[1].sta >0 :
                    pygame.draw.rect(self.screen,(0,0,255),(700,50,300-((300/100)*(100-self.players[1].sta)),50))

        pygame.display.flip()


class Player(object) :
    def __init__(self,img,attack,block):
        self.alive = True
        self.stuck = False
        self.isBlock = False

        self.isWalk = False
        self.img = img
        self.attack = attack
        self.block = block

        self.tempimg = pygame.image.load('Sprites/r_1.png')
        self.cara2 = pygame.image.load('Sprites/c_1.png')
        self.rect = self.tempimg.get_rect()

        self.doingHit = False

        self.hitbox = pygame.Rect(self.rect.x,435,28,60)
        self.punchBox = pygame.Rect(self.rect.x,450,28,30)

        self.health = 100
        self.sta = 100

og =OnlineGame()
while 1 :
    og.update()
