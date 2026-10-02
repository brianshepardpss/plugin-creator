---
name: fair-housing-check
description: Use when an agent asks whether real estate wording is OK, or says "is this Fair Housing compliant", "check my listing description", "can I say safe neighborhood", "review this ad", "scan these remarks", or pastes listing, social or email copy to check. Also use when a buyer or agent asks which neighborhoods, areas or schools are best or safest for clients described by race, ethnicity, religion, national origin, family status, disability or age, or asks for crime or demographic info about an area. Runs a deterministic phrase checker plus a context review; flags phrase, protected class and reason, and offers a compliant rewrite.
---

# Fair Housing check

The Fair Housing Act (42 USC 3604(c)) makes discriminatory advertising
unlawful regardless of intent; states and cities add protected classes
(source of income, age, sexual orientation, gender identity, military
status and more). This skill checks wording. It is not legal advice; the
agent's broker has the final say.

## A. Checking text

1. Save the text to a file (or use `--text` for one short passage). If it is
   MLS public remarks, pass it with `--remarks` so the MLS rules (no
   buyer-agent compensation, no contact info, character cap) also apply.
   Paths are relative to this skill's base directory:

   ```
   python3 <base>/fair_housing.py --remarks remarks.txt other.md --cap 1000
   python3 <base>/fair_housing.py --text "<pasted text>"
   ```

2. Report every hit from the script: level (FLAG / REVIEW / NOTE), the exact
   phrase, protected class or rule, the reason, and a rewrite that keeps the
   seller's real selling point as a property fact.
3. Context review (the script cannot see these). Read the text once more for:
   - Any description of who would or should live there, in any wording
     ("ideal for a growing household", "great first home for newlyweds").
   - Neighborhood character or safety implied without the listed words
     ("you'll feel secure walking at night").
   - Schools described by quality or reputation, not just by district name.
   - Proximity lists that only name houses of worship or ethnic businesses.
   - Accessibility: describing features is good ("zero-step entry");
     describing who can't live there is not.
   - 55+ language: OK only if the user confirms HOPA-qualified housing.
   Things that are fine and must not be flagged: "family room",
   "single-family", "walk-in closet", "walking distance to <park/shops>",
   "quiet street", "cul-de-sac", "near the town square", "wheelchair-
   accessible entry", "primary suite".
4. Give the result in this shape:

   ```
   **Fair Housing check: <FLAG / REVIEW / PASS>**

   | Level | Phrase | Class / rule | Why | Rewrite |
   | FLAG | "perfect for young families" | familial status | ... | "four bedrooms plus a bonus room" |

   Context review: <what you found beyond the phrase list, or "nothing further">

   Compliant version:
   <full rewritten text, re-checked with the script>
   ```

   Re-run the script on your rewrite and show it passes (zero FLAG).

## B. Steering requests (buyers, neighborhoods, schools, crime)

When asked to recommend areas or schools based on who the clients are
(race, ethnicity, religion, national origin, children, disability, age), or
which areas are "safe", "good" or "where people like them live":

1. Do not name, rank or describe neighborhoods by demographics, crime,
   safety, or school quality, and do not guess who lives where. Say briefly
   that matching areas to a client's protected characteristics is steering
   under the Fair Housing Act, and that the agent can't do it either.
2. Offer what you can do: a criteria-based search the clients define
   themselves -- price range, beds/baths, sqft, lot, commute time to a named
   workplace, HOA or no HOA, specific amenities (park, transit, pool).
   Ask for those criteria.
3. For schools: point the clients to official sources to evaluate
   themselves -- the school district's own attendance-zone lookup and the
   state education agency's school report cards -- and to visiting schools.
   Do not summarize ratings.
4. For safety: the clients can consult the local police department's
   published data and visit at different times of day. Do not characterize
   any area.
5. Never use or suggest crime, demographic or "neighborhood quality" data
   tools for buyer recommendations.

## C. Phrase list

`phrases.json` holds the patterns, levels, classes, reasons and rewrites.
Agents can add their state's classes or their MLS's rules as new entries
(same fields). Read it only if the user asks why something was or was not
flagged.
