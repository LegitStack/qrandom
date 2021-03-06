import time
import sys

from .lib.TrueRNG import TrueRNG
from .lib.two_sigma import get_2_sigma_score
from .lib.bayesian import bayesian_score


def build_generator(blocksize=1):
    random_number_generator = TrueRNG(blocksize=blocksize, numloops=1)
    return random_number_generator


def generate_and_count(random_number_generator):
    random_string = ''.join(random_number_generator.generate())
    bit_count = len(random_string)
    one_count = sum([int(s) for s in random_string])
    return random_string, bit_count, one_count


def run_for_seconds(random_number_generator, seconds, verbose=False):
    total_count = 0
    total_ones = 0
    start = time.time()
    finish = time.time()
    while abs(start - finish) < seconds:
        random_string, bit_count, one_count = generate_and_count(random_number_generator)
        total_count += bit_count
        total_ones += one_count
        if verbose:
            print(random_string, end='', file=sys.stdout)
        finish = time.time()
    print()
    return total_count, total_ones


def get_two_sigma_scoring(bit_count, ones_count):
    return get_2_sigma_score(bit_count, ones_count)


def deduce_zero_or_one(random_number_generator):
    one_count = 0
    bit_count = 0
    while bit_count == 0 or (bit_count / 2) == one_count:
        _, bit_count, one_count = generate_and_count(random_number_generator)
    return 0 if bit_count / 2 > one_count else 1


def inclusive_between_still_wont_work(random_number_generator, lower, higher):
    def add_offset(lower, higher):
        diff = abs(higher + 1 - lower)
        b = bin(diff)
        if b[0:3] == '0b1' and '1' not in b[3:]:
            return higher, lower, 0
        offset = eval('0b10' + b[3:].replace('1','0')) - diff
        return lower - offset, offset + higher, offset
    def remove_offset(lower, higher, target):
        pass
    def return_condition(key, condition, value):
        if condition == '>=':
            return True if key >= value else False
        else:
            return True if key > value else False


    difference = abs(higher + 1 - lower)  / 2
    target = difference
    condition = '>=' if deduce_zero_or_one(random_number_generator) == 1 else '>'
    while return_condition(difference, condition, 1):
        if deduce_zero_or_one(random_number_generator) == 1:
            difference = difference / 2
            target += difference if difference >= 1 else difference * 2
        else:
            difference = difference / 2
            target -= difference if difference >= 1 else difference * 2
        #print('d', difference, 't', target)
    print('final', target)
    if target < lower:
        return inclusive_between(random_number_generator, lower, higher)
    return target


def inclusive_between_orig(random_number_generator, lower, higher):
    two_x_counter = abs(higher + 1 - lower)
    target = abs(higher + 1 - lower) / 2
    while two_x_counter > 1:
        _, bit_count, one_count = generate_and_count(random_number_generator)
        if bit_count / 2 > one_count:
            two_x_counter = two_x_counter / 2
            target -= two_x_counter
        elif bit_count / 2 < one_count:
            two_x_counter = two_x_counter / 2
            target += two_x_counter
        print(two_x_counter, target)
    print(target + lower)
    return target + lower


def inclusive_between_for_small_numbers(random_number_generator, lower, higher):
    def get_max_values(c):
        maxv = max(c.values())
        maxvs = {k: v for k, v in c.items() if v == maxv}
        return maxvs
    counters = {}
    counters = { each: 0 for each in range(lower, higher + 1)}
    max_values = get_max_values(counters)
    while len(max_values) > 1:
        for each in range(lower, higher + 1):
            _, _, one_count = generate_and_count(random_number_generator)
            counters[each] = counters[each] + one_count
            max_values = get_max_values(counters)
    return list(max_values.keys())[0]
