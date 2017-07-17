"""
twitch_bot.py:
    Simple Twitch Bot that will fire off KillDozer Commands.
"""
from __future__ import absolute_import, print_function

import logging
import random
import re
import time

import irc
import killdozer


class KilldozerBot(object):

    TWITCH_HOST = 'irc.twitch.tv'
    BOT_NICK = 'killdozerbot'
    PING_RE = re.compile(r'^PING :tmi.twitch.tv$')
    PONG_MSG = 'PONG :tmi.twitch.tv'
    KILLDOZER_COMMANDS = {
        'FORWARD': re.compile(r'^(u|up|fwd|forwards?|f)$', re.IGNORECASE),
        'BACKWARD': re.compile(r'^(d|down|bwd|backwards?|b|back(?:up)?)$', re.IGNORECASE),
        'LEFT': re.compile(r'^(l|left)$', re.IGNORECASE),
        'RIGHT': re.compile(r'^(r|right)$', re.IGNORECASE),
        'BUCKET': re.compile(r'^bucket$', re.IGNORECASE),
    }
    HELP_RE = re.compile(r'^(h|help)$', re.IGNORECASE)
    GREETING_MSG = [
        'Howdy all! Are you ready to fight for freedom?',
        'The Killdozer is online! Go to http://killdozer.online/help for help!'
    ]
    HELP_RATE = 300000  # 5 minutes
    HELP_MSG = [
        'Move Forward: u, up, fwd, forwards, f -- Move Backwards: d, down, bwd, backwards, b, backup',
        'Move Left: l, left -- Move Right: r, right',
        'Trigger Bucket: bucket',
        'Good luck fellow freedom fighter!'
    ]

    def __init__(self, oauth_token, channel_name, cmd_rate=5, sleep_rate=0.1):
        """
        Constructor.

        Args:
            oauth_token (str):      Twitch OAuth Token.
            channel_name (str):     The channel to join.
            cmd_rate (str):         Time, in seconds, between executing
                                        commands.
            sleep_rate (str):       Time, in seconds, before parsing more
                                        chat commands.
        """
        self.cmd_rate = cmd_rate
        self.sleep_rate = sleep_rate
        self._killdozer = killdozer.KilldozerControl()
        self._irc = irc.IRC(host=self.TWITCH_HOST,
                            nick=self.BOT_NICK,
                            password=oauth_token,
                            channel_name=channel_name)

    def __del__(self):
        """
        Destructor.
        """
        self._irc.receive()
        self._irc.send_msg('Killdozer is powering down. Goodbye everyone!')

    def handle_ping(self, msg):
        """
        Handle Twitch "Ping" messages by responding with a "PONG".

        Args:
            msg (str):  The message to check for a "Ping".
        """
        if self.PING_RE.match(msg):
            logging.debug('Got Ping! Sending PONG')
            self._irc.send_raw(self.PONG_MSG)
            return

    def _extract_msg_body(self, msg):
        """
        Strip out all metadata from an incoming message, and get only
            the actual message body.

        Args:
            msg (str):  The message to format.

        Returns:
            list of processed str
        """
        return re.sub(r'^:', '', ' '.join(msg.split()[3:]))

    def _extract_msg_username(self, msg):
        """
        Extract a username form a message.

        Args:
            msg (str):  The message to extract the user from.

        Returns:
            str
        """
        return re.sub(r'^:', '', msg.split()[0].split('!')[0]).strip()

    def _search_for_commands(self, msg):
        """
        Given a message, search it for a command.

        Args:
            msg (str):  The message to search.

        Returns:
            str if command is found, None otherwise.
        """
        for cmd, regex in self.KILLDOZER_COMMANDS.iteritems():
            if regex.match(self._extract_msg_body(msg)):
                logging.debug('Found Command: {}'.format(cmd))
                return cmd

    def _select_command(self, cmds):
        """
        Given a list of commands, select the one that occurs the most.
            In the case of a tie, randomly choose one.

        Args:
            cmds (list):    List of user inputted commands.
        """
        winning_cmd = ''
        winning_count = 0
        cmd_set = set(cmds)
        for cmd in cmd_set:
            count = cmds.count(cmd)
            if count >= winning_count:
                if count == winning_count:
                    winning_count = random.choice([winning_cmd, cmd])
                else:
                    winning_count = count
                winning_cmd = cmd

        return winning_cmd

    def _handle_help(self, msg):
        """
        Search a message for the Help command, if found, DM a user
            the HELP message.

        Arg:
            msg (str):      Msg to search for HELP command.
        """
        if self.HELP_RE.match(self._extract_msg_body(msg)):
            print('USER: {}'.format(self._extract_msg_username(msg)))
            for line in self.HELP_MSG:
                self._irc.send_msg(
                    '/w {username} {line}'.format(
                        username=self._extract_msg_username(msg),
                        line=line
                    )
                )

    def _send_multiline_msg(self, msg_list):
        """
        Send the user a muliline message.

        Args:
            msg (list): List of messages to send.
        """
        for line in msg_list:
            self._irc.receive()
            self._irc.send_msg(line)
            time.sleep(1)

    def _dispatch_command(self, cmd):
        """
        Dispatch the winning command.

        Args:
            cmd (str):  The winning command.
        """
        func = getattr(self._killdozer, 'move_{}'.format(cmd.strip().lower()))
        func()

    def run(self):
        """
        Main Loop.
        """
        cmd_rate_millis = self.cmd_rate * 1000

        self._send_multiline_msg(self.GREETING_MSG)
        self._send_multiline_msg(self.HELP_MSG)

        def current_time_millis():
            return int(round(time.time() * 1000))

        cmds = []
        execute_time = current_time_millis() + cmd_rate_millis
        help_time = current_time_millis() + self.HELP_RATE
        while True:
            input_msgs = self._irc.receive()
            if input_msgs:
                input_msgs = input_msgs.splitlines()
                map(self.handle_ping, input_msgs)
                map(logging.debug, input_msgs)
                map(self._handle_help, input_msgs)
                cmds.extend(
                    filter(lambda x: x is not None,
                           map(self._search_for_commands, input_msgs)))

            if current_time_millis() >= execute_time and cmds:
                logging.debug('CMDS: {}'.format(cmds))
                winning_cmd = self._select_command(cmds)
                logging.debug('Winning CMD: {}'.format(winning_cmd))
                self._irc.send_msg('Winning Command: {}'
                                   .format(winning_cmd.title()))
                self._dispatch_command(winning_cmd)
                cmds = []
                execute_time = current_time_millis() + cmd_rate_millis

            if current_time_millis() >= help_time:
                self._send_multiline_msg(self.HELP_MSG)
                help_time = current_time_millis() + self.HELP_RATE

            time.sleep(self.sleep_rate)
