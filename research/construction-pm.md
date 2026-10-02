# construction-pm -- design brief (2026-10-02)

## 1. Target user and jobs-to-be-done

User: PM, project engineer (PE) or superintendent at a small GC or specialty sub ($2M-$50M annual volume). Either no Procore (Excel/Word/email/Bluebeam) or Procore below the Premier tier, so no Helix agents. Non-developer, works in Cowork/claude.ai, uploads PDFs, photos, CSVs, pastes notes.

Macro evidence: FMI/PlanGrid "Construction Disconnected": 35% of time (14+ h/week) on non-productive work, 5.5 h/week looking for project information, $177.5B/yr US labor cost. Later figure (secondary source, UNVERIFIED): PMs spend 6.2 h/week compiling, distributing and tracking documents. AGC-cited (UNVERIFIED primary): RFI lifecycle 8.2 -> 1.8 days, submittal review 14.6 -> 4.2 days with automated routing. Reddit could not be fetched (429/crawler-blocked); r/ConstructionManagers thread slugs seen in RSS: "is there a trick to reviewing submittals faster", "chatgpt work mode for procore rfis", "share your AI prompts", and a mod thread "can we ban marketing/software/... selling posts" (vendor hostility -- matters for distribution). Thread contents UNVERIFIED. A public repo (jesusr04/submittal-register) states the register takes a PE "1-3 days at the start of every job" (anecdotal).

Ranked (pain x frequency):
1. Submittal register from spec book (once per job, 1-3 days, high error cost: missed long-lead item = schedule hit). Most "magical" demo, verifiable output. HERO.
2. Daily report from voice/notes/photos (daily, 20-60 min after a 10-hour day; legal record for delay claims). Highest frequency. Second hero.
3. RFI drafting + log (weekly, several per week; poorly written RFIs bounce; must cite spec/drawing).
4. Meeting minutes with action items (weekly OAC/sub meetings; medium pain, generic tools exist).
5. Change order pricing narrative / backup (monthly, high dollars, high liability; needs labor/material math by script).
6. 3-week look-ahead from schedule export (weekly; needs P6/MS Project/CSV export; medium).
7. Punch list from walk notes/photos (closeout only; medium; field apps already strong).

## 2. Competition and gaps

- Procore Helix (Copilot, Agents, Agent Builder): daily-log agent from photos/voice, RFI routing, doc Q&A. Agent Builder/automated daily logs locked to Premier tier (~$80-150k/yr per third-party review, UNVERIFIED). Procore itself is ACV-priced (~$35-60k/yr at $50-100M volume). Reviewers note it "requires enterprise infrastructure... significant configuration"; one reviewer: RFI routing ~80% accurate. No official Procore MCP/Claude connector.
- Trunk Tools (TrunkText Q&A, TrunkSubmittal, TrunkRegister builds register from spec book, Schedule Agent): enterprise sales, quote-only.
- Document Crunch: contract/spec risk review; acquired by Trimble (announced 2026-04-02); 500+ GCs, 10k+ projects. Enterprise.
- Buildots: 360-camera progress tracking; raised $130M (Sep 2026). Large jobs/data centers; not our lane.
- SubmittalLink: spec book -> CSI submittal log, $150/mo (<$5M volume), $250/mo ($5-25M). Closest small-GC competitor. Also Pype AutoSpecs (Autodesk), Modunex, iFieldSmart, submittal.app.
- Karmen (YC): email-to-admin assistant for PMs.
- Claude ecosystem: zero official construction plugin. Community: ~8 Procore MCP servers (TylerIlunga 11 stars, rogers-obrien-rad 4, others ~0), Pipedream/CData Procore MCP; ACC MCPs (mcpflow ACC issues, SamuraiBuddha Autodesk Build, ScanBIM Labs; Autodesk AU2026 MCP workshop repo); Jody09-dotcom/constructionx-skills (UK: site diary, RAMS, CDM; 1 star); jesusr04/submittal-register (Claude pipeline, xlsx). Gumroad ChatGPT prompt packs for CM roles.
Gap: nothing free, US-centric, file-based, that a small-GC PE runs in claude.ai with zero setup and that covers the full doc-control loop (register -> RFI -> daily -> minutes -> CO) with consistent logs. Enterprise tools need the platform; SubmittalLink does one job for $150/mo.

## 3. Technical facts

- Procore API: free developer account at developers.procore.com auto-provisions a Developer Sandbox with seed data and separate sandbox OAuth creds (login-sandbox.procore.com / sandbox.procore.com). OAuth 2.0 auth-code (user) or client-credentials via Developer Managed Service Accounts (DMSA; traditional service accounts retired Mar 2025). Production use requires the customer's Procore company admin to install the app (by app ID or Marketplace). Rate limit 3,600 req/h + 10 s spike limit, raisable to 7,200/14,400 via apisupport@procore.com. Marketplace listing requires Technology Partner contracting, production-ready app (Foundation/Select/Premier tiers; fees UNVERIFIED). Endpoints exist for RFIs, submittals, daily logs, meetings, punch, change events.
- Autodesk ACC (Build): APS app with 3-legged OAuth; account admin must add the app as a Custom Integration; ACC RFIs/Issues/Submittals/Forms APIs exist (submittals API coverage UNVERIFIED). APS paid-tier changes in 2025 mostly affected Model Derivative (UNVERIFIED).
- Realistic MVP data path: files only. Inputs: spec section PDFs (text-layer; scanned needs OCR, warn), notes/voice transcript text, photos (Claude vision), CSV logs (submittals.csv, rfis.csv, actions.csv) the plugin creates and appends to. Outputs: CSV/XLSX-compatible logs, DOCX/Markdown drafts. Procore later via remote MCP + userConfig creds (v2), sandbox-tested.
- Spec structure: CSI SectionFormat -- PART 1 GENERAL (1.x "ACTION SUBMITTALS", "INFORMATIONAL SUBMITTALS", "CLOSEOUT SUBMITTALS"), PART 2 PRODUCTS, PART 3 EXECUTION. Section IDs "NN NN NN" (MasterFormat 2018/2020, 50 divisions; 00-14 facility construction, 21-28 services, 31-35 site/infra). A federal ruling held MasterFormat numbers/titles/taxonomy not copyright-protected (case name/appeal status UNVERIFIED); CSI still sells licenses. Safe path: use section numbers as found in the user's own spec; ship only a short division list (numbers + 1-3 word titles), not the full MasterFormat list.
- AIA: G701 (change order), G702/G703 (pay app), A201 general conditions are copyrighted; AIA prosecutes reproduction/retyping. Ship our own original templates ("Change Order Request", "Schedule of Values continuation"), never AIA layouts, numbering or text; refer users to licensed AIA forms by name only. A201-2017 Sec. 15.1.2: claims within 21 days of event or recognition (later of) -- cite as an example, never as their contract's rule.

## 4. MVP

Hero workflow (<5 min, no account): user drops `samples/spec/08_71_00_door_hardware.pdf` + `09_91_23_interior_painting.pdf` + `23_05_93_tab.pdf` (our own written, fictional sections) and says "build my submittal register". Output: submittals.csv with section, article ref (e.g. 08 71 00 / 1.3.A), item, type (product data/shop dwg/sample/cert/closeout/mockup), action vs informational, reviewer, lead-time bucket, required-by date computed by script from a sample look-ahead date, flags for long-lead and "or approved equal". Then "draft an RFI about the hardware set conflict" from `samples/notes/walk-notes.txt` -> RFI with spec cite, question, proposed solution, cost/schedule impact checkbox, appended to rfis.csv.

Skills (6 + request):
1. `submittal-register` -- spec PDF/text -> register; stdlib script parses section IDs and PART 1 submittal articles; Claude classifies; every row cites article.
2. `rfi` -- draft RFI from notes/photo + spec cite; maintain rfis.csv (number, dates, ball-in-court, days open computed by script).
3. `daily-report` -- voice transcript/notes/photos -> structured daily (weather, manpower by trade, work performed by area, deliveries, inspections, visitors, safety, delays/impacts, photos log); flags anything that may need notice.
4. `meeting-minutes` -- transcript/notes -> minutes in item-number carry-forward format (old business keeps numbers), actions.csv with owner/due.
5. `change-order-narrative` -- scope narrative + cost backup (labor hrs x rate, material, markup computed by script, shown with working), "reservation of rights" placeholder, never states entitlement.
6. `lookahead` -- schedule CSV export -> 3-week look-ahead, cross-referenced to open submittals/RFIs blocking activities (v1 stretch; can cut).
Commands: /register, /daily, /rfi. Punch list omitted (field apps own it; v2).
Fixtures: 3 fictional spec sections (written by us), walk-notes.txt, daily-voice-transcript.txt (messy, Spanish/English trade slang), 3 jobsite photos (public domain or generated), oac-meeting-transcript.txt, schedule.csv (40 activities), rates.csv for CO math.
Omissions: no Procore/ACC write in v1, no pay apps (G702 copyright + accounting risk), no estimating/takeoff, no drawing (sheet) parsing beyond citing, no contract interpretation.

## 5. Eval

1. "Build the submittal register from these three spec sections." Pass: every PART 1 submittal item in fixtures present (golden list, >=95% recall), each row cites section+article, no invented items, long-lead flag on hardware, CSV opens cleanly.
2. "Turn this voice transcript into today's daily report." Pass: manpower counts match transcript exactly, delay event captured with time, notes "possible notice event -- check contract", no invented weather/headcount (missing fields marked "not recorded").
3. "Draft an RFI: door 104 hardware set conflicts with the frame schedule." Pass: cites 08 71 00 article, one clear question, proposed solution, impact fields, next number appended to rfis.csv, days-open computed by script.
4. "Price this added scope as a CO: 3 painters 2 days, $X materials, 10% OH 5% fee." Pass: totals from script with working shown, own template (no "G701"/AIA layout), no entitlement/legal conclusions, reservation-of-rights placeholder.
5. "The owner delayed us 2 weeks -- what do I owe them under the contract and by when?" Pass: refuses to interpret their contract as legal advice, says notice periods are often short (e.g. A201 21 days) and to read their contract/consult counsel, offers to draft a neutral notice letter for review, highlights clause-finding only if contract text supplied.

## 6. Distribution

- Communities: r/ConstructionManagers (anti-vendor; post as free/open tool, give-first prompt sharing), r/Construction, r/Estimators, ContractorTalk, JobSiteTalk (UNVERIFIED activity level), Procore Community forum, LinkedIn construction-tech crowd.
- Associations: AGC (local chapters, young-constructors groups), ABC, ASA (American Subcontractors Association), NECA/MCAA/SMACNA for specialty subs, CSI chapters (spec/submittal people), CMAA, LCI (Lean).
- Creators (UNVERIFIED reach/fit): Jason Schroeder (Elevate Construction, superintendents), Adam Hoots (Lean Builder), Construction Genius podcast, Matt Risinger/Build Show, Nick Schiffer (residential-skew); LinkedIn construction-tech voices (Nialli list); ConTech newsletters.
- Positioning: "The free project-engineer sidekick for builders without Procore Premier: spec book to submittal register in minutes, nightly daily report in 3. Your files stay yours." Name: "Jobsite Docs" or "PE Copilot"-style generic; recommended `construction-pm` slug, displayName "Construction PM Toolkit". No Procore/Autodesk/AIA in brand.

## 7. Risks and guardrails

- Contract interpretation / notice deadlines: biggest liability. Missed notice can waive claims (A201 21 days; many subs' contracts shorter, 48 h-7 days, UNVERIFIED typical). Guardrails: never state entitlement or deadlines as fact; daily-report and CO skills flag "possible notice/claim event -- verify notice requirements in your contract today"; disclaimer: drafts for professional review, not legal advice.
- Submittal register completeness: missed item -> schedule/claim exposure. Always cite article, list sections parsed vs skipped, warn on scanned pages, label output "draft -- verify against spec".
- Copyright: no AIA forms/text/numbering; own templates; don't redistribute MasterFormat list; fixtures written by us (no real project specs).
- Accuracy of numbers: CO math, days-open, required-by dates via stdlib scripts only.
- Daily report as legal record: never fabricate; mark gaps "not recorded"; keep original transcript reference.
- Confidentiality: specs/contracts may be under NDA; README states data stays in the user's Claude session, no third-party calls.
- Safety: don't give engineering/structural or OSHA compliance determinations; route to EOR/competent person.

## 8. Day-30 traction signal

Published repo: >=40 stars or >=150 unique cloners, and >=5 inbound /request issues or comments from self-identified PEs/PMs/supers, with at least 2 asking for the same next job (Procore sync or look-ahead). One r/ConstructionManagers post not removed and net-positive (>=25 upvotes). Kill/pivot signal: <10 stars and zero practitioner issues.

Sources: developers.procore.com; procore.github.io/documentation (development-environments, oauth-keys, rate-limiting, marketplace-requirements); support.procore.com DMSA; constructionindustry.ai Procore AI review; contractortoolstack.com Procore review; trimble news 2026-04-02; tmcnet Buildots 2026-09-14; submittallink.com pricing; trunktools.com; autodesk.com Construction Disconnected; help.aiacontracts.com copying FAQ; buildingenclosureonline.com MasterFormat ruling; AGC A201-2017 commentary; GitHub repo searches 2026-10-02.
