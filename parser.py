import os
import re
import string
from collections import defaultdict
from nltk.corpus import words

rootdir = '/Users/luke/Documents/582/CodingStyles/samples/'
file_data = dict()
repositories = ['git', 'php-src', 'redis', 'scikit-learn']

decl_words = defaultdict(lambda: 0)
decl_lines = defaultdict(lambda: list())
decl_repos = defaultdict(lambda: list())
decl_vars = dict()
dict_count = defaultdict(lambda: list())

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

  def repos(self):
    my_repos = list()
    for repo in repositories:
      if self.name in decl_repos[repo]:
        my_repos.append(repo)
    return my_repos

  def snake(self):
    for word in self.name:
      if "_" in word:
        return True
    return False

  def camel(self):
    last_index = 0
    for letter in self.name[1:]:
      if letter.isupper() and self.name[last_index].islower():
        return True
    return False

  def dict_words(self):
    dict_words = list()
    if self.snake() or not self.camel():
      words_list = self.name.split("_")
      for word_to_test in words_list:
        if word_to_test in words.words():
          dict_words.append(word_to_test)
    return dict_words

  def __str__(self):
    return str(
      self.name +
      "\tCamel: " + str(self.camel()) +
      "\tSnake: " + str(self.snake()) +
      "\tDict Words: " + str(self.dict_words()) +
      "\n\tRepositories: " + str(self.repos())
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
  # add code for extracting the words before/after the keyword
  if (re.search(r".*\[([a-zA-Z0-9]+)\].*", decl_word) or
      re.search(r".*->.*", decl_word) or
      re.search(r".*\..*", decl_word)):
    print("array assign: " + decl_word)
    return

  replacement_chars = ["*", "(", ")", "{", "}", "[", "]", "++", "--"]

  for char in replacement_chars:
    decl_word = decl_word.replace(char, "")
  decl_words[decl_word] += 1
  decl_lines[decl_word].append((my_line, repo))
  print(decl_word)

def process_dict():
  for word in decl_words:
    decl_vars[word] = MyVariable(word)
    for repo in repositories:
      if word not in decl_repos[repo]:
        decl_repos[repo].append(word)
        if len(decl_vars[word].dict_words()) > 0:
          dict_count[repo] = (dict_count[repo][0], dict_count[repo][1] + 1)

  sorted_words = sorted(
    list(decl_words.keys()),
    key=lambda k: decl_words[k],
    reverse=True
  )

  # for word in sorted_words[:300]:
  #   print(decl_vars[word])

def report():
  print(dict_count)

main()
