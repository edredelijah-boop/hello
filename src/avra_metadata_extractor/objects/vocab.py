"""Open-vocabulary class list for the YOLOE object index.

Fixed vocabulary used for the scored AVRA submission. Chosen from the kinds of
objects KilometerAudio questions ask about and pruned to classes that YOLOE
detects reliably on real walking-tour frames. Written to
``data/object_classes.txt`` (``<index><TAB><name>``) so a consumer can read the
vocabulary rather than hard-code it.
"""

CLASSES = [
    # people & animals
    "person",
    "dog",
    "cat",
    "bird",
    "duck",
    "horse",
    # vehicles (road)
    "car",
    "bus",
    "truck",
    "bicycle",
    "motorcycle",
    "ambulance",
    "fire engine",
    "garbage truck",
    "police car",
    "taxi",
    # vehicles (rail / water)
    "train",               # also covers tram — decomposer maps tram -> train
    "boat",
    "ferry",
    "cruise ship",
    # street furniture & fixtures
    "bench",
    "umbrella",
    "flag",
    "ladder",
    "tent",
    "awning",
    "traffic light",
    "fire hydrant",
    "trash can",
    "clock",
    "clock tower",
    "bell",
    "statue",
    # rolling objects
    "suitcase",
    "baby stroller",
    "skateboard",
    "shopping cart",
    "wheelchair",
    # sports & misc
    "basketball",
    "ball",
    "ferris wheel",
    "forklift",
    "broom",
    "horse carriage",
    "guitar",
    "drum",
    "television",
    "bottle",
    # validated CLIP-transfer classes
    "fountain",
    "crane",
    "leaf blower",
]

if __name__ == "__main__":
    print(f"Total vocabulary: {len(CLASSES)}")
    assert len(CLASSES) == len(set(CLASSES)), "duplicate class names!"
