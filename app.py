import streamlit as st
from decimal import Decimal, getcontext
import math
import random

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

def calculate_suspicion_score(mad, chi_square, total_count):
    if mad <= 0.006:
        mad_tier = 0
    elif mad <= 0.012:
        mad_tier = 1
    elif mad <= 0.015:
        mad_tier = 2
    else:
        mad_tier = 3

    mad_component = (mad_tier / 3) * 55
    chi_component = min(chi_square / 40, 1) * 45
    raw_score = mad_component + chi_component

    reliability = min(total_count / 300, 1)
    final_score = raw_score * reliability

    return round(min(final_score, 100))

def flag_anomalous_rows(data_with_leading_digits, observed_counts, expected_probabilities, total_count):
    deviations = {}
    for digit in expected_probabilities:
        observed_proportion = observed_counts.get(digit, 0) / total_count
        expected_proportion = expected_probabilities[digit]
        deviations[digit] = observed_proportion - expected_proportion

    sorted_digits = sorted(deviations.items(), key=lambda item: abs(item[1]), reverse=True)
    top_two_digits = [digit for digit, deviation in sorted_digits[:2]]

    flagged_rows = []
    for row_index, leading_digit in data_with_leading_digits:
        if leading_digit in top_two_digits:
            direction = "over-represented" if deviations[leading_digit] > 0 else "under-represented"
            flagged_rows.append({"row": row_index, "leading_digit": leading_digit, "status": direction})

    return flagged_rows

def generate_expense_ledger_demo(seed=42, n=400, fraud_fraction=0.35):
    rng = random.Random(seed)
    rows = []
    fraud_count = round(n * fraud_fraction)
    genuine_count = n - fraud_count

    for _ in range(genuine_count):
        magnitude = rng.uniform(1, 4)
        amount = round(10 ** magnitude, 2)
        rows.append(amount)

    for _ in range(fraud_count):
        amount = round(rng.uniform(400, 499.99), 2)
        rows.append(amount)

    rng.shuffle(rows)
    return rows

def generate_clean_baseline_demo(seed=7, n=1000):
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        magnitude = rng.uniform(1, 6)
        amount = round(10 ** magnitude, 2)
        rows.append(amount)
    return rows

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

st.set_page_config(page_title="Ledger — Is this data suspicious?", layout="wide")
st.title("Ledger")
st.caption("A Benford's Law anomaly screening tool")

st.subheader("01 — Choose a case file")

demo_choice = st.radio(
    "Select a dataset to analyze:",
    ["Expense Ledger (suspicious)", "Clean Baseline", "Upload my own CSV"]
)

if demo_choice == "Expense Ledger (suspicious)":
    data = generate_expense_ledger_demo()
elif demo_choice == "Clean Baseline":
    data = generate_clean_baseline_demo()
else:
    data = None
    st.info("CSV upload coming soon.")

if data is not None:
    st.subheader("02 — Analysis Results")

    observed_counts = {}
    for amount in data:
        result = extract_significant_digits(amount)
        if result is not None:
            leading_digit = result[0]
            observed_counts[leading_digit] = observed_counts.get(leading_digit, 0) + 1

    total_count = len(data)
    expected = first_digit_expected_probabilities()

    chi = chi_square_statistic(observed_counts, expected, total_count)
    mad = mean_absolute_deviation(observed_counts, expected, total_count)
    score = calculate_suspicion_score(mad, chi, total_count)
    conformity = mad_conformity_first_digit(mad)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Suspicion Score", f"{score}/100")
    col2.metric("Chi-Square (df=8)", f"{chi:.2f}")
    col3.metric("MAD Score", f"{mad:.4f}")
    col4.metric("Conformity", conformity)

    st.caption(f"Total rows analyzed: {total_count}")