# app.py
"""
Simple Flask web app to view and edit the captures.db SQLite database.

Usage:
1. Install dependencies:
   pip install flask
2. Place this file in the same folder as captures.db (or let init_db.py create it first).
3. Run:
   python simple_sqlite_editor_app.py
4. Open http://127.0.0.1:5000 in a browser on the same machine.

Features:
- List rows in captures table
- Add a new capture job (is_on=1)
- Edit image_path and captured_at fields inline
- Toggle is_on between 0 and 1
- Delete a row

This single-file app uses Flask and renders the HTML template with render_template_string so no separate template files are required.
"""
from flask import Flask, g, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime

DB_PATH = 'captures.db'
app = Flask(__name__)

# ---------- Database helpers ----------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        need_init = not os.path.exists(DB_PATH)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        if need_init:
            # create table if missing
            cur = db.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                is_on INTEGER DEFAULT 0,
                image_path TEXT,
                captured_at TEXT
            )''')
            db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------- Routes ----------

INDEX_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>captures.db Editor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="p-3">
    <div class="container">
      <h1 class="mb-3">captures.db Editor</h1>

      <div class="mb-3">
        <button id="btn-add" class="btn btn-primary">Add capture job (is_on = 1)</button>
        <button id="btn-refresh" class="btn btn-secondary">Refresh</button>
      </div>

      <div id="alert-placeholder"></div>

      <table class="table table-striped" id="rows-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>is_on</th>
            <th>image_path</th>
            <th>captured_at</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody></tbody>
      </table>

      <p class="text-muted small">Note: This editor runs locally and edits the captures.db file in the same folder as the server. Do not expose it to the public network without additional security.</p>
    </div>

<script>
async function fetchRows(){
  const res = await fetch('/api/rows');
  const data = await res.json();
  const tbody = document.querySelector('#rows-table tbody');
  tbody.innerHTML = '';
  data.rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.id}</td>
      <td><button class="btn btn-sm btn-toggle" data-id="${r.id}">${r.is_on}</button></td>
      <td><input class="form-control form-control-sm inp-path" data-id="${r.id}" value="${r.image_path || ''}"></td>
      <td><input class="form-control form-control-sm inp-ts" data-id="${r.id}" value="${r.captured_at || ''}"></td>
      <td>
        <button class="btn btn-sm btn-save" data-id="${r.id}">Save</button>
        <button class="btn btn-sm btn-delete btn-danger" data-id="${r.id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function showAlert(msg, type='success'){
  const ph = document.getElementById('alert-placeholder');
  ph.innerHTML = `<div class="alert alert-${type} alert-dismissible">${msg}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

document.addEventListener('click', async (e) =>{
  if(e.target.matches('#btn-add')){
    const res = await fetch('/api/add', {method:'POST'});
    const j = await res.json();
    showAlert('Added job id=' + j.id, 'success');
    fetchRows();
  }
  if(e.target.matches('#btn-refresh')){
    fetchRows();
  }
  if(e.target.matches('.btn-save')){
    const id = e.target.dataset.id;
    const path = document.querySelector('.inp-path[data-id="'+id+'"]').value;
    const ts = document.querySelector('.inp-ts[data-id="'+id+'"]').value;
    const res = await fetch('/api/update', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({id: id, image_path: path, captured_at: ts})
    });
    const j = await res.json();
    if(j.success) showAlert('Saved id=' + id, 'success'); else showAlert('Save failed: '+j.error, 'danger');
    fetchRows();
  }
  if(e.target.matches('.btn-delete')){
    if(!confirm('Delete this row?')) return;
    const id = e.target.dataset.id;
    const res = await fetch('/api/delete', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({id: id})
    });
    const j = await res.json();
    if(j.success) showAlert('Deleted id=' + id, 'success'); else showAlert('Delete failed: '+j.error, 'danger');
    fetchRows();
  }
  if(e.target.matches('.btn-toggle')){
    const id = e.target.dataset.id;
    const current = e.target.textContent.trim();
    const newv = current === '1' ? 0 : 1;
    const res = await fetch('/api/toggle', {
      method:'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({id: id, is_on: newv})
    });
    const j = await res.json();
    if(j.success) showAlert('Toggled id=' + id + ' -> ' + newv, 'success'); else showAlert('Toggle failed: '+j.error, 'danger');
    fetchRows();
  }
});

// initial load
fetchRows();
</script>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/api/rows')
def api_rows():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, is_on, image_path, captured_at FROM captures ORDER BY id')
    rows = [dict(r) for r in cur.fetchall()]
    return jsonify(rows=rows)

@app.route('/api/add', methods=['POST'])
def api_add():
    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO captures (is_on) VALUES (1)')
    db.commit()
    return jsonify(success=True, id=cur.lastrowid)

@app.route('/api/update', methods=['POST'])
def api_update():
    data = request.get_json()
    try:
        id = int(data.get('id'))
        image_path = data.get('image_path') or None
        captured_at = data.get('captured_at') or None
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE captures SET image_path=?, captured_at=? WHERE id=?', (image_path, captured_at, id))
        db.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/api/delete', methods=['POST'])
def api_delete():
    data = request.get_json()
    try:
        id = int(data.get('id'))
        db = get_db()
        cur = db.cursor()
        cur.execute('DELETE FROM captures WHERE id=?', (id,))
        db.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/api/toggle', methods=['POST'])
def api_toggle():
    data = request.get_json()
    try:
        id = int(data.get('id'))
        is_on = 1 if int(data.get('is_on')) else 0
        db = get_db()
        cur = db.cursor()
        cur.execute('UPDATE captures SET is_on=? WHERE id=?', (is_on, id))
        db.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
