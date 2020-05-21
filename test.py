import textdistance

PREFIXES = ["у", "от", "о", "раз", "расс", "рас", "со", "с", "при", "проис", "про", "пере", "под", "по", "за", "до", "недо", "на", "вы", "воз", "вз", "в", "из", "ис"]  # Usual verb prefixes
REFLEX1 = 'ся'
REFLEX2 = 'сь'

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

# Init scores to 0
scores = []
lenwords = len(words)
for i in range(lenwords):
    scores.append([])
    for j in range(lenwords):
        scores[i].append(0)

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
    if (word1 in word2) or (word2 in word1):
        return 1

    # if same stem
    w1Stem = possibleStem(word1)
    w2Stem = possibleStem(word2)
    if (w1Stem in w2Stem) or (w2Stem in w1Stem):
        return 1

    #dlDistance = textdistance.damerau_levenshtein.normalized_distance("a", "aa")
    dlDistance = textdistance.damerau_levenshtein(noReflexiveForm(word1), noReflexiveForm(word2))
    if dlDistance <= 1:
        return 1

    return 0

def setScores():
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

setScores()
prettyPrintScores()

verbsWithClusters = []
disabledVerbs = []

def sortWords(i):
    if i in disabledVerbs: # skip verb if she was already clustered
        return None

    currentVerb = words[i]
    cluster = []
    for j in range(lenwords):
        if j in disabledVerbs: # skip verb if she was already clustered
            continue
        score = scores[i][j]
        if score == 1:
            matchedVerb = words[j]
            cluster.append(matchedVerb)
            disabledVerbs.append(j) # disable matchedVerb
    if len(cluster) != 0:
        cluster.insert(0, currentVerb)
        return cluster
    else:
        return currentVerb

for i in range(lenwords):
    e = sortWords(i)
    if e != None:
        verbsWithClusters.append(e)


for e in verbsWithClusters:
    print(str(e))
