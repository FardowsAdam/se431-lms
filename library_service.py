"""Business rules of the library: no input(), no print(), no SQL.

Refactorings (Phase 3):
  RF-1 Extract Method: borrow() is split into one small function per rule.
  RF-2 Separate responsibilities: the rules are here, the menu is in library.py.
  RF-3 Replace magic numbers with named constants (below).
"""
from datetime import datetime, timedelta

MAX_BOOKS = 3          # R2
LOAN_DAYS = 14         # R4
FINE_PER_DAY = 1       # R5
ACTIVE = "ACTIVE"      # R1


class LibraryError(Exception):
    """A business rule refused the request; its text is shown to the user."""


def search_books(db, text):
    return db.search_books(text)                     # R6


def borrow(db, member_id, book_id):
    """Lend one copy and return the due date, or raise LibraryError."""
    check_member(db, member_id)                      # BR-1, BR-2
    check_book(db, book_id)                          # BR-3, BR-4
    check_not_holding(db, member_id, book_id)        # BR-14
    check_limit(db, member_id)                       # BR-5
    return record_loan(db, member_id, book_id)       # R4


def check_member(db, member_id):
    member = db.find_member(member_id)
    if not member:
        raise LibraryError("Member not found")
    if member["status"] != ACTIVE:
        raise LibraryError("Member is not active")


def check_book(db, book_id):
    book = db.find_book(book_id)
    if not book:
        raise LibraryError("Book not found")
    if book["available"] == 0:
        raise LibraryError("Book is unavailable")


def check_not_holding(db, member_id, book_id):
    if db.find_open_loan(member_id, book_id):
        raise LibraryError("Member already has a copy of this book")


def check_limit(db, member_id):
    if db.count_open_loans(member_id) >= MAX_BOOKS:
        raise LibraryError("Borrowing limit reached")


def record_loan(db, member_id, book_id):
    today = datetime.now()
    due = today + timedelta(days=LOAN_DAYS)
    if not db.add_loan(member_id, book_id, today.isoformat(), due.isoformat()):
        raise LibraryError("Book is unavailable")
    return due


def return_book(db, member_id, book_id):
    """Close the loan and return the fine (0 if on time), or raise LibraryError."""
    loan = db.find_open_loan(member_id, book_id)     # BR-8
    if not loan:
        raise LibraryError("Active loan not found")
    fine = calculate_fine(loan["due_date"])
    db.close_loan(loan["id"], book_id)               # BR-10
    return fine


def calculate_fine(due_date):
    days_late = (datetime.now() - datetime.fromisoformat(due_date)).days
    return max(days_late, 0) * FINE_PER_DAY          # BR-7: whole days only
