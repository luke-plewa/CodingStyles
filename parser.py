import os
import re
import string
from collections import defaultdict
from nltk.corpus import words
import nltk

rootdir = '/Users/luke/Documents/582/CodingStyles/samples/'
file_data = dict()
repositories = [
  'git', 'php-src', 'redis', 'scikit-learn',
  'macvim', 'dynomite', 'Arduino'
]

# count of all the words
decl_words = defaultdict(lambda: 0)
# list of all the lines for each word
decl_lines = defaultdict(lambda: list())
# list of all the repos for each word
decl_repos = defaultdict(lambda: list())
# variables for each word's featuresets
decl_vars = dict()

keywords = [
  "auto", "break", "case", "char", "const", "continue", "default", "do",
  "double", "else", "enum", "extern", "float", "for", "goto", "if", "int",
  "long", "register", "return", "short", "signed", "sizeof", "static",
  "struct", "switch", "typedef", "union", "unsigned", "void", "volatile",
  "while"
]

declaration_keywords = [
  "auto", "char", "goto", "union",
  "double", "enum", "extern", "float", "int",
  "long", "short", "signed", "static", "register",
  "struct", "typedef", "unsigned", "void", "volatile"
]

patterns = [
  r"(?:\w+\s+)([a-zA-Z_][a-zA-Z0-9]+)",
]

class MyVariable:
  '''represents a declared variable'''

  def __init__(self, name):
    self.name = name

  def startup(self):
    self.constant = self.m_constant()
    self.snake = self.m_snake()
    self.camel = self.m_camel()
    self.repos = self.m_repos()
    self.dict_words = self.m_dict_words()
    self.types = self.m_types()

  def m_types(self):
    types = defaultdict(lambda: 0)
    for line in decl_lines[self.name]:
      for my_type in declaration_keywords:
        if my_type in str(line):
          print(self.name, my_type)
          types[my_type] += 1
    self.types = types

  def m_repos(self):
    my_repos = list()
    for repo in repositories:
      if self.name in decl_repos[repo]:
        my_repos.append(repo)
    return my_repos

  def m_constant(self):
    for letter in self.name:
      if not ("_" is letter or letter.isupper()):
        return False
    return True

  def m_snake(self):
    for letter in self.name:
      if "_" in letter:
        return True
    return False

  def m_camel(self):
    last_index = 0
    for letter in self.name[1:]:
      if letter.isupper() and self.name[last_index].islower():
        return True
    return False

  def m_dict_words(self):
    dict_words = list()
    if self.m_snake() or not self.m_camel():
      words_list = self.name.split("_")
      for word_to_test in words_list:
        if word_to_test in words.words() and len(word_to_test) > 1:
          dict_words.append(word_to_test)
    return dict_words

  def features(self):
    return {
      "camel": self.camel,
      "snake": self.snake,
      "const": self.constant,
      "dict": len(self.dict_words),
      "length": len(self.name)
    }

  def __str__(self):
    return str(
      self.name +
      "\tCamel: " + str(self.camel) +
      "\tSnake: " + str(self.snake) +
      "\tConstant: " + str(self.constant) +
      "\n\tDict Words: " + str(self.dict_words) +
      "\n\tRepositories: " + str(self.repos)
    )

class MyDocument:
  '''represents a code document'''

  def __init__(self, name, lines):
    self.name = name
    self.lines = lines
    self.declarations = []

  def __str__(self):
    return str([self.name, self.declarations])

def main():
  parse()
  pattern_detect()
  process_dict()
  report()

# add files to public dict
# remove empty directories and non-C files
def parse():
  for repo in repositories:
    file_data[repo] = dict()
    for subdir, dirs, files in os.walk(rootdir + repo):
      for my_file in files:
        filename = os.path.join(subdir, my_file)
        start_index = len(filename) - 2
        if (filename[start_index:] == ".c"):
          try:
            file_p = open(filename, 'r')
            new_file = MyDocument(name=filename, lines=file_p.readlines())
            file_data[repo][my_file] = new_file
            file_p.close()
          except ValueError:
            # print("Skipping a file: " + filename)
            pass
        else:
          print(filename)
          # os.remove(filename)
          # os.rmdir(filename)
      if len(dirs) == 0 and len(files) == 0:
        print('Empty directory: {}'.format(subdir))
        os.rmdir(subdir)

def pattern_detect():
  for repo in file_data:
    for my_file in file_data[repo]:
      for line in file_data[repo][my_file].lines:
        for keyword in declaration_keywords:
          if re.search(keyword, line):
            my_line = line.split()
            last_index = 0
            for word in my_line:
              if word == "=":
                add_word_to_dictionaries(line, my_line[last_index - 1], repo)
              last_index += 1

def add_word_to_dictionaries(my_line, decl_word, repo):
  # some regular expressions to extract the variable
  if re.search(r".*\[([a-zA-Z0-9]+)\].*", decl_word):
    return
  if (re.search(r".*->.*", decl_word) or
      re.search(r".*\..*", decl_word)):
    index = decl_word.rfind(">")
    if index == -1:
      index = decl_word.rfind(".")
    decl_word = decl_word[index + 1:]

  replacement_chars = ["*", "(", ")", "{", "}", "[", "]", "++", "--"]

  for char in replacement_chars:
    decl_word = decl_word.replace(char, "")
  decl_words[decl_word] += 1
  decl_lines[decl_word].append((my_line, repo))
  print(decl_word)

def process_dict():
  for word in decl_words:
    for repo in repositories:
      if word not in decl_repos[repo]:
        decl_repos[repo].append(word)
    decl_vars[word] = MyVariable(word)
    print(word)

  # sorted_words = sorted(
  #   list(decl_words.keys()),
  #   key=lambda k: decl_words[k],
  #   reverse=True
  # )

  # for word in sorted_words[:300]:
  #   print(decl_vars[word])

def report():
  featuresets = list()
  for word in list(decl_vars.keys()):
    featuresets.append((decl_vars[word].features(), decl_vars[word].repos()))
  train_set, test_set = featuresets[(len(featuresets) / 2):], featuresets[:(len(featuresets) / 2)]
  classifier = nltk.NaiveBayesClassifier.train(train_set)
  print("author: " + str(nltk.classify.accuracy(classifier, test_set)))

parse()
