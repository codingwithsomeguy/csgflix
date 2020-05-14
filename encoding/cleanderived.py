import shutil

from config import *


def clean_derived():
    """delete the derived files, leave the original movies"""
    # TODO: add ENCODED_DIR to config.py
    paths = [CLIP_DIR, IMG_DIR, RAW_AUDIO_DIR, AUDIO_DIR, ENCODE_DIR]
    for derived_path in paths:
        print("Deleting:", derived_path)
        shutil.rmtree(derived_path, ignore_errors=True)


if __name__ == "__main__":
    clean_derived()
