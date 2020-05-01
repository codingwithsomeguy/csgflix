import os, json
import wave

import PIL.Image
import numpy as np
from itertools import groupby

def rle_encode(arr):
    result = []
    for name, grp in groupby(arr):
        #print(len(list(grp)), name)
        result.append(len(list(grp)))
        result.append(name)
    return result


def imga(image_filename):
    i1 = PIL.Image.open(image_filename)
    i1a = np.array(i1).flatten()
    i1a = np.array([x >> 1 for x in i1a])
    # Clamp:
    i1a[i1a <= 20] = 0
    # RLE:
    result = rle_encode(i1a.tolist())
    #return json.dumps(i1a.tolist())
    return result


def imgad(base_image_filename, offset_image_filename):
    i1 = PIL.Image.open(base_image_filename)
    i1a = np.array(i1)
    i2 = PIL.Image.open(offset_image_filename)
    i2a = np.array(i2)

    deltai = i1a ^ i2a

    return rle_encode(deltai.flatten().tolist())


def audioarray(audio_filename):
    result = []
    with wave.open(audio_filename) as f:
        audio_data = f.readframes(f.getnframes())
        result = list(audio_data)
    return result


def pack_csgson_codec(movie_set):
    print("pack_csgson_codec:", movie_set)
    out_dir = os.path.join("media", "encoded")
    out_file = os.path.join(out_dir, movie_set + ".csgson")
    if os.path.exists(out_file):
        print("pack_csgson_codec: file exists, skipping:", out_file)
        return

    os.makedirs(out_dir, exist_ok=True)

    packed = {
        "meta": {
            # 0.1 - always RLE
            "version": "0.1",
            # TODO: take this as a param
            "resolution": {
                "width": 426,
                "height": 240,
                "depth": 3
            },
            # TODO: unroll this
            "audio": "unsigned-8bit-mono-8khz"
        },
    }

    # be naive about unpacked video (assume fetchcorpus.py ran)
    image_file = os.path.join("media", "img", movie_set, "i001.png")
    packed["image"] = imga(image_file)
    
    # naively pack all delta frames relative to the one before
    packed["deltas"] = []
    # figure out the last one for the loop, or just keep going until it doesn't exist
    delta_image_num = 2
    done = False
    # TODO: don't rely on fixed size image numbers eg i009.png
    while True:
        last_file = os.path.join("media", "img", movie_set,
            "i%03d.png" % (delta_image_num - 1))
        delta_file = os.path.join("media", "img", movie_set,
            "i%03d.png" % delta_image_num)
        if os.path.exists(delta_file):
            print("Delta:", last_file, delta_file)
            packed["deltas"].append(imgad(last_file, delta_file))
            delta_image_num += 1
        else:
            break

    audio_file = os.path.join("media", "audio", "%s-8khz.wav" % movie_set)
    packed["audio"] = audioarray(audio_file)

    print("pack_csgson_codec: writing", out_file)
    json.dump(packed, open(out_file, "w"))


def main():
    for i in range(2, 7+1):
        pack_csgson_codec("movie%d-240p-0" % i)


if __name__ == "__main__":
    main()
