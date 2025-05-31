import logging

def CreateLogger(name, filename):
    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG)

    if not logger.handlers: # prevent double writing. if there is already a handker we skip.
        handler = logging.FileHandler(filename, mode='w')

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger

def CreateServerLog():
    return CreateLogger('server_logger', 'ServerLog.log')

def CreateClientLog():
    return CreateLogger('client_logger', 'ClientLog.log')

def CreateMouseLog():
    return CreateLogger('mouse_logger', 'MouseLog.log')

def CreateKeyboardLog():
    return CreateLogger('keyboard_logger', 'KeyboardLog.log')
