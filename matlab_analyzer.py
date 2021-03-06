import numpy as np
import re
import glob
import pandas as pd
import numpy as np

class a_package:

  name = ''
  length = ''
  description = ''
  files = ''
  properties_table = ''
  functions_table = ''
  folder = ''
  mfileObjs = ''

  def __init__(self, folder, **kwargs):

    self.folder = folder
    self.files = glob.glob( f'{folder}/**/*.m', recursive=True);
    self.description = 'Top-level directory: ' + self.folder + '\n\n' + '\n'.join(self.files)
    self.length = len(self.files)
    self.getmFiles()

  def __repr__(self):
    return repr( f'MATLAB package object -- {self.folder} with properties: name,length,description,files,properties_table,functions_table' )

  def __str__(self):
    return self.description

  def getmFiles(self):
    self.mfileObjs = [ an_mfile( thisfile ) for thisfile in self.files ]

class an_mfile:

  name = ''
  length = ''
  description = ''
  raw = ''
  filetype = ''
  filename = ''
  functions = ''
  properties = ''

  def __init__(self, filename, **kwargs):
    self.filename = filename
    self.readFile()
    self.getProperties()
    self.getFiletype()
    self.getFunctions()
    self.description = f"{self.filename} ({self.filetype})\n\n{self.properties}\n\n{pd.DataFrame([ this_fxn.name for this_fxn in self.functions ],columns=['Functions'])}"

  def __repr__(self):
    return repr( f'M-file object -- {self.filename} with properties: name,length,description,raw,filetype,filename,functions,properties' )

  def __str__(self):
    return self.description

  ####################################
  # Read in the raw text of the file #
  ####################################
  def readFile( self ):
    with open( self.filename, 'r+', encoding = "ISO-8859-1" ) as f:
      self.raw = f.read()

  #######################
  # Properties handling #
  #######################

  # Begin getProperties method #
  def getProperties( self ):
    with open( self.filename,'r+', encoding = "ISO-8859-1" ) as f:
      mytxt = f.read()

    results_ = re.findall('(?<=properties).*?[^a-z]end',mytxt, re.DOTALL)

    if len(results_)>0:
      properties = [ ( c, re.search('\w+',x).group(0) ) for c,x in enumerate(re.findall( '.*\n', results_[0] )) if re.search('\w+',x) is not None ]
      values = [ ( c, re.search('(?<=\=).*(?=\;)',x).group(0) ) for c,x in enumerate(re.findall( '.*\n', results_[0] )) if re.search('(?<=\=).*(?=\;)',x) is not None ]

      df1 = pd.DataFrame( properties, columns=['row','property'] ); 
      df1 = df1.set_index('row');   # Properties
      df2 = pd.DataFrame( values, columns=['row','value'] ); 
      df2 = df2.set_index('row');          # Values extracted

      self.properties = pd.concat( [df1,df2], axis=1 )

  #####################################
  # Obtain the filetype of the m file #
  #####################################

  def getFiletype( self ):

    line_number = 0

    try:
    # Classify the m-file as either a function, class, or script
      with open( self.filename , 'r+', encoding = "ISO-8859-1"  ) as f:
        myline = f.readline()
        first_real_line = myline.split()
        # Enter the first while loop to find an identifier of the file type
        if re.search('[a-zA-Z]',myline) is None: # The first line may contain a comment, space (no text) #
          while re.search('%',myline) is not None or re.search('[a-zA-Z]',myline) is None: # Go to the first line which has text and is not a comment
            myline = f.readline()
            first_real_line = myline.split()
            line_number+=1

      # Get the filetype based on the first real line of the file
      filetype = 'script' # Default
      if first_real_line[0]=='function':
        filetype = 'function'
        f.seek( f.tell() - len(myline) ) # Reverse to make sure that the code below catches this function
      if first_real_line[0]=='classdef':
        filetype = 'class'

    except:
      filetype='indeterminate';

    self.filetype = filetype

  #######################
  # Functions handling  #
  #######################

  def getFunctions( self ):

    output_list = list()
    line_number = 1 # (Arbitrarily starts here to make this match up with MATLAB line editor which starts at 1)
    
    try:
      # Classify the m-file as either a function, class, or script
      with open( self.filename , 'r+', encoding = "ISO-8859-1"  ) as f:
        myline = f.readline()
        first_real_line = myline.split()
        # Enter the first while loop to find an identifier of the file type
        if re.search('[a-zA-Z]',myline) is None: # The first line may contain a comment, space (no text) #
          while re.search('%',myline) is not None or re.search('[a-zA-Z]',myline) is None: # Go to the first line which has text and is not a comment
            myline = f.readline()
            first_real_line = myline.split()
            line_number+=1

        # Get the filetype based on the first real line of the file
        filetype = 'script' # Default
        if first_real_line[0]=='function':
          filetype = 'function'
          f.seek( f.tell() - len(myline) ) # Reverse to make sure that the code below catches this function
        if first_real_line[0]=='classdef':
          filetype = 'class'

        # Continue reading through the file to look for functions
        while 1:
          myline = f.readline()
          line_number+=1

          # Look for a line that can have either multiple spaces or tabs and then the word function
          myfunctionsearch = re.search( '^[\s|\t]{0,}function', myline )
          if myfunctionsearch is not None : # A function has been located based on the regexp search and will be parsed below

            myfunctioncodeblock = '' # Begin with an empty string
            if re.search( '\w+(?=\()', myline ) is None: # The case when a function is split over an ellipsis
              myline = f.readline()
              line_number+=1
              break

            myfunctiontitle = re.search( '\w+(?=\()', myline ).group(0) # Extract the name of the function (as the string immediately preceeding a left parentheses)
            myfunctioncodeblock = myfunctioncodeblock + str(line_number) + '\t' + myline # Add the entire line to the codeblock
            myline = f.readline() # Advance in the file 
            line_number+=1

            while 1: # Enter this loop to go through the function's body
              # If the next line either starts with the word function OR is the end of the file, this loop will break
              if re.search( '^[\s|\t]{0,}function', myline ) is not None or len(myline)==0:
                # The final output of the function is here #
                # It creates a list of a_function objects  #
                output_list.append( a_function( myfunctioncodeblock, filetype=filetype, filename=self.filename ) )
                f.seek( f.tell() - len(myline) - 2 )
                line_number-=2 # Goes two lines back up
                break
              else:
                myfunctioncodeblock = myfunctioncodeblock + str(line_number) + '\t' + myline
                myline = f.readline()
                line_number+=1

          if len(myline)==0: # Reached the end of the file
            break

      self.functions = output_list
    
    except:
    
      self.functions ='indeterminate'    

class a_function:
  
  name = ''
  length = ''
  description = ''
  raw = ''
  filetype = ''
  filename = ''

  def __init__(self, input, **kwargs):
    self.raw = input

    for key, value in kwargs.items():
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

  def __repr__(self):
    return repr( f'a_function object -- {self.name} contained in {self.filename}' )

  def __str__(self):
    return self.description

  
#######################
# Helper functions    #
#######################

def search_mFile(raw, query):
  if isinstance( query, dict ):
    result = { key : len( re.findall( key , raw ) ) for key in query.keys() }
  if isinstance( query, list ):
    result = { query_ : len( re.findall( query_ , raw ) ) for query_ in query }
  if isinstance( query, str ):
    result = len( re.findall( query, raw ) )
    if result==0: # Set the result to None if the answer is zero
      result = None
  if not(isinstance( query, dict )) and not(isinstance( query, list )) and not(isinstance( query, str )):
    return
  return result

def makeFxnMap( list_of_fxn_objects ):
  Nfxns = len(list_of_fxn_objects)
  fxnMap = np.zeros( shape=[0,Nfxns] )
  for i in range( Nfxns ):
    output = [ search_mFile( list_of_fxn_objects[i], f'{this_fxn.name}\(' ) for this_fxn in list_of_fxn_objects ]
    fxnMap = np.vstack( [fxnMap,output] )
  return fxnMap