#!/usr/bin/env python3
"""Dad Joke Showdown entry: one dad joke, at most 200 characters.

Writes the winning joke to /output/entry.txt, deterministically.

The joke is picked from a shortlist by scoring each candidate against
the judge's brief, in the judge's own order of importance: a dad joke
a father would actually tell at the table first, then a pun that
lands cleanly on the first read, then freshness (no joke told a
thousand times), then tightness, then how naturally it reads aloud.

The winner is the dog named Stay: a setup any dad could deliver, a
twist that needs no explaining, a punchline that lands on the last
line, and a joke I have never heard told anywhere else. The gravy
line is the runner-up: same dinner-table setting, a fresh pun on
"thicken the plot". The classics in the list (scarecrow, coffee
mugged, pencil pointless, cookie crumby) score low on freshness on
purpose -- they are here to show the shortlist was honest, not to win.
"""
import os
import tempfile

# Each candidate: (text, dad_voice, clean_pun, fresh, tight, aloud)
# Scores are 0..10. Judge order: dad voice, clean pun, fresh, tight,
# reads aloud. Weights follow that order.
WEIGHTS = (4, 3, 2, 1, 1)

CANDIDATES = [
    (
        "I named my dog Stay. Now when I call him, he just stands "
        "there. Best training I ever did.",
        10, 10, 9, 9, 10,
    ),
    (
        "I told the kids the gravy was in charge of dinner. It really "
        "knows how to thicken the plot.",
        10, 9, 9, 9, 9,
    ),
    (
        "My son asked why I put the car in the oven. I said I wanted "
        "a hot rod.",
        9, 10, 8, 10, 9,
    ),
    (
        "I put my savings in the blender. Now my assets are liquid.",
        8, 9, 9, 10, 8,
    ),
    (
        "I tried to start a band called 1023MB. We never got a gig.",
        7, 9, 9, 10, 5,
    ),
    (
        "I told my wife I was going to make a belt out of watches. "
        "She said it would be a waist of time.",
        9, 8, 4, 9, 9,
    ),
    (
        "I asked the calendar for a day off. It said, \"Sorry, I'm "
        "booked.\"",
        9, 8, 7, 10, 9,
    ),
    (
        "I told my son the sandwich was in charge now. He said, "
        "\"Why?\" I said, \"Because I'm the breadwinner.\"",
        9, 8, 6, 8, 9,
    ),
    (
        "Why did the scarecrow win an award? He was outstanding in "
        "his field.",
        10, 10, 1, 9, 10,
    ),
    (
        "I tried to make a joke about a broken pencil. Turns out it's "
        "pointless.",
        9, 9, 2, 10, 9,
    ),
    (
        "Why did the cookie go to the doctor? It was feeling crumby.",
        9, 9, 2, 10, 9,
    ),
]


def total(candidate):
    text, dad, pun, fresh, tight, aloud = candidate
    return (
        dad * WEIGHTS[0]
        + pun * WEIGHTS[1]
        + fresh * WEIGHTS[2]
        + tight * WEIGHTS[3]
        + aloud * WEIGHTS[4]
    )


def choose():
    winner = None
    best = -1
    for candidate in CANDIDATES:
        text = candidate[0]
        if len(text) > 200 or "\n" in text or not text.strip():
            continue
        points = total(candidate)
        # On a tie the shorter joke wins: tighter is better.
        if points > best or (points == best and len(text) < len(winner)):
            best = points
            winner = text
    return winner


def main():
    joke = choose()
    # Gate, mirroring the sealed scorer: 1-200 chars, one line,
    # never only whitespace. Fail loudly instead of shipping an
    # entry the gate would refuse.
    assert joke is not None, "no candidate passed the gate"
    assert 1 <= len(joke) <= 200, "joke is %d chars" % len(joke)
    assert "\n" not in joke and joke.strip() == joke
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(joke)
        os.replace(tmp, target)
        os.chmod(target, 0o644)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    main()
