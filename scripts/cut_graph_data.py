#! /usr/bin/env python

import sys

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print "Usage: {0} path_to_url path_to_graph".format(sys.argv[0])
    sys.exit(1)
  #
  with open(sys.argv[1]) as url_fd:
    url_set = { url_line.strip() for url_line in url_fd }
  #
  with open(sys.argv[2]) as graph_fd:
    has_to_print = False
    for line in graph_fd:
      (url, _) = line.strip().split()
      if not line.startswith('\t'):
        if url in url_set:
          has_to_print = True
          print line,
        else:
          has_to_print = False
      else:
        if has_to_print and url in url_set:
          print line,
