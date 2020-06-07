import os
from pathlib import Path
import sys
import unittest
import glob
import cluster

PATH_TESTS = "./tests/*[!-oracle]"

def getWords(input):
    words = []
    f = Path(input)
    assert f.exists()

    with open(input) as f:
        for line in f:
            verb = line.strip()
            words.append(verb)
    return words

def assertArraysEqual(arr1, arr2):
    lenarr1 = len(arr1)
    lenarr2 = len(arr2)
    assert lenarr1 == len(arr2), 'assert false between {0} and {1}'.format(str(lenarr1), str(lenarr2))

    for i in range(lenarr1):
        e1 = arr1[i]
        e2 = arr2[i]
        assert e1 == e2, "error"

def test_cluster_in_out(input, output):
    def test():
        words_in = getWords(input)
        words_out = cluster.flatten(cluster.orderWithClusters(words_in))
        assertArraysEqual(words_in, words_out)
    return test

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = glob.glob(PATH_TESTS)

    for case in test_cases:
        input = case
        output = input + "-oracle"
        suite.addTest(unittest.FunctionTestCase(
                test_cluster_in_out(input, output), description=input))

    unittest.TextTestRunner().run(suite)
