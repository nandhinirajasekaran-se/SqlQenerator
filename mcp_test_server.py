from mcp.server.fastmcp import FastMCP
from typing import List, Dict
from langchain_community.utilities import SQLDatabase
import logging
import sqlite3

mcp = FastMCP("Claims")
db = SQLDatabase.from_uri("sqlite:///claims.db")  # Replace with your actual DB URI
logger = logging.getLogger(__name__)

@mcp.tool()
def get_user_by_id(user_id: str) -> str:
    """Retrieve a single user's details by their user_id"""
    query = """
    SELECT user_id, name, dob, health_card, email, phone, provider_id 
    FROM users 
    WHERE user_id = :user_id
    """
    try:
        results = db.run(query, parameters={"user_id": user_id})
        print(f"[get_user_by_id] Raw result: {results}")  # ✅ Debug line
        return results
    except Exception as e:
        print(f"[get_user_by_id] ❗ Database error: {str(e)}")
        return []

@mcp.tool()
def get_users_by_provider(provider_id: str) -> str:
    """Find all users associated with a specific insurance provider"""
    query = """
    SELECT user_id, name, email, phone 
    FROM users 
    WHERE provider_id = :provider_id
    """
    try:
        results = db.run(query, parameters={"provider_id": provider_id})
        return results
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Policy tools
@mcp.tool()
def get_policies_by_user(user_id: str) -> str:
    """Retrieve all insurance policies for a specific user"""
    query = """
    SELECT p.policy_id, p.policy_number, p.plan_type, 
           p.coverage_start, p.coverage_end, p.monthly_premium,
           ip.name as provider_name
    FROM policies p
    JOIN insurance_providers ip ON p.provider_id = ip.provider_id
    WHERE p.user_id = :user_id AND p.active = TRUE
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

@mcp.tool()
def get_active_policies() -> str:
    """List all currently active insurance policies"""
    query = """
    SELECT p.policy_id, u.name as user_name, ip.name as provider_name,
           p.policy_number, p.coverage_end, p.monthly_premium
    FROM policies p
    JOIN users u ON p.user_id = u.user_id
    JOIN insurance_providers ip ON p.provider_id = ip.provider_id
    WHERE p.active = TRUE
    """
    try:
        return db.run(query)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Claim tools
@mcp.tool()
def get_claims_by_user_id(user_id: str) -> list[Dict]:
    import sqlite3
    """Retrieve all claims submitted by a specific user"""
    try:
        query= """
                SELECT c.claim_id, c.service_date, c.claim_type, 
                       c.amount_claimed, c.amount_approved, c.status,
                       p.policy_number
                FROM claims c
                JOIN policies p ON c.policy_id = p.policy_id
                WHERE c.user_id = ?
                ORDER BY c.service_date DESC
            """
            
        conn = sqlite3.connect("claims.db")
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
            
            # Convert to list of dictionaries
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
    except Exception as e:
        print("Inside error in get_claims_by_user")
        print(f"Database error: {str(e)}")
        return []

@mcp.tool()
def get_claim_details(claim_id: str) -> str:
    """Get detailed information about a specific claim"""
    query = """
    SELECT c.claim_id,
    c.user_id,
    c.provider_id,
    c.policy_id,
    c.service_date,
    c.claim_type,
    c.service_code,
    c.description,
    c.amount_claimed,
    c.amount_approved,
    c.status,
    c.submitted_at,
    u.name as user_name, 
    p.policy_number,
    ip.name as provider_name
    FROM claims c
    JOIN users u ON c.user_id = u.user_id
    JOIN policies p ON c.policy_id = p.policy_id
    JOIN insurance_providers ip ON c.provider_id = ip.provider_id
    WHERE c.claim_id = :claim_id
    """
    try:
        return db.run(query, parameters={"claim_id": claim_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Provider tools
@mcp.tool()
def get_provider_details(provider_id: str) -> str:
    """Get information about an insurance provider"""
    query = """
    SELECT provider_id, name, description
    FROM insurance_providers
    WHERE provider_id = :provider_id
    """
    try:
        return db.run(query, parameters={"provider_id": provider_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

@mcp.tool()
def get_provider_plans(provider_id: str) -> str:
    """List all available plans from a specific insurance provider"""
    query = """
    SELECT plan_id, name, description, base_premium,
           drug_limit, dental_limit, vision_limit
    FROM provider_plans
    WHERE provider_id = :provider_id
    """
    try:
        return db.run(query, parameters={"provider_id": provider_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Payment tools
@mcp.tool()
def get_payments_by_policy(policy_id: str) -> str:
    """Retrieve payment history for a specific policy"""
    query = """
    SELECT payment_id, due_date, paid_date, 
           amount_due, amount_paid, payment_status
    FROM premium_payments
    WHERE policy_id = :policy_id
    ORDER BY due_date DESC
    """
    try:
        return db.run(query, parameters={"policy_id": policy_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Coverage tools
@mcp.tool()
def get_coverage_limits(user_id: str) -> str:
    """Get coverage limits and usage for a specific user"""
    query = """
    SELECT claim_type, year, max_coverage, used_coverage
    FROM coverage_limits
    WHERE user_id = :user_id
    ORDER BY year DESC, claim_type
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Pre-authorization tools
@mcp.tool()
def get_pre_authorizations(user_id: str) -> str:
    """Retrieve pre-authorization requests for a user"""
    query = """
    SELECT auth_id, service_requested, estimated_cost,
           request_date, approved_date, status
    FROM pre_authorizations
    WHERE user_id = :user_id
    ORDER BY request_date DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []
    

# Dental details Tools
@mcp.tool()
def get_dental_details_by_user(user_id: str) -> str:
    """Retrieve all dental details for a specific user with procedure details"""
    query = """
    SELECT c.claim_id, c.service_date, c.status, 
           d.category, d.tooth_code, d.procedure_code
    FROM claims c
    JOIN dental_details d ON c.claim_id = d.claim_id
    WHERE c.user_id = :user_id
    ORDER BY c.service_date DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Drug details Tools  
@mcp.tool()
def get_drug_details_by_user(user_id: str) -> str:
    """Get all prescription drug details for a user with medication details"""
    query = """
    SELECT c.claim_id, c.service_date, c.status,
           d.drug_name, d.DIN_code, d.quantity, d.dosage
    FROM claims c
    JOIN drug_details d ON c.claim_id = d.claim_id
    WHERE c.user_id = :user_id
    ORDER BY c.service_date DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Hospital Visits Tools
@mcp.tool()
def get_hospital_visits_by_user(user_id: str) -> str:
    """Retrieve all hospital visits for a user with stay details"""
    query = """
    SELECT c.claim_id, c.service_date, c.status,
           h.room_type, h.admission_date, h.discharge_date
    FROM claims c
    JOIN hospital_visits h ON c.claim_id = h.claim_id
    WHERE c.user_id = :user_id
    ORDER BY h.admission_date DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Vision Claims Tools
@mcp.tool()
def get_vision_claims_by_user(user_id: str) -> str:
    """Get all vision care claims for a user with product details"""
    query = """
    SELECT c.claim_id, c.service_date, c.status,
           v.product_type, v.coverage_limit, v.eligibility_date
    FROM claims c
    JOIN vision_claims v ON c.claim_id = v.claim_id
    WHERE c.user_id = :user_id
    ORDER BY c.service_date DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Coverage Limits Tools
@mcp.tool()
def get_user_coverage_limits(user_id: str)  -> str:
    """Retrieve all coverage limits and usage for a specific user"""
    query = """
    SELECT claim_type, year, max_coverage, used_coverage,
           (max_coverage - used_coverage) as remaining_coverage
    FROM coverage_limits
    WHERE user_id = :user_id
    ORDER BY year DESC, claim_type
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Claim Audit Tools
@mcp.tool()
def get_claim_audit_logs(user_id: str) -> str:
    """Get audit history for all claims belonging to a user"""
    query = """
    SELECT a.audit_id, a.event_time, a.event_type,
           a.performed_by, c.claim_id, c.claim_type
    FROM claim_audit_logs a
    JOIN claims c ON a.claim_id = c.claim_id
    WHERE c.user_id = :user_id
    ORDER BY a.event_time DESC
    LIMIT 50
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Claim Documents Tools
@mcp.tool()
def get_user_claim_documents(user_id: str) -> str:
    """Retrieve all documents submitted with a user's claims"""
    query = """
    SELECT d.document_id, d.file_name, d.uploaded_at,
           d.document_type, c.claim_id, c.claim_type
    FROM claim_documents d
    JOIN claims c ON d.claim_id = c.claim_id
    WHERE c.user_id = :user_id
    ORDER BY d.uploaded_at DESC
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# User Preferences Tools
@mcp.tool()
def get_user_preferences(user_id: str)  -> str:
    """Get communication preferences and settings for a user"""
    query = """
    SELECT communication_opt_in, consent_to_share_data,
           language_preference, timezone
    FROM user_preferences
    WHERE user_id = :user_id
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

# Communications Log Tools
@mcp.tool()
def get_user_communications(user_id: str)  -> str:
    """Retrieve all communications sent to/from a user"""
    query = """
    SELECT log_id, type, subject, sent_at, status
    FROM communications_log
    WHERE user_id = :user_id
    ORDER BY sent_at DESC
    LIMIT 50
    """
    try:
        return db.run(query, parameters={"user_id": user_id})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []

@mcp.tool()
def ping() -> str:
    """Health check tool"""
    return "pong"

tools = [
    get_user_by_id,
    get_users_by_provider,
    get_policies_by_user,
    get_active_policies,
    get_claims_by_user_id,
    get_provider_details,
    get_provider_plans,
    get_payments_by_policy,
    get_coverage_limits,
    get_pre_authorizations,
    get_dental_details_by_user,
    get_drug_details_by_user,
    get_hospital_visits_by_user,
    get_vision_claims_by_user,
    get_user_coverage_limits,
    get_claim_audit_logs,
    get_user_claim_documents,
    get_user_preferences,
    get_user_communications
]



if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting MCP server...")
    #import sqlite3
    #print("[DEBUG] Manual test of get_user_by_id:")
    #mcp = FastMCP("Claims")
    #db = SQLDatabase.from_uri("sqlite:///claims.db")  # Replace with your actual DB URI
    #logger.info(get_user_by_id("User1")) 
    mcp.run(transport="stdio")
