#!/usr/bin/env python

import sys


class VidRecData:
  def __init__(self, url, linked_views):
    self.url = url
    self.linked_views = linked_views
  def __str__(self):
    return '[url: {0}, linked_views: {1}]'.format(self.url, self.linked_views)



def generate_full_stat_file(rec_file, view_cnt_file, res_file):
  with open(rec_file, 'r') as fd:
    vid_set = { line.strip() for line in fd.xreadlines() if not line.startswith('\t') }
  with open(view_cnt_file, 'r') as fd:
    vid_dict = dict()
    for line in fd.xreadlines():
      data = line.strip().split()
      if data[0] in vid_set:
        vid_dict[data[0]] = data[1]
  with open(rec_file, 'r') as ifd:
    ofd = open(res_file, 'w')
    for line in ifd.xreadlines():
      if line.startswith('\t'):
        ofd.write(line)
      else:
        cur_video = line.strip()
        ofd.write("{0}\t{1}\n".format(cur_video, vid_dict[cur_video]))



def load_recommendation(fpath):
  fd = open(fpath, 'r')
  res_dict = dict()
  cur_video = ''
  for line in fd.xreadlines():
    if line.startswith('\t'):
      data = line.strip().split()
      res_dict[cur_video].append(VidRecData(data[0], data[1][1:-1]))
    else:
      cur_video = line.strip()
      res_dict[cur_video] = list()
  return res_dict



if __name__ == '__main__':
#  if len(sys.argv) != 2:
#    print "Usage: {0} file_with_recomendation".format(sys.argv[0])
#    exit(1)
#  res_dict = load_recommendation(sys.argv[1])
#  print "Loading has been finished"
#  while True:
#    line = raw_input()
#    try:
#      related = res_dict[line]
#      for video_data in related:
#        print video_data
#    except KeyError:
#      print "No such element"
  if len(sys.argv) != 4:
    print "Usage: {0} file_with_recomendation file_with_views_count result_file".format(sys.argv[0])
    exit(1)
  generate_full_stat_file(sys.argv[1], sys.argv[2], sys.argv[3])
