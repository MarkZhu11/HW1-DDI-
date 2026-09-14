# COVID-19 Daily Counts in NYC - Three Data Questions

## Why I Chose This Dataset

I chose the NYC COVID-19 daily counts dataset because it was something really really big that I encountered. I remember taking online classes and RNA tests in highschool back in China. My mom was working for the health department of the city and everyday she was counting the number of deaths. Due to the nature of her job, she couldn't send every information to our family group chat, but she'd always tell us the number of deaths everyday during that disaster. This dataset of COVID-19, in some ways, shows us how a public health crisis changed over time and across different parts of the city, and does the similar job my mom's messages did.

This dataset has 2,054 rows and 55 columns, which is much larger than the minimum requirement. It also has borough categories such as Bronx, Brooklyn, Manhattan, Queens, and Staten Island, which are encoded in column prefixes. That makes the dataset useful for thinking about how CSV files can represent regional relationships.

For the analysis below, I used native Python with `csv.DictReader`. I also removed the final incomplete reporting rows from the main questions by keeping only rows where `INCOMPLETE == 0`. This leaves 2,047 complete rows.

---

## Three Data Questions

### Question 1: How many reporting days had at least 1,000 total cases?

Here I combine confirmed cases and probable cases into one total daily case count. I think this is more meaningful than looking only at confirmed cases because the dataset tracks both types separately.

```python
# Question: How many reporting days had at least 1,000 total cases?
high_case_days = [row for row in complete_rows if row["ALL_DAILY_CASES"] >= 1000]
peak_case_day = max(complete_rows, key=lambda row: row["ALL_DAILY_CASES"])

print("Days:", len(high_case_days))
print("Percent of complete days:", round(len(high_case_days) / len(complete_rows) * 100, 1))
print("First such date:", min(row["date_of_interest"] for row in high_case_days))
print("Last such date:", max(row["date_of_interest"] for row in high_case_days))
print("Peak total-case day:")
print(
    {
        "date_of_interest": peak_case_day["date_of_interest"],
        "ALL_DAILY_CASES": peak_case_day["ALL_DAILY_CASES"],
        "CASE_COUNT": peak_case_day["CASE_COUNT"],
        "PROBABLE_CASE_COUNT": peak_case_day["PROBABLE_CASE_COUNT"],
    }
)
```

Output:

```text
Days: 890
Percent of complete days: 43.5
First such date: 2020-03-15
Last such date: 2024-08-12
Peak total-case day:
{'date_of_interest': datetime.date(2022, 1, 3),
 'ALL_DAILY_CASES': 60929,
 'CASE_COUNT': 55058,
 'PROBABLE_CASE_COUNT': 5871}
```

Why the data structure supports this question:
This works because each row is one date, and the citywide case columns are numeric counts for that date. The date column then lets me identify when this level of spread first and last occurred.

### Question 2: On how many days did NYC have both high hospitalizations and high deaths?

For this question, I define high hospitalizations as at least 100 new hospitalizations in a day and high deaths as at least 25 deaths in a day. This question helps identify the days when COVID-19 had a particularly severe impact on NYC. High hospitalizations indicate that many people were sick enough to require hospital care and there was a heavy pressure on health system, while high deaths indicate serious loss of life. Looking at when both were high shows the days that NYC were impacted the most.

```python
# Question: On how many days did NYC have both high hospitalizations and high deaths?
severity_breakdown = {
    (False, False): 0,
    (False, True): 0,
    (True, False): 0,
    (True, True): 0,
}

for row in complete_rows:
    high_hospitalizations = row["HOSPITALIZED_COUNT"] >= 100
    high_deaths = row["DEATH_COUNT"] >= 25
    severity_breakdown[(high_hospitalizations, high_deaths)] += 1

for (high_hospitalizations, high_deaths), days in severity_breakdown.items():
    print(
        "high_hospitalizations:",
        high_hospitalizations,
        "high_deaths:",
        high_deaths,
        "days:",
        days,
    )
```

Output:

```text
high_hospitalizations: False high_deaths: False days: 1396
high_hospitalizations: False high_deaths: True days: 43
high_hospitalizations: True high_deaths: False days: 326
high_hospitalizations: True high_deaths: True days: 282

Days with both high hospitalizations and high deaths: 282
First both-high date: 2020-03-19
Last both-high date: 2023-01-24
```

Why the data structure supports this question:
This works because hospitalization and death counts are stored in separate columns for the same daily row. Since both measurements belong to the same date, I can apply two conditions to each row and count the days in each true/false combination.

### Question 3: Which borough had the largest cumulative COVID burden in the complete rows?

This question compares borough-level totals for confirmed cases, hospitalizations, and deaths. However, I think I actually need more information such as original population, region area,...to really reveal the meaning of the statistics.

```python
# Question: Which borough had the largest cumulative COVID burden?
boroughs = {
    "Bronx": "BX",
    "Brooklyn": "BK",
    "Manhattan": "MN",
    "Queens": "QN",
    "Staten Island": "SI",
}

borough_rows = []
for borough, prefix in boroughs.items():
    borough_rows.append(
        {
            "borough": borough,
            "confirmed_cases": sum(row[f"{prefix}_CASE_COUNT"] for row in complete_rows),
            "hospitalizations": sum(row[f"{prefix}_HOSPITALIZED_COUNT"] for row in complete_rows),
            "deaths": sum(row[f"{prefix}_DEATH_COUNT"] for row in complete_rows),
        }
    )

borough_totals = sorted(borough_rows, key=lambda row: row["confirmed_cases"], reverse=True)
print(borough_totals)
```

Output:

```text
[{'borough': 'Brooklyn',
  'confirmed_cases': 917605,
  'hospitalizations': 68113,
  'deaths': 14779},
 {'borough': 'Queens',
  'confirmed_cases': 851302,
  'hospitalizations': 61875,
  'deaths': 14095},
 {'borough': 'Manhattan',
  'confirmed_cases': 553815,
  'hospitalizations': 35318,
  'deaths': 6517},
 {'borough': 'Bronx',
  'confirmed_cases': 508499,
  'hospitalizations': 48486,
  'deaths': 8865},
 {'borough': 'Staten Island',
  'confirmed_cases': 213151,
  'hospitalizations': 13915,
  'deaths': 2888}]

Highest confirmed-case total: Brooklyn with 917,605 confirmed cases
```

Why the data structure supports this question:
This works because the CSV repeats the same measurements for each borough. For example, Brooklyn has `BK_CASE_COUNT`, `BK_HOSPITALIZED_COUNT`, and `BK_DEATH_COUNT`. By mapping each prefix to a borough name, I can sum the matching columns and compare borough totals.

---

## What the Data Cannot Answer

One question I would like to answer is: "Which groups of people were most at risk during each wave of COVID-19 in NYC?" This dataset cannot answer that question by itself because it does not include individual-level age, race, income, occupation, vaccination status, testing access, underlying health conditions, or population denominators by borough. It would be misleading to assume that the borough with the largest total case count had the highest individual risk, because boroughs have different population sizes. The dataset can show reported daily counts, but it cannot explain the social or medical reasons behind those counts without additional data.
