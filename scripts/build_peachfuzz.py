"""Peach Fuzz (user's Frantone Peach Fuzz clone) - faithful transcription of the Eagle build
(~/Documents/eagle/projects/Peach Fuzz/Peach Fuzz.sch == .brd).  usage: build_peachfuzz.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('PeachFuzz', 'A3')
FR = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'
FC = 'Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2'
FCE = 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm'
FPOT = 'Potentiometer_THT:Potentiometer_Omeg_PC16BU_Vertical'
FPAD = 'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'
FDIP = 'Package_DIP:DIP-8_W7.62mm'
W = lambda *p: s.wire(*p)
P = s.P
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'R', v, cx, y, 90, fp=FR, desc=desc or f'Resistor {v}', text='t')
def Rv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'R', v, x, cy, 0, fp=FR, desc=desc or f'Resistor {v}', text=side)
def Ch(ref, v, cx, y, desc=None): s.part(ref, 'Device', 'C', v, cx, y, 90, fp=FC, desc=desc or f'Film capacitor {v}', text='t')
def Cv(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'C', v, x, cy, 0, fp=FC, desc=desc or f'Film capacitor {v}', text=side)
def Eh(ref, v, cx, y, plus_right=False, desc=None):   # horizontal electrolytic, + on the left unless plus_right
    s.part(ref, 'Device', 'C_Polarized', v, cx, y, 270 if plus_right else 90, fp=FCE, desc=desc or f'Electrolytic {v}', text='t')
def Ev(ref, v, x, cy, side='r', desc=None): s.part(ref, 'Device', 'C_Polarized', v, x, cy, 0, fp=FCE, desc=desc or f'Electrolytic {v}', text=side)
def POT(ref, v, name, x, y, text):
    s.part(ref, 'Device', 'R_Potentiometer', v, x, y, 0, mirror='x', fp=FPOT, desc=f'{name} pot', text=text, extra={'Panel': name})
def PAD(ref, name, x, y):
    s.part(ref, 'Connector_Generic', 'Conn_01x01', name, x, y, 180, fp=FPAD, desc=f'Wire pad: {name}',
           text=((x - 2.54, y - 1.27), (x - 2.54, y + 1.27), 'right'))
    return P(ref, '1')
def LM386(ref, x, y, cbyp, zr, zc, pads, xin):
    """LM386 at (x, y): + input at (x-3g, y-1g), - input grounded, bypass cap, Zobel, gain pins to wire pads"""
    s.part(ref, 'Amplifier_Audio', 'LM386', 'LM386', x, y, 0, fp=FDIP, desc='Audio power amp (used as a fuzz stage)', text='ic')
    W(P(ref, '2'), (x - g(4), y + g(1)), (x - g(4), y + g(4))); GND((x - g(4), y + g(4)))
    W(P(ref, '6'), (x - g(1), y - g(10))); V9((x - g(1), y - g(10)))
    W(P(ref, '7'), (x, y - g(8)), (x + g(2), y - g(8)))
    Eh(cbyp, '10u', x + g(3.5), y - g(8), desc='LM386 bypass (pin 7)'); W((x + g(2), y - g(8)), P(cbyp, '1'))
    W(P(cbyp, '2'), (x + g(6), y - g(8)), (x + g(6), y - g(7))); GND((x + g(6), y - g(7)))
    GND(P(ref, '4'))
    W(P(ref, '1'), (x, y + g(8)), (x - g(3), y + g(8)))
    W(P(ref, '8'), (x + g(1), y + g(11)), (x - g(3), y + g(11)))
    W(PAD(pads[0][0], pads[0][1], x - g(5), y + g(8)), (x - g(3), y + g(8)))
    W(PAD(pads[1][0], pads[1][1], x - g(5), y + g(11)), (x - g(3), y + g(11)))
    xo = x + g(5)
    W(P(ref, '5'), (xo, y))
    Rv(zr, '10R', xo, y + 3.81, side='r', desc='Zobel (optional, * in Eagle)')
    Cv(zc, '47n', xo, y + g(4.5), side='r', desc='Zobel (optional, * in Eagle)'); GND(P(zc, '2'))
    return (xo, y)

# ================================================================ INPUT PREAMP: TL072 inverting (U3A) + VREF
s.box('INPUT PREAMP: TL072 inverting (U3A), gain = R5 / (R1 || R2)', g(3), g(5), g(52), g(48))
y = g(25)
lab('IN', (g(5), y), 'l')
Rh('R1', '33k', g(10.5), y, desc='Input series'); W((g(5), y), P('R1', '1'))
W(P('R1', '2'), (g(14), y))
Rv('R2', '100k', g(14), y + 3.81, side='r', desc='Input shunt to ground'); GND(P('R2', '2'))
Ch('C1', '100n', g(17.5), y, desc='Input coupling'); W((g(14), y), P('C1', '1'))
s.part('U3', 'Amplifier_Operational', 'TL072', 'TL072', g(28), y + g(1), 0, unit=1, mirror='x', fp=FDIP, desc='Dual op-amp: A = preamp, B unused', text=((g(29), y - g(3)), (g(29), y - g(2)), 'left'))
W(P('C1', '2'), (g(21), y), P('U3', '2'))
yfb, yc = y - g(6), y - g(10)
Rh('R5', '560k', g(26), yfb, desc='Preamp feedback'); Ch('C3', '100p', g(26), yc, desc='Feedback HF roll-off')
W((g(21), y), (g(21), yfb), P('R5', '1')); W((g(21), yfb), (g(21), yc), P('C3', '1'))
yo = y + g(1)
W(P('R5', '2'), (g(33), yfb)); W(P('C3', '2'), (g(33), yc), (g(33), yfb), (g(33), yo))
W(P('U3', '1'), (g(33), yo), (g(34), yo))
Ch('C4', '1u', g(35.5), yo, desc='Coupling to GAIN'); Rh('R6', '9k1', g(40.5), yo, desc='Top of the GAIN divider')
W(P('C4', '2'), P('R6', '1')); W(P('R6', '2'), (g(46), yo)); lab('PRE', (g(46), yo))
W(P('U3', '3'), (g(23), y + g(2)), (g(23), y + g(5))); lab('VREF', (g(23), y + g(5)), 'l')
yv = g(38)
Rv('R3', '33k', g(8), yv - 3.81, side='l', desc='VREF divider'); V9(P('R3', '1'))
W(P('R3', '2'), (g(11), yv), (g(16), yv))
Rv('R4', '33k', g(8), yv + 3.81, side='l', desc='VREF divider'); GND(P('R4', '2'))
Ev('C2', '10u', g(11), yv + 3.81, side='r', desc='VREF decoupling'); GND(P('C2', '2'))
lab('VREF', (g(16), yv))

# ================================================================ STAGE 1: GAIN + LM386 (U1)
s.box('STAGE 1: GAIN divider + LM386 (U1)', g(55), g(5), g(100), g(48))
lab('PRE', (g(58), g(23)), 'l')
POT('RV1', 'A10k', 'GAIN', g(61), g(28), text=((g(59.5), g(33.5)), (g(59.5), g(35)), 'right'))
W((g(58), g(23)), (g(61), g(23)), P('RV1', '3'))
Rv('R7', '100R', g(61), g(31), side='l', desc='GAIN minimum'); GND(P('R7', '2'))
W(P('RV1', '1'), P('R7', '1'))
W(P('RV1', '2'), (g(65), g(28)), (g(67), g(28)))
Cv('C5', '560p', g(65), g(29.5), side='l', desc='U1 input HF roll-off'); GND(P('C5', '2'))
xo, yo = LM386('U1', g(70), g(29), 'C6', 'R8', 'C7', (('J9', 'B1'), ('J10', 'B2')), g(67))
W((xo, yo), (g(79), yo))
Ch('C8', '100n', g(80.5), yo, desc='Stage 1 to stage 2'); W(P('C8', '2'), (g(88), yo)); lab('DRIVE1', (g(88), yo))
s.text('B1/B2 = U1 gain pins 1/8. Open: gain 20. 10u (+ to pin 1): gain 200. 10u + R in series: in between. Avoid a bare wire (DC bias)', g(57), g(46), 1.0)

# ================================================================ STAGE 2: LM386 (U2)
s.box('STAGE 2: LM386 (U2)', g(103), g(5), g(160), g(48))
lab('DRIVE1', (g(106), g(28)), 'l')
Rh('R9', '120k', g(110.5), g(28), desc='Stage 2 input series'); W((g(106), g(28)), P('R9', '1'))
W(P('R9', '2'), (g(115), g(28)))
Cv('C9', '56p', g(113), g(29.5), side='l', desc='U2 input HF roll-off'); GND(P('C9', '2'))
xo, yo = LM386('U2', g(118), g(29), 'C10', 'R10', 'C11', (('J11', 'B3'), ('J12', 'B4')), g(115))
W((xo, yo), (g(127), yo))
Ch('C12', '1u', g(128.5), yo, desc='Stage 2 output coupling'); W(P('C12', '2'), (g(136), yo)); lab('DRIVE2', (g(136), yo))
s.text('B3/B4 = U2 gain pins 1/8. Open: gain 20. 10u (+ to pin 1): gain 200. 10u + R in series: in between. Avoid a bare wire (DC bias)', g(105), g(46), 1.0)

# ================================================================ TONE + VOLUME
s.box('TONE (Big Muff style) + VOLUME', g(3), g(52), g(52), g(88))
yh, yl = g(60), g(68)
lab('DRIVE2', (g(6), yh), 'l'); W((g(6), yh), (g(10), yh))
Rh('R11', '39k', g(13.5), yh, desc='Tone: treble path (original 41k; nearest standard value)'); W((g(10), yh), P('R11', '1'))
Ch('C13', '10n', g(18.5), yh, desc='Tone: treble path'); W(P('R11', '2'), P('C13', '1'))
W((g(10), yh), (g(10), yl))
Rh('R12', '10k', g(13.5), yl, desc='Tone: bass path'); W((g(10), yl), P('R12', '1'))
W(P('R12', '2'), (g(18), yl))
Cv('C14', '470n', g(18), yl + 3.81, side='r', desc='Tone: bass shunt'); GND(P('C14', '2'))
POT('RV2', 'B10k', 'TONE', g(24), g(64), text=((g(22), g(63)), (g(22), g(65)), 'right'))
W(P('C13', '2'), (g(24), yh), P('RV2', '3')); W((g(18), yl), (g(24), yl), P('RV2', '1'))
W(P('RV2', '2'), (g(34), g(64)))
POT('RV3', 'A100k', 'VOLUME', g(34), g(67.5), text=((g(37), g(70)), (g(37), g(71.5)), 'left'))
W((g(34), g(64)), P('RV3', '3')); GND(P('RV3', '1'))
W(P('RV3', '2'), (g(42), g(67.5))); lab('OUT', (g(42), g(67.5)))
s.text('R11 39k: original used 41k. C14 470n as recorded in the original.', g(5), g(85))

# ================================================================ POWER, LED, PADS, U3 unused half + power
s.box('POWER, LED, PADS & TL072 SUPPLY', g(55), g(52), g(160), g(88))
yp = g(60)
j = PAD('J3', '9V', g(58), yp)
s.part('D1', 'Diode', '1N5817', '1N5817', g(66.5), yp, 180, fp='Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal', desc='Series polarity protection', text='t')
W(j, (g(62), yp), P('D1', '2'))
W(P('D1', '1'), (g(71), yp), (g(74), yp), (g(78), yp), (g(82), yp))
V9((g(71), yp)); s.power('PWR_FLAG', (g(74), yp))
Ev('C15', '100u', g(78), yp + 3.81, desc='Supply bulk'); GND(P('C15', '2'))
Cv('C16', '100n', g(82), yp + 3.81, desc='Supply HF'); GND(P('C16', '2'))
Rv('R13', '1k', g(62), yp + 3.81, side='l', desc='LED current (Eagle RLED, from raw 9V before D1)'); W((g(62), yp), P('R13', '1'))
s.part('D2', 'Device', 'LED', 'LED', g(62), yp + g(7), 90, fp='LED_THT:LED_D3.0mm', desc='3mm LED', text=((g(64), yp + g(6.5)), (g(66), yp + g(6.5)), None))
W(P('R13', '2'), P('D2', '2'))
j = PAD('J7', 'LS', g(58), yp + g(11)); W(P('D2', '1'), (g(62), yp + g(11)), j)
for i, (ref, name, net) in enumerate((('J1', 'IN', 'IN'), ('J2', 'OUT', 'OUT'))):
    yy = g(78) + i * g(3.5); j = PAD(ref, name, g(92), yy); W(j, (g(97), yy)); lab(net, (g(97), yy))
for i, (ref, name) in enumerate((('J4', '-V'), ('J5', 'IG'), ('J6', 'OG'), ('J8', 'LG'))):
    yy = g(60) + i * g(3.5); j = PAD(ref, name, g(92), yy); W(j, (g(96), yy)); GND((g(96), yy))
    if ref == 'J4': s.power('PWR_FLAG', (g(95), yy))
xu, yu = g(120), g(66)
s.part('U3', 'Amplifier_Operational', 'TL072', 'TL072', xu, yu, 0, unit=2, fp=FDIP, desc='Dual op-amp: A = preamp, B unused', text=((xu + g(1), yu - g(4)), (xu + g(1), yu - g(3)), 'left'))
W(P('U3', '5'), (g(113), yu - g(1)), (g(113), yu + g(3))); GND((g(113), yu + g(3)))
W(P('U3', '7'), (xu + g(5), yu), (xu + g(5), yu + g(5)), (g(116), yu + g(5)), (g(116), yu + g(1)), P('U3', '6'))
s.part('U3', 'Amplifier_Operational', 'TL072', 'TL072', g(140), g(70), 0, unit=3, fp=FDIP, desc='Dual op-amp: A = preamp, B unused', text=((g(142), g(66)), (g(142), g(74)), 'left'))
V9(P('U3', '8')); GND(P('U3', '4'))
s.text('U3B unused: + to GND, output to - (as in Eagle)', g(108), g(80))

s.write(OUT, {'title': 'Peach Fuzz (as built)', 'date': '2026-09-30', 'rev': 'Eagle 2026-04',
              'company': 'Super-Freq',
              'comments': ['Faithful transcription of ~/Documents/eagle/projects/Peach Fuzz/Peach Fuzz (sch == brd)',
                           'Frantone Peach Fuzz clone: TL072 preamp, two LM386 stages, Big Muff tone, GAIN/TONE/VOLUME',
                           'Refs: GAIN/TONE/VOLUME = RV1-3; IC1-3 = U1-3; RLED = R13; pads IN OUT 9V -V IG OG LS LG B1-B4 = J1-J12']})
print('ok', len(s.syms), 'symbols')
