# coding: utf-8
# authors: Jerzy Wawro, Maciej Wawro
# (C) Galicea 2020


from random import SystemRandom

def random_token(length, byte_filter):
    allowed_bytes = ''.join(c for c in map(chr, range(128)) if byte_filter(c))
    random = SystemRandom()
    return ''.join([random.choice(allowed_bytes) for _ in range(length)])

def alpha_numeric_string(length):
    return random_token(length, str.isalnum)
