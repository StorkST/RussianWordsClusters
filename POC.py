import os
from pathlib import Path
import sys
import unittest
import glob
from cluster import RussianWordsClusters as rwc

PATH_TESTS = "./tests/*"

def getWords(inp):
    words = []
    f = Path(inp)
    assert f.exists()

    with open(inp) as f:
        for line in f:
            verb = line.strip()
            words.append(verb)
    return words

def assertArraysEqual(arr1, arr2):
    lenarr1 = len(arr1)
    lenarr2 = len(arr2)
    assert lenarr1 == len(arr2), 'assert false between {0} and {1}:\n  size {0}: {2}\n  size {1}: {3}'.format(str(lenarr1), str(lenarr2), str(arr1), str(arr2))

    for i in range(lenarr1):
        e1 = arr1[i]
        e2 = arr2[i]
        assert e1 == e2, 'assert false between {0} and {1}'.format(str(e1), str(e2))

def test_cluster_in_out(inp, outp):
    words_in = getWords(inp)
    oracle = getWords(outp)
    russianClusters = rwc(words_in)
    words_out = rwc.flatten(russianClusters.getWordsAndClusters())
    print(str(words_out))

    assertArraysEqual(words_out, oracle)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = glob.glob(PATH_TESTS)
    test_cases.sort()

    nbDel = 0
    for i in range(len(test_cases)): # Hack because can't make glob work as wanted
        if i % 2 == 1:
            del test_cases[i-nbDel]
            nbDel += 1

    j = 1
    for case in test_cases[j:]:
        print("iteration #" + str(j))
        inp = case
        outp = inp + "-oracle"
        test_cluster_in_out(inp, outp)
        j += 1
