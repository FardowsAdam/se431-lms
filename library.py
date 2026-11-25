
from datetime import datetime, timedelta

from library_db import LibraryDatabase


def setup():
    # MR-02: the database is reached only through LibraryDatabase
    return LibraryDatabase()
def search_books(db, text):
    rows = db.search_books(text)

    for row in rows:
        # MR-01: show how many copies are on the shelf
        print(row["id"], row["title"], "-", row["author"],
              "Available:", row["available"], "of", row["copies"], "copies")

    return rows
def borrow(db, member_id, book_id):
    member = db.find_member(member_id)

    if not member:
        print("Member not found")
        return False

    if member["status"] != "ACTIVE":
        print("Member is not active")
        return False

    book = db.find_book(book_id)

    if not book:
        print("Book not found")
        return False

    if book["available"] == 0:
        print("Book is unavailable")
        return False

    # MR-01 (new rule BR-14): with several copies a member could borrow the
    # same title twice; the old system made that impossible, so we keep it so.
    if db.find_open_loan(member_id, book_id):
        print("Member already has a copy of this book")
        return False

    if db.count_open_loans(member_id) >= 3:
        print("Borrowing limit reached")
        return False

    today = datetime.now()
    due = today + timedelta(days=14)

    if not db.add_loan(member_id, book_id, today.isoformat(), due.isoformat()):
        print("Book is unavailable")
        return False

    print("Book borrowed. Due:", due.date())

    return True
def return_book(db, member_id, book_id):
    loan = db.find_open_loan(member_id, book_id)

    if not loan:
        print("Active loan not found")
        return False

    due = datetime.fromisoformat(loan["due_date"])
    today = datetime.now()

    late = (today - due).days
    fine = late if late > 0 else 0

    db.close_loan(loan["id"], book_id)

    print("Book returned")

    if fine:
        print("Fine:", fine)

    return True
def main():
    db = setup()
    while True:
        print("\nLIBRARY")
        print("1 Search")
        print("2 Borrow")
        print("3 Return")
        print("4 Exit")

        choice = input("Choice: ")

        if choice == "1":
            text = input("Search: ")
            search_books(db, text)

        elif choice == "2":
            member = input("Member ID: ")
            book = int(input("Book ID: "))
            borrow(db, member, book)

        elif choice == "3":
            member = input("Member ID: ")
            book = int(input("Book ID: "))
            return_book(db, member, book)

        elif choice == "4":
            db.close()
            break

        else:
            print("Invalid choice")
if __name__ == "__main__":
    main()
