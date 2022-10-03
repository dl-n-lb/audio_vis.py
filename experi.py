import numpy as np
import wave
import math
from struct import unpack

import random
import colorsys

import pygame as pg


class Vis:
    def __init__(self, w=800, h=600):
        pg.init()
        self.w = w
        self.h = h
        self.win = pg.display.set_mode((w, h))
        self.clock = pg.time.Clock()

    def set_fps(self, fps):
        self.fps = fps
        self.clock.tick(fps)

    def play_song(self, file):
        pg.mixer.music.load(file)
        pg.mixer.music.play()
        self.musicfft = MusicFFT(file)

    def loop(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return False
        pg.display.flip()
        return True


class MusicFFT:
    def __init__(self, file, chunk_size, weights, frequency_ranges, scale_factor):
        self.chunk_size = chunk_size
        self.src_file = file
        self.raw_data = wave.open(file, 'r')
        self.sample_rate = self.raw_data.getframerate()
        self.n_channels = self.raw_data.getnchannels()
        self.weights = weights
        self.frequency_ranges = frequency_ranges
        self.scale_factor = scale_factor

    def piff(self, val):  # scale some frequency value into the range of the rfft
        return int(2 * self.chunk_size * val / self.sample_rate)

    def calc_levels(self):
        data = self.raw_data.readframes(self.chunk_size)
        data = unpack("%dh" % (len(data) / 2), data)
        data = np.array(data, dtype="h")
        if (data.size == 0):  # end of song
            return -1

        fourier = np.fft.rfft(data)
        fourier = np.delete(fourier, len(fourier) - 1)
        power = np.abs(fourier)

        output = [0 * len(self.frequency_ranges) - 1]
        for i, j in zip(self.frequency_ranges, self.frequency_ranges[1:]):
            output[i] = np.mean(power[self.piff(i):self.piff(j):1])

        output = np.divide(np.multiply(output, self.weights), self.scale_factor)
        return output


def main():
    vis = Vis(600, 600)
    vis.set_fps(60)
    weighting = []
    frequency_ranges = []
    while vis.loop():
        pass


if __name__ == "__main__":
    main()
