#!/usr/bin/env python

import xxhash
from wand.image import Image
import os
import subprocess
import sys
from ffprobe import FFProbe
import time


def hash_it(string):
    return xxhash.xxh32(string, seed=2).hexdigest()

def newsize(width, height):
    pref_width  = 1500
    pref_height = 500
    pref_ratio = pref_width/pref_height
    ratio = width/height
    if ratio > pref_ratio:
        return pref_width, round(height * (pref_width / width))
    else:
        return round(width * (pref_height / height)), pref_height


def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def generate_thumbs(folder):
    for root, dirs, files in os.walk(folder):
        for name in files:
            f_filename = os.path.join(root, name)
            hashed_name = hash_it(f_filename) + ".jpg"
            if name.endswith((".png", ".jpg")):
                if os.path.isfile(f'thumbs/{hashed_name}'):
                    print("Thumb exists: " + f_filename)
                else:
                    with Image(filename=f_filename) as img:
                        img_name = hashed_name
                        img.format = "jpeg"
                        img.compression_quality = 95
                        img.resize(newsize(img.width, img.height)[0], newsize(img.width, img.height)[1])
                        img.save(filename=f'thumbs/{img_name}')
                    #print("Thumb generated: " + f_filename)
            elif name.endswith((".mp4", ".mkv", ".webm")):
                if os.path.isfile(f'thumbs/{hashed_name}'):
                    print("Thumb exists: " + f_filename)
                else:
                    temp_img = sys.path[0] + '/temp_video_thumb.jpg'
                    video_input = f_filename
                    print("Beep!", get_length(f_filename))
                    seekto = time.strftime('%H:%M:%S',
                                time.gmtime(get_length(f_filename) / 4))
                    print(seekto)
                    subprocess.call(['ffmpeg', '-y', '-i', video_input, '-ss', seekto, '-vframes', '1', temp_img])
                    hashed_name = hash_it(f_filename) + ".jpg"
                    if os.path.isfile(f'thumbs/{hashed_name}'):
                        print("Thumb exists: " + f_filename)
                    else:
                        with Image(filename=temp_img) as img:
                            img_name = hashed_name
                            img.format = "jpeg"
                            img.compression_quality = 95
                            img.resize(newsize(img.width, img.height)[0], newsize(img.width, img.height)[1])
                            img.save(filename=f'thumbs/{img_name}')




generate_thumbs(sys.argv[1])
