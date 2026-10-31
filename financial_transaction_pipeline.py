from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

INPUT_FILE = Path("synthetic_financial_transactions.csv")
OUTPUT_DIR = Path("financial_analysis_output")
REQUIRED_COLUMNS = [
    "Transaction ID", "Transaction date", "Description", "Supplier",
    "Amount", "Category", "Payment reference", "Payment method"
]

# 1. CSV loading and validation
def load_and_validate(path):
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path.resolve()}")

    # on_bad_lines='error' stops processing if a row has a malformed number of fields.
    df = pd.read_csv(path, dtype=str, keep_default_na=False, on_bad_lines="error")

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df = df[REQUIRED_COLUMNS].copy()
    issues = []

    for col in REQUIRED_COLUMNS:
        blank_count = int(df[col].astype(str).str.strip().eq("").sum())
        if blank_count:
            issues.append(f"{col}: {blank_count} blank value(s)")

    # Convert dates and amounts while retaining invalid-row evidence.
    parsed_dates = pd.to_datetime(df["Transaction date"], format="%Y-%m-%d", errors="coerce")
    parsed_amounts = pd.to_numeric(
        df["Amount"].str.replace(",", "", regex=False).str.replace("KES", "", regex=False).str.strip(),
        errors="coerce"
    )

    invalid_date = parsed_dates.isna()
    invalid_amount = parsed_amounts.isna() | (parsed_amounts <= 0)
    invalid_id = df["Transaction ID"].duplicated(keep=False)
    invalid_reference_blank = df["Payment reference"].str.strip().eq("")

    df["Transaction date"] = parsed_dates
    df["Amount"] = parsed_amounts

    # Preserve all rows in the rejected report; continue analysis only with valid essentials.
    reject_mask = invalid_date | invalid_amount | invalid_id | invalid_reference_blank
    rejected = df.loc[reject_mask].copy()
    rejected["Validation issue"] = ""

    for idx in rejected.index:
        reasons = []
        if invalid_date.loc[idx]: reasons.append("Invalid date; expected YYYY-MM-DD")
        if invalid_amount.loc[idx]: reasons.append("Invalid or non-positive amount")
        if invalid_id.loc[idx]: reasons.append("Duplicate Transaction ID")
        if invalid_reference_blank.loc[idx]: reasons.append("Missing payment reference")
        rejected.loc[idx, "Validation issue"] = "; ".join(reasons)

    valid = df.loc[~reject_mask].copy()
    valid["Transaction date"] = valid["Transaction date"].dt.strftime("%Y-%m-%d")
    valid["Amount"] = valid["Amount"].astype(float)

    report = [
        f"Rows read: {len(df)}",
        f"Rows accepted: {len(valid)}",
        f"Rows rejected: {len(rejected)}",
        f"Duplicate transaction IDs found: {int(invalid_id.sum())}",
        f"Invalid dates found: {int(invalid_date.sum())}",
        f"Invalid/non-positive amounts found: {int(invalid_amount.sum())}",
        "Malformed CSV rows: parser raises an error rather than silently accepting them."
    ]
    return valid, rejected, report


# 2. Deterministic expense categorization
CATEGORY_RULES = {
    "Office Supplies": ["stationery", "paper", "ink", "toner", "pens", "files", "notebooks", "office furniture"],
    "Travel": ["travel", "flight", "hotel", "airport", "transport", "trip", "accommodation", "shuttle"],
    "Utilities": ["electricity", "water", "internet", "telephone", "data charges", "utility"],
    "Rent": ["rent", "lease", "meeting room", "warehouse space"],
    "IT & Software": ["software", "cloud", "hosting", "domain", "laptop", "computer", "it support", "licence", "license"],
    "Marketing": ["advertising", "brochure", "printing", "promotional", "social media", "campaign"],
    "Repairs & Maintenance": ["repair", "maintenance", "servicing", "plumbing", "air conditioning", "generator"],
    "Professional Services": ["accounting", "legal", "consulting", "consultation", "tax advisory", "strategy"],
    "Meals & Entertainment": ["catering", "refreshments", "lunch", "meals", "meeting refreshments"],
    "Fuel": ["fuel", "refuelling", "refueling", "petrol", "diesel"],
}

def categorize(description, supplier, existing_category):
    text = f"{description} {supplier}".lower()
    matches = []
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            matches.append(category)
    if len(matches) == 1:
        return matches[0], "Rule-based match"
    if len(matches) > 1:
        return existing_category, "Ambiguous; retained supplied category"
    if existing_category in CATEGORY_RULES:
        return existing_category, "No keyword match; retained supplied category"
    return "Uncategorized", "Needs human/AI review"

def apply_categorization(df):
    results = df.apply(
        lambda r: categorize(r["Description"], r["Supplier"], r["Category"]),
        axis=1
    )
    df = df.copy()
    df["Detected category"] = [x[0] for x in results]
    df["Categorization method"] = [x[1] for x in results]
    return df


# 3. Rule-based duplicate payment detection
def detect_duplicates(df):
    df = df.copy()
    df["Duplicate flag"] = False
    df["Duplicate reason"] = ""

    # A repeated payment reference is a strong duplicate signal.
    repeated_ref = df["Payment reference"].duplicated(keep=False)
    df.loc[repeated_ref, "Duplicate flag"] = True
    df.loc[repeated_ref, "Duplicate reason"] = "Repeated payment reference"

    # Same supplier + amount + date is a possible duplicate; it requires review.
    composite = df.assign(
        _date=pd.to_datetime(df["Transaction date"]).dt.strftime("%Y-%m-%d"),
        _amount=df["Amount"].round(2),
        _supplier_key=df["Supplier"].str.strip().str.casefold()
    )
    same_payment = composite.duplicated(
        subset=["_supplier_key", "_amount", "_date"], keep=False
    )
    idx = df.index[same_payment]
    df.loc[idx, "Duplicate flag"] = True
    current = df.loc[idx, "Duplicate reason"]
    df.loc[idx, "Duplicate reason"] = current.where(
        current.ne(""),
        "Same supplier, amount and date"
    )
    df.loc[idx, "Duplicate reason"] = df.loc[idx, "Duplicate reason"].apply(
        lambda x: x if "Same supplier" in x else x + "; same supplier, amount and date"
    )
    return df


# 4. Statistical and rule-based anomaly detection
def detect_anomalies(df):
    df = df.copy()
    df["Anomaly score"] = np.nan
    df["Isolation Forest flag"] = False
    df["Anomaly reasons"] = ""

    # Features are numeric/encoded and do not use free-text LLM judgments.
    work = df.copy()
    work["_log_amount"] = np.log1p(work["Amount"].clip(lower=0))
    work["_day_of_year"] = pd.to_datetime(work["Transaction date"]).dt.dayofyear
    work["_supplier_frequency"] = work.groupby("Supplier")["Supplier"].transform("count")
    work["_category_code"] = work["Detected category"].astype("category").cat.codes
    work["_method_code"] = work["Payment method"].astype("category").cat.codes

    features = work[[
        "_log_amount", "_day_of_year", "_supplier_frequency",
        "_category_code", "_method_code"
    ]].replace([np.inf, -np.inf], np.nan).fillna(0)

    if len(df) >= 20:
        model = IsolationForest(
            n_estimators=200, contamination=0.05, random_state=42
        )
        predictions = model.fit_predict(features)
        scores = -model.score_samples(features)
        df["Anomaly score"] = scores
        df["Isolation Forest flag"] = predictions == -1

    # Transparent business rules complement the statistical model.
    amount_cutoff = max(300000.00, float(df["Amount"].quantile(0.99)))
    high_amount = df["Amount"] > amount_cutoff
    df.loc[high_amount, "Anomaly reasons"] = "Amount exceeds review threshold"

    duplicate = df["Duplicate flag"]
    df.loc[duplicate, "Anomaly reasons"] = df.loc[duplicate, "Anomaly reasons"].apply(
        lambda x: (x + "; " if x else "") + "Possible duplicate payment"
    )

    # Unusually high supplier payment compared with the dataset median.
    supplier_median = df.groupby("Supplier")["Amount"].transform("median")
    supplier_count = df.groupby("Supplier")["Supplier"].transform("count")
    supplier_outlier = (supplier_count >= 3) & (df["Amount"] > supplier_median * 4)
    df.loc[supplier_outlier, "Anomaly reasons"] = df.loc[supplier_outlier, "Anomaly reasons"].apply(
        lambda x: (x + "; " if x else "") + "More than 4x supplier's median transaction"
    )

    # Monthly spending changes: flag transactions in months whose total is > 2x
    # the median monthly total, provided there are at least 3 months of data.
    dates = pd.to_datetime(df["Transaction date"])
    month_key = dates.dt.to_period("M").astype(str)
    monthly_totals = df.groupby(month_key)["Amount"].sum()
    if len(monthly_totals) >= 3:
        monthly_median = monthly_totals.median()
        unusual_months = monthly_totals[monthly_totals > monthly_median * 2].index
        month_spike = month_key.isin(unusual_months)
        df.loc[month_spike, "Anomaly reasons"] = df.loc[month_spike, "Anomaly reasons"].apply(
            lambda x: (x + "; " if x else "") + "Transaction occurred in a month with unusually high total spend"
        )

    # Include statistical flags in the report, but retain rule evidence separately.
    statistical_only = df["Isolation Forest flag"] & df["Anomaly reasons"].eq("")
    df.loc[statistical_only, "Anomaly reasons"] = "Isolation Forest identified an unusual feature pattern"

    df["Anomaly flag"] = df["Anomaly reasons"].ne("")
    return df


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    df, rejected, validation_lines = load_and_validate(INPUT_FILE)

    categorized = apply_categorization(df)
    duplicated = detect_duplicates(categorized)
    analyzed = detect_anomalies(duplicated)

    analyzed.to_csv(OUTPUT_DIR / "processed_transactions.csv", index=False)
    analyzed.loc[analyzed["Duplicate flag"]].to_csv(
        OUTPUT_DIR / "duplicate_report.csv", index=False
    )
    analyzed.loc[analyzed["Anomaly flag"]].to_csv(
        OUTPUT_DIR / "anomaly_report.csv", index=False
    )
    rejected.to_csv(OUTPUT_DIR / "rejected_records.csv", index=False)

    validation_lines += [
        f"Possible duplicate rows: {int(analyzed['Duplicate flag'].sum())}",
        f"Anomaly rows reported: {int(analyzed['Anomaly flag'].sum())}",
        f"Rows needing categorization review: {int((analyzed['Detected category'] == 'Uncategorized').sum())}",
    ]
    (OUTPUT_DIR / "validation_report.txt").write_text(
        "\n".join(validation_lines) + "\n", encoding="utf-8"
    )

    print("\n".join(validation_lines))
    print(f"\nOutputs saved in: {OUTPUT_DIR.resolve()}")
    print(" - processed_transactions.csv")
    print(" - duplicate_report.csv")
    print(" - anomaly_report.csv")
    print(" - rejected_records.csv")
    print(" - validation_report.txt")


if __name__ == "__main__":
    main()
