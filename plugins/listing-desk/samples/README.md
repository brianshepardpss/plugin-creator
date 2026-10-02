# Sample data (all fictional)

Every name, address, MLS number, phone number and email here is made up.
"Cedar Hollow, TX 75999" and "Pecan Flats, TX 75998" are fictional places.
Phone numbers use the 555-01xx fiction range; emails use example.com.

| File | Used by | What it shows |
|---|---|---|
| mls_export.csv | cma, listing-kit | 40-row export with Matrix-style headers. Messy on purpose: CH26-1007 has no sqft, CH26-1002 appears twice, CH26-1010 uses "$388,250" / "2,120" strings, and CH26-1401's public remarks break Fair Housing and MLS rules. |
| mls_export_renamed.csv | cma | A different vendor's headers ("Sq Ft", "Sold Price", "BR", "FB") plus a blank row and a "TBD" price. |
| subject.md | cma, listing-kit | The subject property facts and seller notes (including wording the copy must not use). |
| purchase_contract.pdf | contract-timeline | A generic fictional purchase agreement (not a state association form). Effective Date Fri 2026-10-09, the Friday before Columbus Day. |
| purchase_contract_scanned.pdf | contract-timeline | The same contract as a slightly skewed, blurred image scan. |
| open_house_signins.csv | follow-up | Sign-in sheet with consent flags, a represented buyer, a duplicate and a blank row. |
| sphere_contacts.csv | nurture-plan | 12 contacts across tiers A/B/C with anniversaries, birthdays and permissions. |
| expected/ | everyone | The bundled scripts' output on these files, for checking your own runs. |

Regenerate the expected outputs from the plugin root, for example:

```
python3 skills/cma/cma.py --csv samples/mls_export.csv --subject samples/subject.md
python3 skills/contract-timeline/timeline.py samples/expected/contract_terms.json
```
