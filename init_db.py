from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('notes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route to display all notes
@app.route('/')
def index():
    conn = get_db_connection()
    notes = conn.execute('''
        SELECT notes.id, notes.title, notes.content, notes.is_important, notes.is_urgent,
               GROUP_CONCAT(tags.name) AS tags
        FROM notes
        LEFT JOIN note_tags ON notes.id = note_tags.note_id
        LEFT JOIN tags ON note_tags.tag_id = tags.id
        GROUP BY notes.id
    ''').fetchall()
    conn.close()
    return render_template('index.html', notes=notes)

# Route to add a new note
@app.route('/add', methods=('GET', 'POST'))
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = request.form['tags'].split(',')
        is_important = 1 if 'is_important' in request.form else 0
        is_urgent = 1 if 'is_urgent' in request.form else 0

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO notes (title, content, is_important, is_urgent) VALUES (?, ?, ?, ?)',
                    (title, content, is_important, is_urgent))
        note_id = cur.lastrowid
        for tag in tags:
            tag = tag.strip()
            if tag:
                cur.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                tag_id = cur.execute('SELECT id FROM tags WHERE name = ?', (tag,)).fetchone()['id']
                cur.execute('INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_note.html')

# Route to view a single note and its history
@app.route('/note/<int:note_id>')
def view_note(note_id):
    conn = get_db_connection()
    note = conn.execute('''
        SELECT notes.*, GROUP_CONCAT(tags.name) AS tags
        FROM notes
        LEFT JOIN note_tags ON notes.id = note_tags.note_id
        LEFT JOIN tags ON note_tags.tag_id = tags.id
        WHERE notes.id = ?
    ''', (note_id,)).fetchone()
    
    # Fetch the history of the note
    history = conn.execute('''
        SELECT * FROM note_history
        WHERE note_id = ?
        ORDER BY updated_at DESC
    ''', (note_id,)).fetchall()
    
    conn.close()
    return render_template('view_note.html', note=note, history=history)

# Route to edit an existing note
@app.route('/edit/<int:note_id>', methods=('GET', 'POST'))
def edit_note(note_id):
    conn = get_db_connection()
    note = conn.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        tags = request.form['tags'].split(',')
        is_important = 1 if 'is_important' in request.form else 0
        is_urgent = 1 if 'is_urgent' in request.form else 0

        conn.execute('UPDATE notes SET title = ?, content = ?, is_important = ?, is_urgent = ? WHERE id = ?',
                     (title, content, is_important, is_urgent, note_id))
        conn.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
        for tag in tags:
            tag = tag.strip()
            if tag:
                conn.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                tag_id = conn.execute('SELECT id FROM tags WHERE name = ?', (tag,)).fetchone()['id']
                conn.execute('INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)', (note_id, tag_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    tags = ', '.join([tag['name'] for tag in conn.execute('''
        SELECT tags.name
        FROM tags
        JOIN note_tags ON tags.id = note_tags.tag_id
        WHERE note_tags.note_id = ?
    ''', (note_id,)).fetchall()])
    conn.close()
    return render_template('edit_note.html', note=note, tags=tags)

# Route to delete a note
@app.route('/delete/<int:note_id>', methods=('POST',))
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
