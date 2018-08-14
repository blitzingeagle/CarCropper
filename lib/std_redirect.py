import os
import sys
from contextlib import contextmanager

@contextmanager
def stdout_redirected(to=os.devnull):
    if type(to) == str:
        fd = sys.stdout.fileno()

        def _redirect_stdout(to):
            sys.stdout.close() # + implicit flush()
            os.dup2(to.fileno(), fd) # fd writes to 'to' file
            sys.stdout = os.fdopen(fd, 'w') # Python writes to fd

        with os.fdopen(os.dup(fd), 'w') as old_stdout:
            with open(to, 'w') as file:
                _redirect_stdout(to=file)
            try:
                yield # allow code to be run with the redirected stdout
            finally:
                _redirect_stdout(to=old_stdout) # restore stdout
    elif type(to) == int:
        fd = os.dup(sys.stdout.fileno())
        os.dup2(to, sys.stdout.fileno())
        try:
            yield
        finally:
            os.dup2(fd, sys.stdout.fileno())


@contextmanager
def stderr_redirected(to=os.devnull):
    if type(to) == str:
        fd = sys.stderr.fileno()

        def _redirect_stderr(to):
            sys.stderr.close() # + implicit flush()
            os.dup2(to.fileno(), fd) # fd writes to 'to' file
            sys.stderr = os.fdopen(fd, 'w') # Python writes to fd

        with os.fdopen(os.dup(fd), 'w') as old_stderr:
            with open(to, 'w') as file:
                _redirect_stderr(to=file)
            try:
                yield # allow code to be run with the redirected stdout
            finally:
                _redirect_stderr(to=old_stderr) # restore stdout
    elif type(to) == int:
        fd = os.dup(sys.stderr.fileno())
        os.dup2(to, sys.stderr.fileno())
        try:
            yield
        finally:
            os.dup2(fd, sys.stderr.fileno())


if __name__ == "__main__":
    print("Hello")

    with stdout_redirected():
        print("from Python")
        os.system("echo non-Python applications are also supported")

    print("Bye")

