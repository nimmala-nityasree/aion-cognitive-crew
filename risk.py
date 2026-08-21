"""
Procurement Twin - Vendor Scoring Engine
Pure Python calculation engine for hackathon prototype.
"""


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

def validate_weights(weights):
    if any(w < 0 for w in weights.values()):
        raise ValueError("Weights cannot be negative.")
    total = sum(weights.values())
    if abs(total - 100) > 0.001:
        raise ValueError(f"Weights must total exactly 100%. Got {total}%.")
    return True


def validate_vendors(vendors):
    if not vendors:
        raise ValueError("Vendor list cannot be empty.")

    for v in vendors:
        if v["price"] <= 0:
            raise ValueError(f"{v['name']}: price must be greater than 0.")
        if v["delivery_days"] <= 0:
            raise ValueError(f"{v['name']}: delivery_days must be greater than 0.")
        if not (0 <= v["quality"] <= 10):
            raise ValueError(f"{v['name']}: quality must be between 0 and 10.")
        if not (0 <= v["reliability"] <= 100):
            raise ValueError(f"{v['name']}: reliability must be between 0 and 100.")
        if v["warranty_years"] < 0:
            raise ValueError(f"{v['name']}: warranty_years cannot be negative.")
    return True


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def normalize_vendors(vendors):
    """
    Returns a new list of vendors with a 'normalized' dict added to each,
    containing 0-100 scores for every criterion.
    """
    min_price = min(v["price"] for v in vendors)
    min_delivery = min(v["delivery_days"] for v in vendors)
    max_quality = max(v["quality"] for v in vendors)
    max_reliability = max(v["reliability"] for v in vendors)
    max_warranty = max(v["warranty_years"] for v in vendors)

    normalized_vendors = []

    for v in vendors:
        normalized = {
            "price": (min_price / v["price"]) * 100,
            "delivery": (min_delivery / v["delivery_days"]) * 100,
            "quality": (v["quality"] / max_quality) * 100 if max_quality > 0 else 0,
            "reliability": (v["reliability"] / max_reliability) * 100 if max_reliability > 0 else 0,
            "warranty": (v["warranty_years"] / max_warranty) * 100 if max_warranty > 0 else 0,
        }

        new_vendor = dict(v)
        new_vendor["normalized"] = normalized
        normalized_vendors.append(new_vendor)

    return normalized_vendors


# ---------------------------------------------------------
# SCORING
# ---------------------------------------------------------

def calculate_scores(normalized_vendors, weights):
    """
    Adds 'contributions' (weighted score per criterion) and
    'overall_score' to each vendor.
    """
    scored_vendors = []

    for v in normalized_vendors:
        n = v["normalized"]

        contributions = {
            "price": n["price"] * (weights["price"] / 100),
            "delivery": n["delivery"] * (weights["delivery"] / 100),
            "quality": n["quality"] * (weights["quality"] / 100),
            "reliability": n["reliability"] * (weights["reliability"] / 100),
            "warranty": n["warranty"] * (weights["warranty"] / 100),
        }

        overall_score = sum(contributions.values())

        new_vendor = dict(v)
        new_vendor["contributions"] = contributions
        new_vendor["overall_score"] = overall_score
        scored_vendors.append(new_vendor)

    return scored_vendors


# ---------------------------------------------------------
# RANKING
# ---------------------------------------------------------

def rank_vendors(scored_vendors):
    """
    Returns vendors sorted by overall_score descending, with 'rank' added.
    """
    ranked = sorted(scored_vendors, key=lambda v: v["overall_score"], reverse=True)
    for i, v in enumerate(ranked, start=1):
        v["rank"] = i
    return ranked


# ---------------------------------------------------------
# RECOMMENDATION
# ---------------------------------------------------------

def generate_recommendation(ranked_vendors):
    """
    The top-ranked vendor is the recommendation.
    """
    return ranked_vendors[0]


def generate_explanation(winner, ranked_vendors, weights):
    """
    Builds a plain-English explanation from the actual calculated
    normalized scores and contributions of the winning vendor.
    """
    n = winner["normalized"]
    c = winner["contributions"]

    # Identify winner's strongest criteria (top 2 by normalized score)
    criterion_labels = {
        "price": "price",
        "delivery": "delivery speed",
        "quality": "quality",
        "reliability": "reliability",
        "warranty": "warranty coverage",
    }

    strengths = sorted(n.items(), key=lambda x: x[1], reverse=True)[:2]
    strength_text = " and ".join(
        f"{criterion_labels[k]} ({v:.2f}/100)" for k, v in strengths
    )

    # Identify which criterion contributed most to the final score
    top_contributor = max(c.items(), key=lambda x: x[1])
    top_contributor_text = (
        f"Its biggest driver was {criterion_labels[top_contributor[0]]}, "
        f"contributing {top_contributor[1]:.2f} points to the overall score "
        f"(weighted at {weights[top_contributor[0]]}%)."
    )

    margin_text = ""
    if len(ranked_vendors) > 1:
        runner_up = ranked_vendors[1]
        margin = winner["overall_score"] - runner_up["overall_score"]
        margin_text = (
            f" It finished {margin:.2f} points ahead of the next best option, "
            f"{runner_up['name']} ({runner_up['overall_score']:.2f})."
        )

    explanation = (
        f"{winner['name']} achieved the highest overall score "
        f"({winner['overall_score']:.2f}/100) under the current weighting. "
        f"Its strongest areas were {strength_text}. "
        f"{top_contributor_text}{margin_text}"
    )

    return explanation


# ---------------------------------------------------------
# MAIN ENGINE
# ---------------------------------------------------------

def run_procurement_scoring(vendors, weights):
    """
    Full pipeline: validate -> normalize -> score -> rank -> recommend -> explain
    Returns a structured results dictionary.
    """
    validate_weights(weights)
    validate_vendors(vendors)

    normalized = normalize_vendors(vendors)
    scored = calculate_scores(normalized, weights)
    ranked = rank_vendors(scored)
    winner = generate_recommendation(ranked)
    explanation = generate_explanation(winner, ranked, weights)

    return {
        "weights": weights,
        "vendors": ranked,          # full detail: normalized, contributions, overall_score, rank
        "recommended_vendor": winner["name"],
        "recommended_score": winner["overall_score"],
        "explanation": explanation,
    }


# ---------------------------------------------------------
# CONSOLE OUTPUT / DEMONSTRATION
# ---------------------------------------------------------

def print_header():
    print("=" * 50)
    print("              PROCUREMENT TWIN")
    print("          VENDOR SCORING ENGINE")
    print("=" * 50)


def print_weights(weights):
    print("\nWEIGHTS")
    print(f"Price: {weights['price']}%")
    print(f"Delivery: {weights['delivery']}%")
    print(f"Quality: {weights['quality']}%")
    print(f"Reliability: {weights['reliability']}%")
    print(f"Warranty: {weights['warranty']}%")


def print_vendor_analysis(ranked_vendors):
    print("\n" + "-" * 50)
    print("VENDOR ANALYSIS")
    print("-" * 50)

    for v in ranked_vendors:
        n = v["normalized"]
        print(f"\n{v['name']}")
        print(f"Price Normalized: {n['price']:.2f}")
        print(f"Delivery Normalized: {n['delivery']:.2f}")
        print(f"Quality Normalized: {n['quality']:.2f}")
        print(f"Reliability Normalized: {n['reliability']:.2f}")
        print(f"Warranty Normalized: {n['warranty']:.2f}")
        print(f"\nOverall Score: {v['overall_score']:.2f}")


def print_ranking(ranked_vendors):
    print("\n" + "=" * 50)
    print("FINAL RANKING")
    print("=" * 50 + "\n")
    for v in ranked_vendors:
        print(f"#{v['rank']} {v['name']} — {v['overall_score']:.2f}")


def print_recommendation(result):
    print("\n" + "=" * 50)
    print("RECOMMENDATION")
    print("=" * 50)
    print(f"\n{result['recommended_vendor']}")
    print(f"Score: {result['recommended_score']:.2f}/100")
    print("\nReason:")
    print(result["explanation"])


def run_scenario(title, vendors, weights):
    print("\n\n" + "#" * 50)
    print(f"# SCENARIO: {title}")
    print("#" * 50)

    result = run_procurement_scoring(vendors, weights)

    print_header()
    print_weights(result["weights"])
    print_vendor_analysis(result["vendors"])
    print_ranking(result["vendors"])
    print_recommendation(result)

    return result


# ---------------------------------------------------------
# STEP 2: RISK INTELLIGENCE
# ---------------------------------------------------------

def validate_requirements(requirements):
    if requirements["budget"] <= 0:
        raise ValueError("Requirements: budget must be greater than 0.")
    if requirements["required_delivery_days"] <= 0:
        raise ValueError("Requirements: required_delivery_days must be greater than 0.")
    if not (0 <= requirements["minimum_quality"] <= 10):
        raise ValueError("Requirements: minimum_quality must be between 0 and 10.")
    if not (0 <= requirements["minimum_reliability"] <= 100):
        raise ValueError("Requirements: minimum_reliability must be between 0 and 100.")
    if requirements["minimum_warranty_years"] < 0:
        raise ValueError("Requirements: minimum_warranty_years cannot be negative.")
    return True


def validate_risk_weights(risk_weights):
    if any(w < 0 for w in risk_weights.values()):
        raise ValueError("Risk weights cannot be negative.")
    total = sum(risk_weights.values())
    if abs(total - 100) > 0.001:
        raise ValueError(f"Risk weights must total exactly 100%. Got {total}%.")
    return True


def calculate_vendor_risk(vendor, requirements):
    """
    Calculates the five individual risk components for a single vendor,
    each capped between 0 and 100.
    """
    delivery_risk = max(0, (vendor["delivery_days"] - requirements["required_delivery_days"])
                         / requirements["required_delivery_days"] * 100)

    budget_risk = max(0, (vendor["price"] - requirements["budget"])
                       / requirements["budget"] * 100)

    quality_risk = max(0, (requirements["minimum_quality"] - vendor["quality"])
                        / requirements["minimum_quality"] * 100)

    reliability_risk = max(0, (requirements["minimum_reliability"] - vendor["reliability"])
                            / requirements["minimum_reliability"] * 100)

    warranty_risk = max(0, (requirements["minimum_warranty_years"] - vendor["warranty_years"])
                         / requirements["minimum_warranty_years"] * 100) \
        if requirements["minimum_warranty_years"] > 0 else 0

    risks = {
        "delivery": min(delivery_risk, 100),
        "budget": min(budget_risk, 100),
        "quality": min(quality_risk, 100),
        "reliability": min(reliability_risk, 100),
        "warranty": min(warranty_risk, 100),
    }

    return risks


def calculate_overall_risk(risks, risk_weights):
    """
    Combines individual risk components into a single overall risk score
    using the provided risk weights.
    """
    overall_risk = (
        risks["delivery"] * (risk_weights["delivery"] / 100) +
        risks["budget"] * (risk_weights["budget"] / 100) +
        risks["quality"] * (risk_weights["quality"] / 100) +
        risks["reliability"] * (risk_weights["reliability"] / 100) +
        risks["warranty"] * (risk_weights["warranty"] / 100)
    )
    return overall_risk


def classify_risk_level(overall_risk):
    """
    Maps a 0-100 overall risk score to a risk level label.
    """
    if overall_risk < 25:
        return "LOW"
    elif overall_risk < 50:
        return "MEDIUM"
    elif overall_risk < 75:
        return "HIGH"
    else:
        return "CRITICAL"


def generate_risk_explanation(vendor, risks, overall_risk, risk_level, requirements):
    """
    Builds a plain-English explanation from the actual calculated risk
    numbers - identifies which factors are driving the risk.
    """
    # Rank risk factors by magnitude, ignore factors with ~0 risk
    ranked_factors = sorted(risks.items(), key=lambda x: x[1], reverse=True)
    significant_factors = [(k, v) for k, v in ranked_factors if v > 0.01]

    if not significant_factors:
        return (f"{risk_level} RISK — {vendor['name']} meets or exceeds every "
                f"requirement with no measurable risk factors.")

    parts = []

    for factor, value in significant_factors:
        if factor == "delivery":
            gap_days = vendor["delivery_days"] - requirements["required_delivery_days"]
            parts.append(f"Delivery exceeds the required deadline by {gap_days} day(s)")
        elif factor == "budget":
            gap_amount = vendor["price"] - requirements["budget"]
            parts.append(f"Price exceeds the budget by {gap_amount:,.0f}")
        elif factor == "quality":
            gap_quality = requirements["minimum_quality"] - vendor["quality"]
            parts.append(f"Quality falls short of the minimum by {gap_quality:.2f} points")
        elif factor == "reliability":
            gap_reliability = requirements["minimum_reliability"] - vendor["reliability"]
            parts.append(f"Reliability falls short of the minimum by {gap_reliability:.2f} points")
        elif factor == "warranty":
            gap_warranty = requirements["minimum_warranty_years"] - vendor["warranty_years"]
            parts.append(f"Warranty falls short of the minimum by {gap_warranty:.2f} year(s)")

    # First factor is the primary driver; remaining factors get a secondary mention
    if len(parts) == 1:
        detail = parts[0] + "."
    else:
        primary = parts[0]
        secondary_labels = {
            "delivery": "Delivery", "budget": "Budget", "quality": "Quality",
            "reliability": "Reliability", "warranty": "Warranty"
        }
        other_factor_names = [secondary_labels[f] for f, _ in significant_factors[1:]]
        if len(other_factor_names) == 1:
            joined = other_factor_names[0]
            verb = "is"
        else:
            joined = ", ".join(other_factor_names[:-1]) + " and " + other_factor_names[-1]
            verb = "are"
        detail = f"{primary}. {joined} {verb} also outside the required range."

    return f"{risk_level} RISK — {detail}"


def assess_vendor_risk(vendor, requirements, risk_weights):
    """
    Full risk pipeline for a single vendor: calculate components,
    combine into overall risk, classify, and explain.
    """
    risks = calculate_vendor_risk(vendor, requirements)
    overall_risk = calculate_overall_risk(risks, risk_weights)
    risk_level = classify_risk_level(overall_risk)
    explanation = generate_risk_explanation(vendor, risks, overall_risk, risk_level, requirements)

    return {
        "name": vendor["name"],
        "risks": risks,
        "overall_risk": overall_risk,
        "risk_level": risk_level,
        "explanation": explanation,
    }


def run_risk_intelligence(vendors, requirements, risk_weights):
    """
    Runs risk assessment across every vendor. Returns a list of
    risk-assessment dictionaries, sorted from lowest to highest risk.
    """
    validate_vendors(vendors)
    validate_requirements(requirements)
    validate_risk_weights(risk_weights)

    assessments = [assess_vendor_risk(v, requirements, risk_weights) for v in vendors]
    assessments.sort(key=lambda a: a["overall_risk"])
    return assessments


def print_risk_header():
    print("\n" + "=" * 50)
    print("           RISK INTELLIGENCE")
    print("=" * 50)


def print_requirements(requirements):
    print("\nREQUIREMENTS")
    print(f"Budget: {requirements['budget']:,.0f}")
    print(f"Required Delivery Days: {requirements['required_delivery_days']}")
    print(f"Minimum Quality: {requirements['minimum_quality']}")
    print(f"Minimum Reliability: {requirements['minimum_reliability']}")
    print(f"Minimum Warranty Years: {requirements['minimum_warranty_years']}")


def print_risk_assessments(assessments):
    print("\n" + "-" * 50)
    print("VENDOR RISK ANALYSIS")
    print("-" * 50)

    for a in assessments:
        r = a["risks"]
        print(f"\n{a['name']}")
        print(f"Delivery Risk: {r['delivery']:.2f}")
        print(f"Budget Risk: {r['budget']:.2f}")
        print(f"Quality Risk: {r['quality']:.2f}")
        print(f"Reliability Risk: {r['reliability']:.2f}")
        print(f"Warranty Risk: {r['warranty']:.2f}")
        print(f"\nOverall Risk: {a['overall_risk']:.2f}")
        print(f"Risk Level: {a['risk_level']}")
        print(f"Explanation: {a['explanation']}")


def run_risk_scenario(title, vendors, requirements, risk_weights):
    print("\n\n" + "#" * 50)
    print(f"# RISK SCENARIO: {title}")
    print("#" * 50)

    print_risk_header()
    print_requirements(requirements)
    assessments = run_risk_intelligence(vendors, requirements, risk_weights)
    print_risk_assessments(assessments)

    return assessments


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":

    vendors = [
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

    default_weights = {
        "price": 35,
        "delivery": 25,
        "quality": 20,
        "reliability": 15,
        "warranty": 5
    }

    delivery_critical_weights = {
        "price": 15,
        "delivery": 45,
        "quality": 20,
        "reliability": 15,
        "warranty": 5
    }

    quality_critical_weights = {
        "price": 20,
        "delivery": 15,
        "quality": 40,
        "reliability": 15,
        "warranty": 10
    }

    run_scenario("1. DEFAULT WEIGHTS", vendors, default_weights)
    run_scenario("2. DELIVERY-CRITICAL WEIGHTS", vendors, delivery_critical_weights)
    run_scenario("3. QUALITY-CRITICAL WEIGHTS", vendors, quality_critical_weights)

    # -------------------------------------------------------
    # STEP 2: RISK INTELLIGENCE
    # -------------------------------------------------------

    requirements = {
        "budget": 520000,
        "required_delivery_days": 7,
        "minimum_quality": 8.5,
        "minimum_reliability": 85,
        "minimum_warranty_years": 2
    }

    risk_weights = {
        "delivery": 30,
        "budget": 20,
        "quality": 20,
        "reliability": 20,
        "warranty": 10
    }

    strict_requirements = {
        "budget": 500000,
        "required_delivery_days": 5,
        "minimum_quality": 9.0,
        "minimum_reliability": 90,
        "minimum_warranty_years": 3
    }

    run_risk_scenario("1. NORMAL REQUIREMENTS", vendors, requirements, risk_weights)
    run_risk_scenario("2. STRICT REQUIREMENTS", vendors, strict_requirements, risk_weights)
