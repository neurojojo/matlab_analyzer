import numpy as np
import re
import pandas as pd

class a_function:
  
  name = ''
  length = ''
  description = ''
  raw = ''
  library = ''
  librarytable = ''
  filetype = ''
  filename = ''

  def __init__(self, input, **kwargs):
    self.raw = input

    for key, value in kwargs.items():
      if key=='library':
        self.library = value
      if key=='filetype':
        self.filetype = value
      if key=='filename':
        self.filename = value

    if re.search( '[^\s]+(?=\()', self.raw ) is not None:
      self.name = re.search( '\w+(?=\()', self.raw ).group(0)
    else:
      print(f'No function found in:\n\n {self.name}')
      return
    self.lines = len( re.findall( '\n', self.raw ) )
    self.description = f'Function: {self.name}\nFilename: {self.filename}\nLines: {self.lines}'
    self.librarytable = self.search( self.library )

  def __repr__(self):
    return repr( f'a_function object -- {self.name} contained in {self.filename}' )

  def __str__(self):
    return self.description

  def search(self, query):
    if isinstance( query, dict ):
      result = { key : len( re.findall( key , self.raw ) ) for key in query.keys() }
    if isinstance( query, list ):
      result = { query_ : len( re.findall( query_ , self.raw ) ) for query_ in query }
    if isinstance( query, str ):
      result = len( re.findall( query, self.raw ) )
    if not(isinstance( query, dict )) and not(isinstance( query, list )) and not(isinstance( query, str )):
      return
    return result

  def evaluate(self):
    evaluation = dict()
    evaluation = self.search( 'for' )
    return evaluation
    

def dissect_mFile_objects( mfile_address ):
  input = 'abc def ghi'
  output = input.split()
  return output

def test( mytext ):
  input = 'abc def ghi'
  output = input.split()
  return output