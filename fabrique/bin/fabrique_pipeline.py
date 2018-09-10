#!/usr/bin/env python

import argparse
from fabrique.executor import Executor

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Test Fabrique pipeline locally')
  parser.add_argument('pipeline', metavar='pipeline', 
                    help='JSON specification of Fabrique pipeline')
  parser.add_argument('data', metavar='data', 
                    help='JSON test data file to run the pipeline on')

  args = parser.parse_args()
  ex = Executor()
  res = ex.execute( open(args.pipeline), open(args.data) )
  for r in res:
    print("Pipeline executed, result:", r)
