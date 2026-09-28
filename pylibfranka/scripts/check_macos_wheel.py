"""Check an installed pylibfranka-macos wheel.

This is the cibuildwheel test command for the pylibfranka-macos wheels. It fails
if pylibfranka loads a library from Homebrew instead of from the wheel, or if
libfranka does not work.
"""

import ctypes
import sys

import pylibfranka

HOMEBREW_PREFIXES = ("/opt/homebrew/", "/usr/local/Cellar/", "/usr/local/opt/")

dyld = ctypes.CDLL(None)
dyld._dyld_image_count.restype = ctypes.c_uint32
dyld._dyld_get_image_name.argtypes = [ctypes.c_uint32]
dyld._dyld_get_image_name.restype = ctypes.c_char_p
images = [dyld._dyld_get_image_name(i).decode() for i in range(dyld._dyld_image_count())]
external = [image for image in images if image.startswith(HOMEBREW_PREFIXES)]
if external:
    sys.exit("pylibfranka loads libraries from outside the wheel:\n  " + "\n  ".join(external))

# Nothing listens on the robot command port locally, so connecting must be refused.
try:
    pylibfranka.Robot("127.0.0.1")
except Exception as e:  # pylibfranka raises its NetworkException as RuntimeError
    if "refused" not in str(e):
        raise
else:
    sys.exit("Connecting to 127.0.0.1 unexpectedly succeeded")

print(f"pylibfranka {pylibfranka.__version__}: loads no Homebrew libraries, libfranka works")
