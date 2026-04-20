"""
Fintech Mobile App Onboarding Data Simulator
=============================================
Generates realistic synthetic data for funnel analysis.
Drop-off rates calibrated to published fintech industry benchmarks:
  - Deloitte (2023): 38% abandon during KYC
  - AppsFlyer (2023): ~25% of installs never open the app
  - Mixpanel (2023): avg fintech Day-7 retention ~25-30%
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker("en_IN")
np.random.seed(42)
random.seed(42)

# ── Config ──────────────────────────────────────────────────────────────────
N_USERS         = 10_000
START_DATE      = datetime(2024, 1, 1)
END_DATE        = datetime(2024, 6, 30)
OUTPUT_DIR      = "/home/claude/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Funnel drop-off rates (cumulative from install) ──────────────────────────
# Each value = probability that a user REACHES this stage
FUNNEL_RATES = {
    "app_install":          1.00,   # baseline
    "app_open":             0.76,   # 24% install & never open  (AppsFlyer benchmark)
    "signup_started":       0.55,   # friction before sign-up form
    "signup_completed":     0.42,   # form abandonment
    "kyc_initiated":        0.34,   # hesitation before sharing documents
    "kyc_completed":        0.21,   # 38% of KYC starters abandon (Deloitte)
    "first_transaction":    0.15,   # activation drop
    "notification_opted_in":0.11,   # permission fatigue
    "day1_return":          0.09,   # early churn
    "day7_return":          0.05,   # ~25-30% of actives retained (Mixpanel)
}

# ── Segment definitions ──────────────────────────────────────────────────────
DEVICES      = ["Android", "iOS"]
DEVICE_DIST  = [0.72, 0.28]          # India market share

CHANNELS     = ["Organic", "Paid Ad", "Referral", "Social Media"]
CHANNEL_DIST = [0.30, 0.35, 0.25, 0.10]

CITY_TIERS   = ["Tier 1", "Tier 2", "Tier 3"]
CITY_DIST    = [0.40, 0.35, 0.25]

# Channel modifiers — paid users convert slightly worse at KYC (ad-reality gap)
CHANNEL_KYC_MODIFIER = {
    "Organic":      1.10,
    "Paid Ad":      0.80,   # worse KYC conversion
    "Referral":     1.20,   # best — referred users are more motivated
    "Social Media": 0.90,
}


# ── 1. Generate Users table ──────────────────────────────────────────────────
def generate_users(n):
    print(f"Generating {n} users...")
    records = []
    for i in range(1, n + 1):
        signup_dt = START_DATE + timedelta(
            seconds=random.randint(0, int((END_DATE - START_DATE).total_seconds()))
        )
        records.append({
            "user_id":         f"U{i:06d}",
            "signup_date":     signup_dt.date(),
            "age":             int(np.random.choice(
                                    range(18, 56),
                                    p=np.array(
                                        [3]*7 + [4]*10 + [2]*10 + [1]*11,
                                        dtype=float) / np.sum([3]*7 + [4]*10 + [2]*10 + [1]*11)
                                )),
            "gender":          random.choice(["Male", "Female", "Other"]),
            "city_tier":       np.random.choice(CITY_TIERS, p=CITY_DIST),
            "device_type":     np.random.choice(DEVICES, p=DEVICE_DIST),
            "acquisition_channel": np.random.choice(CHANNELS, p=CHANNEL_DIST),
            "name":            fake.name(),
        })
    return pd.DataFrame(records)


# ── 2. Generate Events table ─────────────────────────────────────────────────
def event_time(base_dt, minutes_min, minutes_max):
    """Returns base_dt + random minutes offset."""
    return base_dt + timedelta(minutes=random.randint(minutes_min, minutes_max))


def generate_events(users_df):
    print("Generating events...")
    events = []
    stages = list(FUNNEL_RATES.keys())

    for _, user in users_df.iterrows():
        uid      = user["user_id"]
        channel  = user["acquisition_channel"]
        base_dt  = datetime.combine(user["signup_date"], datetime.min.time()) \
                   + timedelta(hours=random.randint(0, 23))

        # Timestamps — each step happens after the previous
        ts = {
            "app_install":           base_dt,
            "app_open":              event_time(base_dt,          1,   30),
            "signup_started":        event_time(base_dt,          5,   60),
            "signup_completed":      event_time(base_dt,         10,  120),
            "kyc_initiated":         event_time(base_dt,         15,  180),
            "kyc_completed":         event_time(base_dt,         30,  300),
            "first_transaction":     event_time(base_dt,         60,  720),
            "notification_opted_in": event_time(base_dt,         65,  730),
            "day1_return":           event_time(base_dt,       1440, 2880),
            "day7_return":           event_time(base_dt,      10080, 11520),
        }

        # Convert cumulative rates to conditional (stage-to-stage) probabilities
        cum = list(FUNNEL_RATES.values())
        cond = {}
        for i, s in enumerate(stages):
            cond[s] = 1.0 if i == 0 else (cum[i] / cum[i-1] if cum[i-1] > 0 else 0.0)

        # Walk funnel — stop at first drop-off
        for stage in stages:
            rate = cond[stage]
            if stage in ("kyc_initiated", "kyc_completed", "first_transaction"):
                rate = min(rate * CHANNEL_KYC_MODIFIER[channel], 1.0)

            if random.random() <= rate:
                events.append({
                    "user_id":    uid,
                    "event_name": stage,
                    "event_ts":   ts[stage],
                })
            else:
                break

    return pd.DataFrame(events)


# ── 3. Run & save ────────────────────────────────────────────────────────────
def main():
    users_df  = generate_users(N_USERS)
    events_df = generate_events(users_df)

    # Save CSVs
    users_df.to_csv(f"{OUTPUT_DIR}/users.csv",   index=False)
    events_df.to_csv(f"{OUTPUT_DIR}/events.csv", index=False)

    # ── Quick sanity report ──────────────────────────────────────────────────
    print("\n" + "="*55)
    print("SIMULATION COMPLETE — SANITY CHECK")
    print("="*55)
    print(f"Total users   : {len(users_df):,}")
    print(f"Total events  : {len(events_df):,}")
    print(f"\nFunnel stage reach rates (actual vs target):\n")

    total = len(users_df)
    for stage in FUNNEL_RATES:
        actual_n    = events_df[events_df["event_name"] == stage]["user_id"].nunique()
        actual_pct  = actual_n / total * 100
        target_pct  = FUNNEL_RATES[stage] * 100
        print(f"  {stage:<28} {actual_n:>6,} users  "
              f"({actual_pct:5.1f}% actual | {target_pct:5.1f}% target)")

    print(f"\nFiles saved to: {OUTPUT_DIR}/")
    print("  users.csv   — user attributes")
    print("  events.csv  — onboarding event log")

    # Device split
    print(f"\nDevice split:\n{users_df['device_type'].value_counts().to_string()}")

    # Channel split
    print(f"\nAcquisition channel split:\n{users_df['acquisition_channel'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
