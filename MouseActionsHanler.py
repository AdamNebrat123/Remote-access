import pyautogui
import logging





def handleMouseAction(typeOfAction, data, client_logger):
    if typeOfAction == 0:
        MouseMove(data)
        client_logger.info("moved!")
    if typeOfAction == 1:
        MouseClickUp(data)
        client_logger.info("clicked up!")

    if typeOfAction == 2:
        MouseClickDown(data)
        client_logger.info("clicked down!")

    if typeOfAction == 3:
        MouseScroll(data)
        client_logger.info("scrolled!")


def MouseClickUp(data):
    nameOfButton = data  # 'left', 'right', or 'middle'
    pyautogui.mouseUp(button=nameOfButton)

def MouseClickDown(data):
    nameOfButton = data # 'left', 'right', or 'middle'
    pyautogui.mouseDown(button=nameOfButton)


def MouseMove(data):
    data = data.split() # data looks like '{x} {y}'
    x = int(data[0])
    y = int(data[1])
    pyautogui.moveTo(x, y)


def MouseScroll(data):
    data = int(data)
    pyautogui.scroll(data)