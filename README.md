# SE431 – Library Management System (LMS) Maintenance Project

Legacy Library Management System given to the maintenance team: Python + SQLite, console menu (Search, Borrow, Return, Exit).

## Run

```bash
python library.py
```

Sample data: members `S1` (Ali) and `S2` (Sara), books 1–3.

## Regression tests

```bash
python tests/regression_tests.py
```

Each test runs the program with typed input and checks what it prints.

## Documents

- `docs/01-program-comprehension.md` – Phase 1: program comprehension and legacy-system analysis

> The code we received had lost its indentation and the `__name__` / `__main__` underscores.
> Commit 01 restores only those characters; no logic was changed.
