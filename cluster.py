import textdistance
import types

class RussianWordsClusters:
    VOWELS = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е']
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

    PREFIXES = ["у", "от", "о", "раз", "расс", "рас", "со", "с", "при", "проис", "про", "пере", "подъ", "под", "по",
            "за", "до", "недо", "на", "вы", "воз", "вз", "въ", "в", "из", "ис"]  # Usual verb prefixes
    REFLEX1 = 'ся'
    REFLEX2 = 'сь'

    words = []
    lenwords = 0
    scores = []

    def __init__(self, words):
        self.words = words
        self.lenwords = len(words)
        self.setScores()

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

    @staticmethod
    def compare(word1, word2):
        # Disable this part?
        w1NoReflex = RussianWordsClusters.noReflexiveForm(word1)
        w2NoReflex = RussianWordsClusters.noReflexiveForm(word2)
        #if (w1NoReflex in w2NoReflex) or (w2NoReflex in w1NoReflex):
        #    return 1

        # if same stem
        w1Stem = RussianWordsClusters.possibleStem(word1)
        w2Stem = RussianWordsClusters.possibleStem(word2)
        # if (w1Stem in w2Stem) or (w2Stem in w1Stem):
        if (w1Stem == w2Stem):
            return 1

        # Find probable transformation of consonants of vowels
        cpm1 = RussianWordsClusters.noReflexiveForm(word1)
        cpm2 = RussianWordsClusters.noReflexiveForm(word2)
        if (len(cpm1) == len(cpm2)):
            diffs = [i for i in range(len(cpm1)) if cpm1[i] != cpm2[i]]
            if len(diffs) == 1:  # Accept only one transformation on a vowel
                i = diffs[0]
                w1Letter = cpm1[i]
                w2Letter = cpm2[i]
                if (w1Letter in RussianWordsClusters.VOWELS) and (w2Letter in RussianWordsClusters.VOWELS):
                    print("MATCHED STEMS WITH VOWELS: " + cpm1 + " AND " + cpm2)
                    return 1
                for pair in RussianWordsClusters.CONSONANT_MUTATIONS:
                    if (w1Letter in pair) and (w2Letter in pair):
                        print("MATCHED CONSONANTS: " + cpm1 + " AND " + cpm2)
                        return 1

        #dlDistance = textdistance.damerau_levenshtein.normalized_distance(noReflexiveForm(word1), noReflexiveForm(word2))
        #if dlDistance <= 0.15:
        #    return 1
        #dlDistance = textdistance.damerau_levenshtein(noReflexiveForm(word1), noReflexiveForm(word2))
        #if dlDistance <= 2:
        #    return 1

        return 0

    def setScores(self):
        # Init scores to 0
        for i in range(self.lenwords):
            self.scores.append([])
            for j in range(self.lenwords):
                self.scores[i].append(0)

        for i in range(self.lenwords):
            for j in range(i, self.lenwords):
                if i == j: # avoid matching one verb with itself
                    continue
                score = RussianWordsClusters.compare(self.words[i],self.words[j])
                self.scores[i][j] = score
                self.scores[j][i] = score # set score the other way. => allows i in "for j in range(i, lenwords)"

    def prettyPrintScores(self):
        for i in range(self.lenwords):
            word = self.words[i]
            deepScores = "["
            for j in range(self.lenwords):
                deepScores += self.words[j] + " " + str(self.scores[i][j]) + ", "
            print (word + ": " + deepScores[:-1] + "]")

    # Returns words matching with word=words[i] and with CRITERIA
    def sortWords(self, i, disabledWords=[], r=3):
        if i in disabledWords: # skip verb if she was already clustered
            return None, disabledWords

        currentWord = self.words[i]
        cluster = []
        for j in range(self.lenwords):
            if j in disabledWords: # skip verb if she was already clustered
                continue

            score = self.scores[i][j]
            if score == 1:
                matchedWord = self.words[j]
                if r > 0:
                    r = r - 1
                    disabledWords.append(i) # To not loop on the current word
                    e, disabledWords = self.sortWords(j, disabledWords, r) # recurse to merge clusters into the top one
                    if isinstance(e, list):
                        cluster.extend(e)
                    else:
                        cluster.append(e)
                else:
                    cluster.append(matchedWord)
                #if j not in disabledWords:
                disabledWords.append(j) # disable matchedWord
        if len(cluster) != 0:
            #if i not in disabledWords: # TODO: why need this?
            cluster.insert(0, currentWord)
            return cluster, disabledWords
        else:
            return currentWord, disabledWords

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

    def getWordsAndClusters(self):
        wordsWithClusters = [] # Elements in this variable will contain either a String or an Array
        nbClusters = 0

        for i in range(self.lenwords):
            e, disabledWords = self.sortWords(i)
            if e != None:
                if isinstance(e, str):
                    wordsWithClusters.append(e)
                    continue

                assert isinstance(e, list)
                # Order words in cluster
                # Shorter first
                # Then reflexive form after its original form (if reflexive available)
                freqCluster = e
                newCluster = []
                nbClusters += 1

                #print (str(newCluster))
                head = RussianWordsClusters.noPrefixWord(freqCluster)
                newCluster.append(head)

                if not RussianWordsClusters.isReflexive(head):
                    subHead = RussianWordsClusters.reflexiveForm(head)
                    if subHead in freqCluster:
                        newCluster.append(subHead)
                #print (str(newCluster))

                for word in sorted(freqCluster):
                    #print ("newCluster: " + str(newCluster))
                    if RussianWordsClusters.isReflexive(word):
                        headWord = RussianWordsClusters.noReflexiveForm(word)
                        if headWord in freqCluster and headWord not in newCluster:
                            newCluster.append(headWord)
                        if word not in newCluster:
                            newCluster.append(word)
                    else:
                        if word not in newCluster:
                            newCluster.append(word)
                        subWord = RussianWordsClusters.reflexiveForm(word)
                        if subWord in freqCluster and subWord not in newCluster:
                            newCluster.append(subWord)

                wordsWithClusters.append(newCluster)

        return wordsWithClusters

if __name__ == '__main__':
    words = []
    with open("./advanced") as f:
        for line in f:
            word = line.strip()
            words.append(word)

    rwc = RussianWordsClusters(words)
    wordsWithClusters = rwc.getWordsAndClusters()

    for e in wordsWithClusters:
        print(str(e))
