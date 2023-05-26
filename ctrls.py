import maya.cmds as cmds
import math

def clearScene():
    cmds.select(all =True)
    cmds.delete()
    
    
def makeArrow():
    length = 2
    myArrow = cmds.curve(n = 'arrow_CTRL', d=1, p=[(0,0,-1), (length,0,-1), (length,0,-2), (length+2,0,0), (length,0,2),(length,0,1),(0,0,1)])
    return(myArrow)  
    
def makeArch():
    
    length = 1
    myArch = cmds.circle(nr= (0,1,0), r=length, sw=90)
    return(myArch)
    
def makeCurvedArrow():
    
    firstArrow = makeArrow()
    secondArrow = makeArrow()
    outerArch = cmds.circle(nr= (0,1,0), r=4, sw=90)
    cmds.setAttr(outerArch[0] +'.tz',3)
    innerArch = cmds.circle(nr= (0,1,0), r=2, sw=90)
    cmds.setAttr(innerArch[0] +'.tz',3)
    cmds.setAttr(secondArrow +'.tz',3)
    cmds.setAttr(secondArrow +'.tx',-3)
    cmds.setAttr(secondArrow +'.ry',-90)
    cmds.attachCurve(firstArrow, secondArrow, outerArch[0], innerArch[0], rpo = False, n = 'curvedArrow_CTRL')
    cmds.delete(firstArrow, secondArrow, outerArch[0], innerArch[0])
    cmds.xform('curvedArrow_CTRL', cp=True)
    cmds.move(1,0,-2, 'curvedArrow_CTRL', a = True)
    cmds.makeIdentity(apply =True, t=True,r=True,s=True)
    
    


def doubleArrow():
    firstArrow = makeArrow()
    secondArrow = makeArrow()
    cmds.setAttr(secondArrow + '.sx', -1)
    cmds.setAttr(secondArrow + '.sz', -1)
    cmds.attachCurve(firstArrow, secondArrow, rpo=False, n = 'doubleArrow_CTRL')
    cmds.delete(firstArrow, secondArrow)
    

def makeQuadArrow():
    firstArrow = makeArrow()
    secondArrow = makeArrow()
    thirdArrow = makeArrow()
    fourthArrow = makeArrow()
    cmds.setAttr(firstArrow +'.tx', 1)
    cmds.setAttr(secondArrow +'.tx', -1)
    cmds.setAttr(secondArrow +'.sx', -1)
    cmds.setAttr(secondArrow +'.sz', -1)
    cmds.setAttr(thirdArrow +'.ry', 90)
    cmds.setAttr(thirdArrow +'.tz', -1)
    cmds.setAttr(fourthArrow +'.ry', -90)
    cmds.setAttr(fourthArrow +'.tz', 1)
    cmds.attachCurve(firstArrow, secondArrow, thirdArrow, fourthArrow, rpo=False, n = 'quadArrow_CTRL')    
    cmds.delete(firstArrow, secondArrow, thirdArrow, fourthArrow,)
    cmds.xform('quadArrow_CTRL', cp=True)

       
def makeCircle():
   
    length = 2
    myCircle = cmds.circle(n = 'circle_CTRL', r=length,)
    return(myCircle)  
    

def makeDiamond():
    
    firstArch = makeArch()
    secondArch = makeArch()
    thirdArch = makeArch()
    fourthArch = makeArch()
    cmds.setAttr(fourthArch[0] +'.ry', 90)
    cmds.setAttr(fourthArch[0] +'.tz', -2)
    cmds.setAttr(thirdArch[0] +'.ry', -90)
    cmds.setAttr(thirdArch[0] +'.tx', -2)
    cmds.setAttr(secondArch[0] +'.ry', -180)
    cmds.setAttr(secondArch[0] +'.tx', -2)
    cmds.setAttr(secondArch[0] +'.tz', -2)
    cmds.attachCurve(firstArch[0], secondArch[0], thirdArch[0], fourthArch[0], rpo = False, n = 'Diamond_CTRL')
    cmds.delete(firstArch[0], secondArch[0], thirdArch[0], fourthArch[0])
    cmds.setAttr('Diamond_CTRL' +'.rx', -90)
    cmds.xform('Diamond_CTRL', cp=True)
    cmds.move(1,1,0, 'Diamond_CTRL', a = True)
    cmds.makeIdentity(apply =True, t=True,r=True,s=True)
    


def makeLollipop():
    length = 2
    #myCandy = cmds.circle(nr= (0,1,0), r=1)
    
    firstArch = makeArch()
    secondArch = makeArch()
    thirdArch = makeArch()
    fourthArch = makeArch()
    cmds.setAttr(secondArch[0] +'.ry', 90)
    cmds.setAttr(thirdArch[0] +'.ry', 180)
    cmds.setAttr(fourthArch[0] +'.ry', 270)
    myBar = cmds.curve(d=1, p=[(0,0,0),(0,0,length)])
    cmds.setAttr(firstArch[0] +'.tz', length+1)
    cmds.setAttr(secondArch[0] +'.tz', length+1)
    cmds.setAttr(thirdArch[0] +'.tz', length+1)
    cmds.setAttr(fourthArch[0] +'.tz', length+1)
    cmds.attachCurve( firstArch, secondArch, thirdArch, fourthArch, myBar, kmk=False, rpo=False, n = 'Lollipop_CTRL')
    cmds.delete( firstArch, secondArch, thirdArch, fourthArch, myBar)
    cmds.move(0,0,0, "Lollipop_CTRL.scalePivot", "Lollipop_CTRL.rotatePivot", absolute=True)
    cmds.setAttr('Lollipop_CTRL' +'.rx', -90)
    cmds.makeIdentity(apply =True, t=True,r=True,s=True)
    
    
def makeCube():
    length = 2
    myCube = cmds.curve(d=1, p=[(0,0,0),(length,0,0),(length,0,length),(0,0,length),(0,0,0),
                                   (0,length,0),(length,length,0),(length,0,0),(length,length,0),
                                   (length,length,length),(length,0,length),(length,length,length),
                                   (0,length,length),(0,0,length),(0,length,length),(0,length,0)])

    cmds.CenterPivot()
    cmds.xform(myCube, cp=True)
    cmds.move(0,0,0, myCube, rpr = True)
    cmds.rename('cube_CTRL')
    cmds.makeIdentity(apply =True, t=True,r=True,s=True)
    return(myCube)

clearScene()    


clearScene()    

makeCurvedArrow()    

makeArrow()

makeQuadArrow()

doubleArrow()

makeDiamond()

makeCircle()    

makeLollipop()

makeCube()
