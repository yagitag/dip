#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import math
import collections
#import loader


MIN_JACCARD_COEF = 0.2


def lemm_title_to_set(lemm_title_str):
  raw_lemms = lemm_title_str.split()
  lemms = set()
  for raw_lemm in raw_lemms:
    if raw_lemm.startswith('('):
      for lemm in raw_lemm[1:-1].split('|'):
        lemms.add(lemm)
    else:
      lemms.add(raw_lemm)
  return lemms



class Config:
  def __init__(self, data_path = '/home/ag/dip_data', graph_data_file = 'graph_data.txt', video_data = 'videos_data',
      video_data_fields = [ ('title', str), ('lemm_title', lemm_title_to_set), ('adult', bool) ]):
    self.data_path = data_path
    self.graph_data_file = graph_data_file
    self.video_data = video_data
    self.video_data_fields = video_data_fields



class Video:

  def __init__(self, url, views, related_video_urls):
    self.url = url
    self.views = int(views)
    self.related = related_video_urls
    self.title = ''
    self.lemm_title = set()
    self.adult = False

def jaccard_coef(set_l, set_r):
  return float(len(set_l & set_r)) / len(set_l | set_r)

def videos_jaccard_coef(vl, vr):
  return jaccard_coef(vl.lemm_title, vr.lemm_title)


class VideoGraph:

  def __init__(self):
    self.video_dict = {}
    self.common_views = 0

  def get(self, url):
    is_new = False
    if not self.video_dict.has_key(url):
      video = Video(url, 0, [])
      self.video_dict[url] = video
      is_new = True
    else:
      video = self.video_dict[url]
    return (is_new, video)

  def load(self, config):
    self.load_graph(config)
    self.load_video_data(config)

  def load_graph(self, config):
    fd = open(config.data_path + '/' + config.graph_data_file, 'r')
    cur_video = None
    for line in fd.xreadlines():
      if line.startswith('\t'):
        (url, linked_views) = line.strip().split()
        (_, linked_video) = self.get(url)
        video.related.append( (linked_video, int(linked_views[1:-1])) )
      else:
        (url, views) = line.strip().split()
        (_, video) = self.get(url)
        video.views = int(views)
        self.common_views += video.views

  def load_video_data(self, config):
    vdata_path = config.data_path + '/' + config.video_data + '/'
    url_fd = open(vdata_path + 'url')
    fields = [ (field, conv_func, open(vdata_path + field)) for (field, conv_func) in config.video_data_fields ]
    #
    for url_line in url_fd:
      video = self.video_dict[url_line.strip()]
      for (field, conv_func, fd) in fields:
        line = fd.readline()
        setattr(video, field, conv_func(line.strip()))

  def calc_real_views(self):
    for vb in self.video_dict.values():
      vb.views = sum( views for (_, views) in vb.related )

  def make_directed(self, cond):
    for vb in self.video_dict.values():
      tmp_list = []
      for (vr, br_views) in vb.related:
        if cond(vb, vr, br_views):
          tmp_list.append( (vr, br_views) )
      vb.related = tmp_list


  def __getitem__(self, key):
    return self.video_dict[key]



def l1_normalize(b_vcnt, r_vcnt, br_vcnt):
  return float(br_vcnt) / (b_vcnt * r_vcnt)

def l2_normalize(b_vcnt, r_vcnt, br_vcnt):
  return float(br_vcnt) / math.sqrt(b_vcnt * r_vcnt)

def mi1_normalize(b_vcnt, r_vcnt, br_vcnt, common_vcnt):
  return float(br_vcnt) / common_vcnt * math.log( float(br_vcnt) * common_vcnt / (b_vcnt * r_vcnt) )

def mi2_normalize(b_vcnt, r_vcnt, br_vcnt, common_vcnt):
  return mi1_normalize(b_vcnt, r_vcnt, br_vcnt, common_vcnt) + mi1_normalize(common_vcnt - b_vcnt, common_vcnt - r_vcnt, common_vcnt - br_vcnt, common_vcnt)

def idf_normalize(b_vcnt, r_vcnt, br_vcnt, common_vcnt):
  return -1. * br_vcnt / b_vcnt * math.log(float(r_vcnt) / common_vcnt)

def logodds_normalize(b_vcnt, r_vcnt, br_vcnt, common_vcnt):
  return float(br_vcnt) * (common_vcnt - b_vcnt) / (b_vcnt * (1 + r_vcnt - br_vcnt))

def my_normalize(b_ulvcnt, r_vcnt, br_vcnt):
  return float(br_vcnt) / (b_ulvcnt * math.log(1. + r_vcnt))
  #return float(br_vcnt) / (b_ulvcnt * math.sqrt(float(r_vcnt))) #i've used log instead sqrt

def prob_normalize(b_ulvcnt, r_vcnt, br_vcnt):
  return br_vcnt / math.sqrt(float(b_ulvcnt))



class Recommender:

  NORM_FUNCS = [
                 #"L1":         l1_normalize,
                 #("L2",         l2_normalize,         0.00001),
                 #"MI1":        mi1_normalize,
                 #"MI2":        mi2_normalize,
                 #("IDF",        idf_normalize),
                 #"LOG_ODDS":   logodds_normalize,
                 ("MY",         my_normalize,         0.0001),
                 #("PROB",       prob_normalize),
               ]

  class VideoWrapper:
    def __init__(self, video, local_score, jaccard_coef, father = None):
      self.video = video #TODO delete it after testing
      #self.score = score
      self.local_score = local_score
      self.jaccard_coef = jaccard_coef
      if not father:
        self.discovery_depth = 0
      else:
        self.discovery_depth = father.discovery_depth + 1
      self.links_cnt = 1 #TODO -//-
      self.father = father #TODO -//-
      self.score = 0.
    def try_to_change_score(self, new_score, new_local_score, new_father):
      if new_score > self.score:
        self.score = new_father
        self.local_score = new_local_score
        self.father = new_father
      self.links_cnt += 1


  def __init__(self, config):
    self.graph = VideoGraph()
    self.graph.load(config)
    #self.graph.calc_real_views()
    #self.graph.make_directed(lambda vb, vr, br_views: vb.views / 2. < vr.views)

  def recommend(self, url, max_depth = 3, min_result_cnt = 5):
    res_list = []
    vbase = self.graph[url]
    #self.VideoWrapper.seed_video = vbase #TODO гавнокод
    for (self.m_name, self.m_func, self.m_threshold) in self.NORM_FUNCS:
      res = self.get_related_videos_bfs(vbase, max_depth, min_result_cnt)
      res = sorted(res, key = lambda vw: vw.score, reverse = True)
      res_list.append( (self.m_name, res) )
    return (vbase, res_list)

  def get_related_videos_dfs(self, vbase, vdict, depth, max_depth, prev_prob):
    if depth < max_depth:
      b_views = sum( br_views for (_, br_views) in vbase.related)
      for (vr, br_views) in vbase.related:
        vnode = vdict.get(vr, None)
        prob = prev_prob * br_views / b_views
        if vnode == None:
          vdict[vr] = self.VNode(prob, depth + 1)
          self.get_related_videos_dfs(vr, vdict, depth + 1, max_depth, prob)
        else:
          vnode.score += prob
          vnode.links_cnt += 1

  def get_related_videos_bfs(self, vseed, max_depth, min_result_cnt):
    res_set = set()
    queue = collections.deque()
    vws = self.VideoWrapper(vseed, 0, 1)
    wrapper = { vseed: vws }
    queue.append(vws)
    depth = 0
    k = 1.
    #
    while queue:
      vwb = queue.popleft()
      #
      if vwb.discovery_depth != depth: # ++depth
        depth = vwb.discovery_depth
        if depth == max_depth: break
        k = 1. / (2 ** (depth + 1) - 1)
      #
      (weight, ans_score, vw) = (2, 0., vwb)
      while vw != vws:
        ans_score += k * weight * vw.local_score
        vw = vw.father
        weight *= 2
      #
      vb = vwb.video
      #print vb.title, len(vb.related) 
      for (vr, br_views) in vb.related:
        #
        if vr.views < vb.views:
          popularity_penalty = (float(vr.views) / vseed.views)
        else:
          popularity_penalty = 1.
        #
        if self.m_name in ("L1", "L2", "MY", "PROB"):
          args = (vb.views, vr.views, br_views)
        else:
          args = (vb.views, vr.views, br_views, self.graph.common_views)
        #
        vwr = wrapper.get(vr, None)
        if vwr == None:
          local_score = self.m_func(*args) * popularity_penalty
          if local_score < self.m_threshold: continue
          jaccard_coef = videos_jaccard_coef(vseed, vr) # Подумать может надо после отсечением
          vwr = self.VideoWrapper(vr, local_score, jaccard_coef, vwb)
          if vwr.jaccard_coef > MIN_JACCARD_COEF: # сдлать локальной
            vwr.local_score *= jaccard_coef
            queue.append(vwr)
          else:
            res_set.add(vwr)
          vwr.score = ans_score + vwr.local_score * k #TODO гавнокод
          wrapper[vr] = vwr
        elif depth + 1 == vwr.discovery_depth:
          if vwr.jaccard_coef > MIN_JACCARD_COEF:
            local_score = self.m_func(*args) * popularity_penalty * jaccard_coef
          else:
            local_score = self.m_func(*args) * popularity_penalty
          score = ans_score + local_score
          vwr.try_to_change_score(score, local_score, vwb)
      #
      if len(res_set) < min_result_cnt and not queue:
         for vw in res_set: queue.append(vw)
    #
    return res_set



if __name__ == '__main__':
  #if len(sys.argv) != 2:
  #  print "Usage: {0} file_with_graph_data".format(sys.argv[0])
  #  exit(1)
  recommender = Recommender(Config())
  print "The initialization is done"
  #
  res_video_print = "\t{5:.3f}|{0:>.10f} -- {4} ({1}, {2} views, {3} links)"
  #
  while True:
    line = raw_input()
    try:
      (url, max_depth) = line.split()
      (seed_video, res_list) = recommender.recommend(url, int(max_depth))
      print "Seed video: {0} ({1} views)".format(seed_video.title, seed_video.views)
      print 10 * '>' + ' CURRENT ' + 10 * '<'
      for (video, _) in seed_video.related[:5]:
        #print my_normalize(seed_video.views, video.views, _) * 
        print "\t{3:.3f} -- {2} ({0}, {1} views)".format(video.url, video.views, video.title, videos_jaccard_coef(video, seed_video))
      for (m_name, res) in res_list:
        print 10 * '>' + ' ' + m_name + ' ' + 10 * '<'
        for vw in res[:10]:
          print res_video_print.format(vw.score, vw.video.url, vw.video.views, vw.links_cnt, vw.video.title, videos_jaccard_coef(vw.video, seed_video))
          while vw.father:
            print '\t' + res_video_print.format(vw.local_score, vw.video.url, vw.video.views, vw.links_cnt, vw.video.title, videos_jaccard_coef(vw.video, seed_video))
            vw = vw.father
    except KeyError:
      print "No such video url"
    except ValueError:
      print "Incorrect input. Usage: url max_depth"
