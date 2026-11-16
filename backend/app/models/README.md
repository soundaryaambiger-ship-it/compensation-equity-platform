SQLAlchemy table definitions are in entities.py. __init__.py imports all models so Base.metadata can discover every table when init_db.py creates the schema.
