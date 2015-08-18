#!/usr/bin/env python

import sys
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

  def __init__(self, url, view_cnt = 0, related_video_urls = list()):
    self.url = url
    self.view_cnt = int(view_cnt)
    self.related_videos = []



class Recommender:

  def __init__(self, fpath):
    self.graph = VideoGraph()
    self.graph.load(fpath)

  def get_related_videos(self, url, max_depth = 3):
    res = collections.defaultdict(float)
    self.get_more_related_videos(url, 0, max_depth, res)
    res = sorted(res.items(), key = lambda t: t[1], reverse = True)
    return res

  def get_more_related_videos(self, url, depth, max_depth, res):
    if depth > max_depth: return
    root_video = self.graph[url]
    for (video, linked_views_cnt) in root_video.related_videos:
      res[video] += float(linked_views_cnt) / video.views_cnt
      self.get_more_related_videos(video.url, depth + 1, max_depth, res)



if __name__ == '__main__':
  if len(sys.argv) != 2:
    print "Usage: {0} file_with_graph_data".format(sys.argv[0])
    exit(1)
  recommender = Recommender(sys.argv[1])
  print "The initialization is done"
  while True:
    line = raw_input()
    (url, max_depth) = line.split()
    res = recommender.get_related_videos(url, int(max_depth))
    for (video, rate) in res[:20]:
      print "\t{0} -- {1}".format(rate, video.url)
