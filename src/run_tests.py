import unittest
import pathlib

loader = unittest.TestLoader()
start_dir = pathlib.Path.cwd()
suite = loader.discover(start_dir / "tests")

runner = unittest.TextTestRunner()
runner.run(suite)