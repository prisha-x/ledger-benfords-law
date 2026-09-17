# Ledger

**[Try it live →](https://ledger-benford-fraud-screen.streamlit.app/)**

Digit patterns can reveal unusual or unexpected behavior in financial data, which is why forensic accountants and auditors use Benford's Law as one screening technique when investigating potential irregularities. This tool analyzes financial or expense data using Benford's Law and statistical tests like MAD and chi-square to detect unusual digit patterns. It then turns those results into a suspicion score, helping identify datasets that may warrant further investigation.

## Why Python and Streamlit

I chose Python and Streamlit because they let me build a real, shareable web app while staying consistent with the Python-based work I've already done. It also made it easier to focus on the statistical analysis and Benford's Law rather than building a separate JavaScript stack just for the interface.

## The Statistics Behind It

The engine tests both the first and second digits of the financial data against their expected Benford distributions. It uses MAD to measure the overall size of the deviation and chi-square to test whether the observed differences are statistically significant. I then combine these results into a suspicion score using my own composite formula, rather than a published or standardized Benford metric. The score is meant to highlight unusual patterns for further investigation, not prove fraud.

## Limitations

This is a screening tool, not proof of fraud—an unusual Benford pattern can have legitimate explanations. The results also become more meaningful with larger datasets, so the tool is best used with several hundred rows rather than small samples.

## How to Run It Locally

1. Clone this repository
2. Create and activate a virtual environment:

python -m venv venv

   On Windows (PowerShell):

venv\Scripts\Activate.ps1

   On Mac/Linux:

source venv/bin/activate

3. Install dependencies:

pip install -r requirements.txt

4. Run the app:

streamlit run app.py

5. Open the local URL shown in your terminal (typically `http://localhost:8501`)

## Credits

This project was developed in the context of MLH Global Hack Week: Data, based on a research question I chose for my group during the Princeton STEM Initiative internship - Advance Math. The MAD conformity thresholds are based on Mark Nigrini's published work on Benford's Law and are used with appropriate attribution.