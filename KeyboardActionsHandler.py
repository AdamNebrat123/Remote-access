import pyautogui
import logging



def handleKeyboardAction(typeOfAction, data, client_logger):
    if typeOfAction == 0:
        PressKey(data)
        client_logger.info(f"Pressed: {data}")
    elif typeOfAction == 1:
        ReleaseKey(data)
        client_logger.info(f"Released: {data}")

def PressKey(data):
    pyautogui.keyDown(data)

def ReleaseKey(data):
    pyautogui.keyUp(data)