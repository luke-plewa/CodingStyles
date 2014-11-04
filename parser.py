import os
rootdir = '/Users/luke/Documents/582/CodingStyles/samples/'
file_data = dict()
repositories = ['git']

class MyDocument:
  '''represents a code document'''

  def __init__(self, name, data):
    self.name = name
    self.data = data

  def __str__(self):
    return str([self.name])

for repo in repositories:
  file_data[repo] = dict()
  for subdir, dirs, files in os.walk(rootdir + repo):
    for file in files:
      filename = os.path.join(subdir, file)
      start_index = len(filename) - 2
      if (filename[start_index:] == ".c"):
        # print(filename)
        my_file = open(filename, 'r')
        new_repo = MyDocument(name=filename, data=my_file.readlines())
        print(new_repo.name)
        file_data[repo][filename] = new_repo
        # print(file_data[my_file])
        my_file.close()
