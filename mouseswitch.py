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

def get_workspaces():
    workspaces = i3.get_workspaces()
    if isinstance(workspaces, list):
        return [ws for ws in workspaces if isinstance(ws, dict)]
    return []

def get_workspace_curr(workspaces=None):
    if workspaces is None:
        workspaces = get_workspaces()
    workspaces_focused = [ws for ws in workspaces if ws['focused'] == True]
    if workspaces_focused:
        return workspaces_focused[0]
    return {}

def get_workspace_rects(workspace):
    return workspace['rect']['width'] - 1, workspace['rect']['height'] - 1

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

def workspace_nth_next(edges, workspace_curr, workspaces):
    workspace_curr_nth = workspace_curr['num']
    if edges in ('left', 'top_left', 'bottom_left'):
        next = [ws['num'] for ws in workspaces if ws['num'] < workspace_curr_nth]
        if not next:
            return workspaces[-1]['num']
        return next[-1]
    elif edges in ('right', 'top_right', 'bottom_right'):
        next = [ws['num'] for ws in workspaces if ws['num'] > workspace_curr_nth]
        if not next:
            return workspaces[0]['num']
        return next[0]
    return -1

def workspace_switch_for(edges):
    if edges in ('left', 'top_left', 'bottom_left'):
        return 'prev'
    elif edges in ('right', 'top_right', 'bottom_right'):
        return 'next'
    return None

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
    workspace_curr = get_workspace_curr()
    x_max, y_max = get_workspace_rects(workspace_curr)
    while True:
        edges = get_edge_or_corner(x_max, y_max)
        if not edges is None:
            workspaces = get_workspaces()
            workspaces_len = len(workspaces)
            logging.debug('workspaces length: %i' % workspaces_len)

            # Just only workspace, do nothing
            if workspaces_len <= 1:
                time.sleep(delay + quiesce)
                continue

            workspace_curr = get_workspace_curr(workspaces)
            x_max, y_max = get_workspace_rects(workspace_curr)

            logging.debug('edges: %s, workspace_curr: %s, workspaces_len: %s' % \
                (edges, workspace_curr, workspaces_len))

            next_for = workspace_switch_for(edges)
            logging.info('exec workspace %s' % next_for)
            if next_for:
                i3.command('workspace', next_for)

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
