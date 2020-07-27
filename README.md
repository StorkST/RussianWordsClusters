# Russian Words Clusters

Russian Words Clusters offers a way to cluster russian words by criterias (by a common stem, by the closeness of vowels or consonants).

For now it supports verbs but was not built for clusterings words that may have different suffixes, as would be a noun and an adjective of a same stem.

It offers options:
  - to merge clusters built on different criterias
  - to input words pairs, useful for clustering verbs and their aspects

The clustering algorithm can be used either with the CLI or with the class's methods.

## Simple example: clustering verbs by stem and vowel transformation

Content of `file1`:
```
выстрелить
отличать
застрелить
отличить
```

`python3.8 cluster.py --input test1 --criterias STEM TRANS --merge`
```
выстрелить
застрелить
отличать
отличить
```

## Usage

#### CLI
The CLI `cluster.py` offers the possibility to cluster words and words pairs.

#### Classes
Classes in `cluster.py` can be called to cluster words. As for usage examples, you can refer to the code in the Main part of `cluster.py`, or to the code contained in the `tests` folder.

Project has a pip package: https://pypi.org/project/russian-words-clusters/</br>
Once the package installed you can import classes into your Python code using `from russianwords.clustering import *`.


## A more complex example: clustering words pairs

Content of `file2`:
```
посещать/посетить
разделять
разбираться/разобраться
выделиться/выделить
изменять/изменить
выделяться/выделять
```

`python3.8 cluster.py --input test2 --criterias STEM TRANS --merge --are-pairs`
```
посещать/посетить
разделять
выделяться/выделять
выделиться/выделить
разбираться/разобраться
изменять/изменить
```
