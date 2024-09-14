import random

PREFIXES = ["Li", "Ar", "Le", "Ze", "Ma", "Ja", "Re", "Ve", "Am", "Jer", "Jav", "Gil", "Zee", "Jos", "Al", "Bl", "Co", "Cla", "Fri", "Ca"]
MIDDLE = ["li", "ma", "va", "todd", "derk", "ne", "le", "ne", "lo", "el", "be", "ind", "rn", "em", "m", "zz", "con", "orp", "rupe", "u"]
SUFFIXES = ["son", "mes", "gan", "iam", "pel", "arm", "za", "er", "pinto", "io", "i", "bert", "zog", "gam", "rt", "le", "de", "into", "v"]
LAST_PREFIXES = ["Ec", "Joh", "Di", "Mo", "Za", "Cr", "Se", "Sk", "Bar", "Val", "Zer", "Via"]
LAST_MIDDLE = ["kart", "mo", "vert", "wart", "mio", "vale", "er", "can", "do"]
LAST_SUFFIXES = ["ie", "ov", "om", "aw", "un", "ot", "el", "in", "ig", "seg", "ov"]

def first_name():
    return random.choice(PREFIXES) + random.choice(MIDDLE) + random.choice(SUFFIXES)

def last_name():
    return random.choice(LAST_PREFIXES) + random.choice(LAST_MIDDLE) + random.choice(LAST_SUFFIXES)

def full_name():
    return f"{first_name()} {last_name()}"