#быть
#мочь/смочь
#говорить/сказать
#хотеть/захотеть
#рассказывать/рассказать

PREFIXES = ["у", "от", "о", "раз", "рас", "расс","со", "с", "при", "про", "проис", "пере", "под", "по", "за", "до", "на", "вы", "воз", "вз", "в", "из"]  # Usual verb prefixes
REFLEX1 = 'ся'
REFLEX2 = 'сь'

words = ["быть", "мочь", "говорить", "казать" ,"сказать" ,"захотеть", "рассказывать", "рассказать"]

# Init scores to 0
scores = []
lenwords = len(words)
for i in range(lenwords):
    scores.append([])
    for j in range(lenwords):
        scores[i].append(0)

def compare(word1, word2):
    if (word1 in word2) or (word2 in word1):
        return 1
    else:
        return 0

def setScores():
    for i in range(lenwords):
        for j in range(lenwords):
            if i == j: # avoid matching one verb with itself
                continue
            score = compare(words[i],words[j])
            scores[i][j] = score

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
        if score == 1:
            matchedVerb = words[j]
            cluster.append(matchedVerb)
            disabledVerbs.append(j) # disable matchedVerb
    if len(cluster) != 0:
        cluster.insert(0, currentVerb)
        verbsWithClusters.append(cluster)
    else:
        verbsWithClusters.append(currentVerb)

print(str(verbsWithClusters))
