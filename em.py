import vis
import pygame as pg
import math
from time import sleep

width = 1280
height = 720

def draw(em, vis_state):
  global width, height
  cnt = len(vis_state["freq_boundaries"])-1
  h = vis_state["height_divs"]
  hh = math.ceil(float(height)/float(h))
  ww = math.ceil(float(width)/float(cnt))
  for i in range(cnt):
    for j in range(h):
      col = vis_state["out"][i+cnt*j]
      if col[0] > 255 or col[1] > 255 or col[2] > 255:
        print(col)
      pg.draw.rect(em, col, [i * ww, j * hh, ww, hh])

def main():
  global width, height
  pg.init()
  em = pg.display.set_mode((width, height))
  done = False
  vis.init()
  pg.mixer.music.set_volume(0.05)
  pg.mixer.music.load(vis.get_state()["playing"])
  pg.mixer.music.play()
  clock = pg.time.Clock()
  print(vis.get_state()["freq_boundaries"])
  while not done:
    state = vis.get_state()
    if vis.update() == -1:
      vis.init()
      pg.mixer.music.load(state["playing"])
      pg.mixer.music.play()
    vis.update()
    draw(em, state)
    for e in pg.event.get():
      if e.type == pg.QUIT:
        done = True
      if e.type == pg.KEYDOWN:
        if e.key == pg.K_n:
          vis.skip_song()
    pg.display.flip()
    clock.tick(state["sample_rate"]/(2*state["chunk"]))
  pg.quit()

if __name__ == "__main__":
  main()
