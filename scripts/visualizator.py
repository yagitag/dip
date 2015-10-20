#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from PIL import Image, ImageTk
import Tkinter as tk
import commands
import tkFont

import recommender

class Visualizator:

  def __init__(self, result_cnt = 5, max_depth = 3):
    #
    print "Configuring recommender"
    self.recommender = recommender.Recommender(recommender.Config())
    #
    print "Configuring visualizator"
    self.root = tk.Tk()
    self.root.attributes('-zoomed', True)
    self.root.protocol('WM_DELETE_WINDOW', self.close)
    self.root.update()
    #
    self.width = self.root.winfo_width()
    self.height = self.root.winfo_height()
    self.width_step  = self.width  / 50 # 2%
    self.height_step = self.height / 50 # 2%
    #
    #
    self.videos = []
    self.images_store = set()
    #
    self.huge_font, self.huge_font_height = self.init_font(20)
    self.main_font, self.main_font_height = self.init_font(15)
    self.rec_font, self.rec_font_height = self.init_font(10)
    self.anc_font, self.anc_font_height = self.init_font(7)
    #
    self.init_frames(result_cnt, max_depth)



  def init_font(self, font_size):
    font = tkFont.Font(self.root)
    font.configure(size = font_size)
    label = tk.Label(self.root, text = '', font = font)
    return font, label.winfo_reqheight()



  def init_frames(self, result_cnt, max_depth, image_ratio = 1200. / 720):
    self.result_cnt = result_cnt
    self.max_depth = max_depth
    #
    self.entry_frame = tk.Frame(
        self.root, width = self.width, height = self.main_font_height)
    self.entry_label = tk.Label(
        self.entry_frame, text = "Search: ", font = self.main_font)
    self.entry = tk.Entry(self.entry_frame, font = self.main_font)
    self.entry.bind('<Return>', self.on_search_event)
    self.entry_frame.pack()
    self.entry_label.pack(side = tk.LEFT)
    self.entry.pack(side = tk.LEFT)
    #
    self.rec_img_width  = (self.width - self.width_step) / self.result_cnt
    self.rec_img_height = int(self.rec_img_width / image_ratio)
    self.rec_frame_width  = self.rec_img_width
    self.rec_frame_height = self.rec_img_height + self.huge_font_height + self.rec_font_height * 3 # 2 на название и 1 на количество просмотров
    #
    self.main_frame_height = self.height - self.height_step - 2 * self.rec_frame_height - self.entry.winfo_reqheight()
    self.main_img_height = self.main_frame_height - self.main_font_height * 3
    self.main_img_width  = int(self.main_img_height * image_ratio)
    self.main_frame_width  = self.main_img_width
    #
    self.anc_frame_height = int(self.main_frame_height / self.max_depth)
    self.anc_img_height = self.anc_frame_height - self.anc_font_height * 3
    self.anc_img_width  = int(self.anc_img_height * image_ratio)
    self.anc_frame_width  = self.anc_img_width + self.width_step / 2
    #
    self.info_frame_width = self.width - self.anc_frame_width - self.main_frame_width
    self.info_frame_width /= 2
    self.info_frame_height = self.main_frame_height
    self.info_frame_max_lines_cnt = self.main_font_height / self.rec_font_height
    #
    self.main_video_frame = tk.Frame(self.root,
        width = self.main_frame_width, height = self.main_frame_height)
    self.old_recs_frame = tk.Frame(self.root,
        width = self.width, height = self.rec_frame_height)
    self.new_recs_frame = tk.Frame(self.root,
        width = self.width, height = self.rec_frame_height)
    self.info_frame = tk.Frame(self.main_video_frame,
        width = self.info_frame_width, height = self.info_frame_height)
    self.ancs_frame = tk.Frame(self.main_video_frame,
        width = self.anc_frame_width, height = self.anc_frame_height)
    self.old_rec_frames = [
        tk.Frame(
          self.old_recs_frame,
          width = self.rec_frame_width,
          height = self.rec_frame_height) for _ in range(self.result_cnt) ]
    self.new_rec_frames = [
        tk.Frame(
          self.new_recs_frame,
          width = self.rec_frame_width,
          height = self.rec_frame_height) for _ in range(self.result_cnt) ]
    self.anc_rec_frames = [
        tk.Frame(
          self.ancs_frame,
          width = self.anc_frame_width,
          height = self.anc_frame_height) for _ in range(self.max_depth) ]
    self.old_recs_label = tk.Label(
        self.old_recs_frame, text = "Old recommendations:", font = self.huge_font)
    self.new_recs_label = tk.Label(
        self.new_recs_frame, text = "New recommendations:", font = self.huge_font)
    #
    self.main_video_frame.pack(fill = 'x', padx = self.width_step / 2)
    self.old_recs_frame.pack()
    self.new_recs_frame.pack()
    self.ancs_frame.pack(side = tk.RIGHT, padx = self.width_step / 2)
    self.info_frame.pack(side = tk.RIGHT, padx = self.info_frame_width)
    self.old_recs_label.pack(side = tk.TOP)
    self.new_recs_label.pack(side = tk.TOP)
    for frame in self.old_rec_frames:
      frame.pack(side = tk.LEFT)
      frame.pack_propagate(False)
    for frame in self.new_rec_frames:
      frame.pack(side = tk.LEFT)
      frame.pack_propagate(False)
    for frame in self.anc_rec_frames:
      frame.pack()
      frame.pack_propagate(False)


  def draw_video_stat(self, video_wrapper, vtype):
    if vtype == 'main' or vtype == 'old_rec':
      text = 'None'
    #elif vtype == 'old_rec':
    #  text = 'Jaccard coef: {0}'.format(video_wrapper.jaccard_coef)
    else:
      text = 'Score: {0}\nJaccard coef: {1}\nLast edge weight: {2}\n'
      text.format(
          video_wrapper.score,
          video_wrapper.jaccard_coef,
          video_wrapper.local_score)
    self.info_frame.text = tk.Label(self.info_frame,
        text = text,
        font = self.rec_font,
        height = self.info_frame_max_lines_cnt,
        anchor = tk.W,
        justify = tk.LEFT)
    self.info_frame.text.pack(fill = 'x')



  def unnamed_func(self, video_wrapper, selected):
    if selected:
      self.draw_video_stat(video_wrapper, vtype)
    if vtype.endswith('rec'):
      vtype = 'rec'
    video = video_wrapper#.video



  def draw_video(self, frame, video, vtype):
    print 'Drawing "{0}" as "{1}"'.format(video.title, vtype)
    #frame.preview = tk.Label(frame, image = video.preview, anchor = tk.W)
    if vtype.endswith('rec'):
      vtype = 'rec'
    font = getattr(self, vtype + '_font')
    text = '\n'.join((video.title, "views: " + str(video.views)))
    frame.video_info = tk.Label(frame,
        text = text, font = font, height = 3, anchor = tk.W, justify = tk.LEFT)
    #frame.preview.pack(fill = 'x')
    frame.video_info.pack(side = tk.LEFT, fill = 'x')



  def draw_ancestors(self, video_wrapper):
    ancestors = [video_wrapper]
    while ancestors[-1].father:
      ancestors.append(ancestors[-1].father)
    ancestors.reverse()
    for i in range(len(ancestors)):
      self.draw_video(self.anc_rec_frames[i], ancestors[i], 'anc')



  def draw(self, main, recommeded):
    #self.images_store.add(main.preview)
    #for (video, _) in main.related: self.images_store.add(video.preview)
    #for (video, ancestors) in recommeded:
    #  self.images_store.add(video.preview)
    #  for video in ancestors: self.images_store.add(video.preview)
    #
    self.draw_video(self.main_video_frame, main, 'main')
    for i in range(min(len(main.related), self.result_cnt)):
      (video, _) = main.related[i]
      self.draw_video(self.old_rec_frames[i], video, 'old_rec')
    for i in range(min(len(recommeded), self.result_cnt)):
      self.draw_video(self.new_rec_frames[i], recommeded[i].video, 'new_rec')



  def test(self):
    image_src = Image.open('/home/ag/Dropbox/dir/dip/test_data/test.jpg')
    main_img = self.resize_image(image_src, 'main')
    rec_img  = self.resize_image(image_src, 'rec')
    anc_img  = self.resize_image(image_src, 'anc')
    #
    rec = recommender.Video('http://tralala.ru/', 100)
    rec.title = 'Recommendated video'
    rec.preview = rec_img
    #
    old_recs = [ (rec, 0) for _ in range(self.result_cnt) ]
    main = recommender.Video('http://tralala.ru/', 100500, old_recs)
    main.title = 'Main video'
    main.preview = main_img
    #
    anc = recommender.Video('http://tralala.ru/', 500)
    anc.title = 'Video-Mother'
    anc.preview = anc_img
    ancs = [ anc for _ in range(self.max_depth) ]
    #
    new_rec = [ (rec, ancs) for i in range(self.result_cnt) ]
    #
    #self.draw(main, new_rec, 0)



  def resize_image(self, image_src, vtype):
    width  = getattr(self, vtype + '_img_width')
    height = getattr(self, vtype + '_img_height')
    image_src = image_src.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image_src)


  def on_search_event(self, event):
    self.search(self.entry.get())


  def search(self, text):
    print 'Parsing "' + text + '"'
    text = text.strip()
    if text.startswith('http://'):
      url = text
    else:
      print 'Searching'
      url = commands.getoutput('./search.sh ' + text)
    #
    print 'Getting recommendation for "' + url + '"'
    (video, recommedations) = self.recommender.recommend(url)
    print 'Drawing'
    (measure_name, results) = recommedations[0]
    self.draw(video, results[:self.result_cnt])


  def run(self):
    self.root.mainloop()



  def close(self):
    self.root.quit()



if __name__ == '__main__':
  vzr = Visualizator()
  #vzr.test()
  vzr.run()
