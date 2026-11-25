# SE431 – Library Management System (LMS) Maintenance Project

Legacy Library Management System given to the maintenance team: Python + SQLite, console menu (Search, Borrow, Return, Exit).

- `library.py` – menu (input and output only)
- `library_service.py` – business rules
- `library_db.py` – database layer (all SQL)

## Run

```bash
python library.py
```

Sample data: members `S1` (Ali) and `S2` (Sara); books 1–3 with 3, 2 and 1 copies.
An old `library.db` is upgraded automatically (MR-01).

## Regression tests

```bash
python tests/regression_tests.py
```

Each test runs the program with typed input and checks what it prints.

## Documents

- `docs/01-program-comprehension.md` – Phase 1: program comprehension and legacy-system analysis
- `docs/02-maintenance.md` – Phase 2: MR-01 (multiple copies) and MR-02 (replace the database)
- `docs/03-refactoring.md` – Phase 3: refactoring
- `docs/04-reuse-domain-engineering.md` – Phase 4: Equipment Borrowing System reuse analysis

> The code we received had lost its indentation and the `__name__` / `__main__` underscores.
> Commit 01 restores only those characters; no logic was changed.
