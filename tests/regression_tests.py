"""Regression tests for the Library Management System.

Usage:   python tests/regression_tests.py

Each test runs library.py in an empty temporary folder (so it starts with a
fresh library.db), types menu choices and checks what the program prints.
They were written in Phase 1 to record what the legacy system does, and are
run again after every change to show that the behaviour is preserved.
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAM = os.path.join(ROOT, "library.py")
SEARCH, BORROW, RETURN, EXIT = "1", "2", "3", "4"


def run(folder, *typed):
    """Run one session in `folder`, typing the given lines, then Exit."""
    keys = "\n".join(list(typed) + [EXIT]) + "\n"
    result = subprocess.run([sys.executable, PROGRAM], input=keys, text=True,
                            capture_output=True, cwd=folder)
    return result.stdout + result.stderr


def sql(folder, statement, params=()):
    """Change the database directly, for situations the menu cannot create."""
    if not os.path.exists(os.path.join(folder, "library.db")):
        run(folder)                       # the first run creates the database
    con = sqlite3.connect(os.path.join(folder, "library.db"))
    con.execute(statement, params)
    con.commit()
    con.close()


def add_overdue_loan(folder, member, book, days_late):
    due = datetime.now() - timedelta(days=days_late)
    sql(folder, "INSERT INTO loans (member_id, book_id, borrow_date, due_date, returned) "
                "VALUES (?, ?, ?, ?, 0)",
        (member, book, (due - timedelta(days=14)).isoformat(), due.isoformat()))
    sql(folder, "UPDATE books SET available = available - 1 WHERE id = ?", (book,))


TESTS = []


def test(function):
    TESTS.append(function)
    return function


# ----------------------------------------------------------------- R6 search
@test
def search_by_author_ignores_case(d):                       # R6
    out = run(d, SEARCH, "martin")
    return ("1 Clean Code - Robert Martin" in out and "2 Refactoring - Martin Fowler" in out
            and "Design Patterns" not in out)


@test
def search_by_title(d):                                      # R6
    return "3 Design Patterns - Gamma et al." in run(d, SEARCH, "Design")


@test
def search_shows_borrowed_book_as_unavailable(d):            # R3, R6 (MR-01: copy count shown)
    run(d, BORROW, "S1", "3")
    return "3 Design Patterns - Gamma et al. Available: 0 of 1 copies" in run(d, SEARCH, "Design")


# ----------------------------------------------------------------- R1-R4 borrow
@test
def borrow_is_due_in_14_days(d):                             # R1, R4
    due = date.today() + timedelta(days=14)
    return f"Book borrowed. Due: {due}" in run(d, BORROW, "S1", "1")


@test
def unknown_member_is_rejected(d):                           # BR-1
    return "Member not found" in run(d, BORROW, "X9", "1")


@test
def inactive_member_is_rejected(d):                          # R1, BR-2
    sql(d, "UPDATE members SET status = 'SUSPENDED' WHERE id = 'S2'")
    return "Member is not active" in run(d, BORROW, "S2", "1")


@test
def status_check_is_case_sensitive(d):                       # BR-2
    sql(d, "UPDATE members SET status = 'active' WHERE id = 'S2'")
    return "Member is not active" in run(d, BORROW, "S2", "1")


@test
def unknown_book_is_rejected(d):                             # BR-3
    return "Book not found" in run(d, BORROW, "S1", "99")


@test
def unavailable_book_is_rejected(d):                         # R3, BR-4
    return "Book is unavailable" in run(d, BORROW, "S1", "3", BORROW, "S2", "3")


@test
def limit_is_three_books(d):                                 # R2, BR-5
    sql(d, "INSERT INTO books (id, title, author, available) "
           "VALUES (4, 'Legacy Code', 'Michael Feathers', 1)")
    out = run(d, BORROW, "S1", "1", BORROW, "S1", "2", BORROW, "S1", "3", BORROW, "S1", "4")
    return out.count("Book borrowed.") == 3 and "Borrowing limit reached" in out


@test
def member_is_checked_before_book(d):                        # BR-6 (check order)
    sql(d, "UPDATE members SET status = 'SUSPENDED' WHERE id = 'S2'")
    out = run(d, BORROW, "S2", "99")
    return "Member is not active" in out and "Book not found" not in out


# ----------------------------------------------------------------- R5 return / fine
@test
def return_on_time_has_no_fine(d):                           # R5
    out = run(d, BORROW, "S1", "1", RETURN, "S1", "1")
    return "Book returned" in out and "Fine:" not in out


@test
def late_return_costs_one_per_day(d):                        # R5, BR-7
    add_overdue_loan(d, "S1", 2, days_late=5)
    out = run(d, RETURN, "S1", "2")
    return "Book returned" in out and "Fine: 5" in out


@test
def return_without_loan_is_rejected(d):                      # BR-8
    return "Active loan not found" in run(d, RETURN, "S1", "1")


@test
def only_the_borrower_can_return(d):                         # BR-8
    return "Active loan not found" in run(d, BORROW, "S1", "1", RETURN, "S2", "1")


@test
def suspended_member_can_still_return(d):                    # BR-9
    run(d, BORROW, "S2", "1")
    sql(d, "UPDATE members SET status = 'SUSPENDED' WHERE id = 'S2'")
    return "Book returned" in run(d, RETURN, "S2", "1")


@test
def returned_book_can_be_borrowed_again(d):                  # BR-10
    out = run(d, BORROW, "S1", "3", RETURN, "S1", "3", BORROW, "S2", "3")
    return out.count("Book borrowed.") == 2


# ----------------------------------------------------------------- MR-01 copies
@test
def copies_are_shared_until_none_left(d):                    # MR-01
    out = run(d, BORROW, "S1", "2", BORROW, "S2", "2", SEARCH, "Refactoring")
    return out.count("Book borrowed.") == 2 and "Available: 0 of 2 copies" in out


@test
def member_cannot_hold_two_copies_of_one_book(d):            # MR-01, BR-14
    out = run(d, BORROW, "S1", "1", BORROW, "S1", "1", SEARCH, "Clean")
    return "Member already has a copy of this book" in out and "Available: 2 of 3 copies" in out


@test
def return_puts_one_copy_back(d):                            # MR-01
    out = run(d, BORROW, "S1", "2", BORROW, "S2", "2", RETURN, "S1", "2", SEARCH, "Refactoring")
    return "Available: 1 of 2 copies" in out


@test
def old_database_is_upgraded(d):                             # MR-01 (existing data kept)
    con = sqlite3.connect(os.path.join(d, "library.db"))     # a database made by the old version
    con.executescript("""
        CREATE TABLE members(id TEXT PRIMARY KEY, name TEXT, status TEXT);
        CREATE TABLE books(id INTEGER PRIMARY KEY, title TEXT, author TEXT, available INTEGER);
        CREATE TABLE loans(id INTEGER PRIMARY KEY AUTOINCREMENT, member_id TEXT, book_id INTEGER,
                           borrow_date TEXT, due_date TEXT, returned INTEGER);
        INSERT INTO members VALUES ('S1', 'Ali', 'ACTIVE');
        INSERT INTO books VALUES (1, 'Clean Code', 'Robert Martin', 0);
        INSERT INTO loans (member_id, book_id, borrow_date, due_date, returned)
            VALUES ('S1', 1, '2026-11-01T10:00:00', '2099-01-01T10:00:00', 0);""")
    con.close()
    out = run(d, SEARCH, "Clean", RETURN, "S1", "1", SEARCH, "Clean")
    return ("Available: 0 of 1 copies" in out and "Book returned" in out
            and "Available: 1 of 1 copies" in out)


# ----------------------------------------------------------------- menu / data
@test
def invalid_menu_choice(d):
    return "Invalid choice" in run(d, "7")


@test
def data_is_kept_between_runs(d):
    run(d, BORROW, "S1", "3")
    return "Book is unavailable" in run(d, BORROW, "S2", "3")


@test
def defect_d1_letters_as_book_id_crash_the_program(d):       # D1 (known defect)
    return "ValueError" in run(d, BORROW, "S1", "abc")


def main():
    failed = 0
    for t in TESTS:
        with tempfile.TemporaryDirectory() as folder:
            ok = t(folder)
        failed += not ok
        print(("PASS  " if ok else "FAIL  ") + t.__name__)
    print(f"\n{len(TESTS) - failed} of {len(TESTS)} tests passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
