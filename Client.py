import socket
import cv2
import logging
import pyautogui
import numpy as np
import LogsCreator
import KBMprotocol
import videoProtocol
import threading



def CaptureScreen():
    """
        Captures the current screen and returns it as a BGR image.

        Takes a screenshot of the entire screen using pyautogui, converts it to
        a NumPy array, and then converts the color format from RGB to BGR
        for OpenCV compatibility.

        :return: The captured screen as a BGR image.
        :rtype: numpy.ndarray
    """
    image = pyautogui.screenshot()

    frame = np.array(image)
    # convert to blue green red (BGR)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame

def SendFramesNonStop(sock, client_logger):
    """
        Continuously captures and sends screen frames over a socket.

        stops on failure or if the ESC key is pressed.

        :param sock: The socket used to send frames.
        :type sock: socket.socket
        :param client_logger: Logger object used to record errors.
        :type client_logger: logging.Logger
    """

    try:
        while True:
            frame = CaptureScreen()

            if not videoProtocol.send_frame(sock, frame):
                print('failed to send img')
                client_logger.error('failed to send img')
                break
            # press ESC to stop
            if cv2.waitKey(1) == 27:
                break
    except Exception:
        client_logger.error('error')
    finally:
        sock.close()

def main():
    client_logger = LogsCreator.CreateClientLog()

    #Connect to video socket
    SERVER_IP = '192.168.1.30'
    PORT_VIDEO = 8200
    video_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_sock.connect((SERVER_IP, PORT_VIDEO))
    print("Connected to server")
    client_logger.info('Connected to server')

    # Connect to action socket
    PORT_ACTIONS = 8201
    actions_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    actions_sock.connect((SERVER_IP, PORT_ACTIONS))
    print("Connected to server")
    client_logger.info('Connected to server')


    # sendFramesThread - thread that sends frames nonstop.
    sendFramesThread = threading.Thread(target=SendFramesNonStop, args=(video_sock, client_logger))

    # start sendFramesThread - start sending frames
    sendFramesThread.start()
    client_logger.info('**********\n* sendFramesThread started! *\n**********')

    # readingActionsThread - thread that read the actions.
    readingActionsThread = threading.Thread(target=KBMprotocol.ReadAction, args=(actions_sock,client_logger))

    # start sendFramesThread - start sending frames
    readingActionsThread.start()
    client_logger.info('**********\n* readingActionsThread started! *\n**********')

if __name__ == '__main__':
    main()