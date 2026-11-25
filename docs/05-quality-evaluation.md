# Phase 5 – Quality Evaluation of the Reengineered Architecture

We measured the six items the brief asks for on the legacy system (commit 01), after the maintenance requests (commit 03), and on the final system (commit 06). Tests are not counted.

**How we measured** (anyone can repeat it):

```bash
pip install radon
radon raw -s library.py library_service.py library_db.py    # LOC, SLOC
radon cc -s -a library.py library_service.py library_db.py  # McCabe cyclomatic complexity
grep -n "def " *.py          # functions          grep -n "^class " *.py   # classes
grep -n "import sqlite3" *.py                     # modules that depend on the database
```

## Results

| Measurement | 01 Legacy | 03 After MR-01/MR-02 | **06 Final** |
|---|---|---|---|
| Files (modules) | 1 | 2 | **3** |
| Lines of code, LOC (all lines / source lines) | 214 / 170 | 212 / 152 | **249 / 173** |
| Number of functions (incl. methods) | 5 | 16 | **25** |
| Number of classes | 0 | 1 (`LibraryDatabase`) | **2** (`LibraryDatabase`, `LibraryError`) |
| Average cyclomatic complexity (radon) | 3.80 | 2.29 | **1.96** |
| Highest cyclomatic complexity | 6 (`borrow`, `main`) | 8 (`borrow`) | **6** (`main`, the menu loop) |
| Cyclomatic complexity of `borrow()` | 6 | 8 | **1** |
| Code smells from Phase 1 still present | 8 of 8 | 5 of 8 | **0** fully present (1 partly) |
| DB dependencies: modules that use SQLite | 1 (the whole system) | 1 (`library_db.py` only) | **1** (`library_db.py` only) |
| DB dependencies: business functions containing SQL | **4 of 5** | 0 | **0** |
| SQL statements | 17, spread over 4 functions | 14, all in the database layer | **14, all in the database layer** |
| Regression tests passing | 20 / 20 | 24 / 24 | **24 / 24** |

## Code smells (Phase 1 list)

| Smell | Status in the final system | Fixed by |
|---|---|---|
| S1 Long Method (`borrow`) | Removed: 7 lines, complexity 1 | RF-1 |
| S2 Mixed responsibilities | Removed: menu, rules and SQL in separate modules | MR-02, RF-2 |
| S3 Direct DB access | Removed: all SQL in `library_db.py` | MR-02 |
| S4 Primitive data | Mostly removed: rows read by column name, named constants. Dates are still stored as text in the database | MR-02, RF-3 |
| S5 Magic numbers | Removed: `MAX_BOOKS`, `LOAN_DAYS`, `FINE_PER_DAY`, `ACTIVE` | RF-3 |
| S6 Duplicated Code | Removed: one `ask_member_and_book()` | RF-4 |
| S7 Global variable | Removed: the database path is a parameter of `LibraryDatabase` | MR-02 |
| S8 No comments / documentation | Removed: each module explains its job; phase documents in `docs/` | all phases |

Defect **D1** (crash on letters as a Book ID) was fixed in commit 06 as corrective maintenance.

## Interpretation

- **Size:** almost unchanged (170 → 173 source lines), even though the system now supports copies, upgrades old databases and handles bad input.
- **More, smaller units:** 5 → 25 functions. The average function is much shorter, and average complexity nearly halved (3.80 → 1.96). The busiest business function, `borrow()`, fell from 8 to 1.
- **Database dependency:** before, changing the database meant editing all 4 business functions. Now it means rewriting one class (`LibraryDatabase`) with the same methods. This is what MR-02 needed.
- **Behaviour preserved:** the regression tests pass at every commit. The only differences from the legacy behaviour are the requested ones: copies (MR-01), rule BR-14 and the D1 fix.
- **Remaining:** dates are stored as text (S4, partly), and fines and return dates are still not stored (D2, D3). These are candidates for future maintenance requests.
