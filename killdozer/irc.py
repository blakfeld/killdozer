"""
irc.py:
    Class to connect to and interact with an IRC server.
"""
from __future__ import absolute_import, print_function

import logging
import select
import socket
import time


class IRC(object):
    def __init__(self,
                 host,
                 channel_name,
                 nick,
                 password=None,
                 port=6667):
        """
        Constructor.

        Args:
            host (str):             The IRC server to connect to.
            channel_name (str):     The channel to join.
            nick (str):             The NICK to use.
            password (str):         The PASS to use.
            port (int):             The port to connect on.
            debug (bool):           Toggle printing debug text.
        """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = host
        self.port = port
        self.nick = nick
        self.password = password
        self.channel_name = self._format_channel_name(channel_name)

        self._connect()

    def _format_channel_name(self, channel_name):
        """
        Ensure that the provided "Channel Name" begins with a "#".

        Args:
            channel_name (str):     The channel name to format.

        Returns:
            str
        """
        if not channel_name.startswith('#'):
            return '#{}'.format(channel_name)
        else:
            return channel_name

    def _connect(self):
        """
        Connect to IRC server.
        """
        self._sock.connect((self.host, self.port))
        self.send_raw('PASS {}'.format(self.password))
        self.send_raw('NICK {}'.format(self.nick))
        self.send_raw('JOIN {}'.format(self.channel_name))

    def send_msg(self, msg):
        """
        Send a message to the configured channel.

        Args:
            msg (str):      The Message to send.
        """
        self.send_raw('PRIVMSG {channel_name} :{msg}'
                      .format(channel_name=self.channel_name, msg=msg))

    def send_raw(self, msg):
        """
        Send a message.

        Args:
            msg (str):  The message to send.
        """
        logging.debug('Sending Raw Message: {msg}'
                      .format(msg=msg.encode('utf-8')))
        self._sock.send('{msg}\r\n'.format(msg=msg.encode('utf-8')))

    def receive(self, byte_count=1024):
        """
        Receive input from the IRC server.

        Args:
            byte_count (int):   The number of bytes to receive from
                                    the socket.

        Returns:
            str
        """
        self._sock.setblocking(0)

        data = None
        sock_ready = select.select([self._sock], [], [], 0.5)
        if sock_ready[0]:
            data = self._sock.recv(byte_count).decode('utf-8').strip()

        self._sock.setblocking(1)
        return data
