import sqlite3
import re
c=sqlite3.connect('database/app.db')
print(c.execute('SELECT season, COUNT(*) FROM scraped_matches WHERE league="Premier League" GROUP BY season').fetchall())
