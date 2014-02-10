#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

if sys.hexversion < 0x02070000:
    print("This script requires Python 2.7 or later.")
    print("Currently run with version: {0}".format(sys.version))
    print("Please install it. The source for Python can be found at: " \
          "http://www.python.org/.")
    sys.exit(-1)

import os
import re
import time
import logging
import argparse
import subprocess

import i3

__version__ = '0.0.1'

DEVNULL = open(os.devnull, 'w')

def get_mouse_location():
    mouse_location = subprocess.check_output(['xdotool', 'getmouselocation'], 
        stdin=DEVNULL, stderr=subprocess.STDOUT)
    return re.findall(r'x:([0-9]+) y:([0-9]+)', str(mouse_location))[0]

def set_mouse_location(x, y):
    subprocess.call(['xdotool', 'mousemove', str(x), str(y)], 
        stdin=DEVNULL, stdout=DEVNULL, stderr=subprocess.STDOUT)

def get_edge_or_corner(x_max, y_max):
    x, y = map(int, get_mouse_location())
    logging.debug('x: %i == %i, y: %i == %i' % (x, x_max, y, y_max))
    if x == 0 and y == 0:
        return 'top_left'
    elif x == 0 and y == y_max:
        return 'bottom_left'
    elif x == x_max and y == 0:
        return 'top_right'
    elif x == 0:
        return 'left'
    elif y == 0:
        return 'top'
    elif x == x_max and y == y_max:
        return 'bottom_right'
    elif x == x_max:
        return 'right'
    elif y == y_max:
        return 'bottom'
    return None

def workspace_nth_next(edges, workspace_curr, workspaces_len):
    workspace_curr_nth = workspace_curr['num']
    if edges in ('left', 'top_left', 'bottom_left'):
        next = workspace_curr_nth - 1
        if next < 1:
            return workspaces_len
        return next
    elif edges in ('right', 'top_right', 'bottom_right'):
        next = workspace_curr_nth + 1
        if next > workspaces_len:
            return 1
        return next
    return -1

def new_mouse_location(edges, x_max, y_max):
    x, y = map(int, get_mouse_location())
    if edges in ('left', 'top_left', 'bottom_left'):
        return x_max - 5, y
    elif edges in ('right', 'top_right', 'bottom_right'):
        return 5, y
    return (-1, -1)

def cmd_behave_screen_edge(delay, quiesce, verbose):
    delay = delay / 1000 if delay > 0 else delay
    quiesce = quiesce / 1000 if quiesce > 0 else delay
    while True:
        try: # https://github.com/ziberna/i3-py/issues/9 
            workspaces = i3.get_workspaces()
        except UnicodeDecodeError as e:
            logging.error('error in i3.get_workspaces() command: %s' % str(e))
            time.sleep(delay * 2)
            continue
        workspaces_len = len(workspaces) if not workspaces is None else 1
        logging.debug('workspaces length: %i' % workspaces_len)

        # Just only workspace, do nothing
        if workspaces_len <= 1:
            time.sleep(delay + quiesce)
            continue

        workspace_root = sorted(workspaces, key=lambda ws: ws['num'])[0]
        workspace_curr = [ws for ws in workspaces if ws['focused'] == True][0]
        x_max = workspace_root['rect']['width'] - 1
        y_max = workspace_root['rect']['height'] - 1

        edges = get_edge_or_corner(x_max, y_max)
        if not edges is None:
            logging.info('[OK] edges: %s, workspace_curr: %s, workspaces_len: %s' % \
                (edges, workspace_curr, workspaces_len))

            next = workspace_nth_next(edges, workspace_curr, workspaces_len)
            logging.debug('exec workspace %i' % next)
            if next != -1:
                i3.command('workspace', str(next))

            x_new, y_new = new_mouse_location(edges, x_max, y_max)
            logging.debug('exec xdotool mousemove %i %i' % (x_new, y_new))
            if x_new != -1 and y_new != -1:
                set_mouse_location(x_new, y_new)

            time.sleep(quiesce)
            continue
        time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(
        usage='%(prog)s edge [options...]',
        description='Mouse switch workspace')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--verbose', action='store_true', default=False, help='verbose mode')
    parser.add_argument('-d', '--delay', type=int, default=150,
        help='delay before activating. During this time your mouse ' \
             'must stay in the area selected (corner or edge) otherwise ' \
             'this timer will reset. Default is no delay 150 (0.15 seconds).')
    parser.add_argument('-q', '--quiesce', type=int, default=200,
        help='quiet time period after activating that no ' \
             'new activation will occur. This helps prevent accidental ' \
             're-activation immediately after an event. Default is 200 (0.2 ' \
             'seconds).')
    options = vars(parser.parse_args())

    logging.basicConfig(level=logging.INFO if not options['verbose'] else logging.DEBUG)
    logging.debug('options: {0}'.format(options))

    cmd_behave_screen_edge(**options)


if __name__ == '__main__':
    main()
