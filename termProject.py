# termProject.py
# Angela Liang + angelali + section J

from pykinect2 import PyKinectV2 as PyKV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import pygame
import sys
import math
import random
import time

class Mickey(object):
    def __init__(self,type):
        self.type = type
        self.imageSurface=pygame.image.load("%s.png"%self.type).convert_alpha()

    #obtain angle of hand rotation
    @staticmethod
    def getTheta(x,y,cx,cy,r):
        if (x-cx)/r < -1:
            xTheta = math.acos(-1)
        elif (x-cx)/r > 1:
            xTheta = math.acos(1)
        else: 
            xTheta = math.acos((x-cx)/r)
        if (y-cy)/r < -1:
            yTheta = math.asin(-1)
        elif (y-cy)/r > 1:
            yTheta = math.asin(1)
        else:
            yTheta = math.asin((y-cy)/r)
        return (xTheta,yTheta)

    def draw(self,surface,x,y,cx,cy,r):
        screenWidth = 1920
        screenHeight = 1080
        if 0 < x < screenWidth and 0 < y < screenHeight:
            if self.type == "leftHand" or self.type == "rightHand":
                xTheta,yTheta = Mickey.getTheta(x,y,cx,cy,r)
                #average angle of rotation in degrees as calculated from x and y
                theta = int(((xTheta + yTheta)/2) * (180/math.pi))
                if theta > 0:
                    for angle in range(theta):
                        rotatedImage = pygame.transform.rotate(
                                                       self.imageSurface,angle)
                elif theta < 0:
                    for angle in range(0,theta,-1):
                        rotatedImage = pygame.transform.rotate(
                                                       self.imageSurface,angle)
                else:
                    rotatedImage = self.imageSurface
                surface.blit(rotatedImage,(x-100,y-100))
            elif self.type == "hat":
                surface.blit(self.imageSurface,(x-200,y-350))

class Mop(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.mopImageSurface = [pygame.image.load("mop.png").convert_alpha(),
                            pygame.image.load("mopFlip.png").convert_alpha()]

    def draw(self,surface,timer):
        if self.x <= 0:                     #ensure mops remain on screen
            self.x = 0
        if self.x >= surface.get_width():
            self.x = surface.get_width() - 200
        #switch between mop images to simulate dancing
        if timer % 20 <= 9:
            surface.blit(self.mopImageSurface[0],(self.x,self.y))
        else:
            surface.blit(self.mopImageSurface[1],(self.x,self.y))
                
    #determine if mop is selected by hand
    def selected(self,handX,handY):
        mopWidth,mopHeight = 300,350
        if self.x < handX < self.x+300 and self.y < handY < self.y+mopHeight:
            return True
        return False

class Star(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.starImageSurface = pygame.image.load("star.png").convert_alpha()

    def draw(self,surface):
        screenWidth,screenHeight = 1920,1080
        if 0 < self.x < screenWidth and 0 < self.y < screenHeight:
            surface.blit(self.starImageSurface,(self.x,self.y))
        
class Water(object):
    def __init__(self,type,level):
        self.type = type
        self.level = level
        #all water images created by Adella Guo
        self.leftWater = [pygame.image.load("Lwater0.gif").convert_alpha(),
                          pygame.image.load("Lwater1.gif").convert_alpha(),
                          pygame.image.load("Lwater2.gif").convert_alpha(),
                          pygame.image.load("Lwater3.gif").convert_alpha(),
                          pygame.image.load("Lwater4.gif").convert_alpha(),
                          pygame.image.load("Lwater5.gif").convert_alpha(),
                          pygame.image.load("Lwater6.gif").convert_alpha()]
        self.rightWater = [pygame.image.load("Rwater0.gif").convert_alpha(),
                           pygame.image.load("Rwater1.gif").convert_alpha(),
                           pygame.image.load("Rwater2.gif").convert_alpha(),
                           pygame.image.load("Rwater3.gif").convert_alpha(),
                           pygame.image.load("Rwater4.gif").convert_alpha(),
                           pygame.image.load("Rwater5.gif").convert_alpha(),
                           pygame.image.load("Rwater6.gif").convert_alpha()]
        
    def draw(self,surface,handX,i):
        screenWidth,screenHeight = 1920,1080
        if self.type == "left":
            if 0 < handX-500 < screenWidth:
                surface.blit(self.leftWater[i],(handX-500,0))
        elif self.type == "right":
            if 0 < handX-300 < screenWidth:
                surface.blit(self.rightWater[i],(handX-300,0))

class Cloud(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.cloudSurface = pygame.image.load("cloud.png").convert_alpha()
        self.font = pygame.font.Font("waltograph.ttf",150)
    
    def draw(self,surface,text):
        surface.blit(self.cloudSurface,(self.x,self.y))
        text = self.font.render(text,True,(0,0,0))
        surface.blit(text,(self.x+200,self.y+100))

    #determine if x,y intersects with cloud
    def intersect(self,x,y):
        cloudWidth = 350
        cloudHeight = 150
        if ((self.x/2 <= x <= (self.x/2+cloudWidth)) and 
            (self.y/2 <= y <= (self.y/2+cloudHeight))):
            return True
        return False

class Subtext(object):
    def __init__(self):
        self.font = pygame.font.Font("waltograph.ttf",80)

    def draw(self,surface):
        text1 = self.font.render("An interactive Disney experience!",
                                  True,(255,255,255))
        surface.blit(text1,(130,300))
        text2 = self.font.render("Angela Liang 15-112 Term Project",
                                  True,(255,255,255))
        surface.blit(text2,(50,950))

class SplashScreen(object):
    def __init__(self):
        self.splashScreen=pygame.image.load("splashScreen.png").convert_alpha()
        self.font = pygame.font.Font("waltograph.ttf",250)
        self.tutorialCloud = Cloud(1200,70)
        self.playCloud = Cloud(1050,500)
        self.subtext = Subtext()

    #create splash screen surface with all images and text
    def createSurface(self):
        surface = pygame.Surface((1920,1080),0,32)
        surface.blit(self.splashScreen,(0,0))
        text = self.font.render("Fantasia",True,(255,255,255))
        surface.blit(text,(100,10))
        self.tutorialCloud.draw(surface,"Tutorial")
        self.playCloud.draw(surface,"Play")
        self.subtext.draw(surface)
        return surface

class LoadScreen(object):
    def __init__(self):
        self.font = pygame.font.Font("waltograph.ttf",150)

    #create load screen surface with all text
    def createSurface(self):
        screenWidth,screenHeight = 1920,1080
        surface = pygame.Surface((screenWidth,screenHeight),0,32)
        pygame.draw.rect(surface,(0,0,0),(0,0,screenWidth,screenHeight))
        loadText = self.font.render("Loading...",True,(255,255,255))
        surface.blit(loadText,(700,screenHeight/4))
        instrucText = self.font.render("Only 1 apprentice at a time please!",
                                        True,(255,255,255))
        surface.blit(instrucText,(200,screenHeight/2))
        return surface

class EndScreen(object):
    def __init__(self):
        self.endScreen = pygame.image.load("endScreen.png").convert_alpha()
        self.font = pygame.font.Font("waltograph.ttf",150)

    def play(self,screen):
        screen.blit(self.endScreen,(0,0))
        text = self.font.render("See ya real soon!",True,(255,255,255))
        screen.blit(text,(70,150))

class Fantasia(object):
    def __init__(self):
        pygame.init()
        self.initModes()
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.initBasics()
        self.initMedia()
        self.initTutorial()
        self.initHandPos()
        self.initHandMore()
        self.initHead()
        self.initMoves()
        self.initObjects()

    def initModes(self):
        self.done = False
        self.introBegin = True
        self.splashScreenBegin = False
        self.begin = False
        self.firstLoop = True
        self.mode = None
        self.paused = False
        self.end = False

    def initBasics(self):
        self.timer = 0
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(
                      (self.screenWidth//2,self.screenHeight//2),
                      pygame.HWSURFACE|pygame.DOUBLEBUF)
        self.kinect = PyKinectRuntime.PyKinectRuntime(
                      PyKV2.FrameSourceTypes_Color|
                      PyKV2.FrameSourceTypes_Body)
        self.bodies = None
        self.frameSurface = pygame.Surface(
                            (self.kinect.color_frame_desc.Width,
                             self.kinect.color_frame_desc.Height),0,32)

    def initMedia(self):
        self.introSound = pygame.mixer.Sound("introSound.wav")
        self.splashScreenSound = pygame.mixer.Sound("splashScreenSound.wav")
        self.sound = pygame.mixer.Sound("fantasia.wav")
        self.intro = pygame.movie.Movie("intro.mpg")
        self.splashScreen = SplashScreen()
        self.font = pygame.font.Font("waltograph.ttf",100)
        self.tutorialCloud = Cloud(1200,70)
        self.playCloud = Cloud(1050,500)
        self.loadScreen = LoadScreen()
        self.mickey1 = pygame.image.load("mickey1.png").convert_alpha()
        self.mickey2 = pygame.image.load("mickey2.png").convert_alpha()

    def initTutorial(self):
        self.tutIntro = True
        self.tutMoveStars = False
        self.tutNewStars = False
        self.tutNewMop = False
        self.tutMoveMop = False
        self.tutSplitMop = False
        self.tutDeleteMop = False
        self.tutNewWater = False
        self.tutPauseMusic = False
        self.tutEnd = False

    def initHandPos(self):
        self.initLeftHandX = None
        self.initLeftHandY = None
        self.initRightHandX = None
        self.initRightHandY = None
        self.leftHandX = 0
        self.leftHandY = 0
        self.leftHandZ = 0
        self.rightHandX = 0
        self.rightHandY = 0
        self.rightHandZ = 0
        self.prevLeftHandY = None
        self.prevLeftHandZ = None
        self.prevRightHandY = None
        self.prevRightHandZ = None

    def initHandMore(self):
        self.prevLeftHandState = PyKV2.HandState_Open
        self.prevRightHandState = PyKV2.HandState_Open
        self.currLeftHandState = None
        self.currRightHandState = None
        self.leftTipX = 0
        self.leftTipY = 0
        self.rightTipX = 0
        self.rightTipY = 0
        self.leftR = 0
        self.rightR = 0

    def initHead(self):
        self.headX = 0
        self.headY = 0
        self.prevHeadY = None

    def initMoves(self):
        self.leftXMove = 0
        self.rightXMove = 0
        self.leftYMove = 0
        self.rightYMove = 0
        self.leftZMove = 0
        self.rightZMove = 0

    def initObjects(self):
        self.mickey = [Mickey("leftHand"),Mickey("rightHand"),Mickey("hat")]
        self.mops = []
        self.stars = self.starsInit()
        self.starFlash = True
        self.spiral = False         #if stars are in spiral formation
        self.shift = False          #if spiral arm is shifted
        self.prevShift = None       #if sprial arm was previously shifted
        self.spiralShift = 0        #number of times spiral arm has shifted
        self.leftWaterTime = None   #time at which water created
        self.newLeftWater = False
        self.leftWater = None
        self.leftWaterHandX = None  #x position at which water initially created
        self.rightWaterTime = None
        self.newRightWater = False
        self.rightWater = None
        self.righWaterHandX = None

    #initialize 10 stars in random locations
    def starsInit(self):
        stars = []
        for star in range(10):
            x = random.randint(0,self.screenWidth)
            y = random.randint(0,self.screenHeight//7)
            stars.append(Star(x,y))
        return stars

    def drawColorFrame(self,frame,surface):
        surface.lock()
        address = self.kinect.surface_as_array(surface.get_buffer())
        ctypes.memmove(address,frame.ctypes.data,frame.size)
        del address
        surface.unlock()

    def updateColorFrame(self):
        if self.kinect.has_new_color_frame():
            frame = self.kinect.get_last_color_frame()
            self.drawColorFrame(frame,self.frameSurface)
            frame = None

    def drawMops(self):
        for mop in self.mops:
            mop.draw(self.frameSurface,self.timer)

    def drawStars(self):
        for i in range(len(self.stars)):
            star = self.stars[i]
            if self.starFlash:
                #draw varying stars at certain times to simulate flashing
                if i % 2 == 0 and self.timer % 20 <= 15:
                    star.draw(self.frameSurface)
                if i % 2 == 1 and self.timer % 15 <= 10:
                    star.draw(self.frameSurface)
            else:
                star.draw(self.frameSurface)

    #reset attributes in order to clear instance of water
    def resetWater(self,water):
        if water.type == "left":
            self.newLeftWater = False
            self.leftWater = None
            self.leftWaterTime = None
            self.leftWaterHandX = None
        elif water.type == "right":
            self.newRightWater = False
            self.rightWater = None
            self.rightWaterTime = None
            self.rightWaterHandX = None

    #draw images at indices corresponding to low water at x location of hand
    def drawLowWater(self,water,waterTime,handX):
        if water.type == "left":
            self.newLeftWater = True
        elif water.type == "right":
            self.newRightWater = True
        if self.timer % waterTime < 3:
            water.draw(self.frameSurface,handX,0)
        elif self.timer % waterTime < 6:
            water.draw(self.frameSurface,handX,1)
        elif self.timer % waterTime < 9:
            water.draw(self.frameSurface,handX,5)
        elif self.timer % waterTime < 12:
            water.draw(self.frameSurface,handX,6)
        elif self.timer % waterTime >= 15:
            self.resetWater(water)

    #draw images at indices corresponding to mid water at x position of hand
    def drawMidWater(self,water,waterTime,handX):
        if water.type == "left":
            self.newLeftWater = True
        elif water.type == "right":
            self.newRightWater = True
        if self.timer % waterTime < 3:
            water.draw(self.frameSurface,handX,0)
        elif self.timer % waterTime < 6:
            water.draw(self.frameSurface,handX,1)
        elif self.timer % waterTime < 9:
            water.draw(self.frameSurface,handX,2)
        elif self.timer % waterTime < 12:
            water.draw(self.frameSurface,handX,4)
        elif self.timer % waterTime < 15:
            water.draw(self.frameSurface,handX,5)
        elif self.timer % waterTime < 18:
            water.draw(self.frameSurface,handX,6)
        elif self.timer % waterTime >= 21:
            self.resetWater(water)

    #draw images at indices corresponding to high water at x location of hand
    def drawHighWater(self,water,waterTime,handX):
        if water.type == "left":
            self.newLeftWater = True
        elif water.type == "right":
            self.newRightWater = True
        if self.timer % waterTime < 3:
            water.draw(self.frameSurface,handX,0)
        elif self.timer % waterTime < 6:
            water.draw(self.frameSurface,handX,1)
        elif self.timer % waterTime < 9:
            water.draw(self.frameSurface,handX,2)
        elif self.timer % waterTime < 12:
            water.draw(self.frameSurface,handX,3)
        elif self.timer % waterTime < 15:
            water.draw(self.frameSurface,handX,4)
        elif self.timer % waterTime < 18:
            water.draw(self.frameSurface,handX,5)
        elif self.timer % waterTime < 21:
            water.draw(self.frameSurface,handX,6)
        elif self.timer % waterTime >= 24:
            self.resetWater(water)

    def drawLeftWater(self):
        if (not self.newLeftWater and self.leftWater != None
            and self.leftWaterTime == None):
            #assign time and x location of hand when water first created
            self.leftWaterTime = self.timer
            self.leftWaterHandX = self.leftHandX
        if self.leftWater != None and self.leftWaterTime != None:
            if self.leftWater.level == "low":
                self.drawLowWater(self.leftWater,self.leftWaterTime,
                                  self.leftWaterHandX)
            elif self.leftWater.level == "mid":
                self.drawMidWater(self.leftWater,self.leftWaterTime,
                                  self.leftWaterHandX)
            elif self.leftWater.level == "high":
                self.drawHighWater(self.leftWater,self.leftWaterTime,
                                   self.leftWaterHandX)

    def drawRightWater(self):
        if (not self.newRightWater and self.rightWater != None
            and self.rightWaterTime == None):
            #assign time and x location of hand when water first created
            self.rightWaterTime = self.timer
            self.rightWaterHandX = self.rightHandX
        if self.rightWater != None and self.rightWaterTime != None:
            if self.rightWater.level == "low":
                self.drawLowWater(self.rightWater,self.rightWaterTime,
                                  self.rightWaterHandX)
            elif self.rightWater.level == "mid":
                self.drawMidWater(self.rightWater,self.rightWaterTime,
                                  self.rightWaterHandX)
            elif self.rightWater.level == "high":
                self.drawHighWater(self.rightWater,self.rightWaterTime,
                                   self.rightWaterHandX)

    def drawWater(self):
        self.drawLeftWater()
        self.drawRightWater()
        
    #initilize x and y locations of hands at start
    def calibrate(self,joints):
        if (joints[PyKV2.JointType_HandLeft].TrackingState != PyKV2.TrackingState_NotTracked):
            self.initLeftHandX = self.kinect.body_joints_to_color_space(joints)[JointType_HandLeft].x
            self.initLeftHandY = self.kinect.body_joints_to_color_space(joints)[JointType_HandLeft].y
        if (joints[PyKV2.JointType_HandRight].TrackingState != PyKV2.TrackingState_NotTracked):
            self.initRightHandX = self.kinect.body_joints_to_color_space(joints)[JointType_HandRight].x
            self.initRightHandY = self.kinect.body_joints_to_color_space(joints)[JointType_HandRight].y

    def draw(self):
        if not self.paused:
            for item in self.mickey:
                if item.type == "leftHand":
                    item.draw(self.frameSurface,self.leftTipX,self.leftTipY,
                              self.leftHandX,self.leftHandY,self.leftR)
                elif item.type == "rightHand":
                    item.draw(self.frameSurface,self.rightTipX,self.rightTipY,
                              self.rightHandX,self.rightHandY,self.rightR)
                if item.type == "hat":
                    item.draw(self.frameSurface,self.headX,self.headY,
                              None,None,None)
            self.drawMops()
            self.drawStars()   
            self.drawWater() 

    #adjust x position of stars depending on hand positions
    def moveStars(self):
        for i in range(len(self.stars)):
            star = self.stars[i]
            if (self.leftHandY < self.screenHeight/2 and 
                self.rightHandY < self.screenHeight/2):
                star.x -= (self.leftXMove+self.rightXMove)

    #create new stars according to hand motion (pointing and moving forward in
        #upper half of screen)
    def newStars(self):
        if (self.currLeftHandState == PyKV2.HandState_Lasso and 
            self.leftZMove > 3 and self.leftHandY < self.screenHeight/2):
            self.stars.append(Star(self.leftHandX,self.leftHandY))
        if (self.currRightHandState == PyKV2.HandState_Lasso and 
            self.rightZMove > 3 and self.rightHandY < self.screenHeight/2):
            self.stars.append(Star(self.rightHandX,self.rightHandY))

    #create new mop according to hand motion (pointing in lower half of screen)
    def newMop(self):
        if (self.currLeftHandState == PyKV2.HandState_Lasso and
            self.leftHandY > self.screenHeight/2):
            #only create one mop for every 100 timer fired
            if self.timer % 100 == 0:
                if self.leftHandY < self.screenHeight-300:
                    self.mops.append(Mop(self.leftHandX,self.leftHandY))
                else:
                    self.mops.append(Mop(self.leftHandX,self.screenHeight-300))
        if (self.currRightHandState == PyKV2.HandState_Lasso and
            self.rightHandY > self.screenHeight/2):
            if self.timer % 100 == 0:
                if self.leftHandY < self.screenHeight-300:
                    self.mops.append(Mop(self.rightHandX,self.rightHandY))
                else:
                    self.mops.append(Mop(self.rightHandX,self.screenHeight-300))

    #adjust x location of mops depending on hand positions
    def moveMops(self):
        for mop in self.mops:
            if (self.leftHandY > self.screenHeight/2 and 
                self.rightHandY > self.screenHeight/2):
                mop.x -= (self.leftXMove+self.rightXMove)*2

    #create additional mop next to last mop according to hand motion (both
        #hands outwards)
    def splitMop(self):
        if (len(self.mops) >= 1 and self.leftXMove > 1 and self.rightXMove < -1
            and self.timer % 30 == 0):
            lastMopX = self.mops[-1].x
            lastMopY = self.mops[-1].y
            #create new mop next to last mop
            self.mops.append(Mop(lastMopX+300,lastMopY))

    #delete mop if selected and hand in closed state
    def deleteMop(self):
        removeIndex = None
        for i in range(len(self.mops)):
            mop = self.mops[i]
            if (mop.selected(self.leftHandX,self.leftHandY) and
                self.currLeftHandState == PyKV2.HandState_Closed):
                removeIndex = i
            elif (mop.selected(self.rightHandX,self.rightHandY) and
                self.currRightHandState == PyKV2.HandState_Closed):
                removeIndex = i
        if removeIndex != None:
            self.mops.pop(removeIndex)

    #create water at appropriate level depending on y position of hand
    def newWater(self):
        leftLevel = None
        if self.leftYMove > 200:
            leftLevel = "high"
        elif self.leftYMove > 150:
            leftLevel = "mid"
        elif self.leftYMove > 100:
            leftLevel = "low"
        if (leftLevel != None and not self.newLeftWater 
                              and self.leftWater == None):
            self.leftWater = Water("left",leftLevel)
        rightLevel = None
        if self.rightYMove > 200:
            rightLevel = "high"
        elif self.rightYMove > 150:
            rightLevel = "mid"
        elif self.rightYMove > 100:
            rightLevel = "low"
        if (rightLevel != None and not self.newRightWater
                               and self.rightWater == None):
            self.rightWater = Water("right",rightLevel)

    #(un)pause music according to hand state (closed=pause vs open=unpause)
    def pauseMusic(self):
        if ((self.currLeftHandState == PyKV2.HandState_Closed and
             self.currRightHandState == PyKV2.HandState_Closed) and
            (self.prevLeftHandState == PyKV2.HandState_Open and
             self.prevRightHandState == PyKV2.HandState_Open)):
            pygame.mixer.pause()
            self.paused = True
            self.prevLeftHandState = self.currLeftHandState
            self.prevRightHandState = self.currRightHandState
        if ((self.currLeftHandState == PyKV2.HandState_Open and
             self.currRightHandState == PyKV2.HandState_Open) and
            (self.prevLeftHandState == PyKV2.HandState_Closed and
             self.prevRightHandState == PyKV2.HandState_Closed)):
            pygame.mixer.unpause()
            self.paused = False
            self.prevLeftHandState = self.currLeftHandState
            self.prevRightHandState = self.currRightHandState

    #determine if hands are crossed in top half of screen
    def handsCross(self):
        if (self.leftHandY < self.screenHeight/2 and
            self.rightHandY < self.screenHeight/2):
            if self.leftHandX > self.rightHandX:
                self.spiral = True
                return True
        return False

    #reassign stars to random locations if hands spread in top third of screen
        #and stars previously in spiral state
    def scatterStars(self):
        if (self.leftHandY < self.screenHeight/3 and
            self.rightHandY < self.screenHeight/3 and self.spiral):
            if self.leftXMove > 1 and self.rightXMove < -1:
                self.starFlash = True
                self.spiral = False
                self.shift = False
                self.prevShift = None
                self.spiralShift = 0
                for star in self.stars:
                    star.x = random.randint(0,self.screenWidth)
                    star.y = random.randint(0,self.screenHeight//5)
    
    #adjust orientation of spiral depending on arm number
    def getOrientation(self,spiralNum):
        shift = (math.pi/4) * self.spiralShift
        return spiralNum * (math.pi/2 + shift)

    #adjust amount spiral arms are shifted depending on time
    def getShift(self):
        if self.timer % 4 < 2:
            self.shift = False
        else:
            self.shift = True
        if self.shift and not self.prevShift:
            self.spiralShift += 1
        self.prevShift = self.shift

    #move stars into logarithmic spirals of 10 stars per arm
    def starSpiral(self):
        if self.handsCross():
            self.starFlash = False
            numSpirals = len(self.stars) // 10
            for spiral in range(1,numSpirals+1):
                startIndex = (spiral-1) * 10
                endIndex = spiral * 10
                for i in range(startIndex,endIndex):
                    star = self.stars[i]
                    a = 70
                    b = 0.5
                    theta = (2*math.pi) / 10
                    t = (i%10) * theta
                    orient = self.getOrientation(spiral)
                    coeff = a*math.e**(b*t)
                    star.x = coeff*math.cos(t+orient)+(self.screenWidth/2)
                    star.y = coeff*math.sin(t+orient)+(self.screenHeight/2)
            self.getShift()
            lastStarIndex = numSpirals * 10
            self.stars = self.stars[:lastStarIndex]
        if self.spiral: self.scatterStars()

    def play(self):
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        self.splitMop()
        self.deleteMop()
        if not self.handsCross():
            self.newWater()
        self.pauseMusic()
        self.starSpiral()
        self.draw()

    #determine if user's head has nodded
    def nod(self):
        if self.prevHeadY != None and self.timer % 20 == 0:
            return (self.headY - self.prevHeadY <= -1)

    def drawTutIntro(self):
        self.frameSurface.blit(self.mickey1,(1550,170))
        str1 = "Welcome young apprentice! I am sorcerer Mickey!"
        mainText = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(mainText,(150,30))
        str2 = "Wait...one more thing! (Nod to continue)"
        subText = self.font.render(str2,True,(0,0,0))
        self.frameSurface.blit(subText,(300,150))

    def drawTutMoveStars(self):
        self.frameSurface.blit(self.mickey2,(100,170))
        str1 = "There we go! Now try swiping left and right up here!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(150,30))

    def doTutMoveStars(self):
        self.updateColorFrame()
        self.drawTutMoveStars()
        self.draw()
        self.moveStars()
        if self.nod():
            self.tutMoveStars = False
            self.tutNewStars = True

    def drawTutNewStars(self):
        self.frameSurface.blit(self.mickey1,(1500,170))
        str1 = "Nice! Use your pointer finger to create new stars up here!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,30))

    def doTutNewStars(self):
        self.updateColorFrame
        self.drawTutNewStars()
        self.draw()
        self.moveStars()
        self.newStars()
        if self.nod():
            self.tutNewStars = False
            self.tutNewMop = True

    def drawTutNewMop(self):
        self.frameSurface.blit(self.mickey2,(100,750))
        str1 = "Oh boy! Now use your pointer finger to create new mops!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,600))

    def doTutNewMop(self):
        self.updateColorFrame()
        self.drawTutNewMop()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        if self.nod():
            self.tutNewMop = False
            self.tutMoveMop = True

    def drawTutMoveMop(self):
        self.frameSurface.blit(self.mickey1,(1500,750))
        str1 = "Great job! Swipe left and right to move mops down here!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,600))

    def doTutMoveMop(self):
        self.updateColorFrame()
        self.drawTutMoveMop()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        if self.nod():
            self.tutMoveMop = False
            self.tutSplitMop = True

    def drawTutSplitMop(self):
        self.frameSurface.blit(self.mickey2,(100,750))
        str1 = "Swell! Push both hands out to split the last mop into two!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,600))

    def doTutSplitMop(self):
        self.updateColorFrame()
        self.drawTutSplitMop()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        self.splitMop()
        if self.nod():
            self.tutSplitMop = False
            self.tutDeleteMop = True

    def drawTutDeleteMop(self):
        self.frameSurface.blit(self.mickey1,(1500,750))
        str1 = "Oh wow! To delete a mop, just select and grab it!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,600))

    def doTutDeleteMop(self):
        self.updateColorFrame()
        self.drawTutDeleteMop()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        self.splitMop()
        self.deleteMop()
        if self.nod():
            self.tutDeleteMop = False
            self.tutNewWater = True

    def drawTutNewWater(self):
        self.frameSurface.blit(self.mickey2,(100,170))
        str1 = "Gosh! Try swiping up to make waves crash up!"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(300,30))

    def doTutNewWater(self):
        self.updateColorFrame()
        self.drawTutNewWater()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        self.splitMop()
        self.deleteMop()
        self.newWater()
        if self.nod():
            self.tutNewWater = False
            self.tutPauseMusic = True

    def drawTutPauseMusic(self):
        self.frameSurface.blit(self.mickey1,(1500,170))
        str1 = "You sure are getting good! Just close both hands to pause"
        text = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(text,(50,30))
        str2 = "the fantasy!"
        textCont = self.font.render(str2,True,(0,0,0))
        self.frameSurface.blit(textCont,(700,120))

    def doTutPauseMusic(self):
        self.updateColorFrame()
        self.drawTutPauseMusic()
        self.draw()
        self.moveStars()
        self.newStars()
        self.newMop()
        self.moveMops()
        self.splitMop()
        self.deleteMop()
        self.newWater()
        self.pauseMusic()
        if self.nod():
            self.tutPauseMusic = False
            self.tutEnd = True

    def drawTutEnd(self):
        self.frameSurface.blit(self.mickey2,(70,270))
        str1 = "Aw, gee! Looks like you're the sorcerer now!"
        mainText = self.font.render(str1,True,(0,0,0))
        self.frameSurface.blit(mainText,(230,30))
        str2 = "But there might be one more secret...Bye bye now!"
        subText = self.font.render(str2,True,(0,0,0))
        self.frameSurface.blit(subText,(150,150))

    def doTutEnd(self):
        self.updateColorFrame()
        self.drawTutEnd()
        self.play()
        if self.nod():
            self.initFromSplash()

    #reinitialize program starting from splash screen
    def initFromSplash(self):
        self.initModes()
        self.introBegin = False
        self.splashScreenBegin = True
        self.initTutorial()
        self.initHandPos()
        self.initHandMore()
        self.initHead()
        self.initMoves()
        self.initObjects()

    def tutorial(self):
        if self.tutIntro:
            self.drawTutIntro()
            if self.nod():
                self.tutIntro,self.tutMoveStars = False,True
        elif self.tutMoveStars: self.doTutMoveStars()
        elif self.tutNewStars: self.doTutNewStars()
        elif self.tutNewMop: self.doTutNewMop()
        elif self.tutMoveMop: self.doTutMoveMop()
        elif self.tutSplitMop: self.doTutSplitMop()
        elif self.tutDeleteMop: self.doTutDeleteMop()
        elif self.tutNewWater: self.doTutNewWater()
        elif self.tutPauseMusic: self.doTutPauseMusic()
        elif self.tutEnd: self.doTutEnd()

    #end program using escape key, restart program from splash screen using
        #space bar
    def keyPress(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end = True
                self.sound.stop()
                self.splashScreenSound.stop()
            elif event.key == pygame.K_SPACE:
                self.initFromSplash()
                self.sound.stop()
                self.splashScreenSound.play()

    #enter play/tutorial mode depending on user mouse press
    def mousePress(self,event):
        if (self.splashScreenBegin and event.type == pygame.MOUSEBUTTONDOWN):
            xClick,yClick = pygame.mouse.get_pos()
            if (self.tutorialCloud.intersect(xClick,yClick)):
                self.mode = "tutorial"
                self.splashScreenBegin = False
                self.splashScreenSound.stop()
            elif (self.playCloud.intersect(xClick,yClick)):
                self.mode = "play"
                self.splashScreenBegin = False
                self.splashScreenSound.stop()

    #account for program in intro and end modes
    def edgeModes(self):
        if self.introBegin:
            self.intro.set_display(self.screen,(0,0,960,540))
            self.introSound.play()
            self.intro.play()
        if self.end:
            endScreen = EndScreen()
            endScreen.play(self.screen)

    #account for program in splash screen and begin modes
    def beginModes(self):
        if self.splashScreenBegin:
            self.splashScreenSound.play()
            self.screen.blit(self.splashScreen.createSurface(),(0,0))
        if self.begin:
            self.updateColorFrame()

    #obtain x,y,z position information for left hand
    def getLeftHand(self,body,joints):
        if (joints[PyKV2.JointType_HandLeft].TrackingState != PyKV2.TrackingState_NotTracked):
            self.leftHandX = self.kinect.body_joints_to_color_space(joints)[JointType_HandLeft].x
            self.leftHandY = self.kinect.body_joints_to_color_space(joints)[JointType_HandLeft].y
            self.leftHandZ = joints[PyKV2.JointType_HandLeft].Position.z
            self.currLeftHandState = body.hand_left_state
            self.leftTipX = self.kinect.body_joints_to_color_space(joints)[PyKV2.JointType_HandTipLeft].x
            self.leftTipY = self.kinect.body_joints_to_color_space(joints)[PyKV2.JointType_HandTipLeft].y
            self.leftR = ((abs(self.leftTipX-self.leftHandX) +
                           abs(self.leftTipY-self.leftHandY)) / 2)

    #obtain x,y,z position information for right hand
    def getRightHand(self,body,joints):
        if (joints[PyKV2.JointType_HandRight].TrackingState != PyKV2.TrackingState_NotTracked):
            self.rightHandX = self.kinect.body_joints_to_color_space(joints)[JointType_HandRight].x
            self.rightHandY = self.kinect.body_joints_to_color_space(joints)[JointType_HandRight].y
            self.rightHandZ = joints[PyKV2.JointType_HandRight].Position.z
            self.currRightHandState = body.hand_right_state
            self.rightTipX = self.kinect.body_joints_to_color_space(joints)[PyKV2.JointType_HandTipRight].x
            self.rightTipY = self.kinect.body_joints_to_color_space(joints)[PyKV2.JointType_HandTipRight].y
            self.rightR = ((abs(self.rightTipX-self.rightHandX) +
                            abs(self.rightTipY-self.rightHandY)) / 2)

    #obtain x,y position information for head
    def getHead(self,joints):
        if (joints[PyKV2.JointType_Head].TrackingState != PyKV2.TrackingState_NotTracked):
            self.headX = self.kinect.body_joints_to_color_space(joints)[JointType_Head].x
            self.headY = self.kinect.body_joints_to_color_space(joints)[JointType_Head].y

    def getPos(self,body,joints):
        self.getLeftHand(body,joints)
        self.getRightHand(body,joints)
        self.getHead(joints)

    #calculate x,y moves depending on changes in hand positions
    def getMoves(self):
        if self.initLeftHandX != None and self.rightXMove != None:
            self.leftXMove = (self.initLeftHandX-self.leftHandX)/50
            self.rightXMove = (self.initRightHandX-self.rightHandX)/50
        if self.leftXMove < 0 :
            self.leftXMove = 0
        if self.rightXMove > 0 :
            self.rightXMove = 0
        if self.prevLeftHandY != None and self.prevRightHandY != None:
            self.leftYMove = self.prevLeftHandY-self.leftHandY
            self.rightYMove = self.prevRightHandY-self.rightHandY
        if self.prevLeftHandZ != None and self.prevRightHandZ != None:
            self.leftZMove = (self.prevLeftHandZ-self.leftHandZ) * 250
            self.rightZMove = (self.prevRightHandZ-self.rightHandZ) * 250

    #reassign hand positions after each time fire
    def adjustPos(self):
        self.prevLeftHandY = self.leftHandY
        self.prevLeftHandZ = self.leftHandZ
        self.prevRightHandY = self.rightHandY
        self.prevRightHandZ = self.rightHandZ
        self.prevHeadY = self.headY

    #update display on screen depending on mode
    def updateDisplay(self):
        aspectRatio = (float(self.frameSurface.get_height())/
                           self.frameSurface.get_width())
        height = int(aspectRatio * self.screen.get_width())
        if not self.end:
            if self.introBegin:
                surfaceToDraw = pygame.transform.scale(self.screen,
                                (self.screen.get_width(),height))
            if self.splashScreenBegin:
                surfaceToDraw = pygame.transform.scale(
                                self.splashScreen.createSurface(),
                                (self.screen.get_width(),height))
            elif not self.introBegin and not self.splashScreenBegin:
                if self.firstLoop:
                    surfaceToDraw = pygame.transform.scale(
                                    self.loadScreen.createSurface(),
                                    (self.screen.get_width(),height))
                elif self.begin:
                    surfaceToDraw = pygame.transform.scale(self.frameSurface,
                                    (self.screen.get_width(),height))
            self.screen.blit(surfaceToDraw,(0,0))
            surfaceToDraw = None

    #adjust modes after transition delays
    def modeControl(self):
        if self.introBegin:
            time.sleep(15)
            self.introBegin = False
            self.splashScreenBegin = True
        if (not self.introBegin and not self.splashScreenBegin
            and self.firstLoop):
            time.sleep(5)
            self.begin = True
            if self.mode == "play":
                self.sound.play()
        if self.end:
            time.sleep(5)
            self.done = True

    #call appropriate helper methods when program begins
    def beginFantasia(self,joints):
        if self.firstLoop:
            self.calibrate(joints)
            self.firstLoop = False
        self.getMoves()
        if self.mode == "play":
            self.play()
        elif self.mode == "tutorial":
            self.tutorial()
        self.adjustPos()

    #update display, clock, timer, and mode
    def update(self):
        self.updateDisplay()
        pygame.display.update()
        self.clock.tick(30)
        self.timer += 1
        self.modeControl()

    def run(self):
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                self.keyPress(event)
                self.mousePress(event)
            self.edgeModes()
            if not self.end:
                self.beginModes()
                if self.kinect.has_new_body_frame():
                    self.bodies = self.kinect.get_last_body_frame()
                    if self.bodies != None:
                        for i in range(self.kinect.max_body_count):
                            body = self.bodies.bodies[i]
                            if body.is_tracked:
                                self.getPos(body,body.joints)
                                if self.begin: self.beginFantasia(body.joints)
            self.update()
        self.kinect.close()
        pygame.quit()

Fantasia().run()

"""
code from Kinect Workshop: lines 4-11, 230-240, 335-340, 343-346, 998-1000,
1017-1018, 1051-1052, 1057-1060, 1066-1071, 1075-1076
"""