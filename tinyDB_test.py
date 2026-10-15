from tinydb import TinyDB, Query

db = TinyDB('db.json')
db.truncate()

db.insert({'type': 'apple', 'count': 7})
db.insert({'type': 'peach', 'count': 3})

print(db.all())
