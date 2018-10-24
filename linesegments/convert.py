#!/usr/bin/env python3

from convert_tools import *

outDir = 'export'

for degree in range(1,32):
  print('Converting degree {}...'.format(degree))
  matrices = getMatrices(os.path.join(outDir, str(degree)))
  convertToJSON(os.path.join(outDir, 'matrices_{}'.format(degree)), matrices)
