"""AC comparison of the Peach Fuzz tone sections (ngspice via KiCad's libngspice). Run with KiCad's python3.
Source = LM386 output (0 ohm). Reports overall gain (dB) from the LM386 output to the VOLUME pot top (volume at max).
 orig : Big Muff tone (R11 39k + C13 10n / R12 10k + C14 470n, TONE B10k) -> VOLUME A100k
 pf2  : James stack as built (Peach Fuzz 2) -> C19 -> R18 10k into an inverting stage (virtual ground), gain -R17/R18
 fix  : same James stack -> C19 -> non-inverting stage (1M bias), gain 1 + R17/R18"""
import ctypes as C, numpy as np
ng = C.CDLL('/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.dylib')
PR = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p); EX = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
_p = PR(lambda s, i, p: 0); _s = PR(lambda s, i, p: 0); _e = EX(lambda *a: 0)
ng.ngSpice_Init(_p, _s, _e, None, None, None, None)
class VI(C.Structure):
    _fields_ = [('n', C.c_char_p), ('t', C.c_int), ('f', C.c_short), ('d', C.POINTER(C.c_double)), ('c', C.c_void_p), ('l', C.c_int)]
ng.ngGet_Vec_Info.restype = C.POINTER(VI)
class VC(C.Structure): _fields_ = [('r', C.c_double), ('i', C.c_double)]
def cvec(n):
    p = ng.ngGet_Vec_Info(n.encode()).contents
    if p.d: return np.array(p.d[:p.l]).astype(complex)
    c = C.cast(p.c, C.POINTER(VC)); return np.array([complex(c[k].r, c[k].i) for k in range(p.l)])
F = [50, 100, 200, 400, 800, 1600, 3200, 6400]
def pot(name, a, b, w, total, pos):   # pos 0..1 = fraction of resistance from pin a (pin 1) to wiper
    r1 = max(total * pos, 1); r2 = max(total * (1 - pos), 1)
    return f'R{name}a {a} {w} {r1:.0f}\nR{name}b {w} {b} {r2:.0f}\n'
def run(kind, tone=0.5, bass=0.5, treb=0.5, r17=180e3, r18=10e3):
    n = '* tone\nVin in 0 dc 0 ac 1\nC12 in t 1u\n'
    if kind == 'orig':
        n += 'R11 t h1 39k\nC13 h1 T3 10n\nR12 t T1 10k\nC14 T1 0 470n\n' + pot('T', 'T1', 'T3', 'out', 10e3, tone) + 'Rvol out 0 100k\n'
    else:
        n += 'R11 t B3 100k\nC14 B3 B2 470p\n' + pot('B', 'B1', 'B3', 'B2', 1e6, bass) + 'C17 B2 B1 4.7n\nR12 B1 0 10k\n'
        n += 'R13 B2 o 180k\nC18 t T3 330p\n' + pot('T', 'T1', 'T3', 'o', 500e3, treb) + 'C13 T1 0 3.3n\nR14 o 0 1Meg\nC19 o x 470n\n'
        if kind == 'pf2':
            n += f'R18 x inv {r18:.0f}\nR17 inv out {r17:.0f}\nE1 out 0 0 inv 1e6\n'
        else:
            n += f'Rb x 0 1Meg\nE1 out 0 x inv 1e6\nR17 out inv {r17:.0f}\nR18 inv c {r18:.0f}\nCg c 0 22u\n'
        n += 'Rvol out 0 100k\n'
    n += '.options noacct\n.end'
    L = n.split('\n'); arr = (C.c_char_p * (len(L) + 1))(*[x.encode() for x in L], None)
    ng.ngSpice_Command(b'destroy all'); ng.ngSpice_Circ(arr)
    out = []
    for f in F:
        ng.ngSpice_Command(f'ac lin 1 {f} {f}'.encode()); out.append(20 * np.log10(abs(cvec('out')[0])))
    return out
def row(lbl, v): print('%-44s' % lbl + ' '.join('%6.1f' % x for x in v))
if __name__ == '__main__':
    print('%-44s' % 'gain dB, LM386 out -> VOLUME top' + ' '.join('%6s' % f for f in F))
    for t in (0.0, 0.5, 1.0): row(f'orig  Big Muff  TONE {t:.0%}', run('orig', tone=t))
    for b, tr in ((0.5, 0.5), (1, 0.5), (0, 0.5), (0.5, 1), (0.5, 0)):
        row(f'pf2   as built  BASS {b:.0%} TREB {tr:.0%}', run('pf2', bass=b, treb=tr))
    for b, tr in ((0.5, 0.5), (1, 0.5), (0, 0.5), (0.5, 1), (0.5, 0)):
        row(f'fix   non-inv   BASS {b:.0%} TREB {tr:.0%}', run('fix', bass=b, treb=tr))
