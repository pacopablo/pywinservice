=================
pywinservice
=================

Scaffolding for running Python programs as Windows NT Services

Usage
--------

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


Notes
---------