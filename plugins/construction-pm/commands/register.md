---
description: Build a cited submittal register from spec sections (try "/register sample")
argument-hint: "[sample | spec files or folder] [schedule.csv]"
---

Use the submittal-register skill to build a submittal register from: $ARGUMENTS

If the argument is "sample" or empty, run it on the plugin's bundled sample
spec sections and schedule, with today's date as the as-of date, and write
submittals.csv to the working folder.
