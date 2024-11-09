import sqlite3

conn = sqlite3.connect('notes.db')
c = conn.cursor()

# Create `notes` table
c.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        is_important INTEGER DEFAULT 0,
        is_urgent INTEGER DEFAULT 0
    )
''')

# Create `tags` table
c.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
''')

# Create `note_tags` table for many-to-many relationship
c.execute('''
    CREATE TABLE IF NOT EXISTS note_tags (
        note_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
    )
''')

# Create `users` table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
''')

# Create `note_history` table to track updates
c.execute('''
    CREATE TABLE IF NOT EXISTS note_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER,
        title TEXT,
        content TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
    )
''')

# Trigger to log history on `notes` updates
c.execute('''
    CREATE TRIGGER IF NOT EXISTS log_note_update
    AFTER UPDATE ON notes
    FOR EACH ROW
    BEGIN
        INSERT INTO note_history (note_id, title, content) VALUES (OLD.id, OLD.title, OLD.content);
    END;
''')

conn.commit()
conn.close()
print("Database initialized with 5 tables and a trigger.")
