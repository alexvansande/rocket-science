#!/usr/bin/env python3
"""
Science ladder (docs/09): which science missions can a player physically fly at each science level?

Science is a threshold (never spent) that gates cards (price.science) and pads. For each level s it
keeps only the engines a player could buy (price.science <= s) and the pad they could own, asks
tower_search for the lightest stack that reaches each science mission, and checks it fits the pad.
Then it walks a greedy ladder: fly the best science mission available, add its reward, repeat.
Ignores money, hand luck and which missions are in the row: it's the best case.

Run from src/:  python3 science_ladder.py
"""
import json, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import tower_search as T
D = json.load(open('../data/cards.json')); B = json.load(open('../data/board.json')); O = json.load(open('../data/objectives.json'))
# board distance from Earth
adj = {}
for l in B['links']: adj.setdefault(l['a'], []).append(l['b']); adj.setdefault(l['b'], []).append(l['a'])
dist = {'earth': 0}; q = ['earth']
while q:
    s = q.pop(0)
    for t in adj[s]:
        if t not in dist: dist[t] = dist[s] + 1; q.append(t)
def need_dv(c):
    if c.get('deep'): return dist['ds%d' % c['deep']]
    return min(dist[a] for a in c['at'])
EQ = {q['name']: q['price']['science'] for q in D['equipment']}
PADS = [(0, 160, 'basic'), (1, 640, 'Orbital'), (3, 2560, 'Heavy'), (6, 3840, 'Super')]
pad = lambda s: max(p for p in PADS if p[0] <= s)
sci_missions = [o for o in O if o.get('reward', {}).get('kind') == 'science']
def flyable(o, s):
    c = o['check']; eq = [n for n in c.get('equip', [])]
    if any(EQ.get(n, 0) > s for n in eq): return None, 'needs ' + '/'.join(f'{n.title()} ⚛{EQ[n]}' for n in eq if EQ.get(n, 0) > s)
    payload = max(c.get('cargo', 0), 2.5 * max(len(eq), c.get('equipCount', 0), 1 if not c.get('cargo') else 0))
    T.set_active_cards(exclude=tuple(e['name'] for e in D['engines'] if e['price']['science'] > s))
    mass, tower = T.minmass_b(payload, need_dv(c))
    if tower is None: return None, 'no stack'
    lift = mass + payload; p = pad(s)
    if lift > p[1]: return None, f'{lift:.0f}t > {p[2]} pad {p[1]}t'
    return lift, ' + '.join(st['card'].title() for st in reversed(tower))
print(f"{'mission':22s} {'Δv':>3s} {'⚛':>2s}  " + "  ".join(f"s={s}" for s in range(0, 7)))
for o in sorted(sci_missions, key=lambda o: need_dv(o['check'])):
    r = o['reward']; cells = []
    for s in range(0, 7):
        lift, why = flyable(o, s); cells.append(' ok ' if lift else ' -- ')
    print(f"{o['name']:22s} {need_dv(o['check']):3d} {str(r.get('n', r.get('set'))):>2s}  " + "  ".join(cells))
print()
for s in (0, 1, 2, 3, 4):
    print(f"--- at ⚛{s} ({pad(s)[2]} pad, {pad(s)[1]}t)")
    for o in sorted(sci_missions, key=lambda o: need_dv(o['check'])):
        lift, why = flyable(o, s)
        print(f"   {o['name']:22s} {'OK  ' + str(round(lift)) + 't: ' if lift else 'no: '}{why}")

# Greedy ladder: start at s (if something gave you the first point), fly the best flyable science mission each time.
print("\nGreedy ladder (best single science mission each flight; sets counted as the next card's gain):")
for start in (1,):
    s, path, fam = start, [], {}
    for flight in range(1, 9):
        best = None
        for o in sci_missions:
            lift, _ = flyable(o, s)
            if not lift: continue
            r = o['reward']
            gain = r['n'] if 'n' in r else (r['set'][min(fam.get(o['name'], 0), 3)] - (r['set'][fam[o['name']] - 1] if fam.get(o['name']) else 0))
            if best is None or gain > best[0]: best = (gain, o['name'])
        if not best: break
        s += best[0]; fam[best[1]] = fam.get(best[1], 0) + 1 if 'set' in [o for o in sci_missions if o['name'] == best[1]][0]['reward'] else 0
        path.append(f"{best[1].title()} +{best[0]} → ⚛{s}")
    print("  start ⚛%d: " % start + " | ".join(path))
