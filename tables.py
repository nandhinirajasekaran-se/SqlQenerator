# Re-run after kernel reset: Re-creating the schema

import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("claims.db")
cursor = conn.cursor()

# Schema creation commands
schema_sql = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    dob DATE,
    health_card TEXT,
    email TEXT,
    phone TEXT,
    provider_id TEXT
);

CREATE TABLE IF NOT EXISTS auth_users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT CHECK (role IN ('user', 'admin', 'agent')),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS insurance_providers (
    provider_id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS provider_plans (
    plan_id TEXT PRIMARY KEY,
    provider_id TEXT,
    name TEXT,
    description TEXT,
    base_premium REAL,
    drug_limit REAL,
    dental_limit REAL,
    vision_limit REAL,
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id)
);

CREATE TABLE IF NOT EXISTS policies (
    policy_id TEXT PRIMARY KEY,
    user_id TEXT,
    provider_id TEXT,
    policy_number TEXT,
    plan_type TEXT,
    coverage_start DATE,
    coverage_end DATE,
    monthly_premium REAL,
    billing_frequency TEXT,
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id)
);

CREATE TABLE IF NOT EXISTS premium_payments (
    payment_id TEXT PRIMARY KEY,
    policy_id TEXT,
    due_date DATE,
    paid_date DATE,
    amount_due REAL,
    amount_paid REAL,
    payment_status TEXT,
    payment_method TEXT,
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    user_id TEXT,
    provider_id TEXT,
    policy_id TEXT,
    service_date DATE,
    claim_type TEXT,
    service_code TEXT,
    description TEXT,
    amount_claimed REAL,
    amount_approved REAL,
    status TEXT,
    submitted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);

CREATE TABLE IF NOT EXISTS dental_details (
    claim_id TEXT PRIMARY KEY,
    category TEXT,
    tooth_code TEXT,
    procedure_code TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS drug_details (
    claim_id TEXT PRIMARY KEY,
    drug_name TEXT,
    DIN_code TEXT,
    quantity INTEGER,
    dosage TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS hospital_visits (
    claim_id TEXT PRIMARY KEY,
    room_type TEXT,
    admission_date DATE,
    discharge_date DATE,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS vision_claims (
    claim_id TEXT PRIMARY KEY,
    product_type TEXT,
    coverage_limit REAL,
    eligibility_date DATE,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS coverage_limits (
    user_id TEXT,
    claim_type TEXT,
    year INTEGER,
    max_coverage REAL,
    used_coverage REAL,
    PRIMARY KEY (user_id, claim_type, year),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS claim_audit_logs (
    audit_id TEXT PRIMARY KEY,
    claim_id TEXT,
    event_time TIMESTAMP,
    event_type TEXT,
    performed_by TEXT,
    notes TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS claim_documents (
    document_id TEXT PRIMARY KEY,
    claim_id TEXT,
    file_name TEXT,
    uploaded_at TIMESTAMP,
    document_type TEXT,
    secure_url TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);

CREATE TABLE IF NOT EXISTS pre_authorizations (
    auth_id TEXT PRIMARY KEY,
    user_id TEXT,
    policy_id TEXT,
    service_requested TEXT,
    estimated_cost REAL,
    request_date DATE,
    approved_date DATE,
    status TEXT,
    agent_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);

CREATE TABLE IF NOT EXISTS communications_log (
    log_id TEXT PRIMARY KEY,
    user_id TEXT,
    type TEXT,
    subject TEXT,
    content TEXT,
    sent_at TIMESTAMP,
    status TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id TEXT PRIMARY KEY,
    communication_opt_in BOOLEAN,
    consent_to_share_data BOOLEAN,
    language_preference TEXT,
    timezone TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

# Execute the schema creation
cursor.executescript(schema_sql)
conn.commit()
conn.close()
