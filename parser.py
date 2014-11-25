import os
import re
import string

rootdir = '/Users/luke/Documents/582/CodingStyles/samples/'
file_data = dict()
repositories = ['git', 'php-src', 'redis', 'scikit-learn']

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
  (r".*int.*", "TRUE"),
  (r"/^\s*class\s/", "TRUE"),
]

class MyVariable:
  '''represents a declared variable'''

  def __init__(self, name, decl_types):
    self.name = name
    self.decl_types = decl_types

  def __str__(self):
    return str([self.name, self.decl_types])

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
          my_file = open(filename, 'r')
          print(filename)
          new_repo = MyDocument(name=filename, lines=my_file.readlines())
          file_data[repo][filename] = new_repo
          my_file.close()
        else:
          print(my_file)
          # git 13kb ->7kb
          # os.remove(filename)
          # os.rmdir(filename)
      if len(dirs) == 0 and len(files) == 0:
        print('Empty directory: {}'.format(subdir))
        os.rmdir(subdir)

def pattern_detect():
  for file_name in file_data:
    for my_file in file_data[file_name]:
      for line in file_data['git'][my_file].lines:
        for item in patterns:
          line = re.sub(item[0], item[1], line)
        if line == "TRUE":
          print(line)

main()
