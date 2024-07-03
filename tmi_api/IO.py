import numpy as np
import cv2 as cv
import pyautogui as pdi
import pydirectinput as pdi
import time as t
import keyboard as keyb
import tminterface as tmi


def screenimage():
    image = pdi.screenshot()
    image = cv.cvtColor(np.array(image),cv.COLOR_RGB2BGR)
    cv.imwrite("image.png",image)

Lkey = ['up','down','left','right']

class controller:

    def press_up(length):
        pdi.keyDown(Lkey[0])
        t.sleep(length)
        pdi.keyUp(Lkey[0])

    def press_down(length):
        pdi.keyDown(Lkey[1])
        t.sleep(length)
        pdi.keyUp(Lkey[1])

    def press_left(length):
        pdi.keyDown(Lkey[2])
        t.sleep(length)
        pdi.keyUp(Lkey[2])

    def press_right(length):
        pdi.keyDown(Lkey[3])
        t.sleep(length)
        pdi.keyUp(Lkey[3])

    def press_up_left(length):
        pdi.keyDown(Lkey[0])
        pdi.keyDown(Lkey[2])
        t.sleep(length)
        pdi.keyUp(Lkey[0])
        pdi.keyUp(Lkey[2])

    def press_up_right(self,length):
        pdi.keyDown(Lkey[0])
        pdi.keyDown(Lkey[3])
        t.sleep(length)
        pdi.keyUp(Lkey[0])
        pdi.keyUp(Lkey[3])

    def key_error():
        print("Error: Invalid key selected")

    def runKey(self,key,length):
        actions = {
            'up': self.press_up,
            'down': self.press_down,
            'left': self.press_left,
            'right': self.press_right,
            'up-left': self.press_up_left,
            'up-right': self.press_up_right}
        runkey = actions.get(key,self.key_error)
        runkey(length)


c = controller

def test():
    t.sleep(2)
    print("running key")
    c.runKey('up',0.2)
    c.runKey('right',0.1)
    c.runKey('left',0.1)
    c.runKey('up',0.2)
    c.runKey('up',3)
    print("end")




