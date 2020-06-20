import textdistance
import types
from enum import Flag, auto

class Link(Flag):
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

    PREFIXES = ["у", "от", "о", "раз", "расс", "рас", "со", "с", "при", "проис", "про", "пре", "пере", "подъ", "под", "по",
            "за", "до", "недо", "на", "вы", "воз", "вз", "въ", "в", "из", "ис"]  # Usual verb prefixes
    REFLEX1 = 'ся'
    REFLEX2 = 'сь'

    words = []
    lenwords = 0
    relations = []
    redirected = []

    def __init__(self, newWords):
        self.words = []
        self.lenwords = 0
        self.relations = []

        self.words = newWords
        self.lenwords = len(newWords)
        self.setRelations()

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
    @staticmethod
    def compare(word1, word2):
        # if same stem
        w1Stem = RussianWordsClusters.possibleStem(word1)
        w2Stem = RussianWordsClusters.possibleStem(word2)
        if (w1Stem == w2Stem):
            return Link.STEM

        # Find probable transformation of consonants or vowels
        cpm1 = RussianWordsClusters.noReflexiveForm(word1)
        cpm2 = RussianWordsClusters.noReflexiveForm(word2)
        if (len(cpm1) == len(cpm2)):
            diffs = [i for i in range(len(cpm1)) if cpm1[i] != cpm2[i]]
            if len(diffs) == 1:  # Accept only one transformation
                i = diffs[0]
                w1Letter = cpm1[i]
                w2Letter = cpm2[i]
                for pair in RussianWordsClusters.VOWEL_MUTATIONS:
                    if (w1Letter in pair) and (w2Letter in pair):
                        print("VOWEL TRANS match: " + cpm1 + " and " + cpm2)
                        return Link.VOWEL_TRANS

                for pair in RussianWordsClusters.CONSONANT_MUTATIONS:
                    if (w1Letter in pair) and (w2Letter in pair):
                        print("CONSONANT TRANS match: " + cpm1 + " and " + cpm2)
                        return Link.CONSONANT_TRANS

        return Link.NONE

    def setRelations(self):
        # Init relations with 0
        newRelations = [[Link.NONE for i in range(self.lenwords)] for j in range(self.lenwords)]
        self.relations = newRelations

        for i in range(self.lenwords):
            for j in range(i, self.lenwords):
                if i == j: # avoid matching one verb with itself
                    continue
                link = RussianWordsClusters.compare(self.words[i],self.words[j])
                self.relations[i][j] = link
                self.relations[j][i] = link # set link the other way. => allows i in "for j in range(i, lenwords)"

    def prettyPrintRelations(self):
        for i in range(self.lenwords):
            word = self.words[i]
            deepRelations = "["
            for j in range(self.lenwords):
                deepRelations += self.words[j] + " " + str(self.relations[i][j]) + ", "
            print (word + ": " + deepRelations[:-1] + "]")

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
    def flatten(wordsWithClusters):
        flat = []
        for e in wordsWithClusters:
            if isinstance(e, str):
                flat.append(e)
            else: # isinstance(e, list)
                flat.extend(e)

        return flat

    # Returns words that match (criteria) with word of value words[i]
    # Returns word of value words[i] if no match was found
    def groupBy(self, criteria, wordsWithClusters, disabledWords=[]):#, r=3):
        for i in range(self.lenwords):
            if i in disabledWords: # skip verb if she was already clustered
                continue
            currentWord = self.words[i]

            for j in range(self.lenwords):
                if j in disabledWords: # skip verb if she was already clustered
                    continue

                link = self.relations[i][j]
                if link & Link.NONE:
                    continue
                if link & criteria:
                    matchedWords = wordsWithClusters[j]
                    #if r > 0:
                    #    r = r - 1
                    #    disabledWords.append(i) # To not loop on the current word
                    #    wordsWithClusters, disabledWords = self.groupBy(criteria, wordsWithClusters, disabledWords, r) # recurse to merge deep clusters into the top one

                    print("extend " + str(i) + " with " + str(j))
                    print("disable " + str(j))
                    wordsWithClusters[i].extend(matchedWords)
                    wordsWithClusters[j] = wordsWithClusters[i]
                    wordsWithClusters[i] = wordsWithClusters[j]

                    self.redirected.append(j)
                    disabledWords.append(j) # disable matchedWord

        return wordsWithClusters, disabledWords

    def getWordsAndClusters(self, clusteringPriorities, mergeClusters):
        #self.prettyPrintRelations()
        wordsWithClusters = []
        for word in self.words:
            wordsWithClusters.append([word])
        disabledWords = []
        self.redirected = []

        for criteria in clusteringPriorities:
            if mergeClusters:
                disabledWords = []
            wordsWithClusters, disabledWords = self.groupBy(criteria, wordsWithClusters, disabledWords)#, 3)
            print(str(wordsWithClusters))
            print(str(disabledWords))

        # Remove redirections
        r = []
        print(str(self.redirected))
        for i in range(self.lenwords):
            if i not in self.redirected:
                r.extend(wordsWithClusters[i])
        return r

if __name__ == '__main__':
    clusteringPriorities = [Link.STEM, Link.TRANS]
    mergeClusters = False
    words = []

    with open("./advanced") as f:
        for line in f:
            word = line.strip()
            words.append(word)

    rwc = RussianWordsClusters(words)
    wordsWithClusters = rwc.getWordsAndClusters(clusteringPriorities, mergeClusters)

    for e in wordsWithClusters:
        print(str(e))
