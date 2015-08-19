#!/usr/bin/env python

import sys
import math
import collections
#import loader


class VideoGraph:

  def __init__(self):
    self.video_dict = {}

  def get(self, url):
    is_new = False
    if not self.video_dict.has_key(url):
      video = Video(url)
      self.video_dict[url] = video
      is_new = True
    else:
      video = self.video_dict[url]
    return (is_new, video)

  def load(self, fpath):
    fd = open(fpath, 'r')
    cur_video = None
    for line in fd.xreadlines():
      if line.startswith('\t'):
        (url, linked_views_cnt) = line.strip().split()
        (_, linked_video) = self.get(url)
        video.related_videos.append( (linked_video, int(linked_views_cnt[1:-1])) )
      else:
        (url, views_cnt) = line.strip().split()
        (_, video) = self.get(url)
        video.views_cnt = int(views_cnt)

  def __getitem__(self, key):
    return self.video_dict[key]



class Video:

  def __init__(self, url, views_cnt = 0, related_video_urls = list()):
    self.url = url
    self.views_cnt = int(views_cnt)
    self.related_videos = []



class Recommender:

  def __init__(self, fpath):
    self.graph = VideoGraph()
    self.graph.load(fpath)

  def get_related_videos(self, url, max_depth = 4, top = 500):
    res = collections.defaultdict(float)
    seed = self.graph[url]
    res = [(seed, 0)]
    while max_depth != 0:
      vdict = collections.defaultdict(float, (item for item in res))
      max_depth -= 1
      for vs in vdict.keys():
        common_linked_views_cnt = sum( linked_views_cnt for (_, linked_views_cnt) in vs.related_videos )
        for (vr, linked_views_cnt) in vs.related_videos:
          norm_coef = common_linked_views_cnt * math.log(vr.views_cnt)
          if norm_coef < 100: continue
          vdict[vr] += float(linked_views_cnt) / norm_coef
      res = sorted(vdict.items(), key = lambda t: t[1], reverse = True)[:top]
    return (seed, res)



if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "Usage: {0} file_with_graph_data".format(sys.argv[0])
    exit(1)
  recommender = Recommender(sys.argv[1])
  print "The initialization is done"
  while True:
    line = raw_input()
    try:
      (url, max_depth, top) = line.split()
      (seed_video, res) = recommender.get_related_videos(url, int(max_depth), int(top))
      print "Seed video views: {0}".format(seed_video.views_cnt)
      for (video, rate) in res[:5]:
        print "\t{0} -- {1} ({2} views)".format(rate, video.url, video.views_cnt)
    except KeyError:
      print "No such video url"
    except ValueError:
      print "Incorrect input. Usage: url max_depth max_count_for_calc"
