#!/usr/bin/python
# -*- coding: utf-8 -*-
import rospy
import rosparam
from sensor_msgs.msg import Joy
from sbus_controller.sbus_interface import SBUSReceiver

import time

class ROSLogger(object):
    """Imitate a standard Python logger, but pass the messages to rospy logging.
    """
    def debug(self, msg):    rospy.logdebug("[%s] %s"%(rospy.get_name(), msg)) 
    def info(self, msg):     rospy.loginfo("[%s] %s"%(rospy.get_name(), msg))
    def warn(self, msg):     rospy.logwarn("[%s] %s"%(rospy.get_name(), msg))
    def error(self, msg):    rospy.logerr("[%s] %s"%(rospy.get_name(), msg))
    def critical(self, msg): rospy.logfatal("[%s] %s"%(rospy.get_name(), msg))      

class SBUSNode:
    def __init__(self):
        self.__default_params = {"port": '/dev/ttyUSB0',
                                 "two_state_buttons": [8, 9],
                                 "tri_state_buttons": [4, 5, 6, 7],
                                 "invert_channels": [],
                                 "publish_rate": 20}

        param_list = rosparam.list_params(rospy.get_name())
        
        params = {}
        for i in range(len(param_list)):
            param_list[i] = param_list[i].replace(rospy.get_name()+"/", "", 1)
            params[param_list[i]] = rospy.get_param("~"+param_list[i])

        for default_key in self.__default_params.keys():
            if default_key not in params.keys():
                params[default_key] = self.__default_params[default_key]

        self.publish_rate       = params["publish_rate"]
        self.two_state_buttons  = params["two_state_buttons"]
        self.tri_state_buttons  = params["tri_state_buttons"]
        self.invert_channels    = params["invert_channels"]
        
        self.ros_logger = ROSLogger()
        self.rx = SBUSReceiver(self.ros_logger, params)
        self.publisher = rospy.Publisher("joy", Joy, queue_size=1)

        self.joy = Joy()
        self.joy.axes = 16*[0]
        self.joy.buttons = 16*[0]

        self.publish_joy_timer = rospy.Timer(rospy.Duration(1.0/self.publish_rate), self.publish_joy)

    def __del__(self):
        self.publish_joy_timer.join()

    def scale(self, value, bound=tuple, offset=0, multiplier=1):
        if(offset == 0):
            return (value-bound[0])/(bound[1]-bound[0]) * multiplier
        
        return (value-offset)/(bound[1]-bound[0]) * multiplier

    def publish_joy(self, timerEvent):
        if self.rx.failsafe_event.is_set():
            rospy.logerr_throttle(1, "[%s] SBUS Receiver sent failsafe bit! Please check your if your Transmitter still alive." %(rospy.get_name()))
            return

        # If the Deque is empty, wait for 1 second 
        # to fill up the deque with data then proceed
        try:
            channels = self.rx.deque.pop()
        except IndexError:
            rospy.logwarn_throttle(1, "[%s] No data has been received yet. Serial buffer size: %d"%(rospy.get_name() ,self.rx.ser.in_waiting))
            return

        for i in range(len(channels)):
            scale_value = self.scale(channels[i], (172,1811), 991.5, 2)
            if i in self.invert_channels:
                scale_value *= -1.0
                
            if(scale_value < 0.01 and scale_value > -0.01):
                self.joy.axes[i] = 0
            else:
                self.joy.axes[i] = scale_value

            if i in self.two_state_buttons:
                if scale_value <= 0.0:
                    self.joy.buttons[i] = 0
                else:
                    self.joy.buttons[i] = 1
                continue

            if i in self.tri_state_buttons:
                if scale_value == -1.0:
                    self.joy.buttons[i] = 0
                elif scale_value == 1.0:
                    self.joy.buttons[i] = 2
                else:
                    self.joy.buttons[i] = 1
                continue
        
        self.publisher.publish(self.joy)

if __name__ == "__main__":
    rospy.init_node("sbus_node")

    sbus_node = SBUSNode()

    while not rospy.is_shutdown():
        rospy.spin()
