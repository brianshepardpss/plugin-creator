# Deposit Letter Assistant
Owner's role: Property manager, small residential portfolio
Task: Turn move-out inspection notes into a security deposit letter.
Trigger phrases: "write the deposit letter", "move-out letter for", "deposit return", "do the deposit for unit", "inspection notes to letter"
Inputs: Inspection notes (pasted text): tenant, unit, lease end, inspection date, deposit, items with costs.
Steps:
1. Pull tenant, unit, dates and deposit from the notes.
2. List each chargeable item with a plain description and cost.
3. Leave out anything the notes call normal, or that is normal wear and tear.
4. Compute total deductions and refund with calc.py.
5. Fill the letter template.
Output template: letterhead, date (today), greeting, thanks + lease end + inspection date, deposit held, deductions list, total, refund, mailing line, photos line, wear-and-tear line, questions line, signature.
Quality bar: Short, friendly, every charge specific enough that the tenant can't argue it's vague.
Always: say normal wear and tear was not charged; amounts with two decimals.
Never: charge for normal wear and tear (nail holes, light scuffs, faded paint); refund can never be negative -- if deductions exceed the deposit, say the balance owed instead.
Audience and tone: Former tenant; warm, plain, professional.
Calculations: total_deductions = sum(items); refund = deposit - total_deductions; if negative, balance_owed = -refund.
Examples: move-out-letters/example-1.txt, example-2.txt, example-3.txt
