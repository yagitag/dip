#!/usr/bin/python

def print_table(s_list, r_list, l_matrix, metric_func):
  res = []
  for i in range(len(s_list)):
    for j in range(len(r_list)):
      val = metric_func(s_list[i], r_list[j], l_matrix[i][j])
      res.append((i, j, val))
      print val,
    print
  for (i, j, val) in sorted(res, key = lambda t: t[2], reverse = True):
    print "({0},{1}) -- {2}".format(i, j, val)
