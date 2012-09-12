# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>
__author__ = 'John Hampton <pacopablo@pacopablo.com>'

from setuptools import setup

setup(
    name='pywinservice',
    version='0.8',
    packages=['pywinservice'],
    author='John Hampton',
    author_email='pacopablo@pacopablo.com',
    description='Scaffolding for running Python programs as Windows NT Services',
    url='https://pacopablo.github.com/pywinservice',
    license='MIT',
    zip_safe = False,
    long_description = """
    pywinservice
    ==============

    pywinservice provides classes and a function that take care of the mess
    having to do with running python as a Windows NT Service.

    Usage
    -------

    .. code-block:: python

        from pywinservice import NTService, NTServiceThread, handle_command_line

        class MyServiceThread(NTServiceThread):

            def run (self):
                while self.notifyEvent.isSet():
                    # do stuff here.  be careful not to block, however, as that will
                    # cause the service to hang when shutting down
                    continue


        class MyService(NTService):
            _svc_name_ = 'myservice'            # used in "net start/stop"
            _svc_display_name_ = "My Service"
            _svc_description_ = "This is what My Service does"
            _svc_thread_class = MyServiceThread


        if __name__ == '__main__':
            handle_command_line(MyService)

    """

)
