from pynput import mouse,keyboard
import queue
import MouseActionsHanler
import KeyboardActionsHandler
import time
import LogsCreator
from pynput.keyboard import Key, KeyCode

"""
FULL PROTOCOL EXPLENATION:

EVERY message that the server sends has this structure:

        | inputDevice |   | typeOfAction |   | lengthOfData |   |------ data -------|
            1 byte             1 byte            4 bytes          lengthOfData bytes         
        
        inputDevice - 
            b'M' - MOUSE
            b'K' - KEYBOARD
            
        typeOfAction - you can see bellow
        lengthOfData - len(data)
        data - data about the action 
"""


DATA_QUEUE = queue.Queue()
last_move_time = 0

""" PROTOCOL """
#=================================
MOUSE = b'M'
KEYBOARD = b'K'

""" typeOfAction """
#=======================
# FOR MOUSE
MOUSE_MOVE = 0
MOUSE_CLICK_UP = 1
MOUSE_CLICK_DOWN = 2
MOUSE_SCROLL = 3

# FOR KEYBOARD
KEYBOARD_PRESS = 0
KEYBOARD_RELEASE = 1
#=======================


#=================================

""" LOGS """
MOUSELOG = LogsCreator.CreateMouseLog()
KEYBOARDLOG = LogsCreator.CreateKeyboardLog()


def ReadAction(sock, client_logger):
    while True:
        try:
            inputDevice = ReceiveExactNumOfBytes(sock, 1)
            if inputDevice is None:
                client_logger.warning("Failed to receive inputDevice. Skipping this iteration.")
                continue

            typeOfAction = ReceiveExactNumOfBytes(sock, 1)
            if typeOfAction is None:
                client_logger.warning("Failed to receive typeOfAction. Skipping this iteration.")
                continue
            typeOfAction = int.from_bytes(typeOfAction, byteorder='big')

            lengthOfData = ReceiveExactNumOfBytes(sock, 4)
            if lengthOfData is None:
                client_logger.warning("Failed to receive lengthOfData. Skipping this iteration.")
                continue
            lengthOfData = int.from_bytes(lengthOfData, byteorder='big')

            data = ReceiveExactNumOfBytes(sock, lengthOfData)
            if data is None:
                client_logger.warning("Failed to receive data payload. Skipping this iteration.")
                continue
            data = data.decode()

            if inputDevice == MOUSE:
                MouseActionsHanler.handleMouseAction(typeOfAction, data, client_logger)
            elif inputDevice == KEYBOARD:
                KeyboardActionsHandler.handleKeyboardAction(typeOfAction, data, client_logger)
            else:
                client_logger.error(f"Unknown input device: {inputDevice}")
        except OSError:       # socket errors
            client_logger.Info("connection closed..")
            print("connection closed..")
            break
        except UnicodeDecodeError as e:
            client_logger.error(f"Decode error: {e}. Skipping.")
            continue
        except Exception as e:
            client_logger.exception(f"Unexpected error: {e}. Continuing.")
            continue



#======================================
#               MOUSE
#======================================

def OnMove(x, y):
    global last_move_time
    now = time.time()
    if now - last_move_time < 0.2:
        return
    last_move_time = now
    inputDevice = b'M'
    typeOfAction = (0).to_bytes(1, 'big')
    y = y - 20 # there a little bit of incompatibility
    data = f'{x} {y}'.encode()
    data = inputDevice + typeOfAction + len(data).to_bytes(4, 'big') + data
    MOUSELOG.info(data)
    # insert the data to the Q
    DATA_QUEUE.put(data)

def OnClick(x, y, button, pressed):
    inputDevice = 'M'.encode()  # MOUSE
    if(pressed):
        typeOfAction = (2).to_bytes(1, 'big') # MOUSE_CLICK_UP
    else:
        typeOfAction = (1).to_bytes(1, 'big') #  MOUSE_CLICK_DOWN
    nameOfButton = button.name # 'left', 'right', 'middle'
    data = nameOfButton.encode()
    data = inputDevice + typeOfAction + len(data).to_bytes(4, 'big') + data
    MOUSELOG.info(data)
    # insert the data to the Q
    DATA_QUEUE.put(data)

def OnScroll(x, y, dx, dy):
    inputDevice = 'M'.encode()  # MOUSE
    typeOfAction = (3).to_bytes(1, 'big') # MOUSE_SCROLL
    data = f'{dy * 100}'.encode()
    data = inputDevice + typeOfAction + len(data).to_bytes(4, 'big') + data
    MOUSELOG.info(data)
    # insert the data to the Q
    DATA_QUEUE.put(data)

def CreateMouseActions():
    while True:
        try:
            with mouse.Listener(on_move=OnMove, on_click=OnClick, on_scroll=OnScroll) as listener:
                listener.join()
        except Exception as e:
            print(f"Mouse listener crashed")
            time.sleep(1)






#======================================
#               KEYBOARD
#======================================

def GetCleanKeyName(key):
    if isinstance(key, KeyCode) and key.char:
        return key.char.lower()
    elif isinstance(key, Key):
        name = key.name
        if 'ctrl' in name:
            name = 'ctrl'
        return name  # for example: 'shift', 'ctrl', 'caps_lock'
    else:
        return str(key)


def OnPress(key):
    inputDevice = 'K'.encode()  # KEYBOARD
    typeOfAction = (0).to_bytes(1, 'big')  # MOUSE_SCROLL
    nameOfKey = GetCleanKeyName(key)
    data = nameOfKey.encode()
    data = inputDevice + typeOfAction + len(data).to_bytes(4, 'big') + data
    KEYBOARDLOG.info(data)
    # put in QUEUE
    DATA_QUEUE.put(data)

def OnRelease(key):
    inputDevice = 'K'.encode()  # KEYBOARD
    typeOfAction = (1).to_bytes(1, 'big')  # MOUSE_SCROLL
    nameOfKey = GetCleanKeyName(key)
    data = nameOfKey.encode()
    data = inputDevice + typeOfAction + len(data).to_bytes(4, 'big') + data
    KEYBOARDLOG.info(data)
    #put in QUEUE
    DATA_QUEUE.put(data)

def CreateKeyboardActions():
    while True:
        try:
            with keyboard.Listener(on_press=OnPress, on_release=OnRelease) as listener:
                listener.join()
        except Exception as e:
            print(f"Keyboard listener crashed")
            time.sleep(1)
def ReceiveExactNumOfBytes(client_socket, size):
    """
    Receives exactly the specified number of bytes from the given socket.

    :param client_socket: The socket to receive data from.
    :type client_socket: socket.socket
    :param size: The exact number of bytes to receive.
    :type size: int
    :return: The received bytes, or None if the connection was closed early.
    :rtype: bytes or None
    """
    data = b''
    try:
        while len(data) < size:
            packet = client_socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
    except OSError:    # OSError catches general socket-related issues
        print('Socket-related error')

    except Exception:
        print('error')
    return data
