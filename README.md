# SE431 – Library Management System (LMS) Maintenance Project

Legacy Library Management System handed to the maintenance team.

- Single file: `library.py` (~200 physical lines, about 100 logical LOC)
- Python 3 + SQLite (`library.db`, created in the working directory)
- Console menu: Search, Borrow, Return, Exit

## Run

```bash
python library.py
```

Seed data: members `S1` (Ali) and `S2` (Sara), books 1–3.

> Note: the code we received had lost its indentation and the `__name__` / `__main__`
> underscores in transit. This commit restores them so the file runs. No logic was changed.
