# Launch plan: Grant Desk

Nothing here gets posted without owner approval, one post at a time.

## Positioning

The funder research Candid charges for, free, plus a drafting partner that
never invents a number.

Proof point for every post: the sample fit memo. "This Waco foundation's
2025 990-PF lists 16 grants to Waco organizations, $480,777 total; the
median comparable grant is $25,000." Show the source URLs and the
[NEEDS DATA] tags, and show a draft check catching an untagged statistic.
Transparency is the pitch. It answers the r/nonprofit backlash ("This grant
was written by a human", consultants "plugging everything into AI").

## Audience and where they are

| Channel | Why | Norms |
|---|---|---|
| r/grantwriting | Working grant writers; funder research and AI-policy questions come up weekly | No promo posts without value. Lead with the method (reading 990-PF Part XV for free) and disclose authorship. Read the sidebar the day of posting. |
| r/nonprofit | EDs and development directors; strong AI-authenticity anxiety | Self-promotion is limited. Post as a how-to ("find who a foundation funds for free") with the tool as a footnote, and answer every comment. |
| Grant Professionals Association (GPA) community / webinars | Credentialed grant professionals who care about ethics and AI policy | Offer a talk on "AI policies by funder and source-tagged drafting", not an ad. Follow GPA's code of ethics framing. |
| NTEN community (Nonprofit Technology Network) | Nonprofit tech staff who install tools for their teams | Share in the AI/tools discussion space with the privacy section up front. |
| State nonprofit associations (Texas Nonprofits, CalNonprofits, Minnesota Council of Nonprofits) | Member newsletters and capacity-building webinars | Pitch a short member article or a free workshop. |
| LinkedIn #grantwriting | Consultants and development directors | Native post with a 30-second screen recording of the fit memo. |
| TechSoup community forum | Small nonprofits looking for free tools | Post in the tools section. Free and MIT, no signup. |

## Post drafts

### r/grantwriting (method first, tool second)

Title: You can see exactly who a foundation funded, for free, from its 990-PF XML (method + free tool inside)

> If you've been paying for a database mainly to answer "who does this
> foundation actually fund, and how much?", that data is public.
> Private foundations list every grant (recipient, city, amount, purpose)
> in Part XV of the 990-PF. ProPublica's free API gives you the
> foundation's latest e-file ID, and the IRS XML for that return is on a
> public S3 bucket (GivingTuesday's 990 Data Lake).
>
> I wrapped that in a free Claude plugin (MIT, no account). Give it an EIN
> and your city and you get the grantee list near you, grant-size
> quartiles, keyword matches and an ask range with the formula shown.
> Every figure carries its tax year and source URL.
>
> It also drafts from your own boilerplate, but every number has to cite
> your fact sheet or it gets marked [NEEDS DATA], and a script fails the
> draft if anything is untagged. Before drafting it asks for the funder's
> AI policy. For NIH (NOT-OD-25-132) it switches to outline-and-edit only.
>
> Example on a fictional org and a real Waco foundation's 2025 return is in
> the repo. I wrote it; not selling anything. I'd like to hear where the
> grantee parsing breaks on your funders.
> github.com/brianshepardpss/grant-desk

### r/nonprofit (how-to, tool as footnote)

Title: How to check if a foundation funds orgs like yours before you write the LOI (free, 10 minutes)

> 1. Find the foundation's EIN on ProPublica Nonprofit Explorer.
> 2. Open its latest 990-PF and go to Part XV, "Grants and Contributions
>    Paid During the Year".
> 3. Count grants in your city or county, note the typical amount, and read
>    the purpose lines. If nothing looks like you, save the LOI.
> 4. Check the box at the top of Part XV. If the foundation "only makes
>    contributions to preselected charitable organizations", it does not
>    take unsolicited proposals.
>
> I got tired of doing this by hand and built a free Claude plugin that
> does steps 1-4 from the IRS XML and shows its sources. It drafts too,
> but it refuses to invent statistics: anything your records don't support
> comes back as [NEEDS DATA]. Link in comments if mods allow.

### LinkedIn (native post with screen recording)

> One EIN in, and out comes: 41 grants, 16 in Waco, a median comparable
> grant of $25,000, and every number linked to the IRS filing.
>
> Grant Desk is a free Claude plugin for small nonprofit teams:
> - who a foundation actually funds (990-PF grantee lists, free)
> - open federal grants from Grants.gov
> - proposal drafts where every claim cites your own records, or gets
>   flagged [NEEDS DATA]
> - word-limit, budget and deadline math done by scripts, not guesses
> - it checks the funder's AI policy before writing a word
>
> MIT, no account, your donor data never leaves your machine.
> #grantwriting #nonprofit #fundraising #philanthropy

### GPA / state association workshop pitch

Subject: Session offer - "Funder AI policies and source-tagged drafting: using AI without losing trust"

> A 45-minute session covering what funders now say about AI (NIH
> NOT-OD-25-132, the Spencer Foundation's disclosure rules, and how to ask
> a program officer), how to keep every claim traceable to your own
> records, and how to read 990-PF Part XV for funder fit at no cost. We
> demo a free, open-source tool but the method works without it.

## Directory listing text

Grant Desk: free funder research and honest grant drafting for small
nonprofits. Shows who a foundation actually funds, using public 990-PF
grantee lists, and searches open federal grants on Grants.gov. Drafts
proposal sections from your own org profile with every claim
source-tagged or marked [NEEDS DATA]. Word limits, budgets and deadlines
are checked by scripts. Checks funder AI-use policies first (outline/edit
only for NIH). Donor thank-you letters are merged locally. MIT, no account.
Keywords: grants, nonprofit, grant writing, 990-PF, foundations,
Grants.gov, fundraising.

Listings: own marketplace (brianshepardpss/plugin-creator), Anthropic
plugin directory, community plugin directories.

## Day-30 signal

Measured on github.com/brianshepardpss/grant-desk and in channel replies,
30 days after the first post. Thresholds come from the brief and are fixed
now. They are never lowered after launch.

- Continue if: >= 50 unique cloners or installs, AND >= 15 users who say
  (issues, comments, DMs) they ran funder-research or grant-draft on their
  own org rather than the sample, AND >= 3 unprompted posts or comments
  in r/grantwriting or GPA spaces, AND >= 2 inbound requests for the same
  feature (likely a board report or CRM import).
- Kill or pivot if: there are installs but fewer than 5 real-org runs.
  That would mean drafting is commoditized by free alternatives, so pivot
  to the funder-data scripts as a standalone product.
