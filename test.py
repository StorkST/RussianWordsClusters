import os
from pathlib import Path
import sys
import unittest
import glob
import cluster

#import importlib
#moduleName = input('cluster')
#importlib.import_module(moduleName)

PATH_TESTS = "./tests/*[!-oracle]"

def test_cluster_in_out(input, output):
    def test():
        a = Path(input)
        b = Path(output)
        assert a.exists()
        assert b.exists()
    return test

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = glob.glob(PATH_TESTS)
    test_cases.append("aa")

    for case in test_cases:
        input = case
        output = input + "-oracle"
        suite.addTest(unittest.FunctionTestCase(
                test_cluster_in_out(input, output), description=input))

    unittest.TextTestRunner().run(suite)
