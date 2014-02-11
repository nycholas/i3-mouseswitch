i3-mouseswitch
==============

This utility for i3, inspired `FVWM-Crystal <http://fvwm-crystal.sourceforge.net>`_, you move between workspaces using the mouse.


Adding i3-mouseswitch to your i3 config
***************************************

1. Installation

::

    $ pip install i3-mouseswitch

or

::

    $ git clone git://github.com/nycholas/i3-mouseswitch.git
    $ cd i3-mouseswitch
    $ python setup.py install


2. Usage

Adding in their settings i3 (~/.i3/config).

::

    # mouse behave screen edge
    exec_always --no-startup-id mouseswitch.py
    

Dependecies
***********

* Python 3.2, 3.3 or later (http://www.python.org)
* i3-py 0.6.5 or later (https://github.com/ziberna/i3-py)


Project Information
*******************

:Author: Nycholas de Oliveira e Oliveira
:E-Mail: nycholas@gmail.com
:Version: v0.0.1 of 2014/02/10
:License: `New BSD License <http://opensource.org/licenses/BSD-3-Clause>`_
