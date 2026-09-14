import csv
from datetime import datetime
from pprint import pprint


CSV_FILE = "COVID-19_Daily_Counts_of_Cases,_Hospitalizations,_and_Deaths_20260914.csv"


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def parse_int(value):
    if value is None or value == "":
        return 0
    return int(str(value).replace(",", ""))


def clean_row(row):
    cleaned = {}
    for key, value in row.items():
        if key == "date_of_interest":
            cleaned[key] = datetime.strptime(value, "%m/%d/%Y").date()
        else:
            cleaned[key] = parse_int(value)

    cleaned["ALL_DAILY_CASES"] = cleaned["CASE_COUNT"] + cleaned["PROBABLE_CASE_COUNT"]
    return cleaned


with open(CSV_FILE, newline="") as file:
    reader = csv.DictReader(file)
    column_names = reader.fieldnames
    rows = [clean_row(row) for row in reader]

# The final dates in this file are marked incomplete, so the questions below use
# only complete rows for comparisons.
complete_rows = [row for row in rows if row["INCOMPLETE"] == 0]

print_section("1. First 2 rows")
pprint(rows[:2], sort_dicts=False)

print_section("2. First row")
pprint(rows[0], sort_dicts=False)

print_section("3. Rows 10-19")
pprint(rows[10:20], sort_dicts=False)

print_section("4. Column names")
print(column_names + ["ALL_DAILY_CASES"])

print_section("5. First 10 values of one column: ALL_DAILY_CASES")
print([row["ALL_DAILY_CASES"] for row in rows[:10]])

print_section("6. First 10 rows of three columns")
three_columns = [
    {
        "date_of_interest": row["date_of_interest"],
        "ALL_DAILY_CASES": row["ALL_DAILY_CASES"],
        "HOSPITALIZED_COUNT": row["HOSPITALIZED_COUNT"],
    }
    for row in rows[:10]
]
pprint(three_columns, sort_dicts=False)

# Question 1: How many reporting days had at least 1,000 total cases
# when confirmed and probable cases are combined?
print_section("Question 1: Complete days with at least 1,000 total cases")
high_case_days = [row for row in complete_rows if row["ALL_DAILY_CASES"] >= 1000]
peak_case_day = max(complete_rows, key=lambda row: row["ALL_DAILY_CASES"])

print("Days:", len(high_case_days))
print("Percent of complete days:", round(len(high_case_days) / len(complete_rows) * 100, 1))
print("First such date:", min(row["date_of_interest"] for row in high_case_days))
print("Last such date:", max(row["date_of_interest"] for row in high_case_days))
print("Peak total-case day:")
pprint(
    {
        "date_of_interest": peak_case_day["date_of_interest"],
        "ALL_DAILY_CASES": peak_case_day["ALL_DAILY_CASES"],
        "CASE_COUNT": peak_case_day["CASE_COUNT"],
        "PROBABLE_CASE_COUNT": peak_case_day["PROBABLE_CASE_COUNT"],
    },
    sort_dicts=False,
)

# Question 2: On how many days did NYC have both high hospitalizations and high
# deaths? I define high hospitalizations as at least 100 in a day and high deaths
# as at least 25 in a day.
print_section("Question 2: High hospitalizations and high deaths")
severity_breakdown = {
    (False, False): 0,
    (False, True): 0,
    (True, False): 0,
    (True, True): 0,
}

both_high_dates = []
for row in complete_rows:
    high_hospitalizations = row["HOSPITALIZED_COUNT"] >= 100
    high_deaths = row["DEATH_COUNT"] >= 25
    severity_breakdown[(high_hospitalizations, high_deaths)] += 1

    if high_hospitalizations and high_deaths:
        both_high_dates.append(row["date_of_interest"])

for (high_hospitalizations, high_deaths), days in severity_breakdown.items():
    print(
        "high_hospitalizations:",
        high_hospitalizations,
        "high_deaths:",
        high_deaths,
        "days:",
        days,
    )

print("Days with both high hospitalizations and high deaths:", len(both_high_dates))
print("First both-high date:", min(both_high_dates))
print("Last both-high date:", max(both_high_dates))

# Question 3: Which borough had the largest cumulative COVID burden in the
# complete rows?
print_section("Question 3: Borough totals in complete rows")
boroughs = {
    "Bronx": "BX",
    "Brooklyn": "BK",
    "Manhattan": "MN",
    "Queens": "QN",
    "Staten Island": "SI",
}

borough_totals = []
for borough, prefix in boroughs.items():
    borough_totals.append(
        {
            "borough": borough,
            "confirmed_cases": sum(row[f"{prefix}_CASE_COUNT"] for row in complete_rows),
            "hospitalizations": sum(row[f"{prefix}_HOSPITALIZED_COUNT"] for row in complete_rows),
            "deaths": sum(row[f"{prefix}_DEATH_COUNT"] for row in complete_rows),
        }
    )

borough_totals.sort(key=lambda row: row["confirmed_cases"], reverse=True)
pprint(borough_totals, sort_dicts=False)

top_borough = borough_totals[0]
print(
    "Highest confirmed-case total:",
    f"{top_borough['borough']} with {top_borough['confirmed_cases']:,} confirmed cases",
)
