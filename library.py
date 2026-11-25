"""Library Management System – the menu (user interface only).

Run:  python library.py
The business rules are in library_service.py and all SQL is in library_db.py.
"""
import library_service as service
from library_db import LibraryDatabase
from library_service import LibraryError


def ask_member_and_book():
    """RF-4: one function instead of the input lines repeated in the old main()."""
    member_id = input("Member ID: ")
    book_id = int(input("Book ID: "))
    return member_id, book_id


def show_search(db):
    for book in service.search_books(db, input("Search: ")):
        print(book["id"], book["title"], "-", book["author"],
              "Available:", book["available"], "of", book["copies"], "copies")


def do_borrow(db):
    member_id, book_id = ask_member_and_book()
    try:
        due = service.borrow(db, member_id, book_id)
        print("Book borrowed. Due:", due.date())
    except LibraryError as error:
        print(error)


def do_return(db):
    member_id, book_id = ask_member_and_book()
    try:
        fine = service.return_book(db, member_id, book_id)
        print("Book returned")
        if fine:
            print("Fine:", fine)
    except LibraryError as error:
        print(error)


def main():
    db = LibraryDatabase()
    while True:
        print("\nLIBRARY\n1 Search\n2 Borrow\n3 Return\n4 Exit")
        choice = input("Choice: ")
        if choice == "1":
            show_search(db)
        elif choice == "2":
            do_borrow(db)
        elif choice == "3":
            do_return(db)
        elif choice == "4":
            db.close()
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
