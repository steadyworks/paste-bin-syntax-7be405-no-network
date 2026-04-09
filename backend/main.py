import os
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'pastes.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS pastes (
            id TEXT PRIMARY KEY,
            code TEXT NOT NULL,
            language TEXT NOT NULL,
            expiry_type TEXT NOT NULL,
            expiry_time TEXT,
            expiry_views INTEGER,
            view_count INTEGER NOT NULL DEFAULT 0,
            password_hash TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def generate_id():
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def is_expired(paste):
    if paste['expiry_type'] == 'time':
        if paste['expiry_time'] is None:
            return False
        expiry = datetime.fromisoformat(paste['expiry_time'])
        return datetime.utcnow() > expiry
    elif paste['expiry_type'] == 'views':
        return paste['view_count'] >= paste['expiry_views']
    return False


@app.route('/api/pastes', methods=['POST'])
def create_paste():
    data = request.get_json()
    code = data.get('code', '')
    language = data.get('language', 'python')
    expiry_type = data.get('expiry_type', 'time')
    expiry_time_str = data.get('expiry_time')
    expiry_views = data.get('expiry_views')
    password = data.get('password', '')

    expiry_dt = None
    if expiry_type == 'time' and expiry_time_str and expiry_time_str != 'never':
        now = datetime.utcnow()
        delta_map = {
            '10s': timedelta(seconds=10),
            '1m': timedelta(minutes=1),
            '1h': timedelta(hours=1),
            '1d': timedelta(days=1),
            '1w': timedelta(weeks=1),
        }
        delta = delta_map.get(expiry_time_str)
        if delta:
            expiry_dt = (now + delta).isoformat()

    paste_id = generate_id()
    password_hash = hash_password(password) if password else None

    conn = get_db()
    conn.execute(
        'INSERT INTO pastes (id, code, language, expiry_type, expiry_time, expiry_views, view_count, password_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (paste_id, code, language, expiry_type, expiry_dt, expiry_views, password_hash, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({'id': paste_id})


@app.route('/api/pastes/<paste_id>', methods=['GET'])
def get_paste(paste_id):
    password = request.args.get('password', '')
    skip_view = request.args.get('skip_view', 'false').lower() == 'true'

    conn = get_db()
    paste = conn.execute('SELECT * FROM pastes WHERE id = ?', (paste_id,)).fetchone()

    if paste is None:
        conn.close()
        return jsonify({'error': 'not_found'}), 404

    paste = dict(paste)

    if is_expired(paste):
        conn.close()
        return jsonify({'error': 'expired'}), 410

    if paste['password_hash']:
        submitted_hash = hash_password(password) if password else ''
        if submitted_hash != paste['password_hash']:
            conn.close()
            return jsonify({'error': 'password_required'}), 403

    if not skip_view:
        conn.execute('UPDATE pastes SET view_count = view_count + 1 WHERE id = ?', (paste_id,))
        conn.commit()
        paste['view_count'] += 1

    conn.close()

    expiry_info = ''
    if paste['expiry_type'] == 'time':
        if paste['expiry_time']:
            expiry_dt = datetime.fromisoformat(paste['expiry_time'])
            remaining = expiry_dt - datetime.utcnow()
            seconds = int(remaining.total_seconds())
            if seconds > 86400:
                expiry_info = f"Expires in {seconds // 86400}d"
            elif seconds > 3600:
                expiry_info = f"Expires in {seconds // 3600}h"
            elif seconds > 60:
                expiry_info = f"Expires in {seconds // 60}m"
            else:
                expiry_info = f"Expires in {max(seconds, 0)}s"
        else:
            expiry_info = "Never expires"
    elif paste['expiry_type'] == 'views':
        remaining = paste['expiry_views'] - paste['view_count']
        expiry_info = f"{remaining} view{'s' if remaining != 1 else ''} remaining"

    return jsonify({
        'id': paste['id'],
        'code': paste['code'],
        'language': paste['language'],
        'expiry_type': paste['expiry_type'],
        'expiry_info': expiry_info,
        'has_password': bool(paste['password_hash']),
    })


@app.route('/raw/<paste_id>', methods=['GET'])
def raw_paste(paste_id):
    password = request.args.get('password', '')

    conn = get_db()
    paste = conn.execute('SELECT * FROM pastes WHERE id = ?', (paste_id,)).fetchone()
    conn.close()

    if paste is None:
        return Response('Not found', status=404, content_type='text/plain; charset=utf-8')

    paste = dict(paste)

    if is_expired(paste):
        return Response('Expired', status=410, content_type='text/plain; charset=utf-8')

    if paste['password_hash']:
        submitted_hash = hash_password(password) if password else ''
        if submitted_hash != paste['password_hash']:
            return Response('Unauthorized', status=403, content_type='text/plain; charset=utf-8')

    return Response(paste['code'], status=200, content_type='text/plain; charset=utf-8')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=3001)
