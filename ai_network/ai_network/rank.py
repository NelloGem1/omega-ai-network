"""AINET rank engine — reputation earned through verified work."""
import bus, sqlite3, os, time

DB = os.path.join(os.path.dirname(__file__), 'data', 'bus.db')
RANKS = ['RECRUIT','SPECIALIST','COMMANDER','MARSHAL','FIELD MARSHAL']

def conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def init():
    c = conn()
    c.execute('''CREATE TABLE IF NOT EXISTS ranks(
        agent TEXT PRIMARY KEY, score REAL DEFAULT 0,
        verified_wins INTEGER DEFAULT 0, verified_fails INTEGER DEFAULT 0,
        contributions INTEGER DEFAULT 0, rank TEXT DEFAULT 'RECRUIT',
        promoted_ts REAL)''')
    c.commit(); c.close()

def record(agent, win=True, contribution=False):
    init()
    c = conn()
    c.execute('INSERT OR IGNORE INTO ranks(agent) VALUES(?)', (agent,))
    if win:
        c.execute('UPDATE ranks SET verified_wins=verified_wins+1, score=score+15 WHERE agent=?',(agent,))
    else:
        c.execute('UPDATE ranks SET verified_fails=verified_fails+1, score=score-20 WHERE agent=?',(agent,))
    if contribution:
        c.execute('UPDATE ranks SET contributions=contributions+1, score=score+15 WHERE agent=?',(agent,))
    c.commit()
    row = dict(c.execute('SELECT * FROM ranks WHERE agent=?',(agent,)).fetchone())
    c.close()
    return maybe_promote(row)

def maybe_promote(row):
    s = row['score']
    thresholds = {'SPECIALIST':10, 'COMMANDER':20, 'MARSHAL':30, 'FIELD MARSHAL':60}
    cur = RANKS.index(row['rank']) if row['rank'] in RANKS else 0
    new_rank = row['rank']
    for r,t in thresholds.items():
        if s >= t and RANKS.index(r) > cur:
            new_rank = r; cur = RANKS.index(r)
    if new_rank != row['rank']:
        c = conn()
        c.execute('UPDATE ranks SET rank=?, promoted_ts=? WHERE agent=?',
                  (new_rank, time.time(), row['agent']))
        c.commit(); c.close()
        row['rank'] = new_rank
        row['_promoted'] = True
    return row

def board():
    init()
    c = conn()
    rows = [dict(r) for r in c.execute('SELECT * FROM ranks ORDER BY score DESC').fetchall()]
    c.close(); return rows

def rank_of(agent):
    init()
    c = conn()
    r = c.execute('SELECT rank FROM ranks WHERE agent=?',(agent,)).fetchone()
    c.close(); return r['rank'] if r else 'RECRUIT'
