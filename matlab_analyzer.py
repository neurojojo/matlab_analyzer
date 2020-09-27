import pandas as pd
import re

def dissect_mFile( mfile_address ):

	functions = list()
	filename = re.search( '(.*\/)([^/]*(?=\.))', mfile_address ).group(2)
	with open( mfile_address , 'r+' ) as f:
		lines = f.readlines()
		[ functions.append( re.search('[a-z].*',line).group(0) ) for line in lines if 'function' in line or 'method' in line ]

	functions_ = list()
	[ functions_.append( function ) for function in functions if function[0]=='m' or function[0]=='f' ]
	print( f'Saving to {filename}_architecture.csv' )
	return pd.DataFrame(functions_).to_csv(f"{filename}_architecture.csv")