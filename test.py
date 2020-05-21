#быть
#мочь/смочь
#говорить/сказать
#хотеть/захотеть
#рассказывать/рассказать

PREFIXES = ["у", "от", "о", "раз", "рас", "расс","со", "с", "при", "про", "проис", "пере", "под", "по", "за", "до", "на", "вы", "воз", "вз", "в", "из"]  # Usual verb prefixes
REFLEX1 = 'ся'
REFLEX2 = 'сь'

words = ["быть", "мочь", "говорить" ,"сказать" ,"захотеть", "рассказывать", "рассказать"]

# Init scores to 0
scores = []
lenwords = len(words)
for i in range(lenwords):
    scores.append([])
    for j in range(lenwords):
        scores[i].append(0)

def compare(word1, word2):
    return 1

def setScores():
    for i in range(lenwords):
        for j in range(lenwords):
            if i == j:
                continue
            score = compare(words[i],words[j])
            scores[i][j] = score

setScores()
print(str(scores))
