import threading
import videoProtocol
import socket
import cv2
import numpy as np
import KBMprotocol
import LogsCreator



def StartListeningSocket(IP, PORT):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    return server_socket

def main():
    server_logger = LogsCreator.CreateServerLog()
    IP_VIDEO = '0.0.0.0'
    PORT_VIDEO = 8200

    # start listening video socket
    video_server_socket = StartListeningSocket(IP_VIDEO, PORT_VIDEO)
    print(f"Video - Waiting for connection in {IP_VIDEO}:{PORT_VIDEO}...")
    server_logger.info(f"Video - Waiting for connection in {IP_VIDEO}:{PORT_VIDEO}...")


    # accept
    video_client_socket, addr = video_server_socket.accept()
    print(f"connected to {addr}")
    server_logger.info(f"connected to {addr}")

    IP_ACTIONS = '0.0.0.0'
    PORT_ACTIONS = 8201
    

    # start listening actions socket
    actions_server_socket = StartListeningSocket(IP_ACTIONS, PORT_ACTIONS)
    print(f"actions - Waiting for connection in {IP_ACTIONS}:{PORT_ACTIONS}...")
    server_logger.info(f"actions - Waiting for connection in {IP_ACTIONS}:{PORT_ACTIONS}...")

    # accept
    actions_client_socket, addr = actions_server_socket.accept()
    print(f"connected to {addr}")
    server_logger.info(f"connected to {addr}")

    # videoShowThread - thread that shows frames nonstop. shows the screen of the client.
    videoShowThread = threading.Thread(target=ShowScreen, args=(video_client_socket,video_server_socket, server_logger))

    # start videoShowThread - start the share screen.
    videoShowThread.start()
    server_logger.info('**********\n* videoShowThread started! *\n**********')


    # listenToMouseActionsThread - thread that listens to MOUSE actions.
    listenToMouseActionsThread = threading.Thread(target=KBMprotocol.CreateMouseActions)

    #start listenToMouseActionsThread - start listening
    listenToMouseActionsThread.start()

    # listenToKeyBoardActionsThread - thread that listens to KEYBOARD actions.
    listenToKeyBoardActionsThread = threading.Thread(target=KBMprotocol.CreateKeyboardActions)

    # start listenToKeyBoardActionsThread - start listening
    listenToKeyBoardActionsThread.start()

    # sendActionsThread - thread that send actions to the client
    sendActionsThread = threading.Thread(target=SendActions, args=(actions_client_socket,actions_server_socket,server_logger))

    # start sendActionsThread - start sending actions to the client.
    sendActionsThread.start()
    server_logger.info('**********\n* sendActionsThread started! *\n**********')

def ShowScreen(video_client_socket, video_server_socket, server_logger):
    try:
        while True:
            # read 4 bytes for the size of the frame (4 bytes - int size)
            raw_len = videoProtocol.ReceiveExactNumOfBytes(video_client_socket, 4)
            if not raw_len:
                break
            img_len = int.from_bytes(raw_len, byteorder='big')

            # read the actual img
            data = videoProtocol.ReceiveExactNumOfBytes(video_client_socket, img_len)
            if not data: # data = 0  - false, else true
                break

            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow('Stream', frame)
                if cv2.waitKey(1) == 27:  # ESC
                    break
            else:
                print('Could not read the frame')
                server_logger.warning('Could not read the frame')
    finally:
        video_client_socket.close()
        video_server_socket.close()
        cv2.destroyAllWindows()

def SendActions(actions_client_socket, actions_server_socket, server_logger):
    try:
        while True:
            data = KBMprotocol.DATA_QUEUE.get() # blocking method that wait for data in the Q
            server_logger.info(repr(data.decode()))
            actions_client_socket.sendall(data)

    except Exception:
            print('error')
            server_logger.error('error')
    finally:
            actions_client_socket.close()
            actions_server_socket.close()
if __name__ == '__main__':
    main()
