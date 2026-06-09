"""
Hand-drawn SVG silhouettes for Triskelion cards.

Each function returns inline SVG markup. The 'active' part is filled white,
everything else is a thin outline (#a0a0a0). Designed for a ~14mm wide
illustration column on a dark fuel-color background.
"""

# Common style attrs
OUT = 'fill="none" stroke="#bdbdbd" stroke-width="0.7" stroke-linejoin="round"'
ACT = 'fill="white" stroke="white" stroke-width="0.7" stroke-linejoin="round"'
THIN = 'fill="none" stroke="#bdbdbd" stroke-width="0.5"'

def style(active):
    """Return the SVG attribute string given whether a part is active."""
    return ACT if active else OUT


# ============================================================
# SATURN V — 3 cards (S-IC, S-II, S-IVB)
# Proportions: total ~110m. S-IC 42m, S-II 24.8m, S-IVB 17.8m,
# IU 1m, Apollo CSM 11m, LM adapter 7m, escape tower 10m
# ============================================================

def saturn_v(stage):
    """stage in {'s1', 's2', 's3', None}"""
    s1 = style(stage == 's1')
    s2 = style(stage == 's2')
    s3 = style(stage == 's3')
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Escape tower -->
      <line x1="20" y1="2" x2="20" y2="8" {THIN}/>
      <rect x="18" y="8" width="4" height="6" {OUT}/>
      <!-- Command Module -->
      <polygon points="14,22 26,22 22,14 18,14" {OUT}/>
      <!-- Service Module + adapter cone -->
      <rect x="14" y="22" width="12" height="6" {OUT}/>
      <polygon points="14,28 26,28 28,36 12,36" {OUT}/>
      <!-- Instrument Unit -->
      <rect x="12" y="36" width="16" height="2" {OUT}/>
      <!-- S-IVB 3rd stage -->
      <rect x="12" y="38" width="16" height="28" {s3}/>
      <!-- Interstage taper S-II/S-IVB -->
      <polygon points="12,66 28,66 30,72 10,72" {OUT}/>
      <!-- S-II 2nd stage -->
      <rect x="10" y="72" width="20" height="46" {s2}/>
      <!-- Interstage taper S-IC/S-II -->
      <polygon points="10,118 30,118 32,124 8,124" {OUT}/>
      <!-- S-IC 1st stage -->
      <rect x="8" y="124" width="24" height="62" {s1}/>
      <!-- Fins -->
      <polygon points="8,170 2,186 8,186" {s1}/>
      <polygon points="32,170 38,186 32,186" {s1}/>
      <!-- Engine block hint -->
      <rect x="11" y="186" width="18" height="3" {s1}/>
    </svg>'''


# ============================================================
# SPACE SHUTTLE STACK — 3 cards (SRB, ET, Orbiter)
# Asymmetric: 2 SRBs flank the ET, Orbiter mounted on side of ET
# Profile view: 1 SRB visible on left, ET center, Orbiter on right
# ============================================================

def shuttle_stack(part):
    """part in {'srb', 'et', 'orbiter'}"""
    srb = style(part == 'srb')
    et = style(part == 'et')
    orb = style(part == 'orbiter')
    return f'''<svg viewBox="0 0 60 180" preserveAspectRatio="xMidYMid meet">
      <!-- SRB (left side) -->
      <rect x="6" y="40" width="10" height="120" {srb}/>
      <polygon points="6,30 16,30 11,16" {srb}/>
      <rect x="7" y="160" width="8" height="4" {srb}/>
      <!-- External Tank (center) -->
      <polygon points="20,18 32,18 30,30 22,30" {et}/>
      <rect x="20" y="30" width="12" height="135" {et}/>
      <polygon points="20,165 32,165 30,172 22,172" {et}/>
      <!-- Orbiter (right side, attached to ET) -->
      <!-- Nose -->
      <polygon points="36,80 42,80 40,72" {orb}/>
      <!-- Fuselage -->
      <rect x="36" y="80" width="6" height="50" {orb}/>
      <!-- Wing -->
      <polygon points="42,116 54,140 42,140" {orb}/>
      <polygon points="36,116 30,140 36,140" {orb}/>
      <!-- Tail fin -->
      <polygon points="36,90 36,76 33,80 33,90" {orb}/>
      <!-- SSME engines hint -->
      <rect x="36" y="130" width="6" height="3" {orb}/>
    </svg>'''


# ============================================================
# STARSHIP STACK — 2 cards (Super Heavy, Starship)
# Super Heavy: tall cylinder, grid fins near top
# Starship: pointed nose, two big flaps top, two small flaps bottom
# ============================================================

def starship_stack(part):
    """part in {'booster', 'upper'}"""
    sh = style(part == 'booster')
    ss = style(part == 'upper')
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Starship upper -->
      <polygon points="14,12 26,12 22,2 18,2" {ss}/>
      <rect x="14" y="12" width="12" height="60" {ss}/>
      <!-- Forward flaps -->
      <polygon points="14,18 8,22 14,28" {ss}/>
      <polygon points="26,18 32,22 26,28" {ss}/>
      <!-- Aft flaps -->
      <polygon points="14,60 6,68 14,72" {ss}/>
      <polygon points="26,60 34,68 26,72" {ss}/>
      <!-- Hot-stage ring / separation -->
      <rect x="12" y="72" width="16" height="2" {OUT}/>
      <!-- Super Heavy booster -->
      <rect x="12" y="74" width="16" height="108" {sh}/>
      <!-- Grid fins (4 visible as 2 in profile) -->
      <rect x="6" y="80" width="6" height="4" {sh}/>
      <rect x="28" y="80" width="6" height="4" {sh}/>
      <!-- Engine block -->
      <rect x="14" y="182" width="12" height="3" {sh}/>
      <polygon points="14,185 26,185 28,189 12,189" {sh}/>
    </svg>'''


# ============================================================
# SOYUZ / R-7 — 2 cards (side boosters, upper)
# 4 conical strap-ons (2 visible in profile), central core, upper, capsule
# ============================================================

def soyuz_r7(part):
    """part in {'boosters', 'upper'}"""
    boost = style(part == 'boosters')
    core = style(False)  # core is never the "active" card in our mapping
    upper = style(part == 'upper')
    return f'''<svg viewBox="0 0 50 180" preserveAspectRatio="xMidYMid meet">
      <!-- Escape tower -->
      <line x1="25" y1="2" x2="25" y2="10" {THIN}/>
      <!-- Capsule -->
      <rect x="22" y="10" width="6" height="8" {OUT}/>
      <!-- Fairing taper -->
      <polygon points="20,32 30,32 28,18 22,18" {OUT}/>
      <!-- Upper stage -->
      <rect x="20" y="32" width="10" height="22" {upper}/>
      <!-- Interstage -->
      <rect x="19" y="54" width="12" height="4" {OUT}/>
      <!-- Central core (Blok-A) -->
      <rect x="19" y="58" width="12" height="92" {core}/>
      <polygon points="19,150 31,150 28,156 22,156" {core}/>
      <!-- Side boosters (Blok B/V/G/D, conical) -->
      <polygon points="6,88 14,88 17,148 3,148" {boost}/>
      <polygon points="36,88 44,88 47,148 33,148" {boost}/>
    </svg>'''


# ============================================================
# APOLLO LM — 2 cards (descent, ascent)
# Descent: octagonal base + 4 landing legs
# Ascent: angular module on top
# ============================================================

def apollo_lm(part):
    """part in {'descent', 'ascent'}"""
    d = style(part == 'descent')
    a = style(part == 'ascent')
    return f'''<svg viewBox="0 0 60 80" preserveAspectRatio="xMidYMid meet">
      <!-- Ascent module: roughly trapezoidal cabin with triangular hump on top -->
      <polygon points="22,18 38,18 36,30 24,30" {a}/>
      <rect x="20" y="30" width="20" height="14" {a}/>
      <!-- RCS quad hint -->
      <rect x="18" y="32" width="2" height="6" {a}/>
      <rect x="40" y="32" width="2" height="6" {a}/>
      <!-- Forward windows hint -->
      <rect x="26" y="22" width="3" height="3" {OUT}/>
      <rect x="31" y="22" width="3" height="3" {OUT}/>
      <!-- Descent stage: octagonal base in profile -->
      <polygon points="15,44 45,44 48,52 12,52" {d}/>
      <rect x="12" y="52" width="36" height="8" {d}/>
      <!-- Descent engine bell -->
      <polygon points="26,60 34,60 32,66 28,66" {d}/>
      <!-- Landing legs (4, shown as 2 in profile + 2 splayed) -->
      <line x1="14" y1="56" x2="4" y2="74" stroke="#bdbdbd" stroke-width="0.8"/>
      <line x1="46" y1="56" x2="56" y2="74" stroke="#bdbdbd" stroke-width="0.8"/>
      <line x1="22" y1="58" x2="14" y2="74" stroke="#bdbdbd" stroke-width="0.8"/>
      <line x1="38" y1="58" x2="46" y2="74" stroke="#bdbdbd" stroke-width="0.8"/>
      <!-- Foot pads -->
      <ellipse cx="4" cy="74" rx="3" ry="1.2" {OUT}/>
      <ellipse cx="56" cy="74" rx="3" ry="1.2" {OUT}/>
      <ellipse cx="14" cy="74" rx="2.5" ry="1" {OUT}/>
      <ellipse cx="46" cy="74" rx="2.5" ry="1" {OUT}/>
    </svg>'''


# ============================================================
# APOLLO CSM (Hypergolic Transfer Stage) — 1 card
# Command module + Service module + single SPS bell
# ============================================================

def apollo_csm():
    sm = style(True)  # the SM (service module) is the active part on this card
    return f'''<svg viewBox="0 0 40 120" preserveAspectRatio="xMidYMid meet">
      <!-- Command module -->
      <polygon points="10,30 30,30 26,12 14,12" {OUT}/>
      <rect x="12" y="10" width="16" height="2" {OUT}/>
      <!-- Service module -->
      <rect x="12" y="30" width="16" height="56" {sm}/>
      <!-- High-gain antenna hint -->
      <line x1="28" y1="50" x2="36" y2="44" stroke="#bdbdbd" stroke-width="0.5"/>
      <circle cx="36" cy="44" r="2" {OUT}/>
      <!-- SPS bell -->
      <polygon points="16,86 24,86 26,98 14,98" {sm}/>
    </svg>'''


# ============================================================
# ATLAS / CENTAUR — 1 card (Centaur upper highlighted)
# Atlas first stage (cylinder), Centaur upper (smaller cylinder), payload
# ============================================================

def atlas_centaur(part):
    """part in {'centaur'}"""
    cent = style(part == 'centaur')
    return f'''<svg viewBox="0 0 40 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="14,30 26,30 22,10 18,10" {OUT}/>
      <rect x="14" y="30" width="12" height="6" {OUT}/>
      <!-- Centaur upper stage (active) -->
      <rect x="14" y="36" width="12" height="34" {cent}/>
      <!-- Twin RL10 hint -->
      <polygon points="16,70 18,76 14,76" {cent}/>
      <polygon points="24,70 26,76 22,76" {cent}/>
      <!-- Interstage -->
      <rect x="12" y="76" width="16" height="4" {OUT}/>
      <!-- Atlas booster -->
      <rect x="12" y="80" width="16" height="84" {OUT}/>
      <!-- RD-180 / engine bell -->
      <polygon points="14,164 26,164 24,172 16,172" {OUT}/>
    </svg>'''


# ============================================================
# PROTON / HYPERGOLIC — 2 cards (boosters, upper Briz-M)
# Proton: 6 oxidizer tanks around central tank, in profile shows
# clustered tanks at the base. Upper stages above.
# ============================================================

def proton(part):
    """part in {'boosters', 'upper'}"""
    b = style(part == 'boosters')
    u = style(part == 'upper')
    return f'''<svg viewBox="0 0 50 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="20,18 30,18 26,4 24,4" {OUT}/>
      <rect x="20" y="18" width="10" height="4" {OUT}/>
      <!-- Briz-M / upper stage -->
      <rect x="20" y="22" width="10" height="18" {u}/>
      <!-- Tapered interstage -->
      <polygon points="20,40 30,40 32,46 18,46" {OUT}/>
      <!-- Second stage -->
      <rect x="18" y="46" width="14" height="40" {OUT}/>
      <!-- Interstage -->
      <rect x="17" y="86" width="16" height="3" {OUT}/>
      <!-- First stage central tank -->
      <rect x="18" y="89" width="14" height="62" {b}/>
      <!-- Side oxidizer tanks (Proton's distinctive cluster - 6 tanks, show 2 in profile) -->
      <rect x="8" y="105" width="10" height="46" {b}/>
      <rect x="32" y="105" width="10" height="46" {b}/>
      <!-- Engine bells -->
      <rect x="9" y="151" width="8" height="5" {b}/>
      <rect x="20" y="151" width="10" height="5" {b}/>
      <rect x="33" y="151" width="8" height="5" {b}/>
    </svg>'''


# ============================================================
# ARIANE 5 — 3 cards (EAP solid boosters, EPC core, ESC-A upper)
# Central hydrolox core (EPC) + 2 solid boosters (EAP) + upper stage
# ============================================================

def ariane5(part):
    """part in {'eap', 'epc', 'esc'}"""
    eap = style(part == 'eap')
    epc = style(part == 'epc')
    esc = style(part == 'esc')
    return f'''<svg viewBox="0 0 50 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="20,18 30,18 26,4 24,4" {OUT}/>
      <rect x="20" y="18" width="10" height="4" {OUT}/>
      <!-- ESC-A upper -->
      <rect x="20" y="22" width="10" height="20" {esc}/>
      <!-- Interstage -->
      <rect x="19" y="42" width="12" height="3" {OUT}/>
      <!-- EPC core stage -->
      <rect x="19" y="45" width="12" height="100" {epc}/>
      <!-- Vulcain 2 engine bell -->
      <polygon points="20,145 30,145 28,153 22,153" {epc}/>
      <!-- EAP solid boosters (2 in profile) -->
      <polygon points="6,42 14,42 11,32" {eap}/>
      <rect x="6" y="42" width="8" height="105" {eap}/>
      <polygon points="36,42 44,42 39,32" {eap}/>
      <rect x="36" y="42" width="8" height="105" {eap}/>
      <!-- SRB nozzles -->
      <rect x="7" y="147" width="6" height="4" {eap}/>
      <rect x="37" y="147" width="6" height="4" {eap}/>
    </svg>'''


# ============================================================
# DELTA IV — 1 card (Hydrolox Booster = first stage)
# Cylindrical hydrolox first stage with RS-68 nozzle
# ============================================================

def delta_iv():
    s1 = style(True)
    return f'''<svg viewBox="0 0 40 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="14,28 26,28 22,8 18,8" {OUT}/>
      <rect x="14" y="28" width="12" height="4" {OUT}/>
      <!-- Upper stage (DCSS) -->
      <rect x="14" y="32" width="12" height="30" {OUT}/>
      <!-- Interstage -->
      <rect x="12" y="62" width="16" height="4" {OUT}/>
      <!-- First stage CBC (Common Booster Core) -->
      <rect x="12" y="66" width="16" height="100" {s1}/>
      <!-- RS-68 engine bell -->
      <polygon points="14,166 26,166 24,176 16,176" {s1}/>
    </svg>'''


# ============================================================
# METHALOX GENERIC (New Glenn / Zhuque-2 style) — 2 cards
# Tall reusable booster with grid fins, methalox upper above
# ============================================================

def methalox_stack(part):
    """part in {'booster', 'upper'}"""
    b = style(part == 'booster')
    u = style(part == 'upper')
    return f'''<svg viewBox="0 0 40 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="14,16 26,16 22,4 18,4" {OUT}/>
      <rect x="14" y="16" width="12" height="4" {OUT}/>
      <!-- Methalox upper -->
      <rect x="14" y="20" width="12" height="36" {u}/>
      <!-- Vacuum engine bell -->
      <polygon points="16,56 24,56 26,62 14,62" {u}/>
      <!-- Interstage -->
      <rect x="12" y="62" width="16" height="4" {OUT}/>
      <!-- Methalox booster (reusable) -->
      <rect x="12" y="66" width="16" height="100" {b}/>
      <!-- Grid fins -->
      <rect x="6" y="74" width="6" height="6" {b}/>
      <rect x="28" y="74" width="6" height="6" {b}/>
      <!-- Engine cluster at base -->
      <rect x="14" y="166" width="12" height="3" {b}/>
      <polygon points="14,169 26,169 28,176 12,176" {b}/>
    </svg>'''


# ============================================================
# VEGA — 1 card (Light Solid Engine = 4-stage all-solid)
# Small thin rocket with 4 stages, distinctive shape
# ============================================================

def vega():
    a = style(True)
    return f'''<svg viewBox="0 0 30 180" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <polygon points="10,24 20,24 17,4 13,4" {OUT}/>
      <!-- Stage 4 (AVUM, liquid) -->
      <rect x="11" y="24" width="8" height="14" {OUT}/>
      <!-- Stage 3 (Zefiro 9) -->
      <rect x="11" y="38" width="8" height="22" {a}/>
      <!-- Stage 2 (Zefiro 23) -->
      <rect x="10" y="60" width="10" height="32" {a}/>
      <!-- Stage 1 (P80, large solid) -->
      <rect x="8" y="92" width="14" height="68" {a}/>
      <!-- Engine bell -->
      <polygon points="10,160 20,160 18,170 12,170" {a}/>
    </svg>'''


# ============================================================
# LIGHT SOLID BOOSTER — 1 card (small strap-on)
# Generic small solid rocket booster shape
# ============================================================

def light_solid_strapon():
    a = style(True)
    return f'''<svg viewBox="0 0 30 120" preserveAspectRatio="xMidYMid meet">
      <!-- Conical nose -->
      <polygon points="9,18 21,18 15,4" {a}/>
      <!-- Main cylinder -->
      <rect x="9" y="18" width="12" height="84" {a}/>
      <!-- Single fin (small) -->
      <polygon points="9,90 4,102 9,102" {a}/>
      <polygon points="21,90 26,102 21,102" {a}/>
      <!-- Nozzle -->
      <polygon points="11,102 19,102 17,110 13,110" {a}/>
    </svg>'''


# ============================================================
# SOLID KICK MOTOR (Star-48) — 1 card
# Small can-shape with single nozzle, often spin-stabilized
# ============================================================

def solid_kick():
    a = style(True)
    return f'''<svg viewBox="0 0 40 60" preserveAspectRatio="xMidYMid meet">
      <!-- Drum body -->
      <rect x="10" y="14" width="20" height="24" {a}/>
      <!-- Spin-stabilization detail (top dome) -->
      <path d="M 10 14 Q 20 8 30 14" {a}/>
      <!-- Nozzle -->
      <polygon points="14,38 26,38 24,50 16,50" {a}/>
    </svg>'''


# ============================================================
# NERVA NUCLEAR ENGINE — 1 card
# Engine on a hydrogen tank, distinctive shape
# ============================================================

def nerva():
    a = style(True)
    return f'''<svg viewBox="0 0 30 120" preserveAspectRatio="xMidYMid meet">
      <!-- LH2 tank (spherical-cylindrical) -->
      <path d="M 9 16 Q 9 8 15 8 Q 21 8 21 16 L 21 70 Q 21 78 15 78 Q 9 78 9 70 Z" {a}/>
      <!-- Reactor shielding ring -->
      <rect x="9" y="78" width="12" height="4" {a}/>
      <!-- Reactor core / pressure vessel -->
      <rect x="10" y="82" width="10" height="14" {a}/>
      <!-- Engine nozzle (large, with characteristic conical taper) -->
      <polygon points="11,96 19,96 22,114 8,114" {a}/>
      <!-- Radiation symbol hint (3 small marks) -->
      <circle cx="15" cy="40" r="1" fill="#bdbdbd"/>
    </svg>'''


# ============================================================
# ION SPACECRAFT (Dawn-style) — 1 card
# Small bus with two large solar panel wings, single ion thruster
# ============================================================

def ion_spacecraft():
    a = style(True)
    return f'''<svg viewBox="0 0 80 60" preserveAspectRatio="xMidYMid meet">
      <!-- Central bus -->
      <rect x="34" y="20" width="12" height="20" {a}/>
      <!-- Solar panel wing (left) - 2 panels with grid -->
      <rect x="2" y="22" width="32" height="16" {a}/>
      <line x1="10" y1="22" x2="10" y2="38" {THIN}/>
      <line x1="18" y1="22" x2="18" y2="38" {THIN}/>
      <line x1="26" y1="22" x2="26" y2="38" {THIN}/>
      <line x1="2" y1="30" x2="34" y2="30" {THIN}/>
      <!-- Solar panel wing (right) -->
      <rect x="46" y="22" width="32" height="16" {a}/>
      <line x1="54" y1="22" x2="54" y2="38" {THIN}/>
      <line x1="62" y1="22" x2="62" y2="38" {THIN}/>
      <line x1="70" y1="22" x2="70" y2="38" {THIN}/>
      <line x1="46" y1="30" x2="78" y2="30" {THIN}/>
      <!-- Ion thruster (small bell at bottom) -->
      <rect x="38" y="40" width="4" height="3" {a}/>
      <polygon points="38,43 42,43 43,48 37,48" {a}/>
      <!-- High-gain antenna on top -->
      <line x1="40" y1="20" x2="40" y2="12" {THIN}/>
      <ellipse cx="40" cy="10" rx="4" ry="2" {OUT}/>
    </svg>'''


# ============================================================
# COMPACT HYPERGOLIC UPPER (Briz-M generic) — 1 card
# Small storable upper stage, no booster
# ============================================================

def hypergolic_upper():
    a = style(True)
    return f'''<svg viewBox="0 0 40 100" preserveAspectRatio="xMidYMid meet">
      <!-- Payload mount -->
      <rect x="14" y="10" width="12" height="3" {OUT}/>
      <!-- Toroidal propellant tank (Briz-M characteristic) -->
      <ellipse cx="20" cy="20" rx="14" ry="6" {a}/>
      <!-- Central thrust structure -->
      <rect x="16" y="26" width="8" height="40" {a}/>
      <!-- Spherical propellant tanks (4, show 2) -->
      <circle cx="10" cy="42" r="5" {a}/>
      <circle cx="30" cy="42" r="5" {a}/>
      <!-- Engine -->
      <polygon points="16,66 24,66 26,76 14,76" {a}/>
    </svg>'''


def mars_ascent_vehicle():
    """Compact two-stage Mars ascent vehicle. Bullet-shaped capsule on top of
    a methalox tank with single central engine and four landing legs splayed out."""
    a = style(True)
    return f'''<svg viewBox="0 0 50 120" preserveAspectRatio="xMidYMid meet">
      <!-- Crew capsule / nose (rounded conical) -->
      <path d="M 25 6 Q 16 6 16 22 L 34 22 Q 34 6 25 6 Z" {a}/>
      <!-- Capsule window -->
      <circle cx="25" cy="14" r="1.8" {OUT}/>
      <!-- Adapter ring -->
      <rect x="16" y="22" width="18" height="3" {OUT}/>
      <!-- Methalox tank (cylindrical body) -->
      <rect x="14" y="25" width="22" height="50" {a}/>
      <!-- Tank pressure rings -->
      <line x1="14" y1="40" x2="36" y2="40" {OUT}/>
      <line x1="14" y1="55" x2="36" y2="55" {OUT}/>
      <!-- Central engine bell -->
      <polygon points="20,75 30,75 33,90 17,90" {a}/>
      <!-- Landing legs (4, two visible) -->
      <line x1="16" y1="70" x2="6"  y2="102" stroke="#bdbdbd" stroke-width="1.2"/>
      <line x1="34" y1="70" x2="44" y2="102" stroke="#bdbdbd" stroke-width="1.2"/>
      <!-- Foot pads -->
      <ellipse cx="6" cy="104" rx="3" ry="1.2" {a}/>
      <ellipse cx="44" cy="104" rx="3" ry="1.2" {a}/>
    </svg>'''


# ============================================================
# EQUIPMENT ICONS (17 items)
# Simple, recognizable, ~24x32mm aspect typical
# Blue stroke for equipment (matches card accent)
# ============================================================

# Equipment uses blue strokes since the bg behind them is light/white
EQ_OUT = 'fill="none" stroke="#1b3a6b" stroke-width="0.7" stroke-linejoin="round"'
EQ_FILL = 'fill="#1b3a6b" stroke="#1b3a6b" stroke-width="0.5"'
BURNER_OUT = 'fill="none" stroke="#a83232" stroke-width="0.7"'
BURNER_FILL = 'fill="#a83232" stroke="#a83232" stroke-width="0.5"'


def eq_crew_capsule():
    return f'''<svg viewBox="0 0 40 50" preserveAspectRatio="xMidYMid meet">
      <!-- Apollo-style capsule -->
      <polygon points="6,40 34,40 28,10 12,10" {EQ_OUT}/>
      <rect x="10" y="8" width="20" height="2" {EQ_OUT}/>
      <!-- Window -->
      <circle cx="20" cy="22" r="3" {EQ_OUT}/>
      <!-- Heat shield ring at base -->
      <rect x="4" y="40" width="32" height="3" {EQ_FILL}/>
    </svg>'''


def eq_heat_shield():
    return f'''<svg viewBox="0 0 50 40" preserveAspectRatio="xMidYMid meet">
      <!-- Curved shield -->
      <path d="M 4 24 Q 25 4 46 24 L 42 30 Q 25 14 8 30 Z" {EQ_FILL}/>
      <!-- Heat tile pattern hint -->
      <line x1="14" y1="18" x2="14" y2="25" {EQ_OUT}/>
      <line x1="20" y1="14" x2="20" y2="22" {EQ_OUT}/>
      <line x1="26" y1="14" x2="26" y2="22" {EQ_OUT}/>
      <line x1="32" y1="18" x2="32" y2="25" {EQ_OUT}/>
    </svg>'''


def eq_atmospheric_return():
    """Combined heat shield (bottom) and parachute (top, deployed)."""
    return f'''<svg viewBox="0 0 50 65" preserveAspectRatio="xMidYMid meet">
      <!-- Canopy (parachute, deployed above) -->
      <path d="M 6 18 Q 25 -2 44 18 L 38 22 Q 25 6 12 22 Z" {EQ_FILL}/>
      <!-- Suspension lines converging to capsule -->
      <line x1="8" y1="20" x2="20" y2="36" {EQ_OUT}/>
      <line x1="18" y1="14" x2="22" y2="36" {EQ_OUT}/>
      <line x1="25" y1="12" x2="25" y2="36" {EQ_OUT}/>
      <line x1="32" y1="14" x2="28" y2="36" {EQ_OUT}/>
      <line x1="42" y1="20" x2="30" y2="36" {EQ_OUT}/>
      <!-- Capsule body -->
      <path d="M 18 36 L 32 36 L 36 48 L 14 48 Z" {EQ_FILL}/>
      <!-- Heat shield curved underside -->
      <path d="M 14 48 Q 25 56 36 48" {EQ_OUT}/>
      <!-- Heat tile hints -->
      <line x1="20" y1="49" x2="20" y2="52" {EQ_OUT}/>
      <line x1="25" y1="50" x2="25" y2="53" {EQ_OUT}/>
      <line x1="30" y1="49" x2="30" y2="52" {EQ_OUT}/>
    </svg>'''


def eq_parachute():
    return f'''<svg viewBox="0 0 50 60" preserveAspectRatio="xMidYMid meet">
      <!-- Canopy -->
      <path d="M 4 26 Q 25 -4 46 26 L 38 30 Q 25 10 12 30 Z" {EQ_FILL}/>
      <!-- Suspension lines -->
      <line x1="6" y1="28" x2="22" y2="52" {EQ_OUT}/>
      <line x1="16" y1="22" x2="24" y2="52" {EQ_OUT}/>
      <line x1="25" y1="20" x2="25" y2="52" {EQ_OUT}/>
      <line x1="34" y1="22" x2="26" y2="52" {EQ_OUT}/>
      <line x1="44" y1="28" x2="28" y2="52" {EQ_OUT}/>
      <!-- Payload -->
      <rect x="22" y="52" width="8" height="6" {EQ_OUT}/>
    </svg>'''


def eq_large_antenna():
    """High-gain communications dish on a mast."""
    return f'''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Parabolic dish -->
      <path d="M 5 12 Q 25 0 45 12 L 42 18 Q 25 8 8 18 Z" {EQ_FILL}/>
      <!-- Dish rim -->
      <ellipse cx="25" cy="13" rx="20" ry="3" {EQ_OUT}/>
      <!-- Feed horn (small box on dish axis) -->
      <rect x="23" y="6" width="4" height="4" {EQ_FILL}/>
      <!-- Support strut from dish to base -->
      <line x1="25" y1="17" x2="25" y2="42" {EQ_OUT}/>
      <!-- Base / equatorial mount -->
      <rect x="18" y="42" width="14" height="3" {EQ_FILL}/>
      <line x1="20" y1="45" x2="18" y2="48" {EQ_OUT}/>
      <line x1="30" y1="45" x2="32" y2="48" {EQ_OUT}/>
    </svg>'''


def eq_landing_gear():
    return f'''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Main strut -->
      <rect x="22" y="6" width="6" height="20" {EQ_FILL}/>
      <!-- Lower bracket -->
      <line x1="25" y1="26" x2="10" y2="40" {EQ_OUT}/>
      <line x1="25" y1="26" x2="40" y2="40" {EQ_OUT}/>
      <!-- Wheel hub axis -->
      <line x1="10" y1="40" x2="40" y2="40" {EQ_OUT}/>
      <!-- Wheels (2) -->
      <circle cx="14" cy="42" r="5" {EQ_FILL}/>
      <circle cx="36" cy="42" r="5" {EQ_FILL}/>
    </svg>'''


def eq_lander_legs():
    return f'''<svg viewBox="0 0 60 50" preserveAspectRatio="xMidYMid meet">
      <!-- Central body -->
      <rect x="22" y="6" width="16" height="14" {EQ_OUT}/>
      <!-- 4 legs splaying out (2 visible as front legs, 2 in back) -->
      <line x1="22" y1="18" x2="6" y2="42" {EQ_OUT}/>
      <line x1="38" y1="18" x2="54" y2="42" {EQ_OUT}/>
      <line x1="26" y1="20" x2="20" y2="42" {EQ_OUT}/>
      <line x1="34" y1="20" x2="40" y2="42" {EQ_OUT}/>
      <!-- Foot pads -->
      <ellipse cx="6" cy="44" rx="4" ry="1.5" {EQ_FILL}/>
      <ellipse cx="54" cy="44" rx="4" ry="1.5" {EQ_FILL}/>
      <ellipse cx="20" cy="44" rx="3" ry="1.2" {EQ_FILL}/>
      <ellipse cx="40" cy="44" rx="3" ry="1.2" {EQ_FILL}/>
    </svg>'''


def eq_pressurised_habitat():
    return f'''<svg viewBox="0 0 60 40" preserveAspectRatio="xMidYMid meet">
      <!-- Cylindrical habitat module with rounded ends -->
      <rect x="14" y="10" width="32" height="20" {EQ_OUT}/>
      <path d="M 14 10 Q 6 20 14 30" {EQ_OUT}/>
      <path d="M 46 10 Q 54 20 46 30" {EQ_OUT}/>
      <!-- Window port -->
      <circle cx="22" cy="20" r="3" {EQ_FILL}/>
      <circle cx="32" cy="20" r="3" {EQ_FILL}/>
      <!-- Docking port hint at one end -->
      <rect x="52" y="18" width="4" height="4" {EQ_FILL}/>
    </svg>'''


def eq_life_support():
    return f'''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Box with grille (recycler unit) -->
      <rect x="6" y="10" width="38" height="32" {EQ_OUT}/>
      <!-- Grille lines -->
      <line x1="10" y1="16" x2="40" y2="16" {EQ_OUT}/>
      <line x1="10" y1="22" x2="40" y2="22" {EQ_OUT}/>
      <line x1="10" y1="28" x2="40" y2="28" {EQ_OUT}/>
      <line x1="10" y1="34" x2="40" y2="34" {EQ_OUT}/>
      <!-- Pipes -->
      <rect x="14" y="2" width="4" height="8" {EQ_FILL}/>
      <rect x="32" y="2" width="4" height="8" {EQ_FILL}/>
    </svg>'''


def eq_comms_satellite():
    return f'''<svg viewBox="0 0 60 50" preserveAspectRatio="xMidYMid meet">
      <!-- Main bus -->
      <rect x="24" y="18" width="12" height="14" {EQ_FILL}/>
      <!-- Solar panels -->
      <rect x="6" y="20" width="16" height="10" {EQ_OUT}/>
      <line x1="14" y1="20" x2="14" y2="30" {EQ_OUT}/>
      <rect x="38" y="20" width="16" height="10" {EQ_OUT}/>
      <line x1="46" y1="20" x2="46" y2="30" {EQ_OUT}/>
      <!-- Large dish antenna -->
      <ellipse cx="30" cy="8" rx="10" ry="3" {EQ_OUT}/>
      <line x1="30" y1="8" x2="30" y2="18" {EQ_OUT}/>
    </svg>'''


def eq_nav_satellite():
    return f'''<svg viewBox="0 0 60 50" preserveAspectRatio="xMidYMid meet">
      <!-- Main bus -->
      <rect x="24" y="18" width="12" height="14" {EQ_FILL}/>
      <!-- Solar panels -->
      <rect x="6" y="22" width="16" height="6" {EQ_OUT}/>
      <rect x="38" y="22" width="16" height="6" {EQ_OUT}/>
      <!-- Multiple antennas (helical for GPS-style) -->
      <line x1="27" y1="18" x2="27" y2="6" {EQ_OUT}/>
      <line x1="30" y1="18" x2="30" y2="4" {EQ_OUT}/>
      <line x1="33" y1="18" x2="33" y2="6" {EQ_OUT}/>
      <!-- Bottom thruster hint -->
      <rect x="28" y="32" width="4" height="3" {EQ_FILL}/>
    </svg>'''


def eq_weather_satellite():
    return f'''<svg viewBox="0 0 60 50" preserveAspectRatio="xMidYMid meet">
      <!-- Bus -->
      <rect x="22" y="14" width="16" height="20" {EQ_FILL}/>
      <!-- Solar panels -->
      <rect x="4" y="20" width="18" height="8" {EQ_OUT}/>
      <rect x="38" y="20" width="18" height="8" {EQ_OUT}/>
      <line x1="13" y1="20" x2="13" y2="28" {EQ_OUT}/>
      <line x1="47" y1="20" x2="47" y2="28" {EQ_OUT}/>
      <!-- Imaging instrument (cylinder on bottom) -->
      <rect x="26" y="34" width="8" height="8" {EQ_OUT}/>
      <circle cx="30" cy="42" r="2" {EQ_FILL}/>
    </svg>'''


def eq_spy_satellite():
    return f'''<svg viewBox="0 0 60 60" preserveAspectRatio="xMidYMid meet">
      <!-- Bus -->
      <rect x="22" y="20" width="16" height="14" {EQ_FILL}/>
      <!-- Solar panels (offset for spy aesthetic) -->
      <rect x="4" y="24" width="16" height="6" {EQ_OUT}/>
      <rect x="40" y="24" width="16" height="6" {EQ_OUT}/>
      <!-- Large optical telescope barrel pointing down -->
      <rect x="24" y="34" width="12" height="20" {EQ_OUT}/>
      <circle cx="30" cy="54" r="5" {EQ_FILL}/>
      <!-- Optical iris hint -->
      <circle cx="30" cy="54" r="2" fill="white"/>
    </svg>'''


def eq_science_package():
    return f'''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Central platform -->
      <rect x="14" y="20" width="22" height="16" {EQ_FILL}/>
      <!-- Instruments sticking up at different angles -->
      <rect x="16" y="6" width="3" height="14" {EQ_OUT}/>
      <line x1="17" y1="6" x2="14" y2="2" {EQ_OUT}/>
      <line x1="17" y1="6" x2="20" y2="2" {EQ_OUT}/>
      <rect x="23" y="10" width="4" height="10" {EQ_OUT}/>
      <circle cx="25" cy="8" r="2" {EQ_OUT}/>
      <rect x="31" y="12" width="3" height="8" {EQ_OUT}/>
      <line x1="32" y1="12" x2="36" y2="6" {EQ_OUT}/>
      <!-- Base feet -->
      <rect x="14" y="36" width="3" height="6" {EQ_OUT}/>
      <rect x="33" y="36" width="3" height="6" {EQ_OUT}/>
    </svg>'''


def eq_rover():
    return f'''<svg viewBox="0 0 60 40" preserveAspectRatio="xMidYMid meet">
      <!-- Chassis/deck -->
      <rect x="8" y="16" width="44" height="10" {EQ_FILL}/>
      <!-- Instrument mast -->
      <rect x="14" y="4" width="2" height="12" {EQ_OUT}/>
      <rect x="11" y="2" width="8" height="4" {EQ_OUT}/>
      <!-- Robotic arm -->
      <line x1="46" y1="16" x2="52" y2="10" {EQ_OUT}/>
      <line x1="52" y1="10" x2="56" y2="14" {EQ_OUT}/>
      <!-- 6 wheels (rocker-bogie) -->
      <circle cx="14" cy="30" r="5" {EQ_OUT}/>
      <circle cx="30" cy="30" r="5" {EQ_OUT}/>
      <circle cx="46" cy="30" r="5" {EQ_OUT}/>
      <!-- Wheel hubs -->
      <circle cx="14" cy="30" r="1.5" {EQ_FILL}/>
      <circle cx="30" cy="30" r="1.5" {EQ_FILL}/>
      <circle cx="46" cy="30" r="1.5" {EQ_FILL}/>
    </svg>'''


def eq_sample_container():
    return f'''<svg viewBox="0 0 40 50" preserveAspectRatio="xMidYMid meet">
      <!-- Capsule outer shell -->
      <polygon points="8,38 32,38 28,12 12,12" {EQ_OUT}/>
      <polygon points="10,12 30,12 22,4 18,4" {EQ_OUT}/>
      <!-- Sample window -->
      <rect x="16" y="22" width="8" height="8" {EQ_FILL}/>
      <!-- Latch mechanism -->
      <rect x="14" y="38" width="12" height="3" {EQ_FILL}/>
      <!-- Carrying handle hint -->
      <path d="M 14 12 Q 20 6 26 12" {EQ_OUT}/>
    </svg>'''


def eq_solar_array():
    return f'''<svg viewBox="0 0 60 40" preserveAspectRatio="xMidYMid meet">
      <!-- Mounting boom -->
      <line x1="30" y1="6" x2="30" y2="36" {EQ_OUT}/>
      <!-- Left wing - 4 panel grid -->
      <rect x="4" y="10" width="24" height="20" {EQ_OUT}/>
      <line x1="10" y1="10" x2="10" y2="30" {EQ_OUT}/>
      <line x1="16" y1="10" x2="16" y2="30" {EQ_OUT}/>
      <line x1="22" y1="10" x2="22" y2="30" {EQ_OUT}/>
      <line x1="4" y1="20" x2="28" y2="20" {EQ_OUT}/>
      <!-- Right wing -->
      <rect x="32" y="10" width="24" height="20" {EQ_OUT}/>
      <line x1="38" y1="10" x2="38" y2="30" {EQ_OUT}/>
      <line x1="44" y1="10" x2="44" y2="30" {EQ_OUT}/>
      <line x1="50" y1="10" x2="50" y2="30" {EQ_OUT}/>
      <line x1="32" y1="20" x2="56" y2="20" {EQ_OUT}/>
      <!-- Sun ray hint -->
      <circle cx="30" cy="4" r="2" {EQ_FILL}/>
    </svg>'''


def eq_deep_space_probe():
    return f'''<svg viewBox="0 0 50 60" preserveAspectRatio="xMidYMid meet">
      <!-- Big high-gain antenna dish -->
      <ellipse cx="25" cy="14" rx="18" ry="6" {EQ_OUT}/>
      <line x1="25" y1="14" x2="25" y2="26" {EQ_OUT}/>
      <!-- Main bus -->
      <rect x="18" y="26" width="14" height="16" {EQ_FILL}/>
      <!-- RTG hanging off side -->
      <rect x="34" y="30" width="14" height="6" {EQ_OUT}/>
      <line x1="36" y1="30" x2="36" y2="36" {EQ_OUT}/>
      <line x1="40" y1="30" x2="40" y2="36" {EQ_OUT}/>
      <line x1="44" y1="30" x2="44" y2="36" {EQ_OUT}/>
      <!-- Boom-mounted instruments -->
      <line x1="18" y1="34" x2="2" y2="34" {EQ_OUT}/>
      <circle cx="2" cy="34" r="2" {EQ_OUT}/>
      <!-- Engine bell -->
      <polygon points="22,42 28,42 30,50 20,50" {EQ_OUT}/>
    </svg>'''


def eq_burner_engine():
    return f'''<svg viewBox="0 0 40 50" preserveAspectRatio="xMidYMid meet">
      <!-- Two small pressurised propellant tanks -->
      <circle cx="14" cy="14" r="6" {BURNER_OUT}/>
      <circle cx="26" cy="14" r="6" {BURNER_OUT}/>
      <!-- Plumbing -->
      <line x1="14" y1="20" x2="14" y2="26" {BURNER_OUT}/>
      <line x1="26" y1="20" x2="26" y2="26" {BURNER_OUT}/>
      <!-- Thrust chamber -->
      <rect x="14" y="26" width="12" height="8" {BURNER_FILL}/>
      <!-- Engine bell -->
      <polygon points="14,34 26,34 30,46 10,46" {BURNER_FILL}/>
    </svg>'''


def eq_consumables():
    """4 ration containers in a 2x2 grid (each = one quarter / consumable).
    The rotation indicators (100%/75%/50%/25%) are drawn separately on the card
    edges by the card layout, not in this silhouette."""
    return f'''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- 2x2 grid of food/ration containers -->
      <!-- top-left -->
      <rect x="6" y="6" width="16" height="16" {EQ_FILL}/>
      <line x1="10" y1="10" x2="18" y2="10" stroke="white" stroke-width="1"/>
      <line x1="10" y1="14" x2="18" y2="14" stroke="white" stroke-width="1"/>
      <line x1="10" y1="18" x2="18" y2="18" stroke="white" stroke-width="1"/>
      <!-- top-right -->
      <rect x="28" y="6" width="16" height="16" {EQ_FILL}/>
      <line x1="32" y1="10" x2="40" y2="10" stroke="white" stroke-width="1"/>
      <line x1="32" y1="14" x2="40" y2="14" stroke="white" stroke-width="1"/>
      <line x1="32" y1="18" x2="40" y2="18" stroke="white" stroke-width="1"/>
      <!-- bottom-left -->
      <rect x="6" y="28" width="16" height="16" {EQ_FILL}/>
      <line x1="10" y1="32" x2="18" y2="32" stroke="white" stroke-width="1"/>
      <line x1="10" y1="36" x2="18" y2="36" stroke="white" stroke-width="1"/>
      <line x1="10" y1="40" x2="18" y2="40" stroke="white" stroke-width="1"/>
      <!-- bottom-right -->
      <rect x="28" y="28" width="16" height="16" {EQ_FILL}/>
      <line x1="32" y1="32" x2="40" y2="32" stroke="white" stroke-width="1"/>
      <line x1="32" y1="36" x2="40" y2="36" stroke="white" stroke-width="1"/>
      <line x1="32" y1="40" x2="40" y2="40" stroke="white" stroke-width="1"/>
    </svg>'''


def eq_greenhouse():
    """Inflatable dome / tunnel greenhouse with plants and a sun symbol."""
    return f'''<svg viewBox="0 0 60 50" preserveAspectRatio="xMidYMid meet">
      <!-- Inflatable arch tunnel -->
      <path d="M 6 38 Q 6 12 30 12 Q 54 12 54 38 Z" {EQ_OUT}/>
      <!-- Cross-frame ribs -->
      <line x1="18" y1="38" x2="18" y2="14" {EQ_OUT}/>
      <line x1="30" y1="38" x2="30" y2="12" {EQ_OUT}/>
      <line x1="42" y1="38" x2="42" y2="14" {EQ_OUT}/>
      <!-- Plants inside (stylized) -->
      <line x1="12" y1="38" x2="12" y2="30" {EQ_OUT}/>
      <circle cx="12" cy="28" r="2" {EQ_FILL}/>
      <line x1="24" y1="38" x2="24" y2="26" {EQ_OUT}/>
      <circle cx="24" cy="24" r="2.5" {EQ_FILL}/>
      <line x1="36" y1="38" x2="36" y2="26" {EQ_OUT}/>
      <circle cx="36" cy="24" r="2.5" {EQ_FILL}/>
      <line x1="48" y1="38" x2="48" y2="30" {EQ_OUT}/>
      <circle cx="48" cy="28" r="2" {EQ_FILL}/>
      <!-- Ground line -->
      <line x1="4" y1="38" x2="56" y2="38" stroke="#1b3a6b" stroke-width="1.5"/>
    </svg>'''


# ============================================================
# DISPATCH MAP — engine name to silhouette function call
# ============================================================

def sea_dragon(part):
    """The two-part Sea Dragon. part in {'first','upper'}.
    Distinctive: fat crude pressure-fed hull, ONE enormous engine bell, launched from the
    waterline (engine bell submerged at ignition, rocket rises out of the sea)."""
    first = style(part == 'first')
    upper = style(part == 'upper')
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Ogive payload nose (payload = always outline) -->
      <path d="M20,4 Q11,26 13,52 L27,52 Q29,26 20,4 Z" {OUT}/>
      <!-- Upper stage (H4) -->
      <rect x="13" y="52" width="14" height="40" {upper}/>
      <!-- Upper engine bell -->
      <polygon points="16,92 24,92 26,100 14,100" {upper}/>
      <!-- Interstage band -->
      <rect x="11" y="101" width="18" height="3" {OUT}/>
      <!-- First stage: fat crude pressure-fed hull (K4) -->
      <rect x="11" y="104" width="18" height="72" {first}/>
      <!-- ONE enormous engine bell -->
      <polygon points="13,176 27,176 33,196 7,196" {first}/>
      <line x1="20" y1="176" x2="20" y2="196" {THIN}/>
      <!-- Waterline (sea launch): engine bell sits in the sea at ignition -->
      <path d="M2,189 q4,-3 8,0 t8,0 t8,0 t8,0 t8,0" {THIN}/>
    </svg>'''


def kerolox_sustainer():
    """K1 — Atlas/Mercury-class slim 'stage-and-a-half' sustainer with a small capsule."""
    body = style(True)
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Launch escape tower -->
      <line x1="20" y1="6" x2="20" y2="20" {THIN}/>
      <!-- Mercury capsule -->
      <polygon points="16,32 24,32 22,20 18,20" {OUT}/>
      <!-- Slim sustainer body -->
      <rect x="15" y="32" width="10" height="138" {body}/>
      <!-- Stage-and-a-half: 1 sustainer + 2 booster bells -->
      <polygon points="15,170 18.5,170 17.5,182 13.5,182" {body}/>
      <polygon points="21.5,170 25,170 26.5,182 22.5,182" {body}/>
      <polygon points="17.5,170 22.5,170 23.5,179 16.5,179" {body}/>
    </svg>'''


def super_heavy_kerolox():
    """K4 'Super Heavy Kerolox Booster' (Nova) — direct-ascent super-Saturn, EIGHT F-1 bells."""
    body = style(True)
    bells = "".join(
        f'<polygon points="{x-0.9:.1f},170 {x+0.9:.1f},170 {x+1.3:.1f},181 {x-1.3:.1f},181" {body}/>'
        for x in (10.2 + 19.6 / 7 * i for i in range(8)))
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Payload stack on top (outline) -->
      <polygon points="17,14 23,14 21,6 19,6" {OUT}/>
      <rect x="15" y="14" width="10" height="20" {OUT}/>
      <polygon points="13,46 27,46 25,34 15,34" {OUT}/>
      <!-- Big booster body (K4) -->
      <rect x="10" y="46" width="20" height="124" {body}/>
      <!-- Stabilising fins -->
      <polygon points="10,158 4,172 10,170" {body}/>
      <polygon points="30,158 36,172 30,170" {body}/>
      <!-- Eight F-1 engine bells -->
      {bells}
    </svg>'''


def kerolox_upper():
    """Ku — Falcon 9 second stage (a single Merlin Vacuum) highlighted on the F9 stack."""
    up = style(True)    # the upper is the active card
    fs = style(False)   # first stage shown in outline
    return f'''<svg viewBox="0 0 40 200" preserveAspectRatio="xMidYMid meet">
      <!-- Payload fairing -->
      <path d="M20,6 Q14,18 15,32 L25,32 Q26,18 20,6 Z" {OUT}/>
      <!-- Second stage (active) -->
      <rect x="15" y="32" width="10" height="46" {up}/>
      <!-- Single Merlin Vacuum bell -->
      <polygon points="16,78 24,78 27,90 13,90" {up}/>
      <!-- Interstage -->
      <rect x="14" y="91" width="12" height="3" {OUT}/>
      <!-- First stage booster (outline) -->
      <rect x="14" y="94" width="12" height="84" {fs}/>
      <!-- Grid fins -->
      <rect x="9" y="98" width="5" height="4" {fs}/>
      <rect x="26" y="98" width="5" height="4" {fs}/>
      <!-- Landing legs -->
      <line x1="14" y1="176" x2="9" y2="190" {fs}/>
      <line x1="26" y1="176" x2="31" y2="190" {fs}/>
      <!-- 9-Merlin base -->
      <polygon points="14,178 26,178 28,190 12,190" {fs}/>
    </svg>'''


def silhouette_for_engine(name, page):
    """Return SVG markup for the given engine card."""
    if name == "KEROLOX SUSTAINER":           return kerolox_sustainer()
    if name == "KEROLOX UPPER":               return kerolox_upper()
    if name == "SEA DRAGON":                  return sea_dragon('first')
    if name == "SUPER HYDROLOX UPPER":        return sea_dragon('upper')
    if name == "SUPER HEAVY KEROLOX BOOSTER": return super_heavy_kerolox()
    # Page 1 (heritage variants) — specific named rockets
    if name == "HEAVY KEROLOX BOOSTER":   return saturn_v('s1')
    if name == "HEAVY HYDROLOX CORE":     return saturn_v('s2')
    if name == "HEAVY HYDROLOX UPPER":    return saturn_v('s3')
    if name == "HYPERGOLIC TRANSFER STAGE": return apollo_csm()
    if name == "MARS ASCENT VEHICLE":     return mars_ascent_vehicle()
    if name == "LIGHT DESCENT ENGINE":    return apollo_lm('descent')
    if name == "LIGHT ASCENT ENGINE":     return apollo_lm('ascent')
    if name == "HEAVY SOLID BOOSTER":     return shuttle_stack('srb')
    if name == "HYDROLOX DROP TANK":      return shuttle_stack('et')
    if name == "ORBITER":                 return shuttle_stack('orbiter')
    if name == "SUPER HEAVY":             return starship_stack('booster')
    if name == "STARSHIP":                return starship_stack('upper')
    if name == "KEROLOX BOOSTER":         return soyuz_r7('boosters')
    if name == "HYDROLOX UPPER":          return atlas_centaur('centaur')
    if name == "HYPERGOLIC UPPER":        return hypergolic_upper()
    if name == "NUCLEAR ENGINE":          return nerva()
    if name == "ION ENGINE":              return ion_spacecraft()
    # Page 2 (generic class) — also covers the page-2 specific entries
    if name == "HYDROLOX BOOSTER":        return delta_iv()
    if name == "HYDROLOX CORE":           return ariane5('epc')
    if name == "SOLID BOOSTER":           return ariane5('eap')
    if name == "LIGHT SOLID BOOSTER":     return light_solid_strapon()
    if name == "LIGHT SOLID ENGINE":      return vega()
    if name == "METHALOX BOOSTER":        return methalox_stack('booster')
    if name == "METHALOX UPPER":          return methalox_stack('upper')
    if name == "KEROLOX UPPER":           return soyuz_r7('upper')
    if name == "HYPERGOLIC BOOSTER":      return proton('boosters')
    if name == "SOLID KICK ENGINE":       return solid_kick()
    if name == "SOLID KICK MOTOR":        return solid_kick()
    return ""


def eq_nuclear_reactor():
    """Compact reactor: cylindrical core with radiator fins, no solar wings."""
    return '''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Reactor core (cylindrical, central) -->
      <rect x="20" y="14" width="10" height="22" fill="#0b6cc4" stroke="#0b6cc4" stroke-width="1.5"/>
      <!-- Radiator fins (panels) on each side -->
      <rect x="6" y="18" width="12" height="14" fill="none" stroke="#0b6cc4" stroke-width="1"/>
      <line x1="6" y1="22" x2="18" y2="22" stroke="#0b6cc4" stroke-width="0.7"/>
      <line x1="6" y1="26" x2="18" y2="26" stroke="#0b6cc4" stroke-width="0.7"/>
      <line x1="6" y1="30" x2="18" y2="30" stroke="#0b6cc4" stroke-width="0.7"/>
      <rect x="32" y="18" width="12" height="14" fill="none" stroke="#0b6cc4" stroke-width="1"/>
      <line x1="32" y1="22" x2="44" y2="22" stroke="#0b6cc4" stroke-width="0.7"/>
      <line x1="32" y1="26" x2="44" y2="26" stroke="#0b6cc4" stroke-width="0.7"/>
      <line x1="32" y1="30" x2="44" y2="30" stroke="#0b6cc4" stroke-width="0.7"/>
      <!-- Radiation trefoil symbol on the core -->
      <circle cx="25" cy="25" r="3" fill="white"/>
      <circle cx="25" cy="20.5" r="1.5" fill="#0b6cc4"/>
      <circle cx="21" cy="27" r="1.5" fill="#0b6cc4"/>
      <circle cx="29" cy="27" r="1.5" fill="#0b6cc4"/>
    </svg>'''


def eq_hydrolox_refinery():
    """Ice harvester + electrolysis: cubic block on the ground with a pipe leading up
    to two output tanks (H2 and O2). Drill into ice below."""
    return '''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Ground line -->
      <line x1="3" y1="42" x2="47" y2="42" stroke="#0b6cc4" stroke-width="1.5"/>
      <!-- Drill / ice shaft (below ground) -->
      <line x1="25" y1="42" x2="25" y2="47" stroke="#0b6cc4" stroke-width="1.5"/>
      <polygon points="22,46 28,46 25,49" fill="#0b6cc4"/>
      <!-- Main electrolysis chamber (rectangular box on ground) -->
      <rect x="14" y="28" width="22" height="14" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <line x1="25" y1="28" x2="25" y2="42" stroke="#0b6cc4" stroke-width="0.7"/>
      <text x="20" y="38" font-family="Helvetica" font-size="6" font-weight="bold" fill="#0b6cc4">H</text>
      <text x="28" y="38" font-family="Helvetica" font-size="6" font-weight="bold" fill="#0b6cc4">O</text>
      <!-- Output tanks (two small cylinders rising above) -->
      <rect x="11" y="10" width="9" height="14" rx="2" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <rect x="30" y="10" width="9" height="14" rx="2" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <!-- Pipes connecting chamber to tanks -->
      <line x1="15.5" y1="24" x2="15.5" y2="28" stroke="#0b6cc4" stroke-width="1"/>
      <line x1="34.5" y1="24" x2="34.5" y2="28" stroke="#0b6cc4" stroke-width="1"/>
    </svg>'''


def eq_methalox_refinery():
    """Sabatier reactor: atmosphere intake (top funnel) + reactor box + dual tank output.
    Visually distinct from hydrolox: has the atmospheric scoop on top."""
    return '''<svg viewBox="0 0 50 50" preserveAspectRatio="xMidYMid meet">
      <!-- Atmospheric intake (funnel at top, showing CO2 inflow) -->
      <polygon points="18,4 32,4 28,12 22,12" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <text x="20" y="10" font-family="Helvetica" font-size="5" font-weight="bold" fill="#0b6cc4">CO</text>
      <!-- Reactor vessel (rounded chamber) -->
      <rect x="13" y="12" width="24" height="18" rx="3" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <text x="17" y="24" font-family="Helvetica" font-size="6" font-weight="bold" fill="#0b6cc4">CH</text>
      <text x="29" y="24" font-family="Helvetica" font-size="6" font-weight="bold" fill="#0b6cc4">O</text>
      <!-- Two output tanks below -->
      <rect x="12" y="34" width="10" height="12" rx="2" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <rect x="28" y="34" width="10" height="12" rx="2" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <!-- Pipes from reactor to tanks -->
      <line x1="17" y1="30" x2="17" y2="34" stroke="#0b6cc4" stroke-width="1"/>
      <line x1="33" y1="30" x2="33" y2="34" stroke="#0b6cc4" stroke-width="1"/>
      <!-- Ground line -->
      <line x1="3" y1="46" x2="47" y2="46" stroke="#0b6cc4" stroke-width="1"/>
    </svg>'''


def eq_light_ascent():
    """LM ascent stage: tiny pressure module with a single hypergolic nozzle below."""
    return '''<svg viewBox="0 0 40 50" preserveAspectRatio="xMidYMid meet">
      <!-- Ascent stage body (boxy crew module) -->
      <rect x="10" y="10" width="20" height="14" fill="none" stroke="#0b6cc4" stroke-width="1.5"/>
      <!-- Window -->
      <circle cx="20" cy="17" r="2" fill="#0b6cc4"/>
      <!-- Small RCS thrusters at corners -->
      <rect x="6" y="11" width="2" height="3" fill="#0b6cc4"/>
      <rect x="32" y="11" width="2" height="3" fill="#0b6cc4"/>
      <!-- Tank section -->
      <rect x="12" y="24" width="16" height="6" fill="none" stroke="#0b6cc4" stroke-width="1"/>
      <!-- Engine bell (small, single) -->
      <polygon points="16,30 24,30 26,38 14,38" fill="#0b6cc4"/>
    </svg>'''


def eq_lunar_mass_driver():
    return f'''<svg viewBox="0 0 64 40" preserveAspectRatio="xMidYMid meet">
      <!-- Lunar ground -->
      <line x1="2" y1="36" x2="44" y2="36" {EQ_OUT}/>
      <!-- Accelerator rail: two parallel rails rising to the right -->
      <line x1="4" y1="34" x2="48" y2="11" {EQ_OUT}/>
      <line x1="4" y1="37" x2="48" y2="14" {EQ_OUT}/>
      <!-- Support pylons -->
      <line x1="12" y1="31" x2="12" y2="36" {EQ_OUT}/>
      <line x1="22" y1="26" x2="22" y2="36" {EQ_OUT}/>
      <line x1="32" y1="20" x2="32" y2="36" {EQ_OUT}/>
      <line x1="42" y1="15" x2="42" y2="36" {EQ_OUT}/>
      <!-- Electromagnetic coil ticks along the rail -->
      <line x1="14" y1="28" x2="16" y2="31" {EQ_OUT}/>
      <line x1="24" y1="23" x2="26" y2="26" {EQ_OUT}/>
      <line x1="34" y1="18" x2="36" y2="21" {EQ_OUT}/>
      <!-- Payload pod launching off the top end -->
      <polygon points="50,11 58,7 60,9 52,14" {EQ_FILL}/>
      <!-- Launch / speed lines -->
      <line x1="54" y1="4" x2="61" y2="2" {EQ_OUT}/>
      <line x1="56" y1="15" x2="62" y2="14" {EQ_OUT}/>
    </svg>'''


def silhouette_for_equipment(name):
    """Return SVG markup for the given equipment card."""
    mapping = {
        "CREW CAPSULE":         eq_crew_capsule,
        "ATMOSPHERIC RETURN":   eq_atmospheric_return,
        "HEAT SHIELD":          eq_heat_shield,
        "PARACHUTE":            eq_parachute,
        "LANDING GEAR":         eq_landing_gear,
        "LIGHT ASCENT ENGINE":  eq_light_ascent,
        "CREW HABITAT":         eq_pressurised_habitat,
        "CONSUMABLES":          eq_consumables,
        "GREENHOUSE":           eq_greenhouse,
        "COMMS SATELLITE":      eq_comms_satellite,
        "LARGE ANTENNA":        eq_large_antenna,
        "SCIENCE PACKAGE":      eq_science_package,
        "ROVER":                eq_rover,
        "SAMPLE CONTAINER":     eq_sample_container,
        "SOLAR ARRAY":          eq_solar_array,
        "NUCLEAR REACTOR":      eq_nuclear_reactor,
        "RTG":                  eq_nuclear_reactor,   # reuses the reactor SVG
        "HYDROLOX REFINERY":    eq_hydrolox_refinery,
        "METHALOX REFINERY":    eq_methalox_refinery,
        "BURNER ENGINE":        eq_burner_engine,
        "LUNAR MASS DRIVER":    eq_lunar_mass_driver,
    }
    fn = mapping.get(name)
    return fn() if fn else ""
