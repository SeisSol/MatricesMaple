#!/usr/bin/env python3
import re
from convert_tools import *

def stripOrderFromName(name):
  match = re.match('.*\((\d*),?(\d*)\)', name)
  #print(match.group(1), match.group(2))
  raw_name = re.sub('\(\d*,?\d*\)', '', name)
  if match.group(2):
    return "{name}({idx})".format(name=raw_name,
                                  idx=match.group(1))
  return raw_name

def main():
  outDir = 'export'

  matrices = getMatrices(outDir)
  for degree in range(1,7):
    # filter out matrices that match degree
    p = re.compile(".*\(\d*,?{}\)".format(degree))
    print('Converting degree {}...'.format(degree))
    cur_matrices = {stripOrderFromName(k) : v
                    for k, v
                    in matrices.items()
                    if p.match(k)}
    print(cur_matrices.keys())
    convertToJSON('export_json/nodalBoundary_matrices_{}'.format(degree + 1), cur_matrices)
    #break
  
if __name__ == '__main__':
  main()

