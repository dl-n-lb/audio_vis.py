import numpy as np 
import wave
from math import *
from struct import unpack

import random
import colorsys

# general idea => take audio as some input (likely wav?)
# process out the audio s.t key information about it is gained
# prolly use fft
# look at changes
# affect some pattern using that data + some random backround fluctuation
# perhaps have like a diffusion effect overall

# possible frequency boundaries
# [0, 100, 250, 525, 950, 1900, 3000, 9000, 20000]
#  [0, 80, 180, 380, 700, 1200, 2100, 5000, 20000]

freq_cnt = 24
height_divs = 14

state = {
  "freq_cnt": freq_cnt,
  "height_divs": height_divs,
  #"source_files": ["song.wav"],
  "source_files": ["music/crabrave.wav", "music/clarity.wav",
        "music/secrets.wav", "music/bekind.wav", "music/onandon.wav",
        "music/dejavu.wav", "music/circlesdubstep.wav", "music/circles.wav",
        "music/fumes.wav"],
  "playing": "",
  "source": [],
  "previous": [],
  "out": [[0, 0, 0] for i in range(freq_cnt * height_divs)],
  "elapsed_time": 0,
  "chunk": 512*2,
  "sample_rate": 0,
  "n_channels": 0,
  "out_levels": [0 for i in range(freq_cnt)],
  "weighting": [2 ** (i*4/freq_cnt + 1) for i in range(freq_cnt)],
  #"weighting": [2, 8, 8, 16, 16, 32, 32, 64],
  "freq_boundaries": [20 + 100 * (1.01 ** (537.3 * float(i) / freq_cnt)-1) for i in range(freq_cnt+1)],
  "data": 0,
  "colors": [[255, 0, 255] for i in range(max(height_divs, freq_cnt))],
  "div_factor": 5000000,
  "effect_scale": 4,
  "hue": 0.8,
  "skip": False,
}

def create_colors(start_hue):
  global state
  bri = 1
  hue = start_hue
  sat = 0.8 
  for i in range(state["height_divs"]):
    hue -= 0.05
    state["colors"][i] = np.multiply(colorsys.hsv_to_rgb(hue, sat, bri), 255).astype(int)

def clear_screen():
  global state
  for i, v in enumerate(state["out"]):
    state["out"][i] = [0, 0, 0]

def skip_song():
    global state
    state["skip"] = True

def diffuse_scr():
  global state, freq_cnt
  r = state["out"]
  for i in range(freq_cnt):
    for j in range(state["height_divs"]):
      shared = 0
      k = i+j*freq_cnt
      if (i != 0):
        r[k-1] = np.add(r[k-1], np.multiply(r[k], 0.25))
        shared += 0.25
      if (i != freq_cnt-1):
        r[k+1] = np.add(r[k+1], np.multiply(r[k], 0.25))
        shared += 0.25
      r[k] = np.multiply(r[k], 1 - shared)
  state["out"] = r
        
def fade_scr(amt):
  global state
  r = state["out"]
  for i in range(len(r)):
    r[i] = np.multiply(r[i], 1-amt)
  state["out"] = r

def init():
  global state

  clear_screen()
  create_colors(0.8)

  song = state["playing"]
  while state["playing"] == song:
    state["playing"] = random.choice(state["source_files"])

  print(state["playing"])
  state["source"] = wave.open(state["playing"], 'r')
  state["sample_rate"] = state["source"].getframerate()
  state["n_channels"] = state["source"].getnchannels()

def length(v2):
  return sqrt(v2[0] ** 2 + v2[1] ** 2)

def piff(v):
  global state
  return int(2*state["chunk"]*v / state["sample_rate"])

def calc_levels(data):
  global state, freq_cnt
  data = unpack("%dh"%(len(data)/2), data)
  data = np.array(data, dtype="h")
  if data.size == 0:
    return -1 # LOL

  fourier = np.fft.rfft(data)
  fourier = np.delete(fourier, len(fourier) - 1)
  power = np.abs(fourier)
  fr = state["freq_boundaries"]

  for i in range(freq_cnt):
    state["out_levels"][i] = np.mean(power[piff(fr[i]): piff(fr[i+1]): 1])

  for i in range(freq_cnt):
    if np.isnan(state["out_levels"][i]):
      state["out_levels"][i] = 0
    state["out_levels"][i] = int(state["out_levels"][i])

  state["out_levels"] = np.divide(np.multiply(state["out_levels"], state["weighting"]),state["div_factor"])
  state["out_levels"] = state["out_levels"].clip(0, state["height_divs"])

  return 0

def update():
  global state, freq_cnt
  if state["skip"]:
    state["skip"] = False
    return -1
  data = state["source"].readframes(state["chunk"])
  if data == '':
    return -1

  diffuse_scr()
  fade_scr(0.33)

  state["hue"] += 0.0001
  create_colors(state["hue"])

  if calc_levels(data) == -1:
    return -1
  for x in range(0, freq_cnt):
    for y in range(0, state["height_divs"]):
      c = state["colors"][x]
      f = state["out_levels"][x] / state["height_divs"] * state["effect_scale"]
      divisor = float(state["height_divs"]) / 2
      state["out"][x+y*freq_cnt] = np.multiply(
        (1 - abs(y-divisor)/(divisor**1.2))**((1-f)*0.5),
        np.add(
          state["out"][x+y*freq_cnt],
          np.multiply(c, f)
        ).clip(0, 254)
      ).clip(0, 254).astype(int)
  return 0
  #print(state["out_levels"])

def main():
  init()
  while True:
    update()

def get_state():
  global state
  return state

# entry point
if __name__ == "__main__":
  main()

