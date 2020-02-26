#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
import.py
Dani van Enk, 11823526
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import csv


def main():
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, "
               "title VARCHAR NOT NULL, author VARCHAR NOT NULL, "
               "year INTEGER NOT NULL, isbn VARCHAR NOT NULL, "
               "review_count INTEGER, average_score DECIMAL);")
    db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, "
               "username VARCHAR NOT NULL, rating DECIMAL, "
               "text VARCHAR NOT NULL, book_id INTEGER REFERENCES books);")

    f = open("../books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (title, author, year, isbn) "
                   "VALUES (:title, :author, :year, :isbn)",
                   {"title": title, "author": author, "year": year,
                    "isbn": isbn})
    db.commit()


if __name__ == "__main__":
    main()
