import os

# Hack to work around Python 3.8+ secure dll loading:
# see https://docs.python.org/3/whatsnew/3.8.html#bpo-36085-whatsnew
if hasattr(os, "add_dll_directory"):
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if os.path.isdir(directory):
            os.add_dll_directory(directory)

from setuptools import setup, Extension

script_dir = os.path.dirname(os.path.realpath(__file__))

# Make sure the script is run in the same directory as the source file.
# Paths for various build outputs(.obj, .lib, etc.) are based on the source
# file path. Running this script in the source directory ensures that these
# are as short as possible.
if not os.path.samefile(script_dir, os.getcwd()):
    print("Setup must be run in the same directory as test_module.c")
    exit(1)

setup(
    name="test_package",
    version="1.0",
    ext_modules=[
        Extension("spam", ["test_module.c"]),
    ],
)
