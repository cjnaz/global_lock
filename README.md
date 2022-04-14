# global_lock.py - Inter-process lock mechanism using posix_ipc

In my applications, I have a few processes all sharing an I2C bus.  global_lock.py provides a lock semaphore 
so that processA can't start accessing the I2C bus while processB is using it.  This lock mechanism is just as effective across threads within a process.  global_lock.py has proven
very robust and efficient.

global_lock.py requires the posix_ipc module from PyPI (https://pypi.org/project/posix-ipc/).

` `  
## global_lock.py interactive/debug features

```
$ ./global_lock.py -h
usage: global_lock.py [-h] [-t GET_TIMEOUT] [-a AUTO_UNGET] [-u UPDATE] LockName {get,unget,state,trace}

Inter-process lock mechanism
Dependency:  posix_ipc module from PyPI (https://pypi.org/project/posix-ipc/)
V0.1 220414
    Demo/testing commands:
        get:    Get/set the lock named LockName.  '-a' specifies a automatic timed unget (only applied if the get was successful).
        unget:  Release LockName.
        state:  Print the current state of LockName.
        trace:  Continuously print the state of LockName.  '-u' specifies update interval (default 1sec).  Ctrl-C to exit.
    

positional arguments:
  LockName              Name of the system-wide lock to access
  {get,unget,state,trace}
                        Command choices

optional arguments:
  -h, --help            show this help message and exit
  -t GET_TIMEOUT, --get-timeout GET_TIMEOUT
                        timeout value for a get call (default 0.5 sec, -1 for no timeout)
  -a AUTO_UNGET, --auto-unget AUTO_UNGET
                        unget the lock after a get (optional delay in (float) sec, for use with get)
  -u UPDATE, --update UPDATE
                        trace update period (default 0.5 sec)
```


` `  
## Using global_lock.py in your code

Import the module and create a named lock handle

    import global_lock
    I2C_LOCK_NAME = "I2C_lock"  

    # Setup / connect to I2C bus lock semaphore
    i2c_lock = global_lock.global_lock(I2C_LOCK_NAME)


Wrap lock-protected resource accesses with get_lock() and unget_lock() calls


    # Get the resource lock
    got_lock = i2c_lock.get_lock(1)   # 1 sec timeout

    if not got_lock:
      logging.warning("Lock request timeout")
    else:
      # do interesting stuff with known/secure access to the I2C bus

      # Release the lock so that other processes & threads can use the resource
      i2c_lock.unget_lock()


` `  
## Setup & usage notes
- Install the posix_ipc module from PyPI (https://pypi.org/project/posix-ipc/)
- Place the global_lock.py module in your project directory.
- Add locking code to your projects that need to run concurrently.
- For debug, run global_lock.py from the CLI to check, trace, and get/unget the lock for testing your code.
- The global_lock.py class presents these interface methods - look at the code and inline doc for more details
  - `__init__()` - Returns a handle to a named lock
  - `get_lock()` - Requests a lock, with an optional timeout.  Returns True if successful.  Note that the default timeout is None, which can result in your code hanging.
  - `unget_lock()` - Releases a lock.  Returns True on success, or False if not currently locked (an extraneous unlock() call - usually benign).
  - `is_locked()` - Returns True if currently locked, else False
  - `lock_value()` - Returns current value of the semaphore count - should be 0 (locked) or 1 (unlocked)
` `  

## Additional usage notes

- global_lock.py uses named locks.  You can have as many active named locks as you need.  Each named lock is independent.
- There is no need to, or capability of disposing of a lock.  It will live forever.  If a prior run of a tool crashed and left the lock set then you will need to manually unlock it using `./global_lock.py <LockName> unget`, or explicitly issue unget() calls in your code startup (if appropriate).
- When the lock is instantiated in your code, you can enable debug logging, which results in lock transactions being printed:

      2c_lock = global_lock.global_lock(I2C_LOCK_NAME, debug=True)

- Lock names in the posix_ipc module have '/' prefixes.  global_lock.py prepends the '/'.  Generally, you can ignore the '/'.
- global_lock.py uses `posix_ipc.Semaphore`, which is a counter mechanism.  `global_lock.get_lock()` decrements the counter to 0, indicating a locked state.  `global_lock.unget_lock()` increments the counter (non-zero is unlocked).
In corner cases, it may be possible to call unget_lock() more than once, such as in a keyboard interrupt handler, which would result in the counter == 2, and the next get_lock() call would decrement the counter to 1, which still indicates unlocked.  And then your applications blow up.
To protect against this failure, the unget_lock() function checks that the current lock state is locked (0) before unlocking (thus incrementing the counter).  If the lock state is not currently locked then the current unlock request is dismissed and a "Extraneous unget, ignored" message is printed.

  - Recommendation:  Your interrupt handler code should issue a possibly extraneous unget() call to cover the case when your code was interrupted while a lock was active.  Usually, no harm done.

` `  
## Known issues and potential enhancements:
- None

` `  
## Version history
- 220414  V0.1  Doc typos and release
- 220111  V0.1  New
