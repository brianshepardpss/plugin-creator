# nav-demo answer key (for evals and reviewers)

True references to `UserRepo.findById` outside its definition: 5.

| File | Line | Call site |
|---|---|---|
| src/Lookups.scala | 5 | `repo.findById(id)` inside the `resolve` extension |
| src/Lookups.scala | 12 | `r.findById(id)` inside `given fromRepo` (via the `Users` alias) |
| src/Lookups.scala | 19 | `users.findById(o.owner)` in `Reports.ownerName` (alias) |
| src/Main.scala | 7 | `users.findById(UserId(1))` direct call |
| src/Main.scala | 11 | `users.findById` eta-expanded to a function value |

Not references (false positives a grep returns): the doc comment on Repos.scala:11,
the `OrderRepo.findById` definition
(Repos.scala:13) and its call (Lookups.scala:22), the string in Lookups.scala:16,
the comment on Lookups.scala:15. Indirect callers (through `resolve`, `NameLookup`,
`ownerName`) are reached through the call sites above.
