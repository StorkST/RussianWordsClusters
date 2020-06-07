from cluster import RussianWordsClusters as rwc

russianClusters = rwc(['абвг', 'быть', 'абвгде', 'бить'])
words_out = rwc.flatten(russianClusters.getWordsAndClusters())

print(str(words_out))
