"""Compare the KiCad netlist with the Eagle Peach Fuzz board netlist (eagle_brd_nets.txt)."""
import re, sys
REF = {'GAIN': 'RV1', 'TONE': 'RV2', 'VOLUME': 'RV3', 'IC1': 'U1', 'IC2': 'U2', 'IC3': 'U3', 'RLED': 'R13',
       'R8*': 'R8', 'R10*': 'R10', 'C7*': 'C7', 'C11*': 'C11',
       'IN': 'J1', 'OUT': 'J2', '9V': 'J3', '-V': 'J4', 'IG': 'J5', 'OG': 'J6', 'LS': 'J7', 'LG': 'J8',
       'B1': 'J9', 'B2': 'J10', 'B3': 'J11', 'B4': 'J12'}
ELEC = {'C2', 'C6', 'C10', 'C15'}
NONPOL = re.compile(r'^(R\d+|C\d+)$')
def eag(ref, pad):
    r = REF.get(ref, ref)
    if r in ELEC: return r, {'+': '1', '-': '2'}[pad]
    if NONPOL.match(r): return r, '*'
    if r == 'D1': return r, {'A': '2', 'C': '1'}[pad]
    if r == 'D2': return r, {'ANODE': '2', 'P$1': '1'}[pad]
    return r, pad
def kic(ref, pad):
    if NONPOL.match(ref) and ref not in ELEC: return ref, '*'
    return ref, pad
E_ = set()
for l in open(sys.argv[1]):
    q = l.split()
    if len(q) < 2 or "('" in l: continue
    n = frozenset(eag(*x.rsplit('.', 1)) for x in q[1:])
    if len(n) > 1: E_.add(n)
K_ = set()
for b in re.split(r'\(net\s*\(code', open(sys.argv[2]).read())[1:]:
    n = frozenset(kic(r, p) for r, p in re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"', b) if not r.startswith('#'))
    if len(n) > 1: K_.add(n)
print('matches the Eagle board:', E_ == K_)
for x in E_ - K_: print(' eagle only:', sorted(x))
for x in K_ - E_: print(' kicad only:', sorted(x))
