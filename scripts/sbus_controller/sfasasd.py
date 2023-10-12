from sbus_interface import SBUSReceiver, SBUSData
import logging 
import time
import numpy as np

default_logger = logging.getLogger(__name__)
default_logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

default_logger.addHandler(ch)

rx = SBUSReceiver(default_logger)

channels = np.zeros((1,3))
while True:

    if(channels.shape[0] > 6):
        channels = channels[1:, :]

    # channels = np.append(channels,[rx.channel[:3]], axis=0)
    # print(np.median(channels[:, 0]))
    # print(rx.queue.get())
    time.sleep(0.01)
