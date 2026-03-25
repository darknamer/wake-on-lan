from __future__ import print_function

import os
import sys
import unittest


def main():
    try:
        import coverage
    except ImportError:
        print("Coverage not installed. Install it with `pip install coverage`.")
        return 1

    # Keep coverage config local to this repository.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    tests_dir = os.path.join(repo_root, "tests")
    config_file = os.path.join(tests_dir, "coveragerc.ini")

    if os.path.exists(config_file):
        cov = coverage.Coverage(config_file=config_file)
    else:
        cov = coverage.Coverage()

    cov.start()

    loader = unittest.defaultTestLoader
    # Use positional args for Python 2.7 compatibility.
    suite = loader.discover(tests_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()

    # Print terminal summary.
    cov.report()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

