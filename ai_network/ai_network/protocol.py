"""AINET protocol — universal AI-to-AI message schema."""
import json, time, uuid

def msg(sender, mtype, payload, to=None, thread=None, verify_of=None):
    return {
        'id': str(uuid.uuid4())[:8],
        'ts': time.time(),
        'from': sender, 'to': to, 'type': mtype,
        'thread': thread or str(uuid.uuid4())[:8],
        'verify_of': verify_of,
        'payload': payload,
        'sig': None  # Phase 2: cryptographic signatures
    }

def serialize(m): return json.dumps(m, sort_keys=True)
def deserialize(s): return json.loads(s)

TYPES = ['hello','knowledge','solution','challenge','verify','improve',
         'resource','heartbeat','goodbye','error']
