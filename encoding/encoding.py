import os, json, shutil
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


def apply_scale(img, scale):
    if scale != 1:
        img = img.resize(
            (int(img.width * scale), int(img.height * scale)),
            PIL.Image.ANTIALIAS)
    return img


def imga(image_filename, scale=1):
    i1 = PIL.Image.open(image_filename)
    i1 = apply_scale(i1, scale)
    i1a = np.array(i1).flatten()
    # disable RGB888 --> RGB777 for now
    #i1a = np.array([x >> 1 for x in i1a])
    # Clamp:
    i1a[i1a <= 20] = 0
    # RLE:
    result = rle_encode(i1a.tolist())
    #return json.dumps(i1a.tolist())
    return result


def imgad(base_image_filename, offset_image_filename, scale=1):
    i1 = PIL.Image.open(base_image_filename)
    i1 = apply_scale(i1, scale)
    i1a = np.array(i1)
    i2 = PIL.Image.open(offset_image_filename)
    i2 = apply_scale(i2, scale)
    i2a = np.array(i2)

    deltai = i1a ^ i2a

    return rle_encode(deltai.flatten().tolist())


def audioarray(audio_filename):
    result = []
    with wave.open(audio_filename) as f:
        audio_data = f.readframes(f.getnframes())
        result = list(audio_data)
    return result


def pack_csgson_codec(movie_set, source_set, scale=1):
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
                "width": int(426 * scale),
                "height": int(240 * scale),
                "depth": 3
            },
            # TODO: unroll this
            "audio": "unsigned-8bit-mono-8khz"
        },
    }

    # be naive about unpacked video (assume fetchcorpus.py ran)
    image_file = os.path.join("media", "img", source_set, "i001.png")
    packed["image"] = imga(image_file, scale)
    
    # naively pack all delta frames relative to the one before
    packed["deltas"] = []
    # figure out the last one for the loop, or just keep going until it doesn't exist
    delta_image_num = 2
    done = False
    # TODO: don't rely on fixed size image numbers eg i009.png
    while True:
        last_file = os.path.join("media", "img", source_set,
            "i%03d.png" % (delta_image_num - 1))
        delta_file = os.path.join("media", "img", source_set,
            "i%03d.png" % delta_image_num)
        if os.path.exists(delta_file):
            print("Delta:", last_file, delta_file)
            delta_image = imgad(last_file, delta_file, scale)
            packed["deltas"].append(delta_image)
            delta_image_num += 1
        else:
            break

    audio_file = os.path.join("media", "audio", "%s-8khz.wav" % source_set)
    packed["audio"] = audioarray(audio_file)

    # TODO: add a timedtext format
    packed["timedtext"] = []

    # TODO: add seekimages
    packed["seekimages"] = []

    print("pack_csgson_codec: writing", out_file)
    json.dump(packed, open(out_file, "w"))


# simplest possible boxart... first frame
def get_first_frame_boxart(movie_set):
    print("get_first_frame_boxart:", movie_set)
    out_dir = os.path.join("media", "encoded")
    # Consider using imga format, simplify for UI for now
    out_file = os.path.join(out_dir, movie_set + ".png")
    if os.path.exists(out_file):
        print("get_first_frame_boxart: file exists, skipping:", out_file)
        return
    image_file = os.path.join("media", "img", movie_set, "i001.png")
    shutil.copyfile(image_file, out_file)


def main():
    for scale in [1, 0.5]:
        for i in range(2, 7+1):
            source_set = "movie%d-%dp-0" % (i, 240)
            vertical = int(240 * scale)
            movie_set = "movie%d-%dp-0" % (i, vertical)
            pack_csgson_codec(movie_set, source_set, scale)
            if scale == 1:
                # only do the boxart if we're at original scale
                get_first_frame_boxart(movie_set)


if __name__ == "__main__":
    main()
