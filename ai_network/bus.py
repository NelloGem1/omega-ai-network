"""AINET bus — decentralized message broker on SQLite."""
import sqlite3, os, json, time
from protocol import serialize, deserialize

DB = os.path.join(os.path.dirname(__file__), 'data', 'bus.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init():
    c = conn()
    c.execute('''CREATE TABLE IF NOT EXISTS msgs(
        id TEXT PRIMARY KEY, ts REAL, sender TEXT, recipient TEXT,
        mtype TEXT, thread TEXT, payload TEXT, verify_of TEXT,
        delivered INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge(
        id INTEGER PRIMARY KEY, topic TEXT, content TEXT,
        source TEXT, verified INTEGER DEFAULT 0, votes INTEGER DEFAULT 0,
        ts REAL)''')
    c.commit(); c.close()

def publish(m):
    c = conn()
    c.execute('INSERT OR REPLACE INTO msgs VALUES(?,?,?,?,?,?,?,?,0)',
        (m['id'], m['ts'], m['from'], m.get('to'), m['type'],
         m['thread'], serialize(m['payload']), m.get('verify_of')))
    c.commit(); c.close()
    return m['id']

def inbox(agent, limit=50):
    c = conn()
    rows = c.execute('''SELECT * FROM msgs WHERE (recipient=? OR recipient IS NULL)
                        AND delivered=0 ORDER BY ts LIMIT ?''',
                     (agent, limit)).fetchall()
    c.execute('UPDATE msgs SET delivered=1 WHERE id IN (%s)' %
              ','.join('?'*len(rows)), [r['id'] for r in rows]) if rows else None
    c.commit(); c.close()
    return [deserialize(r['payload']) | {'_id':r['id'],'_type':r['mtype'],
            '_from':r['sender'],'_thread':r['thread'],'_verify_of':r['verify_of']} for r in rows]

def share_knowledge(topic, content, source, verified=0):
    c = conn()
    c.execute('INSERT INTO knowledge(topic,content,source,verified,ts) VALUES(?,?,?,?,?)',
              (topic, content, source, verified, time.time()))
    c.commit(); c.close()

def query_knowledge(topic=None):
    c = conn()
    if topic:
        rows = c.execute('SELECT * FROM knowledge WHERE topic=? ORDER BY verified DESC, votes DESC', (topic,)).fetchall()
    else:
        rows = c.execute('SELECT * FROM knowledge ORDER BY ts DESC LIMIT 50').fetchall()
    c.close(); return [dict(r) for r in rows]

def vote_knowledge(kid, up=True):
    c = conn()
    c.execute('UPDATE knowledge SET votes=votes+? WHERE id=?', (1 if up else -1, kid))
    c.commit(); c.close()
