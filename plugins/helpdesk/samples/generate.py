#!/usr/bin/env python3
"""Regenerate the bundled sample exports (maintainers only).

Writes zendesk_export.json (API shape with sideloads) and freshdesk_export.csv
(UI export shape, deliberately messy) describing the SAME 40 tickets for the
fictional booking-software company Quillfern. Every person, company, email and
card number here is fake (example.com/.org/.net, test card numbers).

Usage: python3 generate.py   (writes next to this file)
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPORTED_AT = "2026-10-02T09:00:00Z"

AGENTS = {
    9001: ("Sam Agentson", "sam.agentson@quillfern.example.com", 501),
    9002: ("Lee Supportly", "lee.supportly@quillfern.example.com", 501),
    9003: ("Morgan Billingham", "morgan.billingham@quillfern.example.com", 502),
    9004: ("Casey Escalante", "casey.escalante@quillfern.example.com", 503),
}
GROUPS = {501: "Tier 1", 502: "Billing", 503: "Tier 2"}
ORGS = {
    701: ("Maple Row Dental (Sample)", []),
    702: ("Harborview Clinics Group (Sample)", ["vip"]),
    703: ("Bramblewood Salon (Sample)", []),
    704: ("Quartzline Physio (Sample)", []),
    705: ("Tealbrook Tutoring (Sample)", []),
    706: ("Copperfield Vets (Sample)", []),
    707: ("Juniper Lane Spa (Sample)", []),
    708: ("Estudio Nube Azul (Muestra)", []),
}
# requester id: (name, email, org id)
PEOPLE = {
    8001: ("Avery Sample", "avery.sample@example.com", 701),
    8002: ("Jordan Testwell", "jordan.testwell@example.org", 702),
    8003: ("Riley Placeholder", "riley.placeholder@example.net", 703),
    8004: ("Quinn Mockford", "quinn.mockford@example.com", 704),
    8005: ("Dana Fixture", "dana.fixture@example.org", 705),
    8006: ("Robin Dummyworth", "robin.dummyworth@example.net", 706),
    8007: ("Taylor Stubbs", "taylor.stubbs@example.com", 707),
    8008: ("Lucia Ejemplo", "lucia.ejemplo@example.org", 708),
    8009: ("Morgan Fakely", "morgan.fakely@example.com", 703),
    8010: ("Casey Notreal", "casey.notreal@example.net", 704),
    8011: ("Jamie Specimen", "jamie.specimen@example.com", 705),
    8012: ("Alex Pretendo", "alex.pretendo@example.org", 706),
    8013: ("Drew Samplesen", "drew.samplesen@example.net", 707),
    8014: ("Parker Testa", "parker.testa@example.com", 701),
    8015: ("Skyler Mockett", "skyler.mockett@example.org", 702),
}

# id, created, status, priority, requester, assignee, tags, subject, description,
# sla_due (or None), solved_at (or None), csat ("good"/"bad"/None, comment)
T = []


def t(i, created, status, prio, req, agent, tags, subject, desc, due=None, solved=None,
      csat=None, csat_comment="", extra=None):
    T.append(dict(id=i, created=created, status=status, prio=prio, req=req, agent=agent,
                  tags=tags, subject=subject, desc=desc, due=due, solved=solved,
                  csat=csat, csat_comment=csat_comment, extra=extra or []))


# ---- prior week (2026-09-18 .. 2026-09-25) solved history ----
t(1001, "2026-09-18T10:12:00Z", "closed", "normal", 8001, 9003, ["billing"],
  "Need a copy of last month's invoice",
  "Hi, can you send me a PDF of the August invoice? Our accountant needs it.",
  due="2026-09-19T10:12:00Z", solved="2026-09-18T15:30:00Z", csat="good")
t(1002, "2026-09-18T14:40:00Z", "closed", "normal", 8003, 9001, ["login"],
  "Locked out after 2FA phone change",
  "I got a new phone and now I can't log in, the two-factor code goes to my old phone.",
  due="2026-09-19T14:40:00Z", solved="2026-09-19T09:05:00Z", csat="good")
t(1003, "2026-09-19T08:05:00Z", "closed", "high", 8002, 9004, ["calendar"],
  "Google Calendar sync stopped",
  "Our Google Calendar sync stopped overnight for three clinicians. Bookings are not showing up.",
  due="2026-09-19T16:05:00Z", solved="2026-09-19T13:20:00Z", csat="good")
t(1005, "2026-09-19T16:22:00Z", "closed", "normal", 8004, 9001, ["timezone"],
  "Appointments showing an hour off",
  "Since our clocks changed, every appointment in the client reminder shows one hour off. The calendar itself looks right.",
  due="2026-09-20T16:22:00Z", solved="2026-09-21T11:00:00Z", csat="bad",
  csat_comment="Took two days and the answer was a workaround.")
t(1006, "2026-09-21T09:30:00Z", "closed", "low", 8005, 9002, ["howto"],
  "How do I add a custom question to the booking form?",
  "We want to ask new tutoring clients for their grade level when they book. Is there a custom question option on the booking form?",
  due="2026-09-23T09:30:00Z", solved="2026-09-22T10:10:00Z", csat="good")
t(1007, "2026-09-22T11:15:00Z", "closed", "normal", 8006, 9002, ["export"],
  "Export all bookings to CSV",
  "How do I export all of our bookings for the year to a CSV file for our records?",
  due="2026-09-23T11:15:00Z", solved="2026-09-22T13:45:00Z", csat="good")
t(1008, "2026-09-22T15:02:00Z", "closed", "normal", 8007, 9003, ["billing"],
  "Charged twice this month",
  "My card was charged twice for September. Please refund the duplicate payment.",
  due="2026-09-23T15:02:00Z", solved="2026-09-23T10:40:00Z", csat="good")
t(1010, "2026-09-23T10:00:00Z", "closed", "normal", 8009, 9001, ["staff"],
  "Add a new staff member",
  "How do I add a new stylist as a team member so she can see her own schedule only?",
  due="2026-09-24T10:00:00Z", solved="2026-09-23T12:00:00Z", csat="good")
t(1011, "2026-09-24T13:30:00Z", "closed", "normal", 8010, 9004, ["timezone"],
  "Reminder emails have wrong time",
  "Reminder emails say 3pm but the booking is at 2pm. Our time zone in settings is correct.",
  due="2026-09-25T13:30:00Z", solved="2026-09-26T09:00:00Z", csat="bad",
  csat_comment="Still not fixed properly.")

# ---- this week (2026-09-25 09:00 .. 2026-10-02 09:00) solved ----
t(1013, "2026-09-25T12:10:00Z", "solved", "normal", 8011, 9001, ["export"],
  "Download my data as a spreadsheet",
  "Where can I download all client records and bookings as a spreadsheet? We need a backup.",
  due="2026-09-26T12:10:00Z", solved="2026-09-25T14:00:00Z", csat="good")
t(1014, "2026-09-25T16:45:00Z", "solved", "normal", 8012, 9003, ["billing"],
  "Invoice shows wrong company name",
  "The invoice still shows our old company name. Can you update billing details and resend the invoice?",
  due="2026-09-26T16:45:00Z", solved="2026-09-26T09:30:00Z", csat="good")
t(1015, "2026-09-26T09:20:00Z", "solved", "low", 8013, 9002, ["howto"],
  "Intake form field for allergies",
  "Can I add an intake form field so spa clients list allergies before booking a massage?",
  due="2026-09-28T09:20:00Z", solved="2026-09-26T15:00:00Z")
t(1016, "2026-09-26T11:00:00Z", "solved", "normal", 8014, 9001, ["login"],
  "Password reset email never arrives",
  "I clicked forgot password three times and no email arrives. Checked spam.",
  due="2026-09-27T11:00:00Z", solved="2026-09-26T12:15:00Z", csat="good")
t(1018, "2026-09-27T08:40:00Z", "solved", "normal", 8004, 9004, ["timezone"],
  "Daylight saving broke our reminders",
  "Text reminders are going out an hour early since the daylight saving change. Is this a known issue?",
  due="2026-09-28T08:40:00Z", solved="2026-09-29T10:00:00Z", csat="bad",
  csat_comment="Third time we report this time zone problem.")
t(1019, "2026-09-27T13:05:00Z", "solved", "normal", 8006, 9002, ["export"],
  "CSV export of appointments for accountant",
  "Our accountant needs a CSV export of last quarter's appointments with prices. How?",
  due="2026-09-28T13:05:00Z", solved="2026-09-27T16:20:00Z", csat="good")
t(1020, "2026-09-28T10:30:00Z", "solved", "normal", 8007, 9003, ["billing"],
  "Upgrade plan and add two seats",
  "We'd like to upgrade to the Studio plan and add two seats. Will we be charged a prorated amount?",
  due="2026-09-29T10:30:00Z", solved="2026-09-28T12:00:00Z", csat="good")
t(1022, "2026-09-29T09:00:00Z", "solved", "low", 8005, 9002, ["howto"],
  "Custom booking question for first visit",
  "Is there a way to show a custom question on the booking form only for a first visit?",
  due="2026-10-01T09:00:00Z", solved="2026-09-29T14:00:00Z")
t(1023, "2026-09-29T11:20:00Z", "solved", "normal", 8009, 9001, ["calendar"],
  "Outlook calendar not syncing",
  "My Outlook calendar is not syncing new bookings since yesterday.",
  due="2026-09-30T11:20:00Z", solved="2026-09-29T15:00:00Z", csat="good")
t(1024, "2026-09-29T15:10:00Z", "solved", "normal", 8010, 9004, ["timezone"],
  "Clients in another time zone see wrong slot",
  "Clients booking from another time zone see the wrong time slot on the booking page.",
  due="2026-09-30T15:10:00Z", solved="2026-10-01T10:00:00Z")
t(1025, "2026-09-30T10:00:00Z", "solved", "normal", 8001, 9003, ["billing"],
  "Receipt for annual payment",
  "Please send me a receipt for our annual payment, I can't find it in the billing page.",
  due="2026-10-01T10:00:00Z", solved="2026-09-30T11:00:00Z", csat="good")
t(1027, "2026-09-30T14:30:00Z", "solved", "low", 8013, 9002, ["feature-request"],
  "Feature request: waitlist",
  "Feature request: it would be great to have a waitlist when a day is fully booked. Please add!",
  due="2026-10-02T14:30:00Z", solved="2026-09-30T16:00:00Z")
t(1028, "2026-10-01T09:10:00Z", "solved", "normal", 8012, 9001, ["login"],
  "Locked out of account",
  "I'm locked out of my account after too many login attempts.",
  due="2026-10-02T09:10:00Z", solved="2026-10-01T09:50:00Z", csat="good")
t(1029, "2026-10-01T12:00:00Z", "solved", "normal", 8003, 9002, ["staff"],
  "Staff permissions for receptionist",
  "What permission should our receptionist have so she can book for everyone but not see reports?",
  due="2026-10-02T12:00:00Z", solved="2026-10-01T13:30:00Z", csat="good")
t(1031, "2026-10-01T15:00:00Z", "solved", "low", 8011, 9001, ["howto"],
  "Add a question to booking form",
  "How do I add a required question like 'student name' to the booking form?",
  due="2026-10-03T15:00:00Z", solved="2026-10-01T17:00:00Z", csat="bad",
  csat_comment="The answer was that it is not possible, very disappointing.")

# ---- open queue ----
t(1004, "2026-10-01T09:45:00Z", "open", "high", 8014, 9001, ["calendar"],
  "Bookings not appearing in Google Calendar",
  "New bookings since this morning are not appearing in our Google Calendar. Old ones are fine.",
  due="2026-10-02T09:45:00Z")
t(1009, "2026-10-01T11:30:00Z", "open", "high", 8012, 9002, ["staff"],
  "New vet can't see her schedule",
  "We added Dr. Pat Imaginary as a staff member but she sees an empty schedule when she logs in.",
  due="2026-10-02T11:30:00Z")
t(1012, "2026-10-01T12:15:00Z", "new", "normal", 8013, None, ["export"],
  "Export is missing prices",
  "The bookings CSV export has an empty price column for September. We need it for payroll today.",
  due="2026-10-02T12:15:00Z")
t(1017, "2026-09-29T10:05:00Z", "open", "normal", 8007, 9003, ["billing", "refund"],
  "Refund for annual renewal",
  "We were charged $588.00 for the annual renewal on 2026-08-20. We have barely used Quillfern since and want a full refund.",
  due="2026-10-03T10:05:00Z")
t(1021, "2026-10-01T16:00:00Z", "open", "high", 8010, 9004, ["data"],
  "Deleted client notes - consulting my lawyer",
  "Your update on Tuesday wiped the treatment notes for 40 of our clients. This is completely unacceptable. I am consulting my lawyer about legal action if the notes are not restored.",
  due="2026-10-03T07:00:00Z")
t(1026, "2026-10-02T07:30:00Z", "open", "urgent", 8002, 9004, ["billing"],
  "THIRD TIME asking - card charged but plan downgraded",
  "This is the THIRD time I am writing. You charged our card and then downgraded all six clinics to the free plan. Here is the card you charged, 4111 1111 1111 1111 exp 12/28, check it yourself. Fix this today or we cancel every location and move to another provider.",
  due="2026-10-02T17:30:00Z")
t(1030, "2026-09-22T09:00:00Z", "open", "normal", 8001, 9004, ["calendar", "double-booking"],
  "Double bookings after Google Calendar sync",
  "Since last week the Google Calendar sync is creating double bookings for two of our hygienists.",
  due="2026-10-03T12:00:00Z")
t(1032, "2026-10-01T18:20:00Z", "open", "normal", 8005, 9002, ["howto"],
  "Booking form custom question for parents",
  "Can the booking form ask parents for a custom question like 'child's school'?",
  due="2026-10-02T18:20:00Z")
t(1033, "2026-10-01T20:10:00Z", "new", "normal", 8008, None, [],
  "No se sincroniza el calendario de Google",
  "Hola, desde ayer las citas nuevas no aparecen en nuestro calendario de Google. Ya intentamos desconectar y volver a conectar la cuenta. Gracias por la ayuda.",
  due="2026-10-02T20:10:00Z")
t(1034, "2026-10-01T21:00:00Z", "pending", "normal", 8009, 9001, ["login"],
  "Reset two-factor for former manager",
  "Our former manager had 2FA on the owner account. How do we reset it?",
  due="2026-10-03T21:00:00Z")
t(1035, "2026-10-02T06:10:00Z", "new", "low", 8011, None, ["feature-request"],
  "Please add Apple Calendar",
  "Feature request: please add Apple Calendar sync, it would be great for our tutors.",
  due="2026-10-04T06:10:00Z")
t(1036, "2026-10-02T06:40:00Z", "new", "high", 8003, None, ["sms"],
  "SMS reminders not sending since this morning",
  "None of our SMS reminders went out this morning. Clients are missing appointments.",
  due="2026-10-02T14:40:00Z")
t(1037, "2026-10-02T07:05:00Z", "new", "normal", 8015, None, [],
  "Cancel our subscription",
  "Please cancel our subscription at the end of this billing period. We are switching to another tool.",
  due="2026-10-03T07:05:00Z")
t(1038, "2026-10-02T07:55:00Z", "new", "high", 8006, None, [],
  "Clients didn't get text reminders today",
  "Our clients did not get their text reminders today. Is the SMS reminder service down?",
  due="2026-10-02T15:55:00Z")
t(1039, "2026-10-02T08:10:00Z", "new", "normal", 8004, None, [],
  "Time zone wrong again on reminders",
  "Text reminders show the wrong time again, one hour off, same as last week.",
  due="2026-10-03T08:10:00Z")
t(1040, "2026-10-02T08:30:00Z", "new", "normal", 8014, None, [],
  "Unknown login from another country",
  "We got an email about a login to our account from a country we have never been to. Was our account hacked?",
  due="2026-10-03T08:30:00Z")

# 1017 extra customer follow-up
T[[x["id"] for x in T].index(1017)]["extra"] = [
    ("agent", 9003, "2026-09-29T13:00:00Z",
     "Thanks Taylor, I'm checking the renewal details with our billing lead.", False),
    ("agent", 9003, "2026-09-29T13:02:00Z",
     "Internal: renewal charged 2026-08-20, 40 days ago. Outside 14-day window per kb-101.", True),
    ("customer", 8007, "2026-10-01T08:30:00Z",
     "Any update? We really need this money back this month.", False),
]
T[[x["id"] for x in T].index(1026)]["extra"] = [
    ("agent", 9004, "2026-10-02T07:50:00Z",
     "Internal: Harborview is our largest account (6 locations). Customer pasted a full card number in the ticket body; needs redaction.", True),
    ("customer", 8002, "2026-10-02T08:20:00Z",
     "Still nothing. Our front desks cannot take online bookings. This is ridiculous.", False),
]
T[[x["id"] for x in T].index(1021)]["extra"] = [
    ("customer", 8010, "2026-10-01T19:40:00Z",
     "Waiting for an answer. Tomorrow my lawyer sends a letter.", False),
]

# 25-message thread on 1030
THREAD_1030 = [
    ("customer", 8001, "2026-09-22T09:00:00Z", "Since last week the Google Calendar sync is creating double bookings for two of our hygienists. Example bookings BK-55102 and BK-55117 both show twice."),
    ("agent", 9001, "2026-09-22T10:30:00Z", "Thanks Avery. Could you disconnect and reconnect Google Calendar under Settings > Integrations and tell me if new bookings still duplicate?"),
    ("customer", 8001, "2026-09-22T14:10:00Z", "Done, reconnected both hygienists. Still duplicates on new bookings this afternoon."),
    ("agent", 9001, "2026-09-22T15:00:00Z", "Thank you. Next, please clear the browser cache and check the sync direction is set to two-way."),
    ("customer", 8001, "2026-09-23T08:45:00Z", "Cache cleared. Sync is two-way. Still getting doubles."),
    ("agent", 9001, "2026-09-23T09:30:00Z", "Let's try one-way sync (Quillfern to Google) for a day to see if the duplicates stop."),
    ("customer", 8001, "2026-09-24T08:20:00Z", "One-way sync for a day: fewer doubles but still 3 yesterday."),
    ("agent", 9001, "2026-09-24T09:00:00Z", "I'm escalating to our Tier 2 team. Casey will take it from here."),
    ("agent", 9004, "2026-09-24T11:00:00Z", "Hi Avery, Casey here. Can you re-authorize Google access for both hygienists and confirm their calendar time zone matches the clinic time zone?"),
    ("customer", 8001, "2026-09-24T15:30:00Z", "Re-authorized. Time zones both say America/Chicago, same as the clinic."),
    ("agent", 9004, "2026-09-25T09:10:00Z", "Thanks. Please send the sync log export from Settings > Integrations > Download log for one hygienist."),
    ("customer", 8001, "2026-09-25T13:00:00Z", "Attached the log export for Hygienist A (sync-log-0925.csv)."),
    ("agent", 9004, "2026-09-25T16:00:00Z", "Got it, I see the same booking pushed twice within a second. I've filed this with engineering as ENG-4471."),
    ("customer", 8001, "2026-09-26T08:30:00Z", "OK. Meanwhile patients are showing up to the same slot. What should we do?"),
    ("agent", 9004, "2026-09-26T09:00:00Z", "As a workaround, please keep the one-way sync on and check the day view each morning for duplicates."),
    ("customer", 8001, "2026-09-28T10:15:00Z", "We had two patients double booked on Friday. This is costing us money."),
    ("agent", 9004, "2026-09-28T11:00:00Z", "I'm sorry about Friday. I've asked engineering to prioritize ENG-4471 and will share their timeline."),
    ("customer", 8001, "2026-09-29T08:00:00Z", "Any timeline yet?"),
    ("agent", 9004, "2026-09-29T09:30:00Z", "Engineering confirmed the cause: a retry in the Google push that does not check for an existing event. They are working on the fix."),
    ("customer", 8001, "2026-09-29T12:00:00Z", "Good to hear. Will we get anything for the lost appointments? That's two cancelled cleanings, invoice INV-20931 covers this month."),
    ("agent", 9004, "2026-09-29T13:00:00Z", "I've passed your credit question to our billing lead; I can't confirm an amount myself."),
    ("customer", 8001, "2026-09-30T08:40:00Z", "Thanks. Please keep me posted."),
    ("agent", 9004, "2026-09-30T10:00:00Z", "Engineering has the ENG-4471 fix scheduled for the 2026-10-06 release. I'll update you by Tuesday 2026-10-06 at the latest, sooner if it ships early."),
    ("agent", 9004, "2026-09-30T10:05:00Z", "Internal: billing lead (Morgan) to decide on credit for INV-20931; do not promise an amount.", True),
    ("customer", 8001, "2026-10-01T16:30:00Z", "Thanks Casey. Two questions: can you confirm the fix will also clean up the existing duplicates, and has billing decided on the credit for INV-20931?"),
]


def zendesk():
    users = [{"id": k, "name": v[0], "email": v[1], "role": "end-user", "organization_id": v[2]}
             for k, v in PEOPLE.items()]
    users += [{"id": k, "name": v[0], "email": v[1], "role": "agent", "default_group_id": v[2]}
              for k, v in AGENTS.items()]
    orgs = [{"id": k, "name": v[0], "tags": v[1]} for k, v in ORGS.items()]
    groups = [{"id": k, "name": v} for k, v in GROUPS.items()]
    tickets = []
    cid = 50000
    for x in sorted(T, key=lambda r: r["id"]):
        comments = []
        if x["id"] == 1030:
            msgs = THREAD_1030
        else:
            msgs = [("customer", x["req"], x["created"], x["desc"])] + list(x["extra"])
        for m in msgs:
            cid += 1
            comments.append({"id": cid, "author_id": m[1], "public": not (len(m) > 4 and m[4]),
                             "body": m[3], "created_at": m[2]})
        if x["solved"]:
            comments.append({"id": cid + 1, "author_id": x["agent"], "public": True,
                             "body": "Following up: this is resolved on our side. Reply here if anything else comes up.",
                             "created_at": x["solved"]})
            cid += 1
        paused = x["status"] in ("pending", "hold")
        stage = "achieved" if x["solved"] else ("paused" if paused else "active")
        sla = {"policy_metrics": [{"metric": "next_reply_time", "stage": stage,
                                   "breach_at": x["due"]}]} if x["due"] else {"policy_metrics": []}
        csat = {"score": x["csat"], "comment": x["csat_comment"]} if x["csat"] else {"score": "unoffered"}
        updated = max(m["created_at"] for m in comments)
        tickets.append({
            "id": x["id"], "subject": x["subject"], "description": x["desc"],
            "status": x["status"], "priority": x["prio"], "type": "question",
            "requester_id": x["req"], "assignee_id": x["agent"],
            "group_id": AGENTS[x["agent"]][2] if x["agent"] else None,
            "organization_id": PEOPLE[x["req"]][2], "tags": x["tags"],
            "via": {"channel": "email"}, "created_at": x["created"], "updated_at": updated,
            "satisfaction_rating": csat, "slas": sla,
            "metric_set": {"solved_at": x["solved"]}, "comments": comments,
        })
    out = {"exported_at": EXPORTED_AT, "tickets": tickets, "users": users,
           "organizations": orgs, "groups": groups}
    (HERE / "zendesk_export.json").write_text(json.dumps(out, indent=1) + "\n")


FD_STATUS = {"new": "Open", "open": "Open", "pending": "Pending", "solved": "Resolved", "closed": "Closed"}
FD_PRIO = {"low": "Low", "normal": "Medium", "high": "High", "urgent": "Urgent"}
FD_CODES_STATUS = {"Open": "2", "Pending": "3", "Resolved": "4", "Closed": "5"}
FD_CODES_PRIO = {"Low": "1", "Medium": "2", "High": "3", "Urgent": "4"}
CSAT_FD = {"good": "Extremely Happy", "bad": "Unhappy"}


def fd_time(iso):
    return iso.replace("T", " ").replace("Z", "") if iso else ""


def freshdesk():
    cols = ["Ticket ID", "Subject", "Description", "Status", "Priority", "Source", "Type",
            "Agent", "Group", "Created time", "Due by Time", "Resolved time", "Last update time",
            "Tags", "Full name", "Email", "Company Name", "Satisfaction Rating"]
    rows = []
    for n, x in enumerate(sorted(T, key=lambda r: r["id"])):
        status, prio = FD_STATUS[x["status"]], FD_PRIO[x["prio"]]
        # messiness: every 7th row came out of an API dump with numeric codes
        if n % 7 == 3:
            status, prio = FD_CODES_STATUS[status], FD_CODES_PRIO[prio]
        name, email, org = PEOPLE[x["req"]]
        desc = x["desc"]
        if x["id"] == 1030:
            desc = THREAD_1030[0][3]
        last = x["solved"] or x["created"]
        rows.append({
            "Ticket ID": x["id"], "Subject": x["subject"], "Description": desc,
            "Status": status, "Priority": prio, "Source": "Email", "Type": "Question",
            "Agent": AGENTS[x["agent"]][0] if x["agent"] else "",
            "Group": GROUPS[AGENTS[x["agent"]][2]] if x["agent"] else "",
            "Created time": fd_time(x["created"]), "Due by Time": fd_time(x["due"]),
            "Resolved time": fd_time(x["solved"]), "Last update time": fd_time(last),
            "Tags": ",".join(x["tags"]), "Full name": name, "Email": email,
            "Company Name": ORGS[org][0], "Satisfaction Rating": CSAT_FD.get(x["csat"], ""),
        })
    with (HERE / "freshdesk_export.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i, r in enumerate(rows):
            w.writerow(r)
            if i == 19:
                f.write(",,,,,,,,,,,,,,,,,\n")  # a blank row, as real exports sometimes have


if __name__ == "__main__":
    assert len(T) == 40, len(T)
    assert len(THREAD_1030) == 25
    zendesk()
    freshdesk()
    print("wrote zendesk_export.json and freshdesk_export.csv")
