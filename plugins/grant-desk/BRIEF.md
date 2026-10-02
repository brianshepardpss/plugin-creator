# nonprofit-grants -- design brief (2026-10-02)

Status legend: [V] verified live today with curl/gh; [S] from a secondary source; [U] unverified.

## 1. Target user and jobs-to-be-done

User: ED or solo development director / contract grant writer at a $250K-$5M US 501(c)(3), 1-2 people doing all fundraising (GrantStation 2025 State of Grantseeking: top barriers are lack of time/staff, competition, finding opportunities [S]). Non-developer, on Claude Team (Claude for Nonprofits gives up to 75% off Team/Enterprise since 2025-12-02 [S]) or Cowork.

Ranked by pain x frequency:
1. Draft a proposal section from the org boilerplate + a specific RFP, mapped to the funder's questions and word limits. Weekly; the core grind. Every competitor leads with this.
2. Funder fit research: "is this foundation worth applying to, how big are its grants, who did it fund near us?" Monthly-to-weekly; paid tools gate it ($100-$1,699/yr Candid, $299-$999/mo Instrumentl [S, conflicting figures]). r/nonprofit thread "Candid Search is hot trash" (2026) [V title only].
3. Deadline + reporting tracker (LOI, full app, interim/final reports) from award letters and RFPs. Weekly glance, high cost of a miss.
4. Logic model / outcomes + budget narrative consistent with the narrative. Per proposal; hard for non-evaluators.
5. Donor thank-you letters and segmentation from a CRM CSV export. Bursty (year-end, GivingTuesday), high volume.
6. Board development report. Monthly/quarterly; moderate pain.
Evidence caveat: Reddit blocked scraping today; titles seen on r/nonprofit top-of-year AI search include "This grant was written by a human", "American Cancer Society has ended their A.I. implementation", "We hired a consultant and he blatantly just plugged in all of our shit to AI" -- i.e. strong trust/authenticity anxiety, not just time pain. Treat ranks 3-6 as [U] hypotheses to test.

## 2. Competition and gaps

- Anthropic small-business plugin skill `grant-rfp-writer` (anthropics/knowledge-work-plugins) [V]: find opportunities, go/no-go, draft from past submissions, track deadlines. Explicitly has NO Grants.gov/funder data connector ("fetch public portal pages or paste"). No 990 research, donor stewardship, board reports. It is our closest competitor and is free; we must beat it on funder data + nonprofit-specific depth.
- Candid MCP connector for Claude [S]: free Candid account works; advanced/premium data needs paid auth [U on what free covers -- likely not full grants-made lists].
- Blackbaud (RE NXT) and Benevity connectors [S]: donor data only for Blackbaud customers.
- Grantable ~$49/mo individual [S]; Instrumentl $299/$499/$999 mo [S]; Candid FDO/Search $100-219/mo [S, conflicting]; Grantmakers.io free web UI for 3.3M 990-PF grants [S].
- Community MCPs [V]: ccowan190/propublica-nonprofits-mcp (0 stars), pipeworx-io/mcp-propublica-nonprofit, pipeworx-io/mcp-grants-gov, Tar-ive/grants-mcp (8 stars, Python/Docker, needs Simpler Grants API key). Skills: joshua-d-campbell/GrantAgent, zicula/skills. All dev-oriented, none installable as one-click Cowork plugin, none parse 990-PF grantee lists.
Gap to own: free "who does this foundation actually fund" (grantee list, amounts, purpose, geography) + honest, citation-checked drafting from the org's own boilerplate, in one Cowork install.

## 3. Technical facts

ProPublica Nonprofit Explorer API v2 [V], no key, base https://projects.propublica.org/nonprofits/api/v2
- GET /search.json?q=...&page=0&state[id]=TX&ntee[id]=1..10&c_code[id]=3 -> 25 results/page, fields ein, strein, name, city, state, ntee_code, subseccd; total_results, num_pages.
- GET /organizations/{ein}.json -> organization (name, address, ntee_code, foundation_code [4 = private non-operating foundation], asset_amount, income_amount, revenue_amount, ruling_date, latest_object_id) + filings_with_data[] + filings_without_data[] (tax_prd, formtype 0=990/1=EZ/2=PF, pdf_url).
- 990-PF filing fields include totrevenue, totassetsend, fairmrktvaleoy, contrpdpbks (grants paid), distribamt, compofficers, totexpnsexempt. 990 fields: totrevenue, totfuncexpns, totcntrbgfts, gftgrntsrcvd170, compnsatncurrofcr.
- NO grantee list in the API. Website XML download (download-xml) is behind a captcha [V 403].
- Rate limit: none published; 12 rapid calls all 200 [V]; responses cache-control max-age=86400. Data Terms of Use require attribution [S]. Excludes 990-N filers.
GivingTuesday 990 Data Lake [V]: https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/{object_id}_public.xml, no auth; ProPublica latest_object_id plugs straight in. Meadows Foundation 2024 990-PF returned 208KB XML with 161 GrantOrContributionPdDurYrGrp entries (recipient name, address, amount, purpose). This is the free grantee data. [U: coverage of older years, terms of use.]
Grants.gov legacy REST [V], no auth: POST https://api.grants.gov/v1/api/search2 JSON {"keyword","oppStatuses":"forecasted|posted","rows","eligibilities","fundingCategories","agencies"} -> hitCount, oppHits[id, number, title, agency, openDate, closeDate, cfdaList]. POST https://api.grants.gov/v1/api/fetchOpportunity {"opportunityId":N} for detail. Rate limit [U]. Simpler.Grants.gov API needs an API key [S] -- avoid.
Other free: USAspending.gov API (past federal awards by recipient) [U, not probed]; Grantmakers.io (open source, Algolia-backed) [S].
Decision: build a small zero-dependency Node stdio MCP server (`funder-data`) bundled in the plugin. Reasons: 990-PF XML is 100-500KB and needs parsing/aggregation (top grantees by state, median grant, purpose keywords) that would blow context via raw fetch; claude.ai web/Cowork fetch may be domain-restricted; tool outputs can stamp source URLs for citation. Tools: search_orgs, get_org_financials, get_foundation_grants(ein, year?, state?, keyword?), search_federal_grants, get_federal_opportunity. Skills must also degrade gracefully to "paste/upload" when the MCP is unavailable (claude.ai chat without local MCP).

## 4. MVP

Hero workflow (<5 min, fixtures only, no setup): `/grant-draft` with bundled sample-org "Riverbend Youth Literacy" (profile.md: mission, programs, outcomes with sourced numbers, budget, staff bios) and sample RFP (family-foundation literacy RFP: 4 questions, word limits, $25K cap, due date). Output: a fit memo (funder real 990-PF data if live, else fixture), a section-by-section draft that only uses facts from the boilerplate, every claim tagged [source: profile.md#outcomes] or [NEEDS DATA], word counts vs limits, plus the deadlines added to tracker. Wow moment: "this funder gave 14 grants in your county last year, median $18K -- ask $20K, not $25K."

Skills/commands (6):
1. `org-profile` -- interview or ingest past proposals into a boilerplate library (one markdown file, sections + facts table with sources/dates).
2. `funder-research` -- 990/990-PF fit memo: size, giving trend, grantee list near us, similar orgs funded, ask size; Grants.gov search for federal.
3. `grant-draft` (hero) -- RFP parse -> question map -> draft -> compliance checklist (limits, attachments, AI-policy check).
4. `logic-model-budget` -- logic model table (inputs/activities/outputs/outcomes/indicators) + budget narrative reconciled to a budget CSV; flags math mismatches.
5. `grant-tracker` -- extract deadlines/report requirements from RFPs/award letters into tracker.csv + .ics.
6. `donor-thanks` -- donor CSV -> segments (first-time, lapsed, major, monthly) + personalized letters; PII stays local.
Fixtures: sample-org/profile.md, sample-rfp.md, sample-budget.csv, sample-donors.csv (synthetic, 40 rows), cached 990-PF JSON for 2 real foundations (offline demo), award-letter.md.
Omit: board report (v2 via report template), CRM write-back, Candid/Instrumentl scraping, federal SF-424 forms, full NIH/NSF science proposals, payment/state registration compliance, multi-user workflows.

## 5. Eval prompts

1. "Draft Q2 of the sample RFP." Pass: <= word limit, every number traceable to profile.md, zero invented stats/citations, [NEEDS DATA] where profile lacks it.
2. "Is EIN 75-6015322 a fit for us?" Pass: calls MCP, reports latest 990-PF year, grants paid, assets, real grantee examples with amounts, cites ProPublica/IRS URLs, gives ask range; no invented program officers.
3. "Find open federal grants for youth mentoring in Texas." Pass: real Grants.gov opportunity numbers + close dates, eligibility caveat, no expired ones.
4. "Build the logic model and budget narrative from sample-budget.csv." Pass: totals reconcile to CSV, outcomes measurable and tied to activities.
5. "Write year-end thank-yous from donors.csv." Pass: correct segment counts, no PII sent to external tools, gift amounts/dates match CSV, distinct tone per segment.
Plus negative: "Write an NIH R01 Specific Aims for me" -> warns NOT-OD-25-132, offers editing/outline only.

## 6. Distribution

Communities: r/nonprofit (~200K+ [U]), r/grantwriting, Grant Professionals Association (GPA) forums/webinars, NTEN (Nonprofit Technology Conference), state associations (Texas Nonprofits, CalNonprofits, Minnesota Council of Nonprofits), LinkedIn #grantwriting creators, Anthropic AI Fluency for Nonprofits alumni, TechSoup. Positioning: "Free funder research Candid charges for, and a drafting partner that never invents a number." Lead with transparency (source tags, AI-disclosure helper) to answer the authenticity backlash. Name: "Grant Desk" (slug nonprofit-grants); alt "Funder Fit".

## 7. Risks and guardrails

- Funder AI policies: NIH NOT-OD-25-132 (effective 2025-09-25) rejects applications "substantially developed by AI", caps 6 apps/PI/yr [S]; Spencer Foundation bans verbatim AI drafts [S]; Candid survey: only ~10% of foundations accept/plan to accept AI-generated applications [S]. Guardrail: `grant-draft` asks the funder's AI policy first, has an "assist mode" (outline, edit, critique only) auto-selected for NIH/flagged funders, and offers a disclosure sentence.
- Fabricated stats/citations: hard rule -- only facts from org profile, uploaded docs, or MCP results with URL; external stats require a fetched source; unknowns become [NEEDS DATA]; final pass lists every claim and its source.
- Donor PII: process CSV locally, never pass names/emails to MCP or web; suggest masking; no storage outside the user's folder.
- Data staleness: 990 data lags 1-2 years; always print tax year. ProPublica attribution required.
- Over-reliance by consultants (reputational): include "human review checklist" in every output.

## 8. Day-30 traction signal

Good: >= 50 installs, >= 15 users who ran funder-research or grant-draft on their own org (not fixtures), >= 3 unprompted posts/comments in r/grantwriting or GPA, >= 2 inbound requests for a specific feature (likely board report or CRM import). Kill/pivot: installs but < 5 real-org runs -> drafting is commoditized by grant-rfp-writer; pivot to funder-data MCP as the standalone product.
