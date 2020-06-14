from cluster import RussianWordsClusters as rwc
from cluster import Link as link

in_words = [
"абвг",
"абвгде",
"делаться",
"абвгдеёж",
"делать",
"абвгдеёжзи",
"сделать",
"абвгдеёжзийк",
"сделаться",
"выделаться",
"абвгдеёжзийклм",
"выделать",
"абвгдеёжзийклмнопрстуф"
]
#['абвг', 'быть', 'абвгде', 'бить']

russianClusters = rwc(in_words)
words_out = rwc.flatten(russianClusters.getWordsAndClusters([link.STEM]))

print(str(words_out))
