import random

from protocolbuffers import FileSerialization_pb2, PersistenceBlobs_pb2
from sims.sim_info_types import Age, Gender, Species
import sims.sim_spawner
import sims4.resources

from beefy_boyos import config, log

SIM_MODIFIER = 0xC5F6763E
MUSCLES = {0xDE6748A8566A5819: 'arms', 0xE657C169CDD24312: 'forearm', 0xCDEB59691E2516A8: 'back', 0xCD712B208EAB24CB: 'pecs', 0x9BFA831DFFB9033C: 'legs', 0xB2F3991F2D306A8B: 'calves'}
EA_FIRST = {
    'arms': (0x6261A06DDEDEA018, 0xBED14A8430BDD847),
    'forearm': (0x0DD4FE1F16C1C2D5, 0x5A0CB921E44D9D42),
    'back': (0x986563FD375BE39A, 0xD62D482F434C209A),
    'pecs': (0x76D60E43E9435703, 0x2BC50AD1ABE44EB3),
    'legs': (0x179D2C61CC0EF525, 0xA2B59435DF5964B2),
    'calves': (0x1594131061F398A7, 0x715F2BD334269D98),
    'belly': (0x4F2D03EEFE084B0C, 0x02515F22B613AD0B),
    'feet': (0x814A1078EB0A9302, 0xB0D6FB60786FCD15)
}
EA_BUTT_BIG = 0xAC393D794EDC62BD
EA_BUTT_SMALL = 0x177E2F90D59E78EA
LAVA_BUTT = 0x8A251791C00B1565
MUSCLE_TORSO = 0xB6AAA077D59CCE78
BEER_GUT = 0xAA244B33096DC191
NECK_WIDE = 0xE1FB99776698648F
NECK_THIN = 0xCBD0F035DDCF624A
FEET_WIDEN = 0xF9CECA0D48D2810B
FEET_STANDARD = 0xF7BC141B65DBDE3C
CUSTOM = {
    0xDE6748A8566A5819: 'LAVAMANAMADE upper arms', 0xE657C169CDD24312: 'LAVAMANAMADE forearms', 0xCDEB59691E2516A8: 'LAVAMANAMADE back',
    0xCD712B208EAB24CB: 'LAVAMANAMADE chest', 0x9BFA831DFFB9033C: 'LAVAMANAMADE thighs', 0xB2F3991F2D306A8B: 'LAVAMANAMADE calves',
    LAVA_BUTT: 'LAVAMANAMADE butt', MUSCLE_TORSO: 'LAVAMANAMADE muscle torso', BEER_GUT: 'LAVAMANAMADE beer gut',
    NECK_WIDE: 'Golyhawhaw neck up', NECK_THIN: 'Golyhawhaw neck down', FEET_WIDEN: 'Golyhawhaw foot widen', FEET_STANDARD: 'Golyhawhaw foot standard'
}
HEAVY, FIT, LEAN, BONY = 0, 1, 2, 3
ELIGIBLE_AGES = (int(Age.TEEN), int(Age.YOUNGADULT), int(Age.ADULT), int(Age.ELDER))

params = config.DEFAULTS
_original = None
_available = None


def _installed_sliders():
    global _available
    if _available is None:
        found = set()
        for instance, name in CUSTOM.items():
            try:
                exists = sims4.resources.does_key_exist(sims4.resources.Key(SIM_MODIFIER, instance, 0))
            except Exception as ex:
                log.write('Could not check for {}: {!r}'.format(name, ex))
                exists = False
            if exists:
                found.add(instance)
        missing = sorted(name for instance, name in CUSTOM.items() if instance not in found)
        log.write('Custom sliders found: {} of {}{}'.format(len(found), len(CUSTOM), '; missing: ' + ', '.join(missing) if missing else ''))
        _available = found
    return _available


def _usable(key):
    return key not in CUSTOM or key in _installed_sliders()


def _put(facial, key, amount, opposite, keep_larger=False):
    if not _usable(key):
        return
    targets = [facial.body_modifiers]
    if len(facial.aged_body_modifiers):
        targets.append(facial.aged_body_modifiers)
    for modifiers in targets:
        value = amount
        for index in reversed(range(len(modifiers))):
            if modifiers[index].key == key and keep_larger:
                value = max(value, modifiers[index].amount)
            if modifiers[index].key in (key, opposite):
                del modifiers[index]
        if value > 0:
            entry = modifiers.add()
            entry.key = key
            entry.amount = min(1.0, value)


def _random_side(facial, pair):
    if random.random() < params['side_chance']:
        first, second = pair
        if random.random() < 0.5:
            first, second = second, first
        if _usable(first):
            _put(facial, first, random.uniform(*params['side_range']), second)


def _set_physique(proto, raise_index, raise_value, clear_index):
    parts = proto.physique.split(',') if proto.physique else []
    while len(parts) < 4:
        parts.append('0.000')
    try:
        current = float(parts[raise_index] or 0)
    except ValueError:
        current = 0.0
    parts[raise_index] = '{:.3f}'.format(max(min(1.0, raise_value), current))
    parts[clear_index] = '0.000'
    proto.physique = ','.join(parts)


def _trim(ea, lava, master):
    total = ea + lava
    change = total * master - total
    if change >= 0:
        return ea, min(1.0, lava + change)
    cut = -change
    lava_cut = min(lava, cut)
    return max(0.0, ea - (cut - lava_cut)), lava - lava_cut


def _roll_tier(tiers):
    total = 0.0
    for tier in tiers:
        total += tier[1]
    roll = random.uniform(0.0, total)
    chosen = tiers[-1]
    for tier in tiers:
        if roll < tier[1]:
            chosen = tier
            break
        roll -= tier[1]
    strength = chosen[2]
    return random.uniform(*strength) if strength else None


def _stacked(facial, name, lava_key, lava_opposite, lava_amount, master):
    ea_levels = params['ea_levels']
    has_ea = name in EA_FIRST and name in ea_levels
    ea_amount = min(1.0, random.uniform(*ea_levels[name])) if has_ea else 0.0
    if not _usable(lava_key):
        lava_amount = 0.0
    ea_amount, lava_amount = _trim(ea_amount, lava_amount, master)
    if has_ea:
        big, small = EA_FIRST[name]
        _put(facial, big, ea_amount, small, True)
    _put(facial, lava_key, lava_amount, lava_opposite)


def _beef_up(data, dictionary):
    if dictionary is None:
        return data
    if int(dictionary.get('gender', -1)) != int(Gender.MALE) or int(dictionary.get('age', -1)) not in ELIGIBLE_AGES or int(dictionary.get('species', Species.HUMAN)) != int(Species.HUMAN):
        return data
    proto = FileSerialization_pb2.SimData()
    proto.ParseFromString(data)
    facial = PersistenceBlobs_pb2.BlobSimFacialCustomizationData()
    facial.MergeFromString(proto.facial_attr)
    weights = params['weights']
    beef_master = _roll_tier(params['beef_tiers'])
    chub_master = _roll_tier(params['chub_tiers'])
    beefed = beef_master is not None
    if chub_master is not None and params['chubby_requires_beef'] and not beefed:
        chub_master = None
    chubby = chub_master is not None
    butt = random.uniform(*params['butt_floor'])
    if beefed:
        beef_master *= params['beef_master']
        beef = random.uniform(*params['beef_range'])

        def level(name):
            return min(1.0, beef * weights.get(name, 1.0) * random.uniform(*params['beef_spread']))

        butt += random.uniform(*params['butt_beef']) * beef_master
        _set_physique(proto, FIT, random.uniform(*params['fit_range']) * beef_master, BONY)
        for key, name in MUSCLES.items():
            _stacked(facial, name, key, None, level(name), beef_master)
        if not chubby:
            _put(facial, MUSCLE_TORSO, level('muscletorso') * beef_master, BEER_GUT)
        _put(facial, NECK_WIDE, level('neck') * beef_master, NECK_THIN)
        _stacked(facial, 'feet', FEET_WIDEN, FEET_STANDARD, random.uniform(*params['feet_widen']), beef_master)
    else:
        _random_side(facial, (NECK_WIDE, NECK_THIN))
        _random_side(facial, (FEET_WIDEN, FEET_STANDARD))
    if chubby:
        chub_master *= params['chub_master']
        butt += random.uniform(*params['butt_chubby']) * chub_master
        _set_physique(proto, HEAVY, random.uniform(*params['fat_range']) * chub_master, LEAN)
        _stacked(facial, 'belly', BEER_GUT, MUSCLE_TORSO, random.uniform(*params['gut_range']), chub_master)
    _put(facial, EA_BUTT_BIG, min(1.0, butt), EA_BUTT_SMALL, True)
    if butt > 1.0:
        _put(facial, LAVA_BUTT, (butt - 1.0) * params['butt_lava_scale'], None)
    proto.facial_attr = facial.SerializeToString()
    return proto.SerializeToString()


def _generate_household(*args, **kwargs):
    result = _original(*args, **kwargs)
    if not params['enabled']:
        return result
    try:
        dictionaries = kwargs.get('sim_creation_dictionaries')
        if dictionaries is None and args:
            dictionaries = args[0]
        dictionaries = tuple(dictionaries or ())
        updated = []
        for index, data in enumerate(result['sims']):
            updated.append(_beef_up(data, dictionaries[index] if index < len(dictionaries) else None))
        result['sims'] = updated
    except Exception as ex:
        log.write('Left a generated household unchanged after an error: {!r}'.format(ex))
    return result


def reload():
    global params
    params = config.load()
    return params


def start():
    global _original
    reload()
    current = getattr(sims.sim_spawner, 'generate_household', None)
    if not callable(current) or not hasattr(sims.sim_spawner.SimSpawner, 'create_sim_infos'):
        log.write('The game no longer has the generator Beefy Boyos expects; staying inactive.')
        return False
    if current is _generate_household:
        return True
    _original = current
    sims.sim_spawner.generate_household = _generate_household
    log.write('Installed.')
    return True
