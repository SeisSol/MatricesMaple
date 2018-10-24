#!/usr/bin/env python3

import re
import os
import numpy
from collections import OrderedDict
from lxml import etree

def readMatrixMarket(pathToMatrix):
  matrixFile = open(pathToMatrix)
  if (not matrixFile.readline().startswith('%%MatrixMarket matrix array real general')):
    print('Wrong matrix market format in file {}.'.format(pathToMatrix))
    exit(1)

  dimensions = matrixFile.readline().split()
  numberOfRows = int(dimensions[0])
  numberOfColumns = int(dimensions[1])
    
  matrix = numberOfRows * numberOfColumns * [(0, 0, '')]
  entry = 0
  for line in matrixFile:
    # format: row, column, value
    matrix[entry] = (entry % numberOfRows + 1, entry // numberOfRows + 1, line.strip())
    entry = entry + 1
  
  # entries smaller than 1e-15 are considered to be zero
  sparseMatrix = list(filter(lambda x: numpy.abs(numpy.float64(x[2])) > 1e-15, matrix))
  
  return { '#rows':     numberOfRows,
           '#columns':  numberOfColumns,
           'matrix':    sparseMatrix
         }

class Block:
  def __init__(self, writer, braces):
    self.writer = writer
    self.head = braces[0]
    self.foot = braces[1]

  def __enter__(self):
    self.writer(self.head, False)
    self.writer.indent += 1

  def __exit__(self, type, value, traceback):
    self.writer.indent -= 1
    self.writer.deleteLastComma()
    self.writer(self.foot)

class JSON(object):
  def __init__(self, fileName):
    self.fileName = fileName
    self.indent = 0

  def __enter__(self):
    self.out = open(self.fileName, 'w+')
    return self

  def __exit__(self, type, value, traceback):
    self.deleteLastComma()
    self.out.truncate()
    self.out.close()
    self.out = None
  
  def deleteLastComma(self):
    self.out.seek(self.out.tell() - 2, os.SEEK_SET)
    self.out.write('\n')

  def __call__(self, code, needsSep=True):
    indentSpace = self.indent * '  '
    sep = ',' if needsSep else ''
    for line in code.splitlines():
      self.out.write(indentSpace + line + sep + '\n')

  def Dict(self, nofoot=False):
    return Block(self, '{}')

  def List(self, nofoot=False):
    return Block(self, '[]')

  def _format(self, value):
    if isinstance(value, str):
      return '"{}"'.format(value)
    return str(value).replace('\'', '"')

  def dictEntry(self, key, value):
    self('{}: {}'.format(self._format(key), self._format(value)))

def convertToJSON(fileName, matrices):
  with JSON('{}.json'.format(fileName)) as j:
    with j.List():
      for name,matrixMarket in matrices.items():
        with j.Dict():
          j.dictEntry('name', name)
          j.dictEntry('rows', matrixMarket['#rows'])
          j.dictEntry('columns', matrixMarket['#columns'])
          entries = [list(entry) for entry in matrixMarket['matrix']]
          j.dictEntry('entries', entries)

def convertToXml(fileName, matrices):
  root = etree.Element("matrices")
  for name,matrixMarket in matrices.items():
    matrixAttributes = {"name": name, "rows" : str(matrixMarket['#rows']), "columns" : str(matrixMarket['#columns'])}
    matrix = etree.SubElement(root, "matrix", matrixAttributes) 
    for entry in matrixMarket['matrix']:
      entryAttributes = {"row": str(entry[0]), "column": str(entry[1]), "value" : entry[2]}
      etree.SubElement(matrix, "entry", entryAttributes)
  tree = etree.ElementTree(root)
  tree.write('{}.xml'.format(fileName), pretty_print=True, encoding='utf-8')

def extractName(fileName):
  name, extension = os.path.splitext(fileName)
  c = name.split('_')
  name = c.pop(0)
  if len(c) > 0:
    name = name + '({})'.format(','.join(c))
  return name

def getMatrices(dirName):
  matrices = dict()
  for fileName in os.listdir(dirName):
    matrices[extractName(fileName)] = readMatrixMarket(os.path.join(dirName, fileName))
  return matrices
  
