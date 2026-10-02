# Directory submissions

Portal: https://claude.ai/directory/manage (paid plan; GitHub connected on claude.ai with push access to brianshepardpss repos).
Limit: 10 submissions per organization per 24 hours. Each plugin is the root of its own repo: Plugin path empty, branch empty (main).
Every submission: Plugin bundle -> Source -> Validate -> Listing details (from plugin.json + README) -> Data handling -> Compliance (contact brian@press-start-studios.com; the four acknowledgements are the owner's to accept) -> Review and submit (GitHub push webhook, auto-publish on).

Expected holds (not rejections): generic-word names (plugin-creator, helpdesk, plugin-studio) may be 'Name may be confused'; 'Merge Medic for GitLab' may be 'Name matches a known brand'.

## Day 1 (2026-10-02)

### grounded-scala
- Repository: brianshepardpss/grounded-scala
- Reads or stores personal data: No.
- Sends data to services other than declared connectors: No (build tools fetch libraries from Maven repositories as usual).
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### merge-medic
- Repository: brianshepardpss/merge-medic
- Reads or stores personal data: No.
- Sends data to services other than declared connectors: Only to the user's own GitLab instance via the glab CLI with their token; disclosed in README.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### plugin-creator
- Repository: brianshepardpss/plugin-creator-plugin
- Reads or stores personal data: No.
- Sends data to services other than declared connectors: Yes: search terms only, to GitHub API, Hacker News Algolia API, Smithery registry, npm registry and raw.githubusercontent.com; disclosed in README.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### listing-desk
- Repository: brianshepardpss/listing-desk
- Reads or stores personal data: Yes: client contact lists and contract parties from the user's files; not stored beyond the user's own files.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### helpdesk
- Repository: brianshepardpss/helpdesk
- Reads or stores personal data: Yes: support tickets can contain customer names, emails and payment details; card numbers and SSNs are redacted in output; nothing is stored by the plugin.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### structured-hiring
- Repository: brianshepardpss/structured-hiring
- Reads or stores personal data: Yes: candidate scorecards and contact details from the user's ATS or pastes; minimized, never stored except an ids-only ATS action log.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### deal-tender
- Repository: brianshepardpss/deal-tender
- Reads or stores personal data: Yes: CRM contacts and deal notes from the user's Pipedrive or CSV export; not stored beyond the user's own files.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### construction-pm
- Repository: brianshepardpss/construction-pm
- Reads or stores personal data: Minimal: names of project contacts in notes and logs; not stored beyond the user's own files.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### make-my-plugin
- Repository: brianshepardpss/make-my-plugin
- Reads or stores personal data: Possibly: the user's own example documents; the interview asks them to remove private details; stays in their account.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### plugin-studio
- Repository: brianshepardpss/plugin-studio
- Reads or stores personal data: No.
- Sends data to services other than declared connectors: Yes: the user's own repo names to the GitHub API via gh, and idea terms to the same public APIs as plugin-creator; disclosed in README.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

## Day 2 (after 24 h; repos must exist first)

### analyzer-loop
- Repository: brianshepardpss/analyzer-loop
- Reads or stores personal data: No.
- Sends data to services other than declared connectors: No (pub.dev via the user's own flutter/dart commands).
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### restaurant-ops
- Repository: brianshepardpss/restaurant-ops
- Reads or stores personal data: Yes, minimal: staff names and availability for schedule drafts; not stored beyond the user's own files.
- Sends data to services other than declared connectors: No.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted

### grant-desk
- Repository: brianshepardpss/grant-desk
- Reads or stores personal data: Yes: donor names and gift amounts from the user's CSV; processed locally, never sent to any external service.
- Sends data to services other than declared connectors: Yes: EINs, keywords and state codes (no personal data) to ProPublica Nonprofit Explorer API, GivingTuesday 990 Data Lake (S3) and Grants.gov API; disclosed in README.
- Data retention: none by the plugin; files the user asks for stay in their own folder.
- Intended for people under 18: No.
- Status: not submitted
