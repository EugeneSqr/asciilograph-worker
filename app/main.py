import sys
import os
import signal
from time import sleep

from settings import get_settings

def signal_handler(signum, frame):
    print(f"Signal received {signal.Signals(signum).name} ({signum})")
    print(f"Restarting the worker process")
    os.execl(sys.executable, sys.executable, * sys.argv)
    print(f"Restarting done")

signal.signal(signal.SIGHUP, signal_handler)

if __name__ == "__main__":
    while True:
        print(">>>>", get_settings())
        sleep(10)
