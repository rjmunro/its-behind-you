#!/usr/bin/env python
from process import dupes1,dupes2,dupeIds
from pprint import pprint
import sys
sys.stderr.write("%s dupes found\n" % len(dupeIds))

pprint(dupes1,open('a','w'))
pprint(dupes2,open('b','w'))
