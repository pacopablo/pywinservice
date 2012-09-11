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


import sys
import traceback
import win32serviceutil
import win32service
import win32event


from threading import Thread, Event

__all__ = [
    'NTServiceThread',
    'NTServiceFramework',
    'handle_command_line',
]

def getTrace():
    """ retrieve and format an exception into a nice message
    """
    msg = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1],
                                     sys.exc_info()[2])
    msg = ''.join(msg)
    msg = msg.split('\012')
    msg = ''.join(msg)
    msg += '\n'
    return msg


class NullOutput:
    """A stdout / stderr replacement that discards everything."""

    def noop(self, *args, **kw):
        pass
    write = writelines = close = seek = flush = truncate = noop

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def isatty(self):
        return False

    def tell(self):
        return 0

    def read(self, *args, **kw):
        return ''

    readline = read

    def readlines(self, *args, **kw):
        return []


class NTServiceThread(Thread):

    def __init__(self, eventNotifyObj):
        """ Initializes the thread with a signal used for stopping the thread
        """
        Thread.__init__(self)
        self.notifyEvent = eventNotifyObj

    def run (self):
        """ This method must be overwritten.

        The ``run`` method is the core of the server. In this thread the actual
        work the service is providing should be done
        """

        while self.notifyEvent.isSet():
            # do stuff here
            continue



class NTServiceFramework(win32serviceutil.ServiceFramework):
    """ Windows NT Service class for running a bottle.py server """

    _svc_name_ = ''
    _svc_display_name_ = "pywinservice"
    _svc_description_ = "pywinservice: NT Service Framework"
    _svc_thread_class = None

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.redirectOutput()
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)


    def redirectOutput(self):
        """ Redirect stdout and stderr to the bit-bucket.

        Windows NT Services do not do well with data being written to stdout/stderror.
        """
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = NullOutput()
        sys.stderr = NullOutput()

    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        # stop the process if necessary
        self.thread_event.clear()
        self.service_thread.join()

        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    # SvcStop only gets triggered when the user explicitly stops (or restarts)
    # the service.  To shut the service down cleanly when Windows is shutting
    # down, we also need to hook SvcShutdown.
    SvcShutdown = SvcStop

    def SvcDoRun(self):
        import servicemanager

        # log a service started message
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ' (%s)' % self._svc_display_name_))

        while 1:
            self.thread_event = Event()
            self.thread_event.set()
            try:
                if self._svc_thread_class:
                    self.service_thread = self._svc_thread_class(self.thread_event)
                    self.service_thread.start()
                else:
                    servicemanager.LogErrorMsg("No Service thread was provided")
                    self.SvcStop()
            except Exception, info:
                errmsg = getTrace()
                servicemanager.LogErrorMsg(errmsg)
                self.SvcStop()

            rc = win32event.WaitForMultipleObjects((self.hWaitStop,), 0,
                                                   win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                # user sent a stop service request
                self.SvcStop()
                break

        # log a service stopped message
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ' (%s) ' % self._svc_display_name_))



def handle_command_line(srv_class):
    """ Handle command line for installing and removing services

    Yes, this is a simple wrapper around win32serviceutil.HandleCommandLine,
    but I want to present a consistent interface via pywinservice
    """

    win32serviceutil.HandleCommandLine(srv_class)
