from djedjbot.util import make_private_client

if __name__ == '__main__':
    c = make_private_client('chmieljj')
    dev = c.devices()
    pass