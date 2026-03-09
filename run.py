#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) < 2:
    print('Usage: run.py <search_term>')
    print('Example: run.py احمد')
    sys.exit(1)

search_term = sys.argv[1]
sys.argv = ['iraq-search', 'search', search_term, '--limit', '20']

from iraq_db_search.cli import cli
cli()
