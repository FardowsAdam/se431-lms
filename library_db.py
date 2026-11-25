"""Database layer (MR-02).

All SQL is in this file. The rest of the program only calls the methods of
LibraryDatabase and never touches the database directly. To replace SQLite
with another database, write a class with the same methods; nothing else
in the program has to change.
"""
import sqlite3

# Sample data, kept apart from table creation.
# MR-01: the library bought several copies of each book.
SAMPLE_MEMBERS = [("S1", "Ali", "ACTIVE"), ("S2", "Sara", "ACTIVE")]
SAMPLE_BOOKS = [  # id, title, author, copies
    (1, "Clean Code", "Robert Martin", 3),
    (2, "Refactoring", "Martin Fowler", 2),
    (3, "Design Patterns", "Gamma et al.", 1),
]


class LibraryDatabase:
    def __init__(self, path="library.db"):
        self.con = sqlite3.connect(path)
        self.con.row_factory = sqlite3.Row      # read columns by name, not row[0]
        self.create_tables()
        self.add_sample_data()

    def create_tables(self):
        self.con.executescript("""
            CREATE TABLE IF NOT EXISTS members(
                id TEXT PRIMARY KEY, name TEXT, status TEXT);
            CREATE TABLE IF NOT EXISTS books(
                id INTEGER PRIMARY KEY, title TEXT, author TEXT,
                available INTEGER, copies INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS loans(
                id INTEGER PRIMARY KEY AUTOINCREMENT, member_id TEXT, book_id INTEGER,
                borrow_date TEXT, due_date TEXT, returned INTEGER);
        """)
        # MR-01: a database created by the old version has no 'copies' column yet.
        columns = [row["name"] for row in self.con.execute("PRAGMA table_info(books)")]
        if "copies" not in columns:
            self.con.execute("ALTER TABLE books ADD COLUMN copies INTEGER DEFAULT 1")
        self.con.commit()

    def add_sample_data(self):
        for member in SAMPLE_MEMBERS:
            self.con.execute("INSERT OR IGNORE INTO members VALUES (?, ?, ?)", member)
        for book_id, title, author, copies in SAMPLE_BOOKS:
            self.con.execute(
                "INSERT OR IGNORE INTO books (id, title, author, available, copies) "
                "VALUES (?, ?, ?, ?, ?)", (book_id, title, author, copies, copies))
        self.con.commit()

    def find_member(self, member_id):
        return self.con.execute(
            "SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()

    def find_book(self, book_id):
        return self.con.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

    def search_books(self, text):
        pattern = "%" + text + "%"
        return self.con.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ?",
            (pattern, pattern)).fetchall()

    def count_open_loans(self, member_id):
        return self.con.execute(
            "SELECT COUNT(*) FROM loans WHERE member_id = ? AND returned = 0",
            (member_id,)).fetchone()[0]

    def find_open_loan(self, member_id, book_id):
        return self.con.execute(
            "SELECT * FROM loans WHERE member_id = ? AND book_id = ? AND returned = 0",
            (member_id, book_id)).fetchone()

    def add_loan(self, member_id, book_id, borrow_date, due_date):
        """Take one copy off the shelf and record the loan, saved together.
        Returns False if no copy was left."""
        taken = self.con.execute(
            "UPDATE books SET available = available - 1 WHERE id = ? AND available > 0",
            (book_id,)).rowcount
        if taken:
            self.con.execute(
                "INSERT INTO loans (member_id, book_id, borrow_date, due_date, returned) "
                "VALUES (?, ?, ?, ?, 0)", (member_id, book_id, borrow_date, due_date))
        self.con.commit()
        return taken == 1

    def close_loan(self, loan_id, book_id):
        """Mark the loan as returned and put the copy back, saved together."""
        self.con.execute("UPDATE loans SET returned = 1 WHERE id = ?", (loan_id,))
        self.con.execute(
            "UPDATE books SET available = available + 1 WHERE id = ? AND available < copies",
            (book_id,))
        self.con.commit()

    def close(self):
        self.con.close()
