#!/usr/bin/env python3
"""Flag lines that MAY describe a notice or claim event. Standard library only.

Usage: python3 notice_flags.py FILE [FILE ...]      (or pipe text on stdin)

This is a keyword screen, not a legal determination. It finds language that
often accompanies events with contractual notice requirements (differing or
concealed conditions, delays and lost time, owner or architect directives,
added scope, stop-work, weather impacts, incidents) so a person can check
their own contract. It never says whether notice is required or when.
"""
import re
import sys

RULES = [
    ("Differing / concealed condition",
     r"not on (the )?(drawings|plans)|unforeseen|unknown|concealed|abandoned|unexpected|differing|"
     r"didn'?t show|not shown|hit (an?|the) "),
    ("Delay / lost time / disruption",
     r"\bdelay|lost (time|day|hours?)|\blost maybe|stand ?by|idle|waiting on|stopped (work|on|that|the|all)|can'?t proceed|"
     r"moved to the other|out of sequence|re-?sequenc|pushed (back|out)|slip"),
    ("Owner / architect directive or added scope",
     r"owner (wants|asked|directed|requested)|want(s)? to add|\badd (a|an|the)\b|extra work|"
     r"verbal(ly)? (direction|approv)|directed (us|to)|change (it|order|directive)|can you price|"
     r"in writing|field (direction|directive)"),
    ("Stop work / suspension", r"stop(ped)? work|suspend|shut ?down|red[- ]tag"),
    ("Weather impact", r"\brain(ed|ing)?\b.*(stop|lost|delay|couldn'?t)|weather (day|delay)|high winds?|"
     r"(stop|lost|delay|couldn'?t).*\brain"),
    ("Safety incident (also follow your safety program)",
     r"(?<!no )injur|near miss|first aid|incident|osha|recordable"),
]

FOOTER = ("Possible notice/claim event(s) found. This is a keyword screen, not legal advice. "
          "Check the notice and claim provisions of YOUR contract today (time limits can be short) "
          "and talk to your PM or counsel before relying on any deadline.")


def scan(name, text):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for label, pat in RULES:
            if re.search(pat, line, re.I):
                hits.append((name, n, label, line.strip()))
    return hits


def main():
    srcs = [(f, open(f, errors="replace").read()) for f in sys.argv[1:]] or [("stdin", sys.stdin.read())]
    hits = [h for name, t in srcs for h in scan(name, t)]
    if not hits:
        print("No notice-type language found by the keyword screen. That does not mean none exists; "
              "read the notes yourself.")
        return
    print("| Where | Possible event type | Text |")
    print("|---|---|---|")
    for name, n, label, line in hits:
        print(f"| {name}:{n} | {label} | {line[:160]} |")
    print("\n" + FOOTER)


if __name__ == "__main__":
    main()
