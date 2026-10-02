---
name: share-my-plugin
description: Use only when the user asks to share, publish or give away their custom plugin, or says "could this help other people", "share my plugin", "submit this", or "make a public version". Prepares a generalized, anonymized public version and a submission the user sends themselves. Never shares anything automatically.
---

# Prepare a public version the user chooses to share

Sharing is optional and the user's call. Nothing in this skill sends data.

1. Make a copy named `<name>-public/`. Never modify their private plugin.
2. Generalize it:
   - Replace business names, people, places, prices, account numbers and
     anything identifying with neutral placeholders (`<your business>`).
   - Replace their real examples with invented ones in the same style.
   - Keep their method, structure, rules and quality bar; that is the value.
3. Show the user every file of the public copy and ask them to confirm
   nothing private remains. Wait for an explicit yes.
4. Package it with the build-my-plugin skill's `package.py`.
5. Give them two ways to submit to the Plugin Creator community collection:
   - A prefilled GitHub issue they open themselves:
     `https://github.com/brianshepardpss/make-my-plugin/issues/new?labels=community-plugin&title=<URL-encoded "Community plugin: <name>">&body=<URL-encoded: what it does, who it is for, their credit name if they want one>`,
     then attach the `.plugin` file to the issue.
   - Or email the file to brian@press-start-studios.com with the same text.
6. Say what happens next: submissions are reviewed by a person, credited as
   the user asks, and published under the MIT license only with their
   agreement.
