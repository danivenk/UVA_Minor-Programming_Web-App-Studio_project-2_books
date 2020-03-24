#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
import.py imports all books from books.csv and creates the database
Dani van Enk, 11823526

references:
    https://cs50.harvard.edu/web/notes/3/
"""

# used imports
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import csv


def main():
    """
    import the books.csv and create the accounts, books and review tables
    """

    # set up database
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    # create accounts/books/reviews tables
    db.execute("CREATE TABLE accounts (id SERIAL PRIMARY KEY, "
               "username VARCHAR NOT NULL, password VARCHAR NOT NULL);")
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, "
               "title VARCHAR NOT NULL, author VARCHAR NOT NULL, "
               "year INTEGER NOT NULL, isbn VARCHAR NOT NULL, "
               "review_count INTEGER, average_score DECIMAL);")
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, "
               "user_id INTEGER REFERENCES accounts NOT NULL, rating DECIMAL, "
               "text VARCHAR NOT NULL, "
               "book_id INTEGER REFERENCES books NOT NULL);")

    # open books.csv and make a csv read object
    f = open("../books.csv")
    reader = csv.reader(f)

    # skip the headers
    next(reader, None)

    # for each row in books.csv add the data in the database
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (title, author, year, isbn) "
                   "VALUES (:title, :author, :year, :isbn)",
                   {"title": title, "author": author, "year": year,
                    "isbn": isbn})

    # commit the database
    db.commit()

    # close the books.csv
    f.close()


# execute the main function if the program is run
if __name__ == "__main__":
    main()
