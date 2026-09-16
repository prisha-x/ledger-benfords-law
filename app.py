import streamlit as st
from decimal import Decimal, getcontext
import math
import random
import matplotlib.pyplot as plt
import pandas as pd

getcontext().prec = 50

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=IBM+Plex+Mono:wght@400;600&display=swap');

.stApp {
    background-color: #12141A;
    color: #EDE8DA;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
}

[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
}
</style>
"""

def first_digit_expected_probabilities():
    probabilities = {}
    for d in range(1, 10):
        probabilities[d] = math.log10(1 + 1 / d)
    return probabilities

def second_digit_expected_probabilities():
    probabilities = {}
    for d in range(0, 10):
        digit_total = 0
        for k in range(1, 10):
            digit_total += math.log10(1 + 1 / (10 * k + d))
        probabilities[d] = digit_total
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
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
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
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    data = None
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        numeric_columns = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_columns) == 0:
            st.error("No numeric columns found in this file.")
        else:
            selected_column = st.selectbox("Select the numeric column to analyze:", numeric_columns)
            data = df[selected_column].dropna().tolist()

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

    if score < 30:
        gauge_color = "#1F5C57"
    elif score < 60:
        gauge_color = "#D98E3B"
    else:
        gauge_color = "#B23B3B"

    fig_gauge, ax_gauge = plt.subplots(figsize=(4, 2.2), subplot_kw={"projection": "polar"})
    ax_gauge.set_theta_zero_location("W")
    ax_gauge.set_theta_direction(-1)
    ax_gauge.set_thetamin(0)
    ax_gauge.set_thetamax(180)

    ax_gauge.barh(0, 180, left=0, height=1, color="#DCD3B8", edgecolor="none")
    ax_gauge.barh(0, max((score / 100) * 180, 1), left=0, height=0.9, color=gauge_color, edgecolor="none")

    ax_gauge.set_yticklabels([])
    ax_gauge.set_xticklabels([])
    ax_gauge.grid(False)
    ax_gauge.spines['polar'].set_visible(False)
    ax_gauge.set_title(f"Suspicion: {score}/100", fontsize=14, pad=20)

    col_gauge, col_spacer = st.columns([1, 2])
    with col_gauge:
        st.pyplot(fig_gauge)

    st.caption(f"Total rows analyzed: {total_count}")

    if total_count < 300:
        st.warning("⚠ Small sample (n < 300) — deviations at this size can occur by chance. Treat the suspicion score above as low-confidence.")

    st.subheader("First-Digit Distribution")

    digits = list(range(1, 10))
    observed_percentages = [observed_counts.get(d, 0) / total_count * 100 for d in digits]
    expected_percentages = [expected[d] * 100 for d in digits]

    fig, ax = plt.subplots()
    ax.bar(digits, observed_percentages, label="Observed", alpha=0.7)
    ax.plot(digits, expected_percentages, color="red", marker="o", label="Expected (Benford)")
    ax.set_xlabel("Leading Digit")
    ax.set_ylabel("Percentage (%)")
    ax.set_xticks(digits)
    ax.legend()

    st.pyplot(fig)

    st.subheader("Evidence Log — Rows Driving the Anomaly")

    data_with_leading_digits = []
    for row_index, amount in enumerate(data):
        result = extract_significant_digits(amount)
        if result is not None:
            data_with_leading_digits.append((row_index, result[0]))

    flagged = flag_anomalous_rows(data_with_leading_digits, observed_counts, expected, total_count)

    if len(flagged) == 0:
        st.write("No rows flagged — digit distribution stays within expected bounds.")
    else:
        for entry in flagged[:20]:
            row_num = entry["row"]
            amount_value = data[row_num]
            if entry["status"] == "over-represented":
                color = "#D98E3B"
            else:
                color = "#1F5C57"
            st.markdown(
                f"<span style='color:{color}'>Row {row_num}: ${amount_value:.2f} — leading digit {entry['leading_digit']} ({entry['status']})</span>",
                unsafe_allow_html=True
            )