from types import *
import pygame, os, cPickle, random, gzip

from MAP import world, mapgen, mazegen, map, wilds

from UTIL import queue, const, colors, eztext, load_image, misc
from IMG import images, spritesheet

from SCRIPTS import npcScr, mapScr

from random import choice

displayOpts = ['fore', 'back', 'both']

# Eztext courtesy of http://www.pygame.org/project-EzText-920-.html
class Handler():
    
    def __init__(self, cPos):
        self.cursorPos = cPos
        self.currentTile = 0
        self.sideImg, sideRect = load_image.load_image('sidebar.bmp')
        self.npcImg = {}
        npcAvatar = pygame.Surface((const.blocksize, const.blocksize))
        for n in npcScr.npcList:
            npcImgFilename = n+'.bmp'
            npcImgs = images.loadNPC(npcImgFilename)
            self.npcImg[ n ] = npcImgs[2]
        #self.npcImg, npcR = load_image('npc.bmp')
        self.drawMode = False
        self.cursorColor = colors.white
        self.offset = 0
        self.numImages = len(mapImages)
        self.topX = 0
        self.topY = 0
        self.visited = []
        
        self.BFSQueue = queue.Queue()
        
        self.mouseAction = 'draw'
        self.selecting = False
        
        self.selectBoxPoints = None
        
        self.placeNPC = False
        
        self.myMap = myWorld.currentMap
        
        self.editorImages = range(7)
        editorSpriteSheet = spritesheet.spritesheet('editorsheet.bmp')
        for i in range(7):
            self.editorImages[i] = editorSpriteSheet.image_at((i*const.blocksize, 0, const.blocksize, const.blocksize), -1 )
    
    def drawBox(self, pos, color):
        (x,y) = pos
        boxPoints = ( (x,y), (x,y+blocksize), (x+blocksize,y+blocksize), (x+blocksize,y) )
        pygame.draw.lines( gridField, color, True, boxPoints, 1 )

    def switchTile(self):
        self.currentTile += 1
        self.currentTile = self.currentTile % self.numImages
    
    def addMap(self, name):
        myWorld.addMap(name, None)
    
    def tileProperties(self, tile):
        (x, y) = tile
        
        while True:
            infoWin = pygame.Surface((300,270))
            infoWin.fill(colors.black)
            if pygame.font:
                font = pygame.font.SysFont("arial",20)
                infoWin.blit( font.render('Foreground: '+str(self.myMap.getEntry(x, y) ), 1, colors.white, colors.black), (0,0) )
                try:
                    p = self.myMap.grid[x][y].portal
                    p = p[0]+' at '+str(p[1])+', '+str(p[2])
                except AttributeError:
                    p = '-'
                infoWin.blit( font.render('Portal at: '+p, 1, colors.white, colors.black), (0,30) )
                try:
                    s = self.myMap.grid[x][y].shopID
                    s = s[0]+' level '+str(s[1])
                except AttributeError:
                    s = '-'
                infoWin.blit( font.render('Shop: '+s, 1, colors.white, colors.black), (0, 60) )
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    (mX, mY) = pygame.mouse.get_pos()
                    if 200 <= mX < 400 and 200 <= mY < 470:
                        Index = (mY-200)/30
                        if Index == 0:
                            self.myMap.setEntry( x, y, int( self.getInput('Enter tile FG: ') ) )
                        elif Index == 1:
                            self.myMap.grid[x][y].portal = ( self.getInput('Enter target map: '), 
                                                             int( self.getInput('Enter portal x: ') ), 
                                                             int( self.getInput('Enter portal y: ') ) )
                        elif Index == 2:
                            self.myMap.grid[x][y].shopID = ( self.getInput('Enter shop type: '), 
                                                             int( self.getInput('Enter level: ') ) )
                    return
                if event.type == pygame.QUIT:
                    os.sys.exit()
                        
            screen.blit(infoWin, (200, 200) )
            pygame.display.flip()
    
    def removeMap(self):
        mapWin = pygame.Surface((200,420))
        mapWin.fill(colors.black)
        mapList = myWorld.getMapList()
        mapList.sort()
        if pygame.font:
            font = pygame.font.SysFont("arial",20)
            y_ = 0
            for map in mapList:
                mapWin.blit( font.render(map, 1, colors.white, colors.black), (0,y_) )
                y_ += 30
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    (mX, mY) = pygame.mouse.get_pos()
                    if 200 <= mX < 300 and 200 <= mY < 620:
                        mapIndex = (mY-200)/30
                        if mapIndex+1 <= len(mapList):
                            myWorld.removeMapByName( mapList[mapIndex] )
                    return
                if event.type == pygame.QUIT:
                    os.sys.exit()
                        
            screen.blit(mapWin, (200, 200) )
            pygame.display.flip()
    
    def switchMap(self):
        mapWin = pygame.Surface((200,510))
        mapWin.fill(colors.black)
        mapList = myWorld.getMapList()
        mapList.sort()
        if pygame.font:
            font = pygame.font.SysFont("arial",20)
            y_ = 0
            for map in mapList:
                mapWin.blit( font.render(map, 1, colors.white, colors.black), (0,y_) )
                y_ += 30
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    (mX, mY) = pygame.mouse.get_pos()
                    if 200 <= mX < 300 and 0 <= mY < 510:
                        mapIndex = mY/30
                        if mapIndex+1 <= len(mapList):
                            myWorld.currentMap = myWorld.getMapByName( mapList[mapIndex] )#myWorld.worldArray[mapIndex]
                            self.myMap = myWorld.currentMap
                        self.cursorPos = (0,0)
                        self.topX = 0
                        self.topY = 0
                    return
                if event.type == pygame.QUIT:
                    os.sys.exit()
                        
            screen.blit(mapWin, (200, 0) )
            pygame.display.flip()
    
    def getMapInfo(self):
        
        while True:
            infoWin = pygame.Surface((300,330))
            infoWin.fill(colors.black)
            if pygame.font:
                font = pygame.font.SysFont("arial",20)
                infoWin.blit( font.render('Name: '+self.myMap.getName(), 1, colors.white, colors.black), (0,0) )
                infoWin.blit( font.render('Up: '+self.myMap.up[0], 1, colors.white, colors.black), (0,30) )
                if self.myMap.down[0] == 'dungeon':
                    infoWin.blit( font.render('Down: '+self.myMap.down[0]+' '+str(self.myMap.down[1]), 1, colors.white, colors.black), (0,60) )
                else: infoWin.blit( font.render('North: '+self.myMap.neighbors[0], 1, colors.white, colors.black), (0,90) )
                infoWin.blit( font.render('South: '+self.myMap.neighbors[1], 1, colors.white, colors.black), (0,120) )
                infoWin.blit( font.render('East: '+self.myMap.neighbors[2], 1, colors.white, colors.black), (0,150) )
                infoWin.blit( font.render('West: '+self.myMap.neighbors[3], 1, colors.white, colors.black), (0,180) )
                infoWin.blit( font.render('Type: '+self.myMap.type, 1, colors.white, colors.black), (0,210) )
                if myWorld.initialMap.getName() == self.myMap.getName():
                    infoWin.blit( font.render('Initial: Yes', 1, colors.white, colors.black), (0,240) )
                else: infoWin.blit( font.render('Initial: No', 1, colors.white, colors.black), (0,240) )
                try:
                    infoWin.blit( font.render('Level: '+str(self.myMap.level), 1, colors.white, colors.black), (0,270) )
                except AttributeError:
                    infoWin.blit( font.render('Level: -', 1, colors.white, colors.black), (0,270) )
                infoWin.blit( font.render('Size: '+str(self.myMap.getDIM() ), 1, colors.white, colors.black), (0,300) )
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    (mX, mY) = pygame.mouse.get_pos()
                    if 200 <= mX < 400 and 200 <= mY < 530:
                        Index = (mY-200)/30
                        if Index == 0:
                            self.myMap.setName( self.getInput('Enter map name: ') )
                        elif Index == 1:
                            self.myMap.up = ( self.getInput('Enter name of map up: '), )
                        elif Index == 2:
                            mName = self.getInput('Enter name of map down: ')
                            if mName == 'dungeon':
                                self.myMap.down = ( mName, 
                                                int(self.getInput('Enter number of levels: ')),
                                                self.getInput('Enter name of map final map: ') )
                            else: self.myMap.down = (mName,)
                        elif Index == 3:
                            self.myMap.neighbors[0] = self.getInput('Enter name of map north: ')
                        elif Index == 4:
                            self.myMap.neighbors[1] = self.getInput('Enter name of map south: ')
                        elif Index == 5:
                            self.myMap.neighbors[2] = self.getInput('Enter name of map east: ')
                        elif Index == 6:
                            self.myMap.neighbors[3] = self.getInput('Enter name of map west: ')
                        elif Index == 7:
                            self.myMap.type = self.getInput('Enter map type: ')
                        elif Index == 8:
                            myWorld.initialMap = myWorld.getMapByName( self.myMap.getName() )
                        elif Index == 9:
                            self.myMap.level = int( self.getInput('Enter map level: ') )
                        elif Index == 10:
                            self.myMap.changeDimensions( int ( self.getInput('Enter new size: ') ))
                    return
                if event.type == pygame.QUIT:
                    os.sys.exit()
                        
            screen.blit(infoWin, (200, 200) )
            pygame.display.flip()
    
    def importMap(self):
        filename = self.getFilename()
        
        
    #@tail_call_optimized
    def floodFillBFS(self,pieceLocation):
        if (pieceLocation == None):
            return
        (x,y) = pieceLocation
        entryList = []
        for (Cx,Cy) in const.CARDINALS:
            if (self.myMap.getEntry(x,y) == self.myMap.getEntry(x+Cx,y+Cy) and (x+Cx,y+Cy) not in self.visited and ~self.BFSQueue.has( (x+Cy, y+Cy) ) ):
                self.BFSQueue.push( (x+Cx, y+Cy) )
                entryList += [ (x+Cx,y+Cy) ]
                self.visited += [ (x+Cx,y+Cy) ]
            else:
                entryList += [ None ]
        if ( entryList == [None,None,None,None] ):
            return (x,y)
        else:
            return [ (x, y) ] + [ self.floodFillBFS(self.BFSQueue.pop()) ] + [self.floodFillBFS(self.BFSQueue.pop()) ] + [self.floodFillBFS(self.BFSQueue.pop()) ] + [self.floodFillBFS(self.BFSQueue.pop()) ]

    def floodFill(self, tile, start):
        (x,y) = start
        x = x / blocksize
        y = y / blocksize
        self.visited = [ (x,y) ]
        self.BFSQueue.reset()
        floodArea = misc.flatten( self.floodFillBFS( (x,y) ) )
        floodArea = list( set(floodArea) )
        for entry in floodArea:
            (x,y) = entry
            self.myMap.setEntry(x,y,tile)
    
    def getInput(self, msg):
        #get file name
        input = None
        txtbx = eztext.Input(maxlength=300, color=(255,0,0), prompt=msg)
        inputWindow = pygame.Surface( (1200,100) )
        while input == None:
            # make sure the program is running at 30 fps
            clock.tick(30)

            # events for txtbx
            events = pygame.event.get()
            # process other events
            for event in events:
                # close it x button si pressed
                if event.type == pygame.QUIT:
                        os.sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input = txtbx.getValue()

            # clear the screen
            inputWindow.fill((25,25,25))
            # update txtbx
            txtbx.update(events)
            # blit txtbx on the sceen
            txtbx.draw(inputWindow)
            gridField.blit(inputWindow, (100,100) )
            screen.blit(gridField,(0,0))
            # refresh the display
            pygame.display.flip()
        return input
    
    def fillChest(self):
        menuBox = pygame.Surface( (150, 250) )
        itemsList = range(216, 232)+[112,113,114,117,118,119]
        for i in range( len( itemsList ) ):
            menuBox.blit(mapImages[itemsList[i]], (15+((i)%4)*blocksize, 50+((i)/4)*blocksize))
        chestItems = []
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return chestItems
                if event.type == pygame.MOUSEBUTTONDOWN:
                    (mx, my) = event.pos
                    if 115 <= mx < 235 and 150 <= my < 330:
                        itemNum = itemsList[(mx-115)/blocksize + (my-150)/blocksize * 4]
                        if itemNum in range(86, 99):
                            chestItems.append( (itemNum-const.FRUIT1, 1) )
                        elif itemNum == const.GOLD:
                            chestItems.append( (itemNum-const.FRUIT1, int(self.getInput('Enter amount of gold: ')) ) )
                        elif itemNum == const.SPELLBOOK or itemNum == const.PARCHMENT:
                            chestItems.append( (itemNum-const.FRUIT1, int(self.getInput('Enter spell number: ') ) ) )
                        elif itemNum in [112,113,114]:
                            chestItems.append( (itemNum-const.FRUIT1, 
                                                int(self.getInput("Enter weapon level: ")), 
                                                [ int(self.getInput("Enter plus Str: ")),
                                                  int(self.getInput("Enter plus Int: ")),
                                                  int(self.getInput("Enter plus Dex "))   ] ) )
                        elif itemNum in [const.SHIELD,const.BPLATE,const.HELMET]:
                            chestItems.append( (itemNum-const.FRUIT1, 
                                                int(self.getInput("Enter armor level: ")), 
                                                int(self.getInput("Enter resist: ")) ) )
            for item in chestItems:
                menuBox.blit(mapImages[item[0]+const.FRUIT1], (len(chestItems)*blocksize, 15) )
            screen.blit(menuBox, (100,100) )
            pygame.display.flip()
    
    def getFilename(self):
        return self.getInput('Enter filename: ')
    
    def saveMap(self):
        filename = self.getFilename()
        ball = self.myMap.getMapBall()
        try:
            save = gzip.GzipFile(os.getcwd()+'/MAP/LEVELS/'+filename, 'wb')
            cPickle.dump(ball, save)
            save.close()
        except IOError, message:
            print 'Cannot load map:', filename
            return
    
    def loadMap(self, filename=None):
        if filename == None:
            filename = self.getFilename()
        try:
            save = gzip.GzipFile(os.getcwd()+'/MAP/LEVELS/'+filename, 'rb')
            ball = cPickle.load(save)
            save.close()
            self.myMap.installBall(ball)
        except IOError, message:
            print 'Cannot load map:', filename
            return
    
    def saveWorld(self):
        filename = self.getFilename()
        ball = myWorld.getWorldBall()
        try:
            save = gzip.GzipFile(os.getcwd()+'/MAP/WORLDS/'+filename, 'wb')
            cPickle.dump(ball, save)
            save.close()
        except IOError, message:
            print 'Cannot load world:', filename
            return
    def loadWorld(self):
        filename = self.getFilename()
        try:
            loadedWorld = gzip.GzipFile(os.getcwd()+'/MAP/WORLDS/'+filename, 'rb')
            ball = cPickle.load(loadedWorld)
            loadedWorld.close()
            myWorld.installWorldBall(ball,'editor')
            self.myMap = myWorld.getMapByName( ball[1] )
        except IOError, message:
            print 'Cannot load world:', filename
            return
    
    def generateMap(self, type):
        level = int( self.getInput('Enter level: ') )
        if type == 'dungeon':
            rooms = int( self.getInput('Enter # of rooms (max 20): ') )
            MG = mapgen.Generator(self.myMap.getDIM(), level)
            MG.generateMap(rooms)
            self.myMap.installBall( MG.getMapBall() )
        elif type == 'maze':
            MG = mazegen.Generator(self.myMap.getDIM(), level)
            MG.generateMap()
            self.myMap.installBall( MG.getMapBall() )
        elif type == 'wilds':
            MG = wilds.Generator(self.myMap.getDIM(), level)
            MG.generateMap()
            self.myMap.installBall( MG.getMapBall() )
    
    def place(self, x, y, tile):            
        if self.placeNPC:
            self.myMap.NPCs.append( ( (x, y), self.getInput('Enter NPC type: '), self.getInput('Enter message: ') ) )
        else:
            if self.currentTile == const.CHEST:
                self.myMap.addChest( (x, y), self.fillChest())
                param=None
            elif self.currentTile == const.SIGN:
                param = self.getInput('Sign text: ')
            elif self.currentTile in const.doorsList:
                param=None
            else: param=None
            self.myMap.setEntry(x, y, tile, param)
            '''
            elif self.currentTile == const.ITEMSDOOR:
                param = int(self.getInput('Itemshop level: '))
            elif self.currentTile == const.ARMRYDOOR:
                param = int(self.getInput('Armory level: '))
            elif self.currentTile == const.BLKSMDOOR:
                param = int(self.getInput('Blacksmith level: '))
            elif self.currentTile == const.MAGICDOOR:
                param = int(self.getInput('Magicshop level: '))
            '''
        
    def removeNPC(self, x, y):
        for n in self.myMap.NPCs:
            if n[0] == (x, y):
                self.myMap.NPCs.remove(n)
                return
        
    def event_handler(self, event):
        (x,y) = self.cursorPos
        self.drawBox( (x,y), colors.black)
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            count = 5
        else:
            count = 1
        if event.key == pygame.K_RIGHT:
            for i in range(count):
                if( x+blocksize < self.myMap.DIM*blocksize ):
                    x += blocksize
                if x < self.myMap.DIM*blocksize and x == 20*blocksize + self.topX*blocksize:
                    self.topX += 1
                if self.drawMode:
                    self.myMap.setEntry(x/blocksize,y/blocksize,self.currentTile)
                self.cursorPos = (x,y)
        elif event.key == pygame.K_LEFT:
            for i in range(count):
                if( x-blocksize >= 0 ):
                    x -= blocksize
                if x > 0 and x == self.topX*blocksize:
                    self.topX -= 1
                if self.drawMode:
                    self.myMap.setEntry(x/blocksize,y/blocksize,self.currentTile)
                self.cursorPos = (x,y)
        elif event.key == pygame.K_UP:
            for i in range(count):
                if( y-blocksize >= 0 ):
                    y -= blocksize
                if y > 0 and y == self.topY*blocksize:
                    self.topY -= 1
                if self.drawMode:
                    self.myMap.setEntry(x/blocksize,y/blocksize,self.currentTile)
                self.cursorPos = (x,y)
        elif event.key == pygame.K_DOWN:
            for i in range(count):
                if( y+blocksize < self.myMap.DIM*blocksize ):
                    y += blocksize
                if y < self.myMap.DIM*blocksize and y == 20*blocksize + self.topY*blocksize:
                    self.topY += 1
                if self.drawMode:
                    self.myMap.setEntry(x/blocksize,y/blocksize,self.currentTile)
                self.cursorPos = (x,y)
        elif event.key == pygame.K_p:
            self.loadMap()
        elif event.key == pygame.K_t:
            self.saveMap()
        elif event.key == pygame.K_SPACE:
            self.place(x/blocksize, y/blocksize, self.currentTile)
        elif event.key == pygame.K_ESCAPE:
            os.sys.exit()
        elif event.key == pygame.K_d:
            self.drawMode = not self.drawMode
        elif event.key == pygame.K_s:
            self.saveWorld()
        elif event.key == pygame.K_l:
            self.loadWorld()
        elif event.key == pygame.K_r:
            self.removeMap()
        elif event.key == pygame.K_f:
            self.floodFill(self.currentTile, (x,y) )
        elif event.key == pygame.K_g:
            self.generateMap( self.getInput('Enter type: ') )
        elif event.key == pygame.K_e:
            self.offset += 32
            if self.offset == 256:
                self.offset = 0
        elif event.key == pygame.K_x:
            self.removeNPC( x/blocksize, y/blocksize )
        elif event.key == pygame.K_n:
            print 'NPCs: '
            print self.myMap.NPCs
        elif event.key == pygame.K_i:
            self.getMapInfo()
        elif event.key == pygame.K_m:
            self.switchMap()
        elif event.key == pygame.K_a:
            self.addMap( self.getInput('Enter title of new map: ') )
        elif event.key == pygame.K_p:
            self.importMap( self.getInput('Enter filename of map: ') )
        elif event.key == pygame.K_RETURN:
            self.tileProperties( (x/blocksize, y/blocksize) )
        elif event.key == pygame.K_PLUS:
            self.currentTile += 1
        elif event.key == pygame.K_MINUS:
            self.currentTile -= 1
        
        # special
        elif event.key == pygame.K_q:
            self.randomTrees()
    
    def select(self, start):
        startX, startY = start
        endX = startX
        endY = startY
        self.selectBoxPoints = None
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.selectBox = self.selectBoxPoints
                    return (endX, endY)
                (tempX, tempY) = pygame.mouse.get_pos()
                if tempX > 600:
                    tempX = 600
                    pygame.mouse.set_pos([tempX,tempY])
                if tempY > 600:
                    tempY = 600
                    pygame.mouse.set_pos([tempX,tempY])
                endX = tempX/blocksize + 1
                endY = tempY/blocksize + 1
                self.updateDisplay()
                self.selectBoxPoints = ( (startX*blocksize,startY*blocksize), 
                                          (startX*blocksize,(startY+(endY-startY))*blocksize), 
                                          (endX*blocksize,endY*blocksize), 
                                          ((startX+(endX-startX))*blocksize,startY*blocksize) )
                pygame.draw.lines( gridField, colors.red, True, self.selectBoxPoints, 1 )
                screen.blit(gridField, (0,0) )
                pygame.display.flip()
    
    def move(self, start):
        (p1, p2, p3, p4) = self.selectBoxPoints
        sX, sY = start
        xDim = (p3[0]-p1[0])/blocksize
        yDim = (p3[1]-p1[1])/blocksize
        (tempX, tempY) = pygame.mouse.get_pos()
        xOffset = (tempX/blocksize)-(p1[0]/blocksize)
        yOffset = (tempY/blocksize)-(p1[1]/blocksize)
        oldTopX = ( (tempX/blocksize)-xOffset )
        oldTopY = ( (tempY/blocksize)-yOffset )
        newTopX = None
        newTopY = None
        selectionImg = pygame.Surface( (xDim*blocksize, yDim*blocksize) )
        emptyImg = pygame.Surface( (xDim*blocksize, yDim*blocksize) )
        for i in range(xDim):
            for j in range(yDim):
                selectionImg.blit( mapImages[ self.myMap.getEntry(oldTopX+i, oldTopY+j) ], (i*blocksize, j*blocksize) )
                emptyImg.blit( mapImages[ 0 ], (i*blocksize, j*blocksize) )
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if newTopX == None or newTopY == None:
                        return
                    else:
                        self.myMap.mapMove( (sX/blocksize, sY/blocksize), ( xDim, yDim ), (newTopX, newTopY) )
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    return
                elif event.type == pygame.MOUSEMOTION:
                    (tempX, tempY) = pygame.mouse.get_pos()
                    # upper left hand corner
                    newTopX = ( (tempX/blocksize)-xOffset )
                    newTopY = ( (tempY/blocksize)-yOffset )
                    oldTopX = p1[0]/blocksize
                    oldTopY = p1[1]/blocksize
                    if oldTopX == newTopX and oldTopY == newTopY :
                        pass
                    elif 0 <= newTopX*blocksize and (newTopX+ ((p3[0]-p1[0])/blocksize) )*blocksize < 1200 and 0 <= newTopX*blocksize and (newTopY+ ((p3[1]-p1[1])/blocksize) )*blocksize < 1200:
                        self.selectBoxPoints = ( (newTopX*blocksize,newTopY*blocksize), 
                                                 (newTopX*blocksize,(newTopY+ ((p3[1]-p1[1])/blocksize) )*blocksize), 
                                                 ((newTopX+ ((p3[0]-p1[0])/blocksize) )*blocksize,(newTopY+ ((p3[1]-p1[1])/blocksize) )*blocksize), 
                                                 ((newTopX+ ((p3[0]-p1[0])/blocksize) )*blocksize,newTopY*blocksize) )
                        (p1, p2, p3, p4) = self.selectBoxPoints
                        self.updateDisplay()
                        gridField.blit( emptyImg, (sX*blocksize, sY*blocksize) )
                        gridField.blit( selectionImg, (newTopX*blocksize, newTopY*blocksize) )
                        pygame.draw.lines( gridField, colors.red, True, self.selectBoxPoints, 1 )
                        screen.blit(gridField, (0,0) )
                        pygame.display.flip()
    def randomTrees(self):
        for i in range(self.myMap.getDIM() ):
            for j in range(self.myMap.getDIM() ):
                if self.myMap.getEntry(i, j) in mapScr.pines:
                    self.myMap.setEntry(i, j, choice(mapScr.pines) )

    def mouseHandler(self, e):
        (mx, my) = e.pos
        if 0 <= mx < gridField.get_width() and 0 <= my < gridField.get_height():
            if e.button == 1:
                if self.mouseAction == 'draw':
                    if self.placeNPC:
                        self.myMap.NPCs.append( ( (mx/blocksize, my/blocksize), self.getInput('Enter NPC type: '), self.getInput('Enter message: ') ) )
                    else:
                        if self.currentTile == const.CHEST:
                            self.myMap.addChest( (mx/blocksize,my/blocksize), self.fillChest())
                            level=None
                        elif self.currentTile == const.ITEMSDOOR:
                            level = int(self.getInput('Itemshop level: '))
                        elif self.currentTile == const.ARMRYDOOR:
                            level = int(self.getInput('Armory level: '))
                        elif self.currentTile == const.BLKSMDOOR:
                            level = int(self.getInput('Blacksmith level: '))
                        elif self.currentTile == const.MAGICDOOR:
                            level = int(self.getInput('Magicshop level: '))
                        else: level = None
                        self.myMap.setEntry(mx/blocksize,my/blocksize,self.currentTile, level)
                    self.cursorPos = ( (mx/blocksize)*blocksize, (my/blocksize)*blocksize )
                elif self.mouseAction == 'select':
                    if self.selectBoxPoints is not None:
                        (p1, p2, p3, p4) = self.selectBoxPoints
                        if p1[0] <= mx < p3[0] and p1[1] <= my < p3[1]:
                            self.move( (p1[0], p1[1]) )
                        else: self.selection = ( (mx/blocksize, my/blocksize), self.select( (mx/blocksize, my/blocksize) ) )
                    else: self.selection = ( (mx/blocksize, my/blocksize), self.select( (mx/blocksize, my/blocksize) ) )
            elif e.button == 3:
                pass
        elif gridField.get_width()+50 <= mx < gridField.get_width()+80 and 170 <= my < 200:
            self.placeNPC = not self.placeNPC
        elif gridField.get_width()+50 <= mx < gridField.get_width()+170 and 200 <= my < 440:
            if e.button == 1:
                self.currentTile = ( self.offset + (mx-gridField.get_width()-45)/blocksize + (my-200)/blocksize * 4 )
            elif e.button == 3: self.myMap.defaultBkgd = ( self.offset + (mx-gridField.get_width()-45)/blocksize + (my-200)/blocksize * 4 )
        elif gridField.get_width()+65 <= mx < gridField.get_width()+95 and 500 <= my < 530:
            self.offset -= 32
            if self.offset < 0:
                self.offset = 224
        elif gridField.get_width()+95 <= mx < gridField.get_width()+125 and 500 <= my < 530:
            self.offset += 32
            if self.offset == 256:
                self.offset = 0
        elif gridField.get_width()+50 <= mx < gridField.get_width()+80 and 530 <= my < 560:
            self.myMap.mapCut()
        elif gridField.get_width()+80 <= mx < gridField.get_width()+110 and 530 <= my < 560:
            self.myMap.mapCopy(self.selection)
        elif gridField.get_width()+110 <= mx < gridField.get_width()+140 and 530 <= my < 560:
            self.myMap.mapPaste()
        elif gridField.get_width()+65 <= mx < gridField.get_width()+95 and 560 <= my < 590:
            self.mouseAction = 'draw'
        elif gridField.get_width()+95 <= mx < gridField.get_width()+125 and 560 <= my < 590:
            self.mouseAction = 'select'
        
    
    def mouseUpdate(self):
        (mx, my) = pygame.mouse.get_pos()
        if 650 <= mx < 770 and 200 <= my < 440:
            boxPoints = ( (mx,my), (mx,my+blocksize), (mx+blocksize,my+blocksize), (mx+blocksize,my) )
            pygame.draw.lines( screen, colors.red, True, boxPoints, 1 )
    
    def updateDisplay(self):
        gridField.fill(colors.black)
        for i in range(self.topX, self.topX+40):
            for j in range(self.topY, self.topY+40):
                if self.myMap.getEntry(i,j) in range(24, 86):
                    gridField.blit( mapImages[self.myMap.defaultBkgd], ( (i-self.topX)*blocksize,(j-self.topY)*blocksize) )
                gridField.blit( mapImages[self.myMap.getEntry(i,j)], ( (i-self.topX)*blocksize,(j-self.topY)*blocksize) )
                if (i,j) == self.myMap.heroStart:
                    gridField.blit( mapImages[const.HEROSTART], ( (i-self.topX)*blocksize,(j-self.topY)*blocksize) )
                if self.myMap.shops is not None:
                    for s in self.myMap.shops:
                        (sX, sY) = s
                        (imgN, ht) = images.siteImgDict[ self.myMap.shops[s][0] ]
                        gridField.blit( mapImages[ imgN ], (sX*blocksize - blocksize - (self.topX * blocksize), sY*blocksize - ( ht*blocksize) - (self.topY * blocksize) ) )
        for n in self.myMap.NPCs:
            (x,y) = n[0]
            gridField.blit(self.npcImg[ n[1] ], ((x-self.topX)*blocksize, (y-self.topY)*blocksize) )
        (x,y) = self.cursorPos
        x = x - self.topX*blocksize
        y = y - self.topY*blocksize
        if self.drawMode:
            self.cursorColor = colors.yellow
        else:
            self.cursorColor = colors.white
        if self.selectBoxPoints is not None:
            pygame.draw.lines( gridField, colors.red, True, self.selectBoxPoints, 1 )

        boxPoints = ( (x,y), (x,y+blocksize), (x+blocksize,y+blocksize), (x+blocksize,y) )
        pygame.draw.lines( gridField, self.cursorColor, True, boxPoints, 1 )
        self.sideImg, sideRect = load_image.load_image('sidebar.bmp')
        if self.placeNPC: self.sideImg.blit(self.npcImg['king'],(50,50))
        else: self.sideImg.blit(mapImages[self.currentTile],(50,50))
        self.sideImg.blit(mapImages[self.myMap.defaultBkgd],(50,130))
        if self.mouseAction == 'draw':
            self.sideImg.blit(self.editorImages[5], (50,80) )
        else: self.sideImg.blit(self.editorImages[6], (50,80) )
        self.sideImg.blit(self.npcImg['king'], (50,170) )
        for i in range(8):
            for j in range(4):
                self.sideImg.blit(mapImages[self.offset + j + (4*i)], (50+j*blocksize, 200+(i*blocksize)))
        
        toolBox = pygame.Surface( (90, 90) )
        toolBox.blit( self.editorImages[0], (15,0) )
        toolBox.blit( self.editorImages[1], (45,0) )
        toolBox.blit( self.editorImages[2], (0,30) )
        toolBox.blit( self.editorImages[3], (30,30) )
        toolBox.blit( self.editorImages[4], (60,30) )
        toolBox.blit( self.editorImages[5], (15,60) )
        toolBox.blit( self.editorImages[6], (45,60) )
        self.sideImg.blit(toolBox, (50,500) )
        (x,y) = self.cursorPos
        entryBox = pygame.Surface((150,30))
        entryBox.fill(colors.black)
        if pygame.font:
            font = pygame.font.SysFont("arial",12)
            entry = font.render(str(self.myMap.getEntry( (x+self.topX)/blocksize, (y+self.topY)/blocksize))+' '+'x:'+str(x)+'('+str(x/blocksize)+')'+' y:'+str(y)+'('+str(y/blocksize)+')',1, colors.white, colors.black )
            entryBox.blit(entry,(0,0))
            self.sideImg.blit(entryBox,(50,450))
        if self.drawMode:
            msgBox = pygame.Surface( ( 186, 60 ) )
            msgBox.fill( colors.grey )
            if pygame.font:
                font = pygame.font.SysFont("arial", 24)
                msgText = font.render( 'draw', 1, colors.red, colors.yellow )
                msgBox.blit(msgText, (10,10) )
            self.sideImg.blit( msgBox, (50,100) )
            #pygame.display.flip()
        screen.blit(self.sideImg, (1200,0) )
    

# Set the height and width of the screen
size=[1400,800]
screen=pygame.display.set_mode(size)

images.load()
mapImages = images.mapImages


pygame.init()
pygame.key.set_repeat(50, 100)
clock = pygame.time.Clock()

cursorPos = (0,0)

#self.myMap = map.edMap()
myWorld = world.World('editor')
myHandler = Handler(cursorPos)

blocksize = 30

gridField = pygame.Surface( [2*const.DIM*blocksize, 2*const.DIM*blocksize] )

os.sys.setrecursionlimit(15000)


def main():
    myHandler.updateDisplay()
    while True :
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                myHandler.event_handler(event)
                myHandler.updateDisplay()
            if event.type == pygame.MOUSEBUTTONDOWN:# or event.type == pygame.MOUSEBUTTONUP:
                myHandler.mouseHandler(event)
                myHandler.updateDisplay()
            if event.type == pygame.QUIT:
                os.sys.exit()
        myHandler.mouseUpdate()
        #myHandler.updateDisplay()
        screen.blit(gridField, (0,0) )
        pygame.display.flip()

main()