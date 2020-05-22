import textdistance
import types

VOWELS = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е']
CONSONANT_MUTATIONS = [ # https://en.wikipedia.org/wiki/Consonant_mutation#Russian
    ['к', 'ч'],
    ['г', 'ж'],
    ['х', 'ш'],
    ['т', 'ч'],
    ['д', 'ж'],
    ['з', 'ж'],
    ['с', 'ш'],
    ['ц', 'ч']
]

PREFIXES = ["у", "от", "о", "раз", "расс", "рас", "со", "с", "при", "проис", "про", "пере", "под", "по", "за", "до", "недо", "на", "вы", "воз", "вз", "в", "из", "ис"]  # Usual verb prefixes
REFLEX1 = 'ся'
REFLEX2 = 'сь'

words = []

scores = []
def noReflexiveForm(verb):
    newForm = verb
    reflexive = (verb.endswith(REFLEX1) or verb.endswith(REFLEX2))

    if reflexive:
        return newForm[:-2]
    return newForm

def noPrefix(verb):
    newForm = verb
    for prefix in PREFIXES:
        if verb.startswith(prefix):
            return newForm[len(prefix):]

    return newForm

def possibleStem(verb):
    return noReflexiveForm(noPrefix(verb))

def compare(word1, word2):
    # Disable this part?
    w1NoReflex = noReflexiveForm(word1)
    w2NoReflex = noReflexiveForm(word2)
    #if (w1NoReflex in w2NoReflex) or (w2NoReflex in w1NoReflex):
    #    return 1

    # if same stem
    w1Stem = possibleStem(word1)
    w2Stem = possibleStem(word2)
    # if (w1Stem in w2Stem) or (w2Stem in w1Stem):
    if (w1Stem == w2Stem):
        return 1

    # With stem?
    cpm1 = noReflexiveForm(word1)
    cpm2 = noReflexiveForm(word2)
    if (len(cpm1) == len(cpm2)):
        diffs = [i for i in range(len(cpm1)) if cpm1[i] != cpm2[i]]
        if len(diffs) == 1:  # Accept only one transformation on a vowel
            i = diffs[0]
            w1Letter = cpm1[i]
            w2Letter = cpm2[i]
            if (w1Letter in VOWELS) and (w2Letter in VOWELS):
                print("MATCHED STEMS WITH VOWELS: " + cpm1 + " AND " + cpm2)
                return 1
            for pair in CONSONANT_MUTATIONS:
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

def setScores():
    # Init scores to 0
    for i in range(lenwords):
        scores.append([])
        for j in range(lenwords):
            scores[i].append(0)

    for i in range(lenwords):
        for j in range(i, lenwords):
            if i == j: # avoid matching one verb with itself
                continue
            score = compare(words[i],words[j])
            scores[i][j] = score
            scores[j][i] = score # set score the other way. => allows i in "for j in range(i, lenwords)"

def prettyPrintScores():
    for i in range(lenwords):
        word = words[i]
        deepScores = "["
        for j in range(lenwords):
            deepScores += words[j] + " " + str(scores[i][j]) + ", "
        print (word + ": " + deepScores[:-1] + "]")

def sortWords(i, disabledWords=[], r=1):
    if i in disabledWords: # skip verb if she was already clustered
        return None, disabledWords

    currentVerb = words[i]
    cluster = []
    for j in range(lenwords):
        if j in disabledWords: # skip verb if she was already clustered
            continue

        score = scores[i][j]
        if score == 1:
            matchedVerb = words[j]
            if r > 0:
                r = r - 1
                disabledWords.append(i) # To not loop on the current word
                e, disabledWords = sortWords(j, disabledWords, r) # recurse to merge clusters into the top one
                if isinstance(e, list):
                    cluster.extend(e)
                else:
                    cluster.append(e)
            else:
                cluster.append(matchedVerb)
            #if j not in disabledWords:
            disabledWords.append(j) # disable matchedVerb
    if len(cluster) != 0:
        #if i not in disabledWords: # TODO: why need this?
        cluster.insert(0, currentVerb)
        return cluster, disabledWords
    else:
        return currentVerb, disabledWords

words = [
    "быть",
    "мочь",
    "говорить",
    "сказать" ,
    "захотеть",
    "рассказывать",
    "рассказать",
    "кататься",
    "катать",
    "скатить",
    "катить",
    "покатиться",
    "катиться",
    "пробегать",
    "пробежать",
    "бегать",
    "бежать"
]
words = []

with open("./intermediate") as f:
    for line in f:
        verb = line.strip()
        words.append(verb)

lenwords = len(words)

setScores()
#prettyPrintScores()

verbsWithClusters = []
nbClusters = 0

for i in range(lenwords):
    e, disabledWords = sortWords(i)
    if e != None:
        verbsWithClusters.append(e)
        if isinstance(e, list):
            nbClusters += 1

print("Number of clusters: " + str(nbClusters))
for e in verbsWithClusters:
    print(str(e))

