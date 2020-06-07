import os
from pathlib import Path
import sys
import unittest
import glob
from cluster import RussianWordsClusters as rwc

#PATH_TESTS = './tests/!(*oracle)' # Somehow it doesn't work
PATH_TESTS = "./tests/*"

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
        assert e1 == e2, 'assert false between {0} and {1}'.format(str(e1), str(e2))

def test_cluster_in_out(input, output):
    def test():
        words_in = getWords(input)
        russianClusters = rwc(words_in)

        words_out = rwc.flatten(russianClusters.getWordsAndClusters())

        assertArraysEqual(words_in, words_out)
    return test

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = glob.glob(PATH_TESTS)
    test_cases.sort()

    nbDel = 0
    for i in range(len(test_cases)): # Hack because can't make glob work as wanted
        if i % 2 == 1:
            del test_cases[i-nbDel]
            nbDel += 1
    print (str(test_cases))

    for case in test_cases:
        input = case
        output = input + "-oracle"
        suite.addTest(unittest.FunctionTestCase(
                test_cluster_in_out(input, output), description=input))

    unittest.TextTestRunner().run(suite)
