# TODO: Cleanup the hackery

import os
from glob import glob
from urllib.request import urlretrieve

from config import *


def make_short_videos():
    os.makedirs(CLIP_DIR, exist_ok=True)
    for filename in glob(os.path.join(DEST_DIR, "*.mp4")):
        file_part = os.path.splitext(os.path.split(filename)[-1])[0]
        clip_filename = os.path.join(CLIP_DIR, file_part + "-240p-0.mp4")
        if os.path.exists(clip_filename) == False:
            cmd = "ffmpeg -y -i '%s' -t %d -s 426x240 '%s'" % (
                filename, CLIP_LENGTH, clip_filename)
            print(cmd)
            os.system(cmd)
        else:
            print("File %s exists, skipping" % clip_filename)


def extract_images_from_videos():
    os.makedirs(IMG_DIR, exist_ok=True)
    for filename in glob(os.path.join(CLIP_DIR, "*.mp4")):
        file_part = os.path.splitext(os.path.split(filename)[-1])[0]
        out_dir = os.path.join(IMG_DIR, file_part)

        if os.path.exists(out_dir) == False:
            os.makedirs(out_dir, exist_ok=True)
            cmd = "ffmpeg -i '%s' -vsync 0 '%s/i%%3d.png'" % (filename, out_dir)
            print(cmd)
            os.system(cmd)
        else:
            print("Dir %s exists, skipping" % out_dir)


def extract_audio_from_video():
    os.makedirs(RAW_AUDIO_DIR, exist_ok=True)
    for filename in glob(os.path.join(CLIP_DIR, "*.mp4")):
        file_part = os.path.splitext(os.path.split(filename)[-1])[0]
        aac_filename = os.path.join(RAW_AUDIO_DIR, file_part + ".aac")
        wav_filename = os.path.join(RAW_AUDIO_DIR, file_part + ".wav")
        if os.path.exists(aac_filename) == False:
            cmd = "ffmpeg -i '%s' -vsync 0 -vn -acodec copy '%s'" % (filename, aac_filename)
            print(cmd)
            os.system(cmd)

            cmd2 = "faad -o '%s' '%s'" % (wav_filename, aac_filename)
            print(cmd2)
            os.system(cmd2)
        else:
            print("Dir %s exists, skipping" % aac_filename)


def transcode_audio_to_lowquality():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    for filename in glob(os.path.join(RAW_AUDIO_DIR, "*.wav")):
        file_part = os.path.splitext(os.path.split(filename)[-1])[0]
        lowquality_filename = os.path.join(AUDIO_DIR, file_part + "-8khz.wav")
        if os.path.exists(lowquality_filename) == False:
            cmd = "sox '%s' -b 8 -c 1 -r 8000 '%s'" % (filename, lowquality_filename)
            print(cmd)
            os.system(cmd)
        else:
            print("File %s exists, skipping" % lowquality_filename)


def fetchcorpus():
    os.makedirs(DEST_DIR, exist_ok=True)
    for i in range(2, 7 + 1):
        filename = "movie%d.mp4" % i
        url = "%s/%s" % (BASE_URL, filename)
        full_filename = os.path.join(DEST_DIR, filename)
        if os.path.exists(full_filename) == False:
            print("Fetching %s to %s" % (url, full_filename))
            urlretrieve(url, filename=full_filename)
        else:
            print("File %s exists, skipping" % full_filename)

    # also get the metadata / catalog.json
    url = "%s/catalog.json" % BASE_URL
    full_filename = os.path.join(DEST_DIR, "catalog.json")
    if os.path.exists(full_filename) == False:
        print("Fetching %s to %s" % (url, full_filename))
        urlretrieve(url, filename=full_filename)
    else:
        print("File %s exists, skipping" % full_filename)


def main():
    fetchcorpus()
    make_short_videos()
    extract_images_from_videos()
    extract_audio_from_video()
    transcode_audio_to_lowquality()


if __name__ == "__main__":
    # TODO: test these are there
    # depends on ffmpeg (mp4 / image unpacking), faad (aac --> wav),
    #   sox (wav --> 8khz resampling)
    main()
