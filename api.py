"""
Procurement Twin - API Layer

Connects the five existing backend engines to a REST API so a frontend
UI can call them over HTTP:

    scoring.py      -> Step 1: Vendor Scoring
    risk.py         -> Step 2: Risk Intelligence
    savings.py      -> Step 3: Savings Intelligence
    what_if.py      -> Step 4: What-If Intelligence
    explanation.py  -> Step 5: AI Decision Explanation & Summary

No scoring/risk/savings/what-if math is reimplemented here - every
calculation is delegated to the existing functions in those files.
This file only exposes them as HTTP endpoints, validates input,
and shapes the JSON responses.

Run with:
    pip install flask flask-cors
    python api.py

Server starts at: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------------------------------------------------------
# IMPORT EXISTING ENGINE FUNCTIONS (no logic duplicated)
# ---------------------------------------------------------

# Step 1: Vendor Scoring (scoring.py)
from scoring import run_procurement_scoring

# Step 2: Risk Intelligence (risk.py)
from risk import run_risk_intelligence

# Step 3: Savings Intelligence (savings.py)
from savings import (
    run_savings_intelligence,
    rank_savings,
    generate_value_insight,
    format_inr,
)

# Step 4: What-If Intelligence (what_if.py)
from what_if import run_what_if_analysis

# Step 5: AI Decision Explanation & Summary (explanation.py)
from explanation import generate_decision_summary


# ---------------------------------------------------------
# APP SETUP
# ---------------------------------------------------------

app = Flask(__name__)
CORS(app)  # allow the frontend (different origin/port) to call this API


# ---------------------------------------------------------
# DEFAULT DATA
# Used to pre-fill the frontend and as fallbacks when a request
# doesn't override a particular input.
# ---------------------------------------------------------

DEFAULT_VENDORS = [
    {
        "name": "ABC",
        "price": 520000,
        "delivery_days": 5,
        "quality": 9.2,
        "reliability": 92,
        "warranty_years": 2
    },
    {
        "name": "Vendor B",
        "price": 490000,
        "delivery_days": 12,
        "quality": 7.8,
        "reliability": 76,
        "warranty_years": 1
    },
    {
        "name": "Vendor C",
        "price": 510000,
        "delivery_days": 7,
        "quality": 9.5,
        "reliability": 95,
        "warranty_years": 3
    }
]

DEFAULT_WEIGHTS = {
    "price": 35,
    "delivery": 25,
    "quality": 20,
    "reliability": 15,
    "warranty": 5
}

DELIVERY_CRITICAL_WEIGHTS = {
    "price": 15,
    "delivery": 45,
    "quality": 20,
    "reliability": 15,
    "warranty": 5
}

QUALITY_CRITICAL_WEIGHTS = {
    "price": 20,
    "delivery": 15,
    "quality": 40,
    "reliability": 15,
    "warranty": 10
}

DEFAULT_REQUIREMENTS = {
    "budget": 520000,
    "required_delivery_days": 7,
    "minimum_quality": 8.5,
    "minimum_reliability": 85,
    "minimum_warranty_years": 2
}

STRICT_REQUIREMENTS = {
    "budget": 500000,
    "required_delivery_days": 5,
    "minimum_quality": 9.0,
    "minimum_reliability": 90,
    "minimum_warranty_years": 3
}

DEFAULT_RISK_WEIGHTS = {
    "delivery": 30,
    "budget": 20,
    "quality": 20,
    "reliability": 20,
    "warranty": 10
}

DEFAULT_BUDGET = 520000


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def error_response(message, status_code=400):
    return jsonify({"success": False, "error": str(message)}), status_code


def get_body():
    """Returns the parsed JSON body, or an empty dict if none was sent."""
    return request.get_json(silent=True) or {}


# ===========================================================
# HEALTH CHECK
# ===========================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"success": True, "status": "Procurement Twin API is running"})


# ===========================================================
# DEFAULTS
# Lets the frontend pre-populate its forms with sensible sample data.
# ===========================================================

@app.route("/api/defaults", methods=["GET"])
def get_defaults():
    return jsonify({
        "success": True,
        "data": {
            "vendors": DEFAULT_VENDORS,
            "weights": DEFAULT_WEIGHTS,
            "delivery_critical_weights": DELIVERY_CRITICAL_WEIGHTS,
            "quality_critical_weights": QUALITY_CRITICAL_WEIGHTS,
            "requirements": DEFAULT_REQUIREMENTS,
            "strict_requirements": STRICT_REQUIREMENTS,
            "risk_weights": DEFAULT_RISK_WEIGHTS,
            "budget": DEFAULT_BUDGET,
        }
    })


# ===========================================================
# STEP 1: VENDOR SCORING
# ===========================================================

@app.route("/api/score", methods=["POST"])
def score_vendors():
    """
    Body (all optional - falls back to defaults):
    {
        "vendors": [...],
        "weights": {"price":35, "delivery":25, "quality":20, "reliability":15, "warranty":5}
    }
    """
    body = get_body()
    vendors = body.get("vendors", DEFAULT_VENDORS)
    weights = body.get("weights", DEFAULT_WEIGHTS)

    try:
        result = run_procurement_scoring(vendors, weights)
    except (ValueError, KeyError, ZeroDivisionError) as e:
        return error_response(e)

    return jsonify({"success": True, "data": result})


# ===========================================================
# STEP 2: RISK INTELLIGENCE
# ===========================================================

@app.route("/api/risk", methods=["POST"])
def assess_risk():
    """
    Body (all optional - falls back to defaults):
    {
        "vendors": [...],
        "requirements": {...},
        "risk_weights": {...}
    }
    """
    body = get_body()
    vendors = body.get("vendors", DEFAULT_VENDORS)
    requirements = body.get("requirements", DEFAULT_REQUIREMENTS)
    risk_weights = body.get("risk_weights", DEFAULT_RISK_WEIGHTS)

    try:
        result = run_risk_intelligence(vendors, requirements, risk_weights)
    except (ValueError, KeyError, ZeroDivisionError) as e:
        return error_response(e)

    return jsonify({"success": True, "data": result})


# ===========================================================
# STEP 3: SAVINGS INTELLIGENCE
# ===========================================================

@app.route("/api/savings", methods=["POST"])
def calculate_savings():
    """
    Body (all optional - falls back to defaults):
    {
        "vendors": [...],
        "budget": 520000,
        "recommended_name": "ABC",       # optional - for the value insight
        "recommended_score": 95.21,      # optional - for the value insight
        "recommended_risk_level": "LOW"  # optional - for the value insight
    }
    """
    body = get_body()
    vendors = body.get("vendors", DEFAULT_VENDORS)
    budget = body.get("budget", DEFAULT_BUDGET)

    try:
        savings_list = run_savings_intelligence(vendors, budget)
        ranked_savings = rank_savings(list(savings_list))
    except (ValueError, KeyError, ZeroDivisionError) as e:
        return error_response(e)

    response_data = {
        "savings": savings_list,
        "ranking": ranked_savings,
    }

    # If the frontend already knows who Step 1 recommended, also return
    # the value insight for that vendor.
    recommended_name = body.get("recommended_name")
    recommended_score = body.get("recommended_score")
    recommended_risk_level = body.get("recommended_risk_level")

    if recommended_name and recommended_score is not None and recommended_risk_level:
        try:
            insight = generate_value_insight(
                recommended_name, recommended_score, recommended_risk_level, savings_list
            )
            response_data["value_insight"] = insight
        except StopIteration:
            return error_response(f"Vendor '{recommended_name}' not found in savings results.")

    return jsonify({"success": True, "data": response_data})


# ===========================================================
# STEP 4: WHAT-IF INTELLIGENCE
# ===========================================================

@app.route("/api/whatif", methods=["POST"])
def what_if_analysis():
    """
    Body (all optional - falls back to defaults, which reproduces the
    "priority change" scenario: default weights -> delivery-critical weights):
    {
        "vendors": [...],
        "original_weights": {...},
        "new_weights": {...},
        "original_requirements": {...},
        "new_requirements": {...},
        "risk_weights": {...}
    }
    """
    body = get_body()
    vendors = body.get("vendors", DEFAULT_VENDORS)
    original_weights = body.get("original_weights", DEFAULT_WEIGHTS)
    new_weights = body.get("new_weights", DELIVERY_CRITICAL_WEIGHTS)
    original_requirements = body.get("original_requirements", DEFAULT_REQUIREMENTS)
    new_requirements = body.get("new_requirements", DEFAULT_REQUIREMENTS)
    risk_weights = body.get("risk_weights", DEFAULT_RISK_WEIGHTS)

    try:
        result = run_what_if_analysis(
            vendors, original_weights, new_weights,
            original_requirements, new_requirements, risk_weights
        )
    except (ValueError, KeyError, ZeroDivisionError) as e:
        return error_response(e)

    return jsonify({"success": True, "data": result})


# ===========================================================
# STEP 5: AI DECISION EXPLANATION & SUMMARY
# (Also serves as the full end-to-end pipeline for the frontend:
#  Scoring -> Risk -> Savings -> What-If -> Decision Explanation)
# ===========================================================

@app.route("/api/decision", methods=["POST"])
def full_decision_pipeline():
    """
    Runs the complete pipeline and returns every stage's output plus the
    final rule-based decision summary.

    Body (all optional - falls back to defaults):
    {
        "vendors": [...],
        "weights": {...},                  # scoring weights
        "requirements": {...},              # risk requirements
        "risk_weights": {...},
        "budget": 520000,

        # what-if comparison inputs (optional)
        "whatif_original_weights": {...},
        "whatif_new_weights": {...},
        "whatif_original_requirements": {...},
        "whatif_new_requirements": {...}
    }
    """
    body = get_body()

    vendors = body.get("vendors", DEFAULT_VENDORS)
    weights = body.get("weights", DEFAULT_WEIGHTS)
    requirements = body.get("requirements", DEFAULT_REQUIREMENTS)
    risk_weights = body.get("risk_weights", DEFAULT_RISK_WEIGHTS)
    budget = body.get("budget", DEFAULT_BUDGET)

    whatif_original_weights = body.get("whatif_original_weights", weights)
    whatif_new_weights = body.get("whatif_new_weights", DELIVERY_CRITICAL_WEIGHTS)
    whatif_original_requirements = body.get("whatif_original_requirements", requirements)
    whatif_new_requirements = body.get("whatif_new_requirements", requirements)

    try:
        # Step 1
        scoring_results = run_procurement_scoring(vendors, weights)

        # Step 2
        risk_results = run_risk_intelligence(vendors, requirements, risk_weights)

        # Step 3
        savings_results = run_savings_intelligence(vendors, budget)

        # Step 4
        what_if_results = run_what_if_analysis(
            vendors,
            whatif_original_weights, whatif_new_weights,
            whatif_original_requirements, whatif_new_requirements,
            risk_weights
        )

        # Step 5
        decision_summary = generate_decision_summary(
            scoring_results, risk_results, savings_results, what_if_results
        )

    except (ValueError, KeyError, ZeroDivisionError, StopIteration) as e:
        return error_response(e)

    return jsonify({
        "success": True,
        "data": {
            "scoring": scoring_results,
            "risk": risk_results,
            "savings": savings_results,
            "what_if": what_if_results,
            "decision": decision_summary,
        }
    })


# ===========================================================
# ERROR HANDLERS
# ===========================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed on this endpoint."}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error."}), 500


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)