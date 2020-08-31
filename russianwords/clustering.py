from pathlib import Path
import argparse
import types
import re
import sys
import copy
from enum import Flag, auto

class Relation(Flag):
    NONE = auto()
    STEM = auto()
    VOWEL_TRANS = auto()
    CONSONANT_TRANS = auto()
    TRANS = VOWEL_TRANS | CONSONANT_TRANS
    ALL = STEM | TRANS

class RussianWordsClusters:

    VOWELS = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е']
    # TODO: manage consonant / vowel transformations with harsh consonants and ы -> и
    VOWEL_MUTATIONS = [ # https://en.wikipedia.org/wiki/Vowel_reduction_in_Russian
        ['а', 'е', 'и', 'о'],
        ['ы', 'о'],
        ['и', 'ё'],
        ['о', 'ё'],
        ['и', 'я'],
        ['а', 'я'],
        ['и', 'ю'],
        ['у', 'ю']
    ]
    CONSONANT_MUTATIONS = [ # https://en.wikipedia.org/wiki/Consonant_mutation#Russian
        ['к', 'ч'],
        ['г', 'ж'],
        ['г', 'ч'],
        ['х', 'ш'],
        ['т', 'ч'],
        ['д', 'ж'],
        ['з', 'ж'],
        ['с', 'ш'],
        ['ц', 'ч']
    ]

    PREFIXES = [ # https://en.wiktionary.org/wiki/Category:Russian_verbal_prefixes and more (when ъ)
            "присо", "предо",
            "без",
            "вы", "взо", "вз", "въ", "воз", "вос", "во", "в",
            "до",
            "за",
            "изо", "из", "ис",
            "недо", "надо", "над", "на", "низо", "низ", "нис",
            "ото", "от", "обо", "объ", "об", "о",
            "при", "проис", "про", "пред", "пре", "пере", "пона", "подъ", "подо", "под", "по",
            "разъ", "разо", "раз", "рас",
            "со", "съ", "с",
            "у"
    ]  # Usual verb prefixes
    REFLEX1 = 'ся'
    REFLEX2 = 'сь'

    words = []
    lenwords = 0
    relations = []

    def __init__(self, newWords):
        self.relations = []

        self.words = newWords
        self.lenwords = len(newWords)

    @staticmethod
    def endsWithVowel(word):
        for v in RussianWordsClusters.VOWELS:
            if word.endswith(v):
                return True
        return False

    @staticmethod
    def isReflexive(word):
        return (word.endswith(RussianWordsClusters.REFLEX1) or word.endswith(RussianWordsClusters.REFLEX2))

    @staticmethod
    def reflexiveForm(word):
        newForm = word
        reflexive = RussianWordsClusters.isReflexive(word)

        if not reflexive:
            if RussianWordsClusters.endsWithVowel(word):
               newForm += RussianWordsClusters.REFLEX2
            else:
               newForm += RussianWordsClusters.REFLEX1
        return newForm

    @staticmethod
    def noReflexiveForm(word):
        newForm = word
        reflexive = (word.endswith(RussianWordsClusters.REFLEX1) or word.endswith(RussianWordsClusters.REFLEX2))

        if reflexive:
            return newForm[:-2]
        return newForm

    @staticmethod
    def noPrefix(word):
        newForm = word
        for prefix in RussianWordsClusters.PREFIXES:
            if word.startswith(prefix):
                return newForm[len(prefix):]

        return newForm

    @staticmethod
    def possibleStem(word):
        return RussianWordsClusters.noReflexiveForm(RussianWordsClusters.noPrefix(word))

    # Return 1 when:
    # * stem == stem (stem being the part without one of the PREFIXES and without reflexive form
    # * word1 != word2 by one edit of a vowel of consonant as defined with the tranformation pairs
    def compare(self, word1, word2, criterias=[]):
        blacklist = ["*"] # In case special characters are used to represent words

        if (word1 in blacklist) or (word2 in blacklist):
            return Relation.NONE

        # Words have the same stem if
        #   1. they are equals without the reflexive form and without the prefix
        #   this is useful for comparing verbs where both verbs have prefixes. However we cannot be sure we remove prefixes or the first letters of the word (TODO: check that what is removed is not the next letters of the stem. Ex: видеть. Only solution I see is using pymorphy)
        #    , but it is not sufficient for следить as it assumes that следить has the prefix с- when it's part of its stem
        w1Stem = RussianWordsClusters.possibleStem(word1)
        w2Stem = RussianWordsClusters.possibleStem(word2)
        if (w1Stem == w2Stem):
            return Relation.STEM

        # special case. Example: расспрашивать/расспросить - опрашивать/опросить
        if word1.startswith("расс") or word2.startswith("расс"):
            paccWord = ""
            otherWord = ""
            if word1.startswith("расс"):
                paccWord = word1
                otherWord = word2
            else:
                paccWord = word2
                otherWord = word1
            exPacc = RussianWordsClusters.noReflexiveForm(paccWord)
            exPacc = paccWord[len("расс"):]
            otherWord = RussianWordsClusters.possibleStem(otherWord)
            if (exPacc == otherWord):
                return Relation.STEM

        #   2. The result of the "longer non reflexive word" minus the "shorter non reflexive word" may give a known verb Prefix
        #    , if that's the case then we can assume the two verbs have the same stem
        cmp1 = RussianWordsClusters.noReflexiveForm(word1)
        cmp2 = RussianWordsClusters.noReflexiveForm(word2)
        shorterWord = ""
        longerWord = ""
        if (cmp1 == cmp2):
            return Relation.STEM

        if (len(cmp1) < len(cmp2)):
            shorterWord = cmp1
            longerWord = cmp2
        else:
            shorterWord = cmp2
            longerWord = cmp1

        if longerWord.endswith(shorterWord):
            possiblePrefix = re.sub(shorterWord + '$', '', longerWord)
            if possiblePrefix in RussianWordsClusters.PREFIXES:
                return Relation.STEM

        # Find probable transformation of consonants or vowels
        if (len(cmp1) == len(cmp2)):
            diffs = [i for i in range(len(cmp1)) if cmp1[i] != cmp2[i]]
            if len(diffs) == 1:  # Accept only one transformation
                i = diffs[0]
                w1Letter = cmp1[i]
                w2Letter = cmp2[i]
                for pair in RussianWordsClusters.VOWEL_MUTATIONS:
                    if (w1Letter in pair) and (w2Letter in pair):
                        #print("VOWEL TRANS match: " + cmp1 + " and " + cmp2)
                        return Relation.VOWEL_TRANS

                for pair in RussianWordsClusters.CONSONANT_MUTATIONS:
                    if (w1Letter in pair) and (w2Letter in pair):
                        #print("CONSONANT TRANS match: " + cmp1 + " and " + cmp2)
                        return Relation.CONSONANT_TRANS

        return Relation.NONE

    def setRelations(self, criterias):
        # Init relations with 0
        newRelations = [[Relation.NONE for i in range(self.lenwords)] for j in range(self.lenwords)]
        self.relations = newRelations

        for i in range(self.lenwords):
            for j in range(i, self.lenwords):
                if i == j: # avoid matching one verb with itself
                    continue
                link = self.compare(self.words[i],self.words[j], criterias)
                self.relations[i][j] = link
                self.relations[j][i] = link # set link the other way. => allows i in "for j in range(i, lenwords)"

    def prettyPrintRelations(self):
        maxSize = len(max(self.words, key=len))
        for i in range(self.lenwords):
            word = self.words[i]
            deepRelations = "["
            for j in range(self.lenwords):
                deepRelations += self.words[j] + " " + str(self.relations[i][j]) + ", "
            print(str(i) + "." + word.ljust(maxSize) + ": " + str(deepRelations) + "]")

    def cleanWAC(self, wac, redirections=[]):
        r = []
        flatA = []
        for i in range(self.lenwords):
            if (i not in redirections) and (wac[i] != {}): # can be empty if redirections were cleaned
                value = wac[i]["value"]
                flatA.extend(value)
        for n in flatA:
            r.append(self.words[n])
        return r

    # Pretty print Words And Clusters and Remove redirections
    def ppWAC(self, wac, redirections=[]):
        print(str(self.cleanWAC(wac, redirections)))

    def pWAC(self, wac, redirections=[]):
        r = []
        for i in range(self.lenwords):
            if i in redirections:
                r.append({})
            else:
                r.append(wac[i])
        print(str(r))

    # Returns the first word without a prefix
    # If no word can be found without a prefix, returns the first word from the list
    @staticmethod
    def noPrefixWord(array):
        assert (len(array) >= 1)

        for word in array:
            hasPrefix = False
            for prefix in RussianWordsClusters.PREFIXES:
                if word.startswith(prefix):
                    hasPrefix = hasPrefix or True
            if not hasPrefix:
                return word

        return array[0]

    @staticmethod
    def flatten(wac):
        flat = []
        for e in wac:
            if isinstance(e, str):
                flat.append(e)
            else: # isinstance(e, list)
                flat.extend(e)

        return flat

    # Returns words that match with word of value words[i]
    # Returns word of value words[i] if no match was found
    def groupOn(self, i, criterias, wac, disabledWords=[], redirections=[]):
        nbCriterias = len(criterias)
        #if i in disabledWords: # skip verb if she was already clustered
        #    return wac, disabledWords, redirections

        currentWord = self.words[i]
        currentCriteria = criterias[0]

        newWords = [] # Contains words matching with currentWord
        for j in range(self.lenwords):
            if j in disabledWords: # skip verb if she was already clustered
                continue

            link = self.relations[i][j]
            if link & Relation.NONE:
                continue
            if link & currentCriteria:
                wac[i]["type"] = currentCriteria
                wac[i]["value"].extend(wac[j]["value"])
                wac[j] = wac[i]
                newWords.append(j)
                redirections.append(j)
                disabledWords.append(j) # disable a verb once its clustered
                if i not in disabledWords:
                    disabledWords.append(i)

        # Append words with criterias of lower priority
        for w in newWords:
            wac, disabledWords, redirections =\
                self.groupOn(w, [currentCriteria], wac, disabledWords, redirections)

        return wac, disabledWords, redirections

    # Returns the position of a word of reference i in the array of subsets WAC
    # Returne None if not found
    def getNewSubsetId(self, k, wac):
        for i in range(len(wac)):
            subset = wac[i]
            if subset == {}:
                continue
            if k in subset["value"]:
                return i

        return None

    def getWordsAndClusters(self, criterias, mergeCriterias):
        self.setRelations(criterias)
        #self.prettyPrintRelations()

        wac = []
        for n in range(self.lenwords):
            e = {"type": Relation.NONE, "value": [n]}
            wac.append(e)
        disabledWords = []
        redirections = []

        # Build groups using recursion, e.i. if a-b and b-c then we build the group a-b-c
        # Option mergeCriterias merges groups of different criterias as long as there is a link between words
        # e.i. if a-b and b+c then we build the group a-b+c

        # a-b-c
        builtClusters = [] # clusters formed after each Criteria
        for criteria in criterias:
            for i in range(self.lenwords):
                if i in builtClusters: # We avoid mixing a cluster built from one Criteria with a cluster of another Criteria
                    continue
                wac, disabledWords, redirections =\
                    self.groupOn(i, [criteria], wac, disabledWords, redirections)
            builtClusters = disabledWords

        if mergeCriterias:
            # 1. Clean redirections
            newWAC = []
            for i in range(self.lenwords):
                if i in redirections:
                    newWAC.append({})
                else:
                    newWAC.append(wac[i])
            wac = newWAC

            # 2. set cluster relations
            # Pour chaque sous-ensemble du groupe on récupère sa relation qu'on affecte à
            # un nouveau tableau des relations en 2D prenant :
            #   * pour indice i = l'indice actuel du tableau wac
            #   * pour indice j = l'indice actuel du tableau wac
            #   * pour valeur = la relation la plus forte (selon les critères définis) entre les éléments de 2 sous-ensembles
            newClusterRelations = [[Relation.NONE for i in range(self.lenwords)] for j in range(self.lenwords)]
            wordsRelations = copy.deepcopy(self.relations)
            disabledClusters = []
            copywac = copy.copy(wac) # would be better to use but it is needed to refresh subsets in the following code

            for criteria in criterias[1:]: # warn: not tested with more than 2 criterias, could merge too many clusters and not have the expected behaviour
                for i, e in enumerate(wac): # Pour chaque sous-ensemble
                    if e == {}:
                        continue
                    else:
                        assert i == e["value"][0] # assert que le premier element d'un sous-ensemble est égal à la position du sous-ensemble dans le WAC

                    t = e["type"] # type de cluster
                    for numWord in e["value"]: # Pour chaque element d'un sous-ensemble, récupérer les liens du tableau original des relations
                        if numWord in disabledClusters:
                            continue
                        for k in range(self.lenwords): # Looking for a k matching with numWord. If it matches we create a clusterRelation
                            link = wordsRelations[numWord][k]
                            if k in disabledClusters:
                                continue

                            if k in e["value"]: # Skip. We are not interested by relations with words already in the subset
                                continue

                            if link & Relation.NONE:
                                continue

                            if link & criteria: # TODO: need improvements to manage 2+ criterias => would have to prioritize criterias relations before assignement in newClusterRelations
                                subsetId = self.getNewSubsetId(k, wac)
                                assert subsetId >= 0 and subsetId < len(wac)
                                newClusterRelations[i][subsetId] = criteria
                                wac[i]["value"].extend(wac[subsetId]["value"])
                                wac[subsetId] = {}
                                disabledClusters.append(k)

        return self.cleanWAC(wac, redirections)

class RussianWordsPairsClusters(RussianWordsClusters):

    # Return 1 when one word in a pair matches at least one word in the other pair
    # TODO: optimise by splitting words at the init of the object instead of splitting them N times
    def compare(self, wordpair1, wordpair2, criterias):
        wp1 = wordpair1.split("/")
        wp11 = ""
        wp12 = ""
        if len(wp1) == 1:
            wp11 = wp1[0]
            wp12 = wp1[0]
        else:
            assert len(wp1) == 2
            wp11 = wp1[0]
            wp12 = wp1[1]

        wp2 = wordpair2.split("/")
        wp21 = ""
        wp22 = ""
        if len(wp2) == 1:
            wp21 = wp2[0]
            wp22 = wp2[0]
        else:
            assert len(wp2) == 2
            wp21 = wp2[0]
            wp22 = wp2[1]

        cmps = []
        cmps.append(super().compare(wp11,wp21))
        cmps.append(super().compare(wp11,wp22))
        cmps.append(super().compare(wp12,wp21))
        cmps.append(super().compare(wp12,wp22))

        # choose between different Relation knowing the criteria of priority for clustering
        for criteria in criterias:
            for cmp in cmps:
                if criteria & cmp:
                    return criteria

        return Relation.NONE

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clustering of russian words')
    parser.add_argument('-in', '--input', dest='input', required=True, help='')
    parser.add_argument('-p', '--are-pairs', dest='arepairs', required=False, action="store_true", help='')
    parser.add_argument('-c', '--criterias', dest='criterias', required=True, nargs='+', help='')
    parser.add_argument('-m', '--merge', dest='merge', required=False, action="store_true", help='')
    args = parser.parse_args()

    mergeCriterias = args.merge

    input = args.input
    f = Path(input)
    assert f.exists()

    words = []
    with open(input) as f:
        for line in f:
            word = line.strip()
            words.append(word)

    clusteringPriorities = []
    for criteria in args.criterias:
        val = getattr(Relation, criteria, None)
        if val == None:
            print("Criterias argument - Unexpected Relation attribute: " + criteria)
            sys.exit(1)
        clusteringPriorities.append(val)

    rwc = None
    if args.arepairs:
        rwc = RussianWordsPairsClusters(words)
    else:
        rwc = RussianWordsClusters(words)

    wac = rwc.getWordsAndClusters(clusteringPriorities, mergeCriterias)

    for e in wac:
        print(str(e))
