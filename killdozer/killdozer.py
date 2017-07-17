"""
killdozer.py:
    Control the KillDozer.
"""
from __future__ import absolute_import, print_function

import logging
import time

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


class KilldozerControl(object):
    PIN_MAP = {
        'LEFT_FORWARD': 2,
        'LEFT_BACKWARD': 3,
        'RIGHT_FORWARD': 17,
        'RIGHT_BACKWARD': 4,
        'BUCKET': 27
    }

    def __init__(self):
        """
        Constructor.
        """
        self._init_relay()

    def __del__(self):
        """
        Destructor.
        """
        GPIO.cleanup()

    def _init_relay(self):
        """
        Initialize the relay.
        """
        for pin in self.PIN_MAP.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

    def _toggle_pins(self, pins, sleep_time=2):
        """
        Toggle a list of pins om adm off.

        Args:
            sleep_time (int):   Time, in seconds, to leave a pin toggled
                                    in the "on" state. This is effectively
                                    how long an action runs.
        """
        for pin in pins:
            GPIO.output(pin, GPIO.LOW)
        time.sleep(sleep_time)
        for pin in pins:
            GPIO.output(pin, GPIO.HIGH)

    def move_forward(self):
        """
        Move the Killdozer Forward.
        """
        logging.debug('Moving Forward')
        self._toggle_pins([
            self.PIN_MAP['LEFT_FORWARD'],
            self.PIN_MAP['RIGHT_FORWARD'],
        ])

    def move_backward(self):
        """
        Move the Killdozer Backwards.
        """
        logging.debug('Moving Backward')
        self._toggle_pins([
            self.PIN_MAP['LEFT_BACKWARD'],
            self.PIN_MAP['RIGHT_BACKWARD'],
        ])

    def move_left(self):
        """
        Move the Killdozer Left.
        """
        logging.debug('Moving Right')
        self._toggle_pins([
            self.PIN_MAP['LEFT_BACKWARD'],
        ], 0.5)

    def move_right(self):
        """
        Move the Killdozer Right.
        """
        logging.debug('Moving Right')
        self._toggle_pins([
            self.PIN_MAP['RIGHT_BACKWARD'],
        ], 0.5)

    def move_bucket(self):
        """
        Trigger the Killdozer Bucket.
        """
        logging.debug('Moving Right')
        self._toggle_pins([
            self.PIN_MAP['BUCKET'],
        ])
