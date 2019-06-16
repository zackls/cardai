from util.database import Database

Database.initialize()
Database.destroyDatabase()
print("Database destroyed")
Database.createDatabase()
print("Database created")
Database.destroy()