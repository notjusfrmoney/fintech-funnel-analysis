# Fintech Mobile App Onboarding Funnel Analysis

A end-to-end data analytics project. tracked users through an app onboarding funnel, find where they drop off, and recommend fixes backed by data.

---

## The Business Problem

A fintech app ran a 6-month growth campaign and got 10,000 installs. Despite spending heavily on Paid Ads (35% of all users came from this channel), the overall conversion to first transaction was critically low. The questions I tried to answer:

- Where exactly in the funnel are users dropping off?
- Which acquisition channels are actually worth the spend?
- Does city tier (metro vs Tier 2/3) affect conversion?
- Are certain cohorts (signup weeks) performing better than others?
- What's driving the Day-7 retention problem?

---

## Key Findings

| Finding | Number |
|--------|--------|
| Overall conversion (install → first transaction) | **15.9%** |
| Biggest single drop-off step | **KYC: 35.8%** |
| Best acquisition channel | **Referral: 25.1%** |
| Worst acquisition channel | **Paid Ad: 7.0%** |
| Referral vs Paid Ad gap | **3.6× better** |
| Day-1 retention (vs 40–50% benchmark) | **9.6%** |
| Day-7 retention (vs 25–30% benchmark) | **5.4%** |
| Average D1 → D7 decay | **44.2%** |
| City Tier conversion difference | **None — all ~15.8%** |

The two biggest problems: KYC friction is killing 1 in 3 users, and 90% of users don't come back the next day after installing.

---

## Recommendations

1. **Fix KYC first** — it's the single biggest drop-off point (35.8%). Progressive disclosure UI (step 1 of 3 instead of one long form), Aadhaar OTP pre-fill, and real-time photo quality feedback would all help.
2. **Reallocate Paid Ad budget to Referral** — Paid Ad is the largest channel by volume (35% of users) but converts at only 7%. Referral converts at 25.1%. Even shifting 10% of Paid Ad budget to a referral incentive programme would meaningfully improve blended conversion.
3. **Days 2–6 re-engagement push sequence** — personalised notifications based on where the user stopped (e.g. "Your KYC is 80% done — complete it to unlock cashback") to recover the D1→D7 drop.
4. **Expand to Tier 2/3 markets without hesitation** — the data shows zero conversion penalty in smaller cities. Tier 3 actually has a slightly better Day-7 retention (5.8%) than Tier 1 (5.2%).

---

## Project Structure

```
fintech-funnel-analysis/
│
├── data/
│   ├── users_clean.csv          # 10,000 users with attributes and funnel stage
│   ├── events_clean.csv         # 36,932 event-level records
│   ├── cohort_summary.csv       # 26 weekly cohorts with conversion + retention
│   ├── funnel_stages.csv        # 10 funnel stages with drop-off rates
│   ├── channel_summary.csv      # Channel-level performance summary
│   └── segment_summary.csv      # Tier, age, device, gender breakdown
│
├── notebooks/
│   ├── phase2_cleaning.ipynb         # Data validation and cleaning
│   ├── phase3_funnel_analysis.ipynb  # Funnel, segmentation, KYC deep-dive
│   ├── phase4_cohort_retention.ipynb # Weekly cohorts, D1/D7 retention
│   └── phase5_visualisations.ipynb  # Export-ready chart suite (14 charts)
│
├── charts/                      # All 14 exported PNG charts
│
├── dashboard/
│   └── fintech_funnel.pbix      # Power BI dashboard (3 pages)
│
├── fintech_simulator.py         # Data simulation script
└── README.md
```

---

## Dataset

The dataset is fully synthetic but calibrated to published industry benchmarks:

- **AppsFlyer 2023** — 24% of installs never open the app (used for app_open drop-off)
- **Deloitte 2023** — 38% of users abandon during KYC (used for KYC drop-off calibration)
- **Mixpanel 2023** — Day-7 fintech retention is 25–30% for top apps (used as retention benchmark)

User attributes (age, city tier, gender, device) were generated using the Faker library with realistic Indian fintech user distributions.

**Why synthetic?** Real onboarding data from fintech companies is not publicly available — it's protected under India's DPDP Act and company NDAs. Synthetic data built on published benchmarks is industry-standard practice for portfolio projects, and is also how many companies do internal testing before launching features.

---

## Tech Stack

| Tool | Used For |
|------|---------|
| Python (Pandas, NumPy) | Data simulation, cleaning, analysis |
| Plotly | Interactive and export-ready charts |
| Faker | Generating realistic Indian user profiles |
| Jupyter Notebook | Analysis workflow (inside VSCode) |
| Power BI Desktop | 3-page interactive dashboard |

---

## Power BI Dashboard

Three pages:

**Page 1 — Funnel Overview**
10-stage funnel chart, step drop-off bar chart with conditional colouring (red = critical), 4 KPI cards, slicers for channel/device/city tier.

**Page 2 — Cohort & Retention**
D1 vs D7 retention trend with industry benchmark bands, cohort heatmap (26 weeks), cohort size + conversion combo chart, cohort health scatter plot.

**Page 3 — User Segments**
Channel conversion horizontal bar, volume vs quality scatter, city tier bars, age group bars, gender donut, KYC deep-dive panel.

---

## How to Run

**Python notebooks:**
```bash
git clone https://github.com/YOUR_USERNAME/fintech-funnel-analysis
cd fintech-funnel-analysis
pip install pandas numpy plotly faker kaleido
# Open notebooks in order: phase2 → phase3 → phase4 → phase5
```

**Power BI dashboard:**
- Open `dashboard/fintech_funnel.pbix` in Power BI Desktop
- If data doesn't load, go to Home → Transform data → Data source settings → update the file paths to where you've saved the CSVs

---

## What I Learned

- Funnel analysis is more about asking the right questions than knowing the right tools — the KYC insight only emerged when I segmented by channel, not from the overall funnel view
- Synthetic data for portfolio projects is harder than it sounds — getting realistic drop-off patterns required reading actual industry reports, not just making up numbers
- Power BI's conditional formatting on bar charts is underrated for telling a data story quickly — the red KYC bar communicates the problem faster than any written insight
- Cohort analysis confirmed that the funnel problem is structural, not seasonal — no week solved it on its own, which rules out timing/campaign explanations


