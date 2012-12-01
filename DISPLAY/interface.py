import pygame, math, os
from pygame.locals import *

import random

from IMG import images
from UTIL import const, colors, load_image, button
from DISPLAY import text
from math import ceil, floor

#import threading
import Queue

class Interface( ):
    def __init__(self, screen, iH):
        self.textBox = pygame.Surface((251, 75))
        self.textBox.fill( colors.black )
        #for displaying messages or menus
        self.screen = screen
        self.invItems = []
        imgNames = ["interface_m.bmp", "interface.bmp"]
        self.imgs = range(2)
        for i in range( len(imgNames) ):
            self.imgs[i], r = load_image.load_image(imgNames[i],None)
        self.state = 'mainmenu'
        self.mainImg = self.imgs[0]
        self.scrollText = ['']*3
        self.On = True
        self.popupWin = None
        self.popupLoc = None
        self.inputHandler = iH
        images.load()
    
    def writeText(self, surface, loc, text, fgc, bgc, size=14, font=os.getcwd()+"/FONTS/gothic.ttf"):
        font = pygame.font.Font(font, size)
        surface.blit( font.render(text, 1, fgc, bgc), loc )

    def boxStat(self, stat, mStat, fgc, bgc, loc):
        (x, y) = loc
        maxBoxWidth = 90
        maxBox = pygame.Surface( (90, 11) )
        maxBox.fill(bgc)
        maxBox.set_alpha(192)
        currBoxWidth = int(90 * float(stat)/float(mStat))
        if currBoxWidth > 0:
            currBox = pygame.Surface( (currBoxWidth, 11) )
            currBox.fill(fgc)
            currBox.set_alpha(127)
            #self.mainImg.blit( maxBox, loc )
            self.mainImg.blit( currBox, loc )
        else: pass
    
    def circleStat(self, stat, fgc, bgc, loc, radius, mStat=20):
        pygame.draw
        (cx,cy) = loc
        tx = cx
        ty = cy - radius
        deg = int(360 * float(stat)/float(mStat))
        rad = math.radians(deg)
        pygame.draw.circle(self.mainImg, bgc, loc, radius)
        pygame.draw.line(self.mainImg, fgc, (tx,ty), (cx,cy))
        pygame.draw.line(self.mainImg, fgc, (cx,cy), (cx+ radius*math.sin( rad ), cy- radius*math.cos( rad ) ) )
        rect = (cx-radius,cy-radius,radius*2,radius*2)
        pygame.draw.arc(self.mainImg,fgc,rect,0,rad,1)
    
    def drawClock(self, x, y, Ticker):
        secs = Ticker.getSecs()
        mins = Ticker.getMins()
        hrs = Ticker.getHours()
        sRad = math.radians( 360* ( float(secs)/float(60) ) )
        mRad = math.radians( 360* ( float(mins)/float(60) ) )
        hRad = math.radians( 360* ( float(hrs)/float(12) ) )
        pygame.draw.line(self.mainImg, colors.black, (x,y), (x+ 14*math.sin( sRad ), y- 14*math.cos( sRad ) ) )
        pygame.draw.line(self.mainImg, colors.grey, (x,y), (x+ 12*math.sin( mRad ), y- 12*math.cos( mRad ) ), 2 )
        pygame.draw.line(self.mainImg, colors.grey, (x,y), (x+ 9*math.sin( hRad ), y- 9*math.cos( hRad ) ), 2)
        
    def update( self, game=None ):
        if self.state == 'mainmenu':
            self.mainImg = self.imgs[0]
            self.screen.blit( pygame.transform.scale(self.mainImg, (int(ceil(300 * 2.4)), 
                                                                    int(ceil(233 * 2.4)) ) ), (0, int(ceil(300 * 2.4))) )
            return
        self.mainImg = self.imgs[1].copy()
        stats = game.myHero.getPlayerStats()
        (cHP, mHP, cMP, mMP, sth, dex, itl, scr, kys, cEX, nEX, psn) = stats
        (armor, weapon) = ( game.myHero.getArmorEquipped(), game.myHero.getWeaponEquipped() )
        #self.mainImg, r = load_image.load_image("interface.bmp",None)
        #draw stats
        self.boxStat(cHP, mHP, colors.red, colors.black, (23, 163) )
        self.boxStat(cMP, mMP, colors.blue, colors.black, (23, 181) )
        self.boxStat(cEX, nEX, colors.green, colors.black, (23, 199) )
        
        if game.myHero.isPoisoned:
            self.mainImg.blit(images.mapImages[const.POISON], (134, 142))
        elif game.myHero.isDamned:
            self.mainImg.blit(images.mapImages[const.DAMNATION], (134, 142))
        
        # ticker
        self.drawClock(35, 142, game.Ticker)

        # gold
        goldBox = pygame.Surface( (30,30) )
        goldBox.blit( images.mapImages[const.GOLD], (0,0) )
        self.writeText(goldBox, (5,17), '$'+str(game.myHero.getGold()), colors.white, colors.black,10)
        self.mainImg.blit( goldBox, (134, 105) )
        # keys
        keyBox = pygame.Surface( (30,30) )
        keyBox.blit( images.mapImages[const.KEY], (-5,0) )
        self.writeText(keyBox, (13,17), 'x'+str(kys), colors.white, colors.black,10)
        self.mainImg.blit( keyBox, (97, 105) )
        
        if self.popupWin is not None:
            self.mainImg.blit( self.popupWin, self.popupLoc )
        
        self.mainImg.blit( self.textBox, (23,23) )
        self.screen.blit( pygame.transform.scale(self.mainImg, (720, 560) ), (0, 720) )
    
    def txtMessage(self, msg, game):
        width = 24
        '''
        for i in range( int( ceil( len(msg)/width ) ) ):
            if i > 0:
                self.writeTxtMessage( msg[ i*width:(i+1)*width], 
                                  game)
            else:
                self.writeTxtMessage( str(game.Ticker.getHours()%24)+":"+str(game.Ticker.getMins()%60)+'.'+str(game.Ticker.getSecs())+'-'+ msg[ i*width:(i+1)*width], 
                                  game)
        '''
        self.writeTxtMessage( str(game.Ticker.getHours()%24)+":"+str(game.Ticker.getMins()%60)+'.'+str(game.Ticker.getSecs())+'-'+ msg,
                              game)
        if game is not None:
            self.update(game)
    
    def writeTxtMessage(self, msg, game):
        self.textBox = pygame.Surface((254, 75))
        self.textBox.fill( colors.black )
        self.scrollText[0] = self.scrollText[1]
        self.scrollText[1] = self.scrollText[2]
        self.scrollText[2] = msg
        for i in range(3):
            Msg = text.Text( self.scrollText[i], os.getcwd()+"/FONTS/STEELFIS.TTF", 11, colors.white, colors.black, True, 60 )
            #Msg = pygame.transform.scale(Msg, ( int(ceil(Msg.get_width()*1.1)),   Msg.get_height() ))
            #Msg = font.render( self.scrollText[i], 1, colors.white, colors.black)
            self.textBox.blit(Msg, (0,25*i) )
    
    # displays message along with image of face
    def npcMessage(self, message, img):
        msgText = text.Text(message, os.getcwd()+"/FONTS/devinne.ttf", 14, colors.white, colors.gold, True, 16)
        for i in range( 0, 255, 8 ):
            borderBox = pygame.Surface( ( msgText.get_width()+ int(ceil(img.get_width()*2.4))+ int(ceil(20*2.4)), 
                                          msgText.get_height()+ int(ceil(img.get_width()*2.4)) ) )
            borderBox.fill( colors.grey )
            #borderBox.blit(msgText, (int(ceil(50*2.4)), int(ceil(10*2.4))) )
            borderBox.set_alpha( int(ceil(i*0.1)) )
            msgText.set_alpha(i)
            self.screen.blit( borderBox, 
                            ( self.screen.get_width()/2-borderBox.get_width()/2 , 150 ) )
            self.screen.blit( pygame.transform.scale(img,
                                                   (int(ceil(img.get_width()*2.4)),
                                                    int(ceil(img.get_width()*2.4)) ) ), 
                            ( self.screen.get_width()/2-borderBox.get_width()/2 + int(ceil(10*2.4)),
                              150 + int(ceil(10*2.4))  ) )
            self.screen.blit( msgText, 
                            ( (self.screen.get_width()/2-borderBox.get_width()/2)+int(ceil(50*2.4)) , 150 ) )
            pygame.display.flip()
        '''
        for i in range( 10, ( msgText.get_width()+ int(ceil(img.get_width()*2.4))+ int(ceil(20*2.4)) )/2, 5 ):
            borderBox = pygame.Surface( ( i*2, msgText.get_height()+ int(ceil(img.get_width()*2.4)) ) )
            borderBox.fill( colors.grey )
            borderBox.set_alpha(128)
            borderBox.blit( pygame.transform.scale(img,
                                                   (int(ceil(img.get_width()*2.4)),
                                                    int(ceil(img.get_width()*2.4)) ) ), 
                            (int(ceil(10*2.4)),
                             int(ceil(10*2.4))  ) )
            borderBox.blit(msgText, (int(ceil(50*2.4)), int(ceil(10*2.4))) )
            self.screen.blit( borderBox, 
                            ( self.screen.get_width()/2- i, 150 ) )
            
            self.screen.blit(pygame.transform.scale(borderBox,
                                                    (int( ceil(borderBox.get_width()*2.4)) , 
                                                     int( ceil(borderBox.get_height()*2.4) ) ) ), 
                                                     ( (self.screen.get_width()/2- msgText.get_width()/2) - i, 
                                                        150 ) )
            pygame.display.flip()
        ''' 
        while (pygame.event.wait().type != pygame.MOUSEBUTTONDOWN): pass
    
    # same as npcMessage but returns yes/no input
    def npcDialog(self, message, img):
        msgText = text.Text(message, os.getcwd()+"/FONTS/devinne.ttf", 18, colors.white, colors.gold, True)
        borderBox = pygame.Surface( ( msgText.get_width()+ int(ceil(img.get_width()*2.4))+ int(ceil(20*2.4)), 
                                      msgText.get_height()+ int(ceil(img.get_width()*2.4)) ) )
        borderBox.fill( colors.grey )
        buttons = [ button.Button( ( (self.screen.get_width()/2-borderBox.get_width()/2)+int(ceil(50*2.4)),
                                 150 + msgText.get_height() ),
                                 'Yes' ),
                    button.Button( ( (self.screen.get_width()/2-borderBox.get_width()/2)+int(ceil(50*2.4))+(borderBox.get_width()-200),
                                 150 + msgText.get_height() ),
                                 'No' )
                   ]
        for i in range( 0, 255, 8 ):
            #borderBox.blit(msgText, (int(ceil(50*2.4)), int(ceil(10*2.4))) )
            borderBox.set_alpha( int(ceil(i*0.1)) )
            msgText.set_alpha(i)
            self.screen.blit( borderBox, 
                            ( self.screen.get_width()/2-borderBox.get_width()/2 , 150 ) )
            self.screen.blit( pygame.transform.scale(img,
                                                   (int(ceil(img.get_width()*2.4)),
                                                    int(ceil(img.get_width()*2.4)) ) ), 
                            ( self.screen.get_width()/2-borderBox.get_width()/2 + int(ceil(10*2.4)),
                              150 + int(ceil(10*2.4))  ) )
            self.screen.blit( msgText, 
                            ( (self.screen.get_width()/2-borderBox.get_width()/2)+int(ceil(50*2.4)) , 150 ) )
            for b in buttons:
                self.screen.blit(b.img, (b.locX, b.locY ) )
            pygame.display.flip()
        
        while True:
            for e in pygame.event.get():
                e_ = self.inputHandler.getCmd(e)
                if e_ == pygame.K_RETURN:
                    return
                else:
                    (x, y) = pygame.mouse.get_pos()
                    for b in buttons:
                        if b.hit( x, y ):
                            return b.msg
        
    def boxMessage(self, message):
        
        msgText = text.Text(message, os.getcwd()+"/FONTS/devinne.ttf", 18, colors.white, colors.gold, True)
        for i in range( 0, 255, 8 ):
            borderBox = pygame.Surface( ( msgText.get_width(), msgText.get_height() ) )
            borderBox.fill( colors.grey )
            borderBox.set_alpha( int(ceil(i*0.1)) )
            msgText.set_alpha(i)
            self.screen.blit( borderBox, 
                            ( self.screen.get_width()/2-borderBox.get_width()/2, 150 ) )
            self.screen.blit( msgText, 
                            ( self.screen.get_width()/2-borderBox.get_width()/2, 150 ) )
            pygame.display.flip()
            
        while (pygame.event.wait().type != pygame.MOUSEBUTTONDOWN): pass