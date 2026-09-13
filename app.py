import streamlit as st
from decimal import Decimal, getcontext
import math

getcontext().prec = 50

def first_digit_expected_probabilities():
    probabilities = {}
    for d in range(1, 10):
        probabilities[d] = math.log10(1 + 1 / d)
    return probabilities

def second_digit_expected_probabilities():
    probabilities = {}
    for d in range(0, 10):
        total = 0
        for k in range(1, 10):
            total += math.log10(1 + 1 / (10 * k + d))
        probabilities[d] = total
    return probabilities

def chi_square_statistic(observed_counts, expected_probabilities, total_count):
    chi_square = 0
    for digit in expected_probabilities:
        observed = observed_counts.get(digit, 0)
        expected = expected_probabilities[digit] * total_count
        chi_square += ((observed - expected) ** 2) / expected
    return chi_square

def mean_absolute_deviation(observed_counts, expected_probabilities, total_count):
    k = len(expected_probabilities)
    total_deviation = 0
    for digit in expected_probabilities:
        observed_proportion = observed_counts.get(digit, 0) / total_count
        expected_proportion = expected_probabilities[digit]
        total_deviation += abs(observed_proportion - expected_proportion)
    mad = total_deviation / k
    return mad

def mad_conformity_first_digit(mad):
    if mad <= 0.006:
        return "Close conformity"
    elif mad <= 0.012:
        return "Acceptable conformity"
    elif mad <= 0.015:
        return "Marginal conformity"
    else:
        return "Nonconformity"

def mad_conformity_second_digit(mad):
    if mad <= 0.008:
        return "Close conformity"
    elif mad <= 0.010:
        return "Acceptable conformity"
    elif mad <= 0.012:
        return "Marginal conformity"
    else:
        return "Nonconformity"

def extract_significant_digits(number):
    number = abs(number)
    if number == 0:
        return None
    decimal_number = Decimal(str(number)).quantize(Decimal('1.' + '0' * 15))
    digit_string = str(decimal_number).replace('.', '').replace('-', '')
    digit_string = digit_string.lstrip('0').rstrip('0')
    if len(digit_string) == 0:
        return None
    leading_digit = int(digit_string[0])
    second_digit = int(digit_string[1]) if len(digit_string) > 1 else None
    return leading_digit, second_digit
