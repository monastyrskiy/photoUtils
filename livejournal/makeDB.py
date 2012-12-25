#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

db = 'livejournal.db'
conn = sqlite3.connect(db)

conn.execute('DROP TABLE IF EXISTS users')
conn.execute('DROP TABLE IF EXISTS friends')
conn.execute('DROP TABLE IF EXISTS journals')

conn.execute('''CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL)'''
    )

conn.execute('''CREATE TABLE friends (
    user_id INTEGER,
    journal_id INTEGER,
    add_date TEXT)''',
    )

conn.execute('''CREATE TABLE journals (
    journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    login VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL)'''
    )


conn.execute('''
    INSERT INTO journals (name, login, password)
    VALUES ('monastyrskiy', 'monastyrskiy', 'Burisoma1')'''
    )

conn.commit()
conn.close()
