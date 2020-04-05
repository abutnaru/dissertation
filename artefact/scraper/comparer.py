#!/usr/bin/env -S conda run -n dissertation python
"""
This is for experimentation purposes
"""
from PIL import Image


def is_special_case(subjectImage):
    cases = {
        "malicious": "cases/malicious.png",
        "not_found": "cases/not_found.png",
        "not_reachable": "cases/not_reachable.png",
        "not_reachable_2": "cases/not_reachable_2.png",
        "blocked": "cases/blocked.png",
        "webhost_sleeping": "cases/sleeping.png",
    }
    identities = []
    for case in cases:
        i1 = Image.open(cases[case])
        i2 = Image.open(subjectImage)
        assert i1.mode == i2.mode, "Different kinds of images."
        assert i1.size == i2.size, "Different sizes."
        pairs = zip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
            # For grayscale
            dif = sum(abs(p1 - p2) for p1, p2 in pairs)
        else:
            dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

        ncomponents = i1.size[0] * i1.size[1] * 3
        dif_percentage = (dif / 255.0 * 100) / ncomponents
        if dif_percentage < 1:
            identities.append((case, dif_percentage))
    if len(identities) == 0:
        return False

    min_diff = 100
    min_case = ""
    for result in identities:
        case, percentage = result
        if percentage < min_diff:
            min_diff = percentage
            min_case = case
    return (min_case, min_diff)


print(
    is_special_case(
        "chrome/http:____www.onkoma.jp__read-invoice__index.php?rec=Scotiabank.SAC@scotiabank.com.pe.png"
    )
)
