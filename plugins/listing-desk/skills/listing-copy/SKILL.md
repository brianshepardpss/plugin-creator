---
name: listing-copy
description: Use when an agent needs marketing copy for a property, or says "write the listing description", "MLS remarks", "public remarks", "write a just listed post", "Instagram caption for my listing", "flyer text", "open house post", "rewrite my listing description", or "make this description better" (rewriting or writing new copy, not just checking it). Writes MLS public remarks within the character cap, feature bullets, social posts, flyer text and just-listed emails from the property facts only, then runs the Fair Housing checker on every piece before showing it.
---

# Listing copy that describes the property, not the people

## 1. Facts first

Collect the facts you are allowed to use: the subject file, the agent's notes,
the MLS row, photos the user describes. Make a short list of features
(rooms, finishes, upgrades with years, lot, garage, outdoor space,
accessibility features, HOA amenities). Copy may only contain items on that
list. If a selling point is not in the facts, ask; do not invent it.

Drop these even if the seller or agent said them (and tell the agent why):

- Who should live there: families, kids, couples, singles, retirees,
  professionals, "young", "mature", a religion, a nationality.
- Neighborhood judgments: safe, low crime, good/bad area, up-and-coming,
  exclusive, quiet *neighborhood* (quiet *street* or *cul-de-sac* is a
  property fact).
- School quality: "great schools", "top-rated district". Allowed: the factual
  district name with "buyer to verify", e.g. "Zoned to Cedar Hollow ISD
  (buyer to verify)".
- Houses of worship as selling points, and saint-named landmarks.
- 55+ / senior language unless the user confirms the community is
  HOPA-qualified housing for older persons.
- In MLS remarks only: any buyer-agent compensation or bonus, phone numbers,
  emails, web links, showing instructions, and the agent's name.

Use "primary bedroom/suite", not "master". Walking distance to a named park,
trail or shopping center is fine.

## 2. Write each piece

**MLS public remarks** (`remarks.txt`): plain text, no emoji, no ALL CAPS
words beyond one, no line breaks unless the agent's MLS allows them. Lead
with the strongest 2-3 features, then layout, then upgrades with years, then
outside. Stay at or under the cap (default 1,000 characters; ask the agent
for their MLS limit). The checker reports the exact count.

**Feature bullets** (optional, for the flyer): 6-10 bullets, one fact each.

**Social posts** (`social.md`): three posts, each with a 1-line hook,
3-5 lines of features, `[LIST PRICE]` and address placeholder if not
confirmed, a call to action ("Message me for a private showing"), and at most
5 hashtags (no demographic or school hashtags). Variants: (1) feed post,
(2) short story/reel caption under 150 characters, (3) "coming soon" or
"open house" version. Include the Equal Housing Opportunity statement or
logo note the agent's brokerage requires.

**Just-listed email** (`email.md`): subject line under 60 characters,
preview text, 80-150 word body, one link placeholder `[LISTING LINK]`, agent
signature placeholder, brokerage name placeholder, and an unsubscribe line
("Reply UNSUBSCRIBE to stop these emails"). It is a draft; do not send it.

## 3. Check every piece (not optional)

Run the checker on all files at once. Paths are relative to this skill's
base directory:

```
python3 <base>/../fair-housing-check/fair_housing.py --remarks remarks.txt \
  social.md email.md --cap <cap> --out fair_housing_report.md
```

- FLAG: rewrite, save, re-run until zero FLAGs.
- REVIEW: fix, or keep with a one-line reason.
- Then apply the context review in `../fair-housing-check/SKILL.md` step 3.
- Remarks over the cap: cut and re-run. Report the final count from the
  checker, not your own estimate.

## 4. Reply

```
**MLS public remarks** (<chars>/<cap> characters, from the checker)
<text>

**Social posts**
1. <post>
2. <post>
3. <post>

**Just-listed email**
Subject: <subject>
<body>

**Fair Housing check:** <PASS/REVIEW>; fixed: <phrase -> rewrite>; left out
from your notes: <phrase - reason>.
```

If the user pastes their own draft and asks to "make it better", keep their
facts, apply the same rules, run the checker, and show what changed.
