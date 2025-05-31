import cv2
import socket

def send_frame(sock, frame):
    """
    Compresses and sends a video frame over the given socket.

    The frame is JPEG-compressed to reduce its size, then sent with a 4-byte
    length prefix indicating the size of the data.

    :param sock: The socket to send data through.
    :type sock: socket.socket
    :param frame: The video frame to be sent (as a NumPy array).
    :type frame: numpy.ndarray
    :return: True if the frame was successfully encoded and sent, False otherwise.
    :rtype: bool
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    result, img_encoded = cv2.imencode('.jpg', frame, encode_param)
    if not result:
        return False

    data = img_encoded.tobytes()
    sock.sendall(len(data).to_bytes(4, 'big'))
    sock.sendall(data)
    return True


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
