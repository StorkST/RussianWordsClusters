#быть
#мочь/смочь
#говорить/сказать
#хотеть/захотеть
#рассказывать/рассказать

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
        return 0.9

    return 0

def setScores():
    for i in range(lenwords):
        for j in range(i, lenwords):
            if i == j: # avoid matching one verb with itself
                continue
            score = compare(words[i],words[j])
            scores[i][j] = score
            scores[j][i] = score # set score the other way. => allows i in "for j in range(i, lenwords)"

setScores()
print(str(scores))

verbsWithClusters = []
disabledVerbs = []
for i in range(lenwords):
    if i in disabledVerbs: # skip verb if he was already clustered
        continue

    currentVerb = words[i]
    cluster = []
    for j in range(lenwords):
        score = scores[i][j]
        if score >= 0.9:
            matchedVerb = words[j]
            cluster.append(matchedVerb)
            disabledVerbs.append(j) # disable matchedVerb
    if len(cluster) != 0:
        cluster.insert(0, currentVerb)
        verbsWithClusters.append(cluster)
    else:
        verbsWithClusters.append(currentVerb)

for e in verbsWithClusters:
    print(str(e))
