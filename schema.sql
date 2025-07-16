CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name VARCHAR(100),
    dob DATE,
    health_card VARCHAR(20),
    email VARCHAR(100),
    phone VARCHAR(20),
    provider_id VARCHAR(50)
);



CREATE TABLE auth_users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password_hash TEXT,
    role VARCHAR(20) CHECK (role IN ('user', 'admin', 'agent')),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);



CREATE TABLE insurance_providers (
    provider_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    description TEXT
);



CREATE TABLE provider_plans (
    plan_id UUID PRIMARY KEY,
    provider_id VARCHAR(50),
    name VARCHAR(100),
    description TEXT,
    base_premium DECIMAL(10,2),
    drug_limit DECIMAL(10,2),
    dental_limit DECIMAL(10,2),
    vision_limit DECIMAL(10,2),
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id)
);



CREATE TABLE policies (
    policy_id UUID PRIMARY KEY,
    user_id UUID,
    provider_id VARCHAR(50),
    policy_number VARCHAR(50),
    plan_type VARCHAR(50),
    coverage_start DATE,
    coverage_end DATE,
    monthly_premium DECIMAL(10,2),
    billing_frequency VARCHAR(20),
    active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id)
);



CREATE TABLE premium_payments (
    payment_id UUID PRIMARY KEY,
    policy_id UUID,
    due_date DATE,
    paid_date DATE,
    amount_due DECIMAL(10,2),
    amount_paid DECIMAL(10,2),
    payment_status VARCHAR(20),
    payment_method VARCHAR(50),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);



CREATE TABLE claims (
    claim_id UUID PRIMARY KEY,
    user_id UUID,
    provider_id VARCHAR(50),
    policy_id UUID,
    service_date DATE,
    claim_type VARCHAR(50),
    service_code VARCHAR(50),
    description TEXT,
    amount_claimed DECIMAL(10,2),
    amount_approved DECIMAL(10,2),
    status VARCHAR(20),
    submitted_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (provider_id) REFERENCES insurance_providers(provider_id),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);



CREATE TABLE dental_details (
    claim_id UUID PRIMARY KEY,
    category VARCHAR(50),
    tooth_code VARCHAR(10),
    procedure_code VARCHAR(20),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE drug_details (
    claim_id UUID PRIMARY KEY,
    drug_name VARCHAR(100),
    DIN_code VARCHAR(20),
    quantity INTEGER,
    dosage VARCHAR(50),
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE hospital_visits (
    claim_id UUID PRIMARY KEY,
    room_type VARCHAR(50),
    admission_date DATE,
    discharge_date DATE,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE vision_claims (
    claim_id UUID PRIMARY KEY,
    product_type VARCHAR(50),
    coverage_limit DECIMAL(10,2),
    eligibility_date DATE,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE coverage_limits (
    user_id UUID,
    claim_type VARCHAR(50),
    year INT,
    max_coverage DECIMAL(10,2),
    used_coverage DECIMAL(10,2),
    PRIMARY KEY (user_id, claim_type, year),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);



CREATE TABLE claim_audit_logs (
    audit_id UUID PRIMARY KEY,
    claim_id UUID,
    event_time TIMESTAMP,
    event_type VARCHAR(50),
    performed_by VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE claim_documents (
    document_id UUID PRIMARY KEY,
    claim_id UUID,
    file_name VARCHAR(200),
    uploaded_at TIMESTAMP,
    document_type VARCHAR(50),
    secure_url TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(claim_id)
);



CREATE TABLE pre_authorizations (
    auth_id UUID PRIMARY KEY,
    user_id UUID,
    policy_id UUID,
    service_requested TEXT,
    estimated_cost DECIMAL(10,2),
    request_date DATE,
    approved_date DATE,
    status VARCHAR(20),
    agent_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
);



CREATE TABLE communications_log (
    log_id UUID PRIMARY KEY,
    user_id UUID,
    type VARCHAR(20),
    subject TEXT,
    content TEXT,
    sent_at TIMESTAMP,
    status VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);



CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY,
    communication_opt_in BOOLEAN,
    consent_to_share_data BOOLEAN,
    language_preference VARCHAR(10),
    timezone VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);