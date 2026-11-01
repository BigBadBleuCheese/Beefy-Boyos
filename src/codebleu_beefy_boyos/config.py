import configparser
import os

from codebleu_beefy_boyos import log, paths

DEFAULT_TEXT = """; Beefy Boyos
; Gives randomly generated male Sims (teen through elder) builds that use
; LAVAMANAMADE's and Golyhawhaw's body sliders alongside EA's.
; Only Sims the game generates are affected. Sims you make in CAS, premades
; and Gallery Sims are left alone. Changes apply to Sims generated after the
; file is read (game load, or the beefyboyos.reload cheat).
;
; Ranges are written "low-high" (for example 0.75-0.85) or as a single number.
; Slider values run from 0 (off) to 1 (all the way).

[General]
; false turns the mod off without uninstalling it.
enabled = true

[Beef Tiers]
; Each generated male rolls one tier. Format: name = chance, strength
; Chances are relative weights; they don't need to add up to 1.
; Strength "none" means the game's own build. 1.0 is the full Beefy Boyos look.
; Below 1.0, LAVAMANAMADE's sliders are toned down first, then EA's.
normal = 0.4, none
well built = 0.5, 0.75-0.85
chad = 0.1, 1.0

[Chub Tiers]
; Rolled separately from beef, so a Sim can be both.
normal = 0.7, none
chubby = 0.225, 0.65-0.75
big bear = 0.075, 1.0

[Overall]
; Multiplies every beef or chub strength above. 0.8 tones everyone down a bit.
beef strength = 1.0
chub strength = 1.0
; true means only beefed Sims can be chubby.
chubby only if beefed = false

[Beef]
; How beefy a beefed Sim is before the per-slider weights below.
level = 0.22-0.38
; How far each body part can drift from the others. 0.9-1.1 keeps them consistent.
part variation = 0.9-1.1
; EA's muscle (fitness) for beefed Sims.
muscle = 0.75-1.0

[LAVAMANAMADE Weights]
; How hard each LAVAMANAMADE slider is pushed on beefed Sims, relative to the
; beef level. 2.0 is twice as much, 0.5 is half.
upper arms = 1.3
forearms = 2.0
back = 2.2
chest = 0.5
thighs = 1.3
calves = 2.0
muscle torso = 1.0
neck = 1.5

[EA Sliders When Beefed]
; EA's slider for each body part is raised to this first; LAVAMANAMADE's
; slider then adds on top.
upper arms = 1.0
forearms = 1.0
shoulders = 0.7-0.9
torso width = 0.7-0.9
thighs = 1.0
calves = 1.0
feet = 0.8-1.0
; Golyhawhaw's foot width, added after EA's feet.
foot width = 0.05-0.25

[Chub]
; EA's fat for chubby Sims.
fat = 0.4-0.8
; EA's belly slider first, then LAVAMANAMADE's beer gut on top.
belly = 0.6-1.0
beer gut = 0.1-0.4

[Butt]
; Everyone gets at least this much EA butt. No pancakes.
minimum = 0.2-0.35
; Added when beefed and when chubby. Once EA's butt slider is full, the rest
; goes into LAVAMANAMADE's, so only Sims who are both get the really big ones.
from beef = 0.5-0.7
from chub = 0.5-0.7
lavamanamade share = 1.0

[Everyone Else]
; Sims who aren't beefed: chance of a random Golyhawhaw neck and foot width,
; and how far it goes.
chance = 0.5
amount = 0.1-0.6
"""

_SETTINGS = (
    ('General', 'enabled', 'bool', ('enabled',)),
    ('Overall', 'beef strength', 'float', ('beef_master',)),
    ('Overall', 'chub strength', 'float', ('chub_master',)),
    ('Overall', 'chubby only if beefed', 'bool', ('chubby_requires_beef',)),
    ('Beef', 'level', 'range', ('beef_range',)),
    ('Beef', 'part variation', 'range', ('beef_spread',)),
    ('Beef', 'muscle', 'range', ('fit_range',)),
    ('LAVAMANAMADE Weights', 'upper arms', 'float', ('weights', 'arms')),
    ('LAVAMANAMADE Weights', 'forearms', 'float', ('weights', 'forearm')),
    ('LAVAMANAMADE Weights', 'back', 'float', ('weights', 'back')),
    ('LAVAMANAMADE Weights', 'chest', 'float', ('weights', 'pecs')),
    ('LAVAMANAMADE Weights', 'thighs', 'float', ('weights', 'legs')),
    ('LAVAMANAMADE Weights', 'calves', 'float', ('weights', 'calves')),
    ('LAVAMANAMADE Weights', 'muscle torso', 'float', ('weights', 'muscletorso')),
    ('LAVAMANAMADE Weights', 'neck', 'float', ('weights', 'neck')),
    ('EA Sliders When Beefed', 'upper arms', 'range', ('ea_levels', 'arms')),
    ('EA Sliders When Beefed', 'forearms', 'range', ('ea_levels', 'forearm')),
    ('EA Sliders When Beefed', 'shoulders', 'range', ('ea_levels', 'back')),
    ('EA Sliders When Beefed', 'torso width', 'range', ('ea_levels', 'pecs')),
    ('EA Sliders When Beefed', 'thighs', 'range', ('ea_levels', 'legs')),
    ('EA Sliders When Beefed', 'calves', 'range', ('ea_levels', 'calves')),
    ('EA Sliders When Beefed', 'feet', 'range', ('ea_levels', 'feet')),
    ('EA Sliders When Beefed', 'foot width', 'range', ('feet_widen',)),
    ('Chub', 'fat', 'range', ('fat_range',)),
    ('Chub', 'belly', 'range', ('ea_levels', 'belly')),
    ('Chub', 'beer gut', 'range', ('gut_range',)),
    ('Butt', 'minimum', 'range', ('butt_floor',)),
    ('Butt', 'from beef', 'range', ('butt_beef',)),
    ('Butt', 'from chub', 'range', ('butt_chubby',)),
    ('Butt', 'lavamanamade share', 'float', ('butt_lava_scale',)),
    ('Everyone Else', 'chance', 'float', ('side_chance',)),
    ('Everyone Else', 'amount', 'range', ('side_range',)),
)


def _parse_range(text):
    text = text.strip()
    separator = text.find('-', 1)
    if separator < 0:
        value = float(text)
        return value, value
    low = float(text[:separator])
    high = float(text[separator + 1:])
    return min(low, high), max(low, high)


def _parse_bool(text):
    lowered = text.strip().lower()
    if lowered in ('true', 'yes', 'on', '1'):
        return True
    if lowered in ('false', 'no', 'off', '0'):
        return False
    raise ValueError(text)


_PARSERS = {'float': lambda text: float(text.strip()), 'range': _parse_range, 'bool': _parse_bool}


def _parse_tiers(parser, section):
    tiers = []
    for name, text in parser.items(section):
        chance_text, _, strength_text = text.partition(',')
        chance = float(chance_text.strip())
        strength_text = strength_text.strip().lower()
        strength = None if strength_text in ('', 'none') else _parse_range(strength_text)
        if chance > 0:
            tiers.append((name, chance, strength))
    if not tiers:
        raise ValueError('no tiers with a chance above 0')
    return tiers


def _read(text):
    parser = configparser.ConfigParser(comment_prefixes=(';', '#'), inline_comment_prefixes=(';',), interpolation=None)
    parser.read_string(text)
    return parser


def _store(params, target, value):
    if len(target) == 1:
        params[target[0]] = value
    else:
        params.setdefault(target[0], {})[target[1]] = value


def _build(parser, fallback, problems):
    params = {'weights': {}, 'ea_levels': {}}
    for section, key, kind, target in _SETTINGS:
        try:
            value = _PARSERS[kind](parser.get(section, key))
        except (configparser.Error, ValueError) as ex:
            if fallback is None:
                raise
            problems.append('[{}] {}: {}'.format(section, key, ex))
            value = fallback[target[0]] if len(target) == 1 else fallback[target[0]][target[1]]
        _store(params, target, value)
    for section, name in (('Beef Tiers', 'beef_tiers'), ('Chub Tiers', 'chub_tiers')):
        try:
            params[name] = _parse_tiers(parser, section)
        except (configparser.Error, ValueError) as ex:
            if fallback is None:
                raise
            problems.append('[{}]: {}'.format(section, ex))
            params[name] = fallback[name]
    return params


DEFAULTS = _build(_read(DEFAULT_TEXT), None, [])


def load():
    path = paths.config_path()
    if not os.path.exists(path):
        try:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(DEFAULT_TEXT)
            log.write('Wrote default settings to {}'.format(path))
        except OSError as ex:
            log.write('Could not write default settings to {}: {}'.format(path, ex))
            return DEFAULTS
    try:
        with open(path, 'r', encoding='utf-8-sig') as file:
            parser = _read(file.read())
    except (OSError, configparser.Error) as ex:
        log.write('Could not read {}, using defaults: {}'.format(path, ex))
        return DEFAULTS
    problems = []
    params = _build(parser, DEFAULTS, problems)
    for problem in problems:
        log.write('Using the default for {}'.format(problem))
    log.write('Read settings from {}'.format(path))
    return params
