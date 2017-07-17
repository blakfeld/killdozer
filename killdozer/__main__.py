#!/usr/bin/env python
"""
killdozer: TwitchBot to Control an RC Bulldozer - Because Why Not?

Usage:
    killdozer --oauth-token=<TOKEN> --channel-name=<NAME> [options]
    killdozer --config-file=<FILE> [options]

Options:
    -v --verbose        Toggle verbose output.
    --cmd-rate=RATE     Time, in seconds, between executing commands [default=5]
    --sleep-rate=RATE   Time, in seconds, between parsing commands [default=0.1]
    -h --help           Display this message
"""
from __future__ import absolute_import, print_function

import logging
import os
import sys

import yaml
from docopt import docopt

from twitch_bot import KilldozerBot


def parse_config_file(fpath):
    """
    Parse a given config file.

    Args:
        fpath (str):    Path to config file.

    Returns:
        dict
    """
    if not os.path.isfile(fpath):
        raise RuntimeError('ERROR: Unable to find config file at path: {}'
                           .format(fpath))

    with open(fpath, 'r') as f:
        return yaml.safe_load(f)


def parse_config(args):
    """
    Parse our CLI/config file into something useful.

    Args:
        args (dict):    CLI args.

    Returns:
        dict
    """
    if args.get('--config-file'):
        config = parse_config_file(args.get('--config-file'))
    else:
        config = {
            'oauth_token': args['--oauth-token'],
            'channel_name': args['--channel-name'],
            'cmd_rate': args['--cmd-rate'],
            'sleep_rate': args['--sleep-rate'],
        }

    return config


def main():
    """
    Main.
    """
    args = docopt(__doc__)
    if args.get('--verbose'):
        logging.basicConfig(level=logging.DEBUG)
    config = parse_config(args)
    kdBot = KilldozerBot(**config)
    kdBot.run()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Exiting!')
        sys.exit(1)
