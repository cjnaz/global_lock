#!/usr/bin/env python3
"""Inter-process lock mechanism
Dependency:  posix_ipc module from PyPI (https://pypi.org/project/posix-ipc/)
"""

__version__ = "V0.1 220414"

#==========================================================
#
#  Chris Nelson, 2022
#
# 220414  V0.1  Doc typos and release
# 220111  V0.0  New
#
# Changes pending
#   
#==========================================================

import posix_ipc

class global_lock():

    def __init__ (self, lockname, debug=False):
        if not lockname.startswith('/'):
            lockname = '/'+lockname         # Lockname is required to start with '/'
        self.lockname = lockname
        self.lock = posix_ipc.Semaphore(self.lockname, flags=posix_ipc.O_CREAT, mode=0o0600, initial_value=1)
        self.debug = debug
        # if self.debug:
        #     print (f"Lock instance created using <{self.lockname}> ({self.lock.value})")

    def get_lock(self, timeout=None):
        """Request a resource lock
        Returns
            True:  Lock successfully acquired, no timeout
            False: Lock request failed, timed out
        """
        try:
            self.lock.acquire(timeout)          # =0 == locked
            if self.debug:
                print (f"<{self.lockname}> lock request successful ({self.lock.value})")
            return True
        except posix_ipc.BusyError:
            if self.debug:
                print (f"<{self.lockname}> lock request timed out  ({self.lock.value})")
            return False

    def unget_lock(self):
        """Release a resource lock
        Returns
            True:  Lock successfully released
            False: Seems like a redundant unget call - unget ignored
        """
        if self.lock.value == 0:
            self.lock.release()                 # >0 == unlocked
            if self.debug:
                print (f"<{self.lockname}> lock released ({self.lock.value})")
            return True
        else:                                   # In case of unbalanced unget calls only release once
            if self.debug:
                print (f"<{self.lockname}> Extraneous unget, ignored ({self.lock.value})")
            return False
            
    def is_locked(self):
        """
        Returns True if currently locked, else False
        """
        _locked = True if self.lock.value == 0 else False
        if self.debug:
            print (f"<{self.lockname}> is currently {'locked' if _locked else 'unlocked'} ({self.lock.value})")
        return _locked

    def lock_value(self):
        """Get lock semaphore count
        Returns current value of the semaphore count - should be 0 (locked) or 1 (unlocked)
        """
        return self.lock.value


if __name__ == '__main__':

    docplus = """
    Demo/testing commands:
        get:    Get/set the lock named LockName.  '-a' specifies a automatic timed unget (only applied if the get was successful).
        unget:  Release LockName.
        state:  Print the current state of LockName.
        trace:  Continuously print the state of LockName.  '-u' specifies update interval (default 1sec).  Ctrl-C to exit.
    """
    import argparse
    from time import sleep

    TESTING_GET_TIMEOUT = 0.5
    TESTING_TRACE_PERIOD = 0.5
    LOCK_DEBUG = True


    parser = argparse.ArgumentParser(description=__doc__ + __version__+docplus, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('LockName',
                        help="Name of the system-wide lock to access")
    parser.add_argument('Cmd', choices=['get', 'unget', 'state', 'trace'],
                        help="Command choices")
    parser.add_argument('-t', '--get-timeout', type=float, default=TESTING_GET_TIMEOUT,
                        help=f"timeout value for a get call (default {TESTING_GET_TIMEOUT} sec, -1 for no timeout)")
    parser.add_argument('-a', '--auto-unget', type=float,
                        help="unget the lock after a get (optional delay in (float) sec, for use with get)")
    parser.add_argument('-u', '--update', type=float, default=TESTING_TRACE_PERIOD,
                        help=f"trace update period (default {TESTING_TRACE_PERIOD} sec)")
    args = parser.parse_args()

    lock = global_lock(args.LockName, LOCK_DEBUG)

    if args.Cmd == "get":
        _timeout = args.get_timeout
        if _timeout == -1:
            _timeout = None
        get_status = lock.get_lock(timeout=_timeout)
        if get_status and args.auto_unget:
                print (f"Release lock after <{args.auto_unget}> sec delay")
                sleep(args.auto_unget)
                lock.unget_lock()

    elif args.Cmd == "unget":
        lock.unget_lock()

    elif args.Cmd == "state":
        lock.is_locked()

    elif args.Cmd == "trace":
        while True:
            lock.is_locked()
            sleep (args.update)

    else:
        print ("How did we get here?")
