# -*- coding: utf-8 -*-

from __future__ import absolute_import

import argparse
import sys

import yaml

from log2mq import Log2MQ


def read_config(filepath):
    """read target yaml config file"""
    config = None
    with open(filepath) as f:
        config = yaml.load(f.read())
    return config

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--config', required=True)

    option = ap.parse_args()

    config = read_config(option.config)

    _ = Log2MQ(config=config)
    _.transfer()

if __name__ == '__main__':
    sys.exit(main())
