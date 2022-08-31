from Brain import Management

from signal import signal, SIGINT

if __name__ == "__main__":
    p = Management()
    signal(SIGINT, p.saveOnExit)
    p.mainSystemLoop()
