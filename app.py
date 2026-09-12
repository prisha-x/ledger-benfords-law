import streamlit as st
from decimal import Decimal, getcontext

getcontext().prec = 50
import math

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
