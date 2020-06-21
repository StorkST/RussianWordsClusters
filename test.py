import os
from pathlib import Path
import sys
import unittest
import glob
from cluster import RussianWordsClusters as rwc
from cluster import Link

#PATH_TESTS = './tests/!(*oracle)' # Somehow it doesn't work
PATH_MERGE_TESTS = "./tests/merge/*"
PATH_NOTMERGE_TESTS = "./tests/not-merge/*"

def getWords(input):
    words = []
    f = Path(input)
    assert f.exists()

    with open(input) as f:
        for line in f:
            verb = line.strip()
            words.append(verb)
    return words

def assertArraysEqual(arr, oracle, words_in):
    lenarr = len(arr)
    lenoracle = len(oracle)
    assert lenarr == len(oracle), 'assert false between {0} and {1}:\n  size {0}: {2}\n  size {1}: {3}'.format(str(lenarr), str(lenoracle), str(arr), str(oracle))

    maxSize = len(max(arr, key=len))
    pr = ""
    assertFalse = False
    for i in range(lenarr):
        e1 = arr[i]
        e2 = oracle[i]
        pr += "\n" + words_in[i].ljust(maxSize) + " | " + e2.ljust(maxSize) + " | " + e1.ljust(maxSize)
        if e1 != e2:
            assertFalse = True
            pr += " << Was expecting ORACLE == ACTUAL"

    assert(not assertFalse), "\n" + "BEFORE".ljust(maxSize) + " | " + "ORACLE".ljust(maxSize) + " | " + "ACTUAL".ljust(maxSize) + pr

def test_cluster_in_out(input, output, merge):
    def test():
        words_in = getWords(input)
        oracle = getWords(output)
        russianClusters = rwc(words_in)

        words_out = rwc.flatten(russianClusters.getWordsAndClusters([Link.STEM, Link.TRANS], merge))
        assertArraysEqual(words_out, oracle, words_in)
    return test

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = []
    test_merge_cases = glob.glob(PATH_MERGE_TESTS)
    test_merge_cases.sort()

    test_notmerge_cases = glob.glob(PATH_NOTMERGE_TESTS)
    test_notmerge_cases.sort()

    # MERGE TESTS
    nbDel = 0
    for i in range(len(test_merge_cases)): # Hack because can't make glob work as wanted
        if i % 2 == 1:
            del test_merge_cases[i-nbDel]
            nbDel += 1

    for case in test_merge_cases:
        input = case
        output = input + "-oracle"
        suite.addTest(unittest.FunctionTestCase(
                test_cluster_in_out(input, output, True), description=input))

    # NOT MERGE TESTS
    nbDel = 0
    for i in range(len(test_notmerge_cases)): # Hack because can't make glob work as wanted
        if i % 2 == 1:
            del test_notmerge_cases[i-nbDel]
            nbDel += 1

    for case in test_notmerge_cases:
        input = case
        output = input + "-oracle"
        suite.addTest(unittest.FunctionTestCase(
                test_cluster_in_out(input, output, False), description=input))

    unittest.TextTestRunner().run(suite)
