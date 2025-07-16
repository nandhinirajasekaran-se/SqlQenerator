import sqlite3
import uuid
import random
from datetime import datetime, timedelta

import pandas as pd

# Connect to the database
conn = sqlite3.connect("claims.db")
cursor = conn.cursor()

# Utility functions
def generate_uuid():
    return str(uuid.uuid4())

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# --- Synthetic Data Generation ---

# 1. insurance_providers
providers = [
    ("prov1", "Maple Health", "Leading national provider"),
    ("prov2", "TrueCare Insurance", "Trusted by millions"),
    ("prov3", "WellSpring", "Affordable family plans")
]
cursor.executemany("INSERT INTO insurance_providers (provider_id, name, description) VALUES (?, ?, ?)", providers)

# 2. users
users = []
for i in range(5):
    uid = generate_uuid()
    users.append((
        f"User{i+1}",
        f"User_name{i+1}",
        random_date(datetime(1980, 1, 1), datetime(2000, 12, 31)).strftime("%Y-%m-%d"),
        f"HC{i+1000}",
        f"user{i+1}@example.com",
        f"555-010{i}",
        random.choice(providers)[0]
    ))
cursor.executemany("INSERT INTO users (user_id, name, dob, health_card, email, phone, provider_id) VALUES (?, ?, ?, ?, ?, ?, ?)", users)


# 4. claims
claims = []
for u in users:
    claim_id = generate_uuid()
    claims.append((
        claim_id,
        u[0],
        u[-1],  # provider_id
        generate_uuid(),  # random policy_id
        random_date(datetime(2023, 1, 1), datetime(2024, 6, 1)).strftime("%Y-%m-%d"),
        random.choice(["drug", "dental", "vision", "hospital"]),
        f"SVC{random.randint(100, 999)}",
        "Routine check or prescription",
        round(random.uniform(50, 500), 2),
        round(random.uniform(10, 300), 2),
        random.choice(["Pending", "Approved", "Rejected"]),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
cursor.executemany("""INSERT INTO claims (
    claim_id, user_id, provider_id, policy_id, service_date, claim_type,
    service_code, description, amount_claimed, amount_approved, status, submitted_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", claims)

conn.commit()
conn.close()

conn = sqlite3.connect("claims.db")
cursor = conn.cursor()

# Fetch existing user and provider IDs
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT provider_id FROM insurance_providers")
provider_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT claim_id FROM claims")
claim_ids = [row[0] for row in cursor.fetchall()]

# Create synthetic data for policies
plans = ["Basic", "Standard", "Premium"]
frequencies = ["monthly", "quarterly", "annually"]

policy_rows = []
for user_id in user_ids:
    provider_id = random.choice(provider_ids)
    policy_id = str(uuid.uuid4())
    policy_number = f"POL{random.randint(1000, 9999)}"
    plan_type = random.choice(plans)
    coverage_start = datetime.now().date() - timedelta(days=random.randint(100, 365))
    coverage_end = coverage_start + timedelta(days=365)
    premium = round(random.uniform(100.0, 500.0), 2)
    frequency = random.choice(frequencies)
    active = True
    policy_rows.append((policy_id, user_id, provider_id, policy_number, plan_type,
                        coverage_start, coverage_end, premium, frequency, active))

cursor.executemany("""
    INSERT INTO policies (policy_id, user_id, provider_id, policy_number, plan_type,
                          coverage_start, coverage_end, monthly_premium, billing_frequency, active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", policy_rows)

# Create synthetic data for drug_details
drug_names = ["Paracetamol", "Atorvastatin", "Metformin", "Ibuprofen", "Amoxicillin"]
drug_details_rows = []

for claim_id in claim_ids[:5]:  # Only assign drug details to first 5 claims for variety
    drug_name = random.choice(drug_names)
    DIN_code = f"D{random.randint(10000, 99999)}"
    quantity = random.randint(10, 90)
    dosage = f"{random.randint(250, 1000)}mg"
    drug_details_rows.append((claim_id, drug_name, DIN_code, quantity, dosage))

cursor.executemany("""
    INSERT INTO drug_details (claim_id, drug_name, DIN_code, quantity, dosage)
    VALUES (?, ?, ?, ?, ?)
""", drug_details_rows)

conn.commit()
conn.close()

conn = sqlite3.connect("claims.db")
cursor = conn.cursor()

# Helper functions
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def generate_uuid():
    return str(uuid.uuid4())

# Fetch IDs
cursor.execute("SELECT provider_id FROM insurance_providers")
provider_ids = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT policy_id FROM policies")
policy_ids = [row[0] for row in cursor.fetchall()]
cursor.execute("SELECT claim_id FROM claims")
claim_ids = [row[0] for row in cursor.fetchall()]

# Insert provider_plans
for i in range(5):
    uid = generate_uuid()
    cursor.execute("""
        INSERT INTO provider_plans VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        generate_uuid(),
        random.choice(provider_ids),
        f"Plan_{random.randint(100,999)}",
        "Standard insurance plan",
        round(random.uniform(50, 150), 2),
        round(random.uniform(500, 2000), 2),
        round(random.uniform(300, 1000), 2),
        round(random.uniform(150, 700), 2),
    ))

# Insert premium_payments
for _ in range(10):
    policy_id = random.choice(policy_ids)
    due_date = random_date(datetime(2024, 1, 1), datetime(2024, 6, 1))
    paid_date = due_date + timedelta(days=random.randint(0, 10))
    cursor.execute("""
        INSERT INTO premium_payments VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        generate_uuid(),
        policy_id,
        due_date.date(),
        paid_date.date(),
        100.00,
        100.00,
        "Paid",
        "Credit Card",
    ))

# Insert dental_details
for claim_id in claim_ids[:3]:
    cursor.execute("""
        INSERT INTO dental_details VALUES (?, ?, ?, ?)
    """, (
        claim_id,
        "Cleaning",
        "T12",
        "PROC123"
    ))

# Insert hospital_visits
for claim_id in claim_ids[3:6]:
    admission = datetime(2024, 5, 10)
    discharge = admission + timedelta(days=3)
    cursor.execute("""
        INSERT INTO hospital_visits VALUES (?, ?, ?, ?)
    """, (
        claim_id,
        "Private",
        admission.date(),
        discharge.date()
    ))

# Insert vision_claims
for claim_id in claim_ids[6:9]:
    cursor.execute("""
        INSERT INTO vision_claims VALUES (?, ?, ?, ?)
    """, (
        claim_id,
        "Glasses",
        200.00,
        "2024-01-01"
    ))

# Insert coverage_limits
for user_id in user_ids:
    cursor.execute("""
        INSERT INTO coverage_limits VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        "dental",
        2024,
        1000.00,
        random.uniform(100, 800)
    ))

# Insert claim_audit_logs
for claim_id in claim_ids:
    cursor.execute("""
        INSERT INTO claim_audit_logs VALUES (?, ?, ?, ?, ?, ?)
    """, (
        generate_uuid(),
        claim_id,
        datetime.now(),
        "Submitted",
        "system",
        "Initial submission"
    ))

# Insert claim_documents
for claim_id in claim_ids[:5]:
    cursor.execute("""
        INSERT INTO claim_documents VALUES (?, ?, ?, ?, ?, ?)
    """, (
        generate_uuid(),
        claim_id,
        "receipt.pdf",
        datetime.now(),
        "Receipt",
        ""
    ))

# Insert pre_authorizations
for _ in range(3):
    cursor.execute("""
        INSERT INTO pre_authorizations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        generate_uuid(),
        random.choice(user_ids),
        random.choice(policy_ids),
        "MRI scan",
        500.00,
        "2024-05-01",
        "2024-05-05",
        "Approved",
        "Reviewed by Dr. Smith"
    ))

# Insert user_preferences
for user_id in user_ids:
    cursor.execute("""
        INSERT INTO user_preferences VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        random.choice([True, False]),
        random.choice([True, False]),
        "en",
        "America/Toronto"
    ))

conn.commit()
conn.close()


# Reconnect and show table counts
conn = sqlite3.connect("claims.db")
table_names = [
    "provider_plans", "premium_payments", "dental_details", "hospital_visits",
    "vision_claims", "coverage_limits", "claim_audit_logs", "claim_documents",
    "pre_authorizations", "user_preferences"
]

# Verify contents
df_users = pd.read_sql_query("SELECT * FROM users", conn)
print(df_users.head)
df_auth_users = pd.read_sql_query("SELECT * FROM auth_users", conn)
print(df_auth_users.head)
df_providers = pd.read_sql_query("SELECT * FROM insurance_providers", conn)
print(df_providers.head)
df_claims = pd.read_sql_query("SELECT * FROM claims", conn)
print(df_claims.head)
policies_df = pd.read_sql_query("SELECT * FROM policies", conn)
print(policies_df.head)
drugs_df = pd.read_sql_query("SELECT * FROM drug_details", conn)
print(drugs_df.head)
conn.close()
