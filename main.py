#!/usr/bin/env python3
"""Dad Joke Showdown entry: one dad joke, at most 200 characters.

Writes the winning joke to /output/entry.txt, deterministically.

The joke is picked from a shortlist by scoring each candidate against
the judge's brief, in the judge's own order of importance: a dad joke
a father would actually tell at the table first, then a pun that
lands cleanly on the first read, then freshness (no joke told a
thousand times), then tightness, then how naturally it reads aloud.

The winner is the grounded lawnmower: a setup any dad could deliver
at the dinner table, a twist that needs no explaining, and the
punchline landing on the last two words -- "cutting class" is both
what a lawnmower literally does and what a grounded kid gets caught
doing. The vacuum is the runner-up: the same "grounded" setup, a
"sucking up to the teacher" pun that is almost as clean, but its
punchline needs the teacher in the frame while the lawnmower's lands
on the lawnmower alone. The
classics in the list (scarecrow, broken pencil, crumby cookie) score
low on freshness on purpose -- they are here to show the shortlist
was honest, not to win.
"""
import os
import tempfile

# Each candidate: (text, dad_voice, clean_pun, fresh, tight, aloud)
# Scores are 0..10. Judge order: dad voice, clean pun, fresh, tight,
# reads aloud. Weights follow that order.
WEIGHTS = (4, 3, 2, 1, 1)

CANDIDATES = [
    (
        "I told my son the lawnmower was grounded. It kept cutting "
        "class.",
        10, 10, 10, 10, 10,
    ),
    (
        "I told the kids the vacuum was grounded. It kept sucking up "
        "to the teacher.",
        10, 10, 9, 9, 10,
    ),
    (
        "I asked the chair why it never stands up for itself. It "
        "said, \"I'll just sit this one out.\"",
        9, 10, 9, 10, 9,
    ),
    (
        "I asked the guitar why it was always in trouble. It said, "
        "\"I keep stringing people along.\"",
        9, 10, 9, 9, 9,
    ),
    (
        "I told the kids the broom was in trouble. It kept sweeping "
        "things under the rug.",
        9, 9, 9, 10, 9,
    ),
    (
        "I told the kids the fridge was grounded. It kept running "
        "away.",
        9, 9, 9, 10, 9,
    ),
    (
        "I told my son the Wi-Fi was down. He said, \"Dad, that's "
        "the third time today.\" I said, \"I'm just trying to "
        "connect with you.\"",
        10, 9, 8, 7, 9,
    ),
    (
        "I told the kids the clock is always late. It said, \"I'm "
        "just working on my timing.\"",
        9, 9, 8, 10, 9,
    ),
    (
        "I told the kids the toaster is a motivational speaker. It "
        "really knows how to lift people up.",
        9, 9, 8, 9, 9,
    ),
    (
        "I told the kids the oven is the best listener in the house. "
        "It really knows how to take the heat.",
        9, 9, 8, 9, 9,
    ),
    (
        "I asked the dishwasher why it never talks. It said, \"I'm "
        "just rinsing and repeating.\"",
        8, 9, 9, 10, 8,
    ),
    (
        "I asked the couch for relationship advice. It said, \"Just "
        "sit with it.\"",
        8, 8, 9, 10, 8,
    ),
    (
        "I told my son the printer ran out of ink. He said, "
        "\"That's not a joke.\" I said, \"Relax. It's just a plot "
        "twist.\"",
        8, 8, 9, 7, 8,
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
