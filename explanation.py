"""
Procurement Twin - AI Decision Explanation Engine

This module converts the outputs from the scoring, risk,
savings, and what-if engines into a clear final explanation.

No new scoring or risk formulas are introduced here.
"""


# ---------------------------------------------------------
# LABELS
# ---------------------------------------------------------

CRITERION_LABELS = {
    "price": "price",
    "delivery": "delivery",
    "quality": "quality",
    "reliability": "reliability",
    "warranty": "warranty",
}


# ---------------------------------------------------------
# STRENGTH ANALYSIS
# ---------------------------------------------------------

def identify_strength_factors(winner_detail, top_n=2):
    """
    Returns the winner's strongest normalized criteria.
    """
    normalized = winner_detail["normalized"]

    return sorted(
        normalized.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]


def identify_weakest_factor(winner_detail):
    """
    Returns the winner's weakest normalized criterion.
    """
    normalized = winner_detail["normalized"]

    return min(
        normalized.items(),
        key=lambda x: x[1]
    )


# ---------------------------------------------------------
# RISK EXPLANATION
# ---------------------------------------------------------

def describe_risk_advantage(winner_risk, risk_results):
    """
    Compares the recommended vendor's risk against competitors.
    """

    others = [
        r for r in risk_results
        if r["name"] != winner_risk["name"]
    ]

    if not others:
        return (
            f"Risk score is {winner_risk['overall_risk']:.2f}/100 "
            f"({winner_risk['risk_level']})."
        )

    best_other_risk = min(
        r["overall_risk"]
        for r in others
    )

    if winner_risk["overall_risk"] <= best_other_risk:

        return (
            f"It has the lowest risk profile among all evaluated vendors "
            f"at {winner_risk['overall_risk']:.2f}/100 "
            f"({winner_risk['risk_level']})."
        )

    return (
        f"It carries a {winner_risk['overall_risk']:.2f}/100 "
        f"risk score ({winner_risk['risk_level']}), "
        f"which is higher than the best alternative "
        f"({best_other_risk:.2f}/100), but its stronger procurement "
        f"score makes it the recommended option."
    )


# ---------------------------------------------------------
# FINANCIAL EXPLANATION
# ---------------------------------------------------------

def describe_financial_position(winner_savings):
    """
    Explains the recommended vendor's financial position.
    """

    difference = winner_savings["budget_difference"]
    percentage = winner_savings["savings_percentage"]

    if difference > 0:

        return (
            f"Priced ₹{abs(difference):,.0f} under budget, "
            f"providing {percentage:.2f}% potential savings."
        )

    elif difference < 0:

        return (
            f"Priced ₹{abs(difference):,.0f} over budget, "
            f"representing a {abs(percentage):.2f}% premium."
        )

    return "Priced exactly at the procurement budget."


# ---------------------------------------------------------
# TRADE-OFF ANALYSIS
# ---------------------------------------------------------

def generate_trade_off(winner_detail, all_vendor_details):
    """
    Identifies the winner's weakest criterion and checks whether
    another vendor performs better on it.
    """

    weakest_criterion, weakest_score = identify_weakest_factor(
        winner_detail
    )

    competitors = [
        v for v in all_vendor_details
        if v["name"] != winner_detail["name"]
    ]

    if not competitors:
        return "No competing vendors were available for comparison."

    best_competitor = max(
        competitors,
        key=lambda v: v["normalized"][weakest_criterion]
    )

    competitor_score = best_competitor["normalized"][
        weakest_criterion
    ]

    if competitor_score > weakest_score:

        return (
            f"{winner_detail['name']}'s weakest area is "
            f"{CRITERION_LABELS[weakest_criterion]} "
            f"({weakest_score:.2f}/100). "
            f"{best_competitor['name']} performs better on this factor "
            f"({competitor_score:.2f}/100), but the winner's advantages "
            f"on other criteria outweigh this gap."
        )

    return (
        f"{winner_detail['name']} has no significant weakness "
        f"relative to the other evaluated vendors."
    )


# ---------------------------------------------------------
# WHAT-IF EXPLANATION
# ---------------------------------------------------------

def generate_whatif_insight(what_if_results):
    """
    Explains whether the recommendation changed after simulation.
    """

    before_name = what_if_results["before"]["recommended_name"]
    after_name = what_if_results["after"]["recommended_name"]

    if before_name != after_name:

        intro = (
            f"The recommendation changed from {before_name} "
            f"to {after_name} when the procurement priorities changed."
        )

    else:

        intro = (
            f"The recommendation remained {after_name} "
            f"even after the priorities and requirements were adjusted."
        )

    return (
        f"{intro} "
        f"{what_if_results['explanation']}"
    )


# ---------------------------------------------------------
# FINAL DECISION SUMMARY
# ---------------------------------------------------------

def generate_decision_summary(
    scoring_results,
    risk_results,
    savings_results,
    what_if_results
):
    """
    Combines the outputs of all previous intelligence engines
    into one final decision summary.
    """

    winner_name = scoring_results["recommended_vendor"]
    winner_score = scoring_results["recommended_score"]

    winner_detail = next(
        v for v in scoring_results["vendors"]
        if v["name"] == winner_name
    )

    winner_risk = next(
        r for r in risk_results
        if r["name"] == winner_name
    )

    winner_savings = next(
        s for s in savings_results
        if s["name"] == winner_name
    )

    strengths = identify_strength_factors(
        winner_detail
    )

    strength_bullets = [
        f"Leads on {CRITERION_LABELS[criterion]} "
        f"({score:.2f}/100)"
        for criterion, score in strengths
    ]

    risk_bullet = describe_risk_advantage(
        winner_risk,
        risk_results
    )

    financial_bullet = describe_financial_position(
        winner_savings
    )

    trade_off = generate_trade_off(
        winner_detail,
        scoring_results["vendors"]
    )

    whatif_insight = generate_whatif_insight(
        what_if_results
    )

    return {
        "winner_name": winner_name,
        "winner_score": winner_score,
        "winner_risk": winner_risk,
        "winner_savings": winner_savings,
        "strength_bullets": strength_bullets,
        "risk_bullet": risk_bullet,
        "financial_bullet": financial_bullet,
        "trade_off": trade_off,
        "whatif_insight": whatif_insight,
    }


# ---------------------------------------------------------
# CONSOLE OUTPUT
# ---------------------------------------------------------

def print_decision_summary(summary):

    print("\n" + "=" * 60)
    print("       PROCUREMENT TWIN — FINAL DECISION")
    print("=" * 60)

    print("\n🏆 RECOMMENDED VENDOR")
    print(summary["winner_name"])

    print(
        f"\nOverall Score: "
        f"{summary['winner_score']:.2f}/100"
    )

    print(
        f"Risk Level: "
        f"{summary['winner_risk']['risk_level']}"
    )

    print(
        f"Risk Score: "
        f"{summary['winner_risk']['overall_risk']:.2f}/100"
    )

    # -----------------------------------------------------
    # FINANCIAL IMPACT
    # -----------------------------------------------------

    print("\n💰 FINANCIAL IMPACT")

    savings = summary["winner_savings"]

    print(
        f"Quoted Price: ₹{savings['quoted_price']:,.0f}"
    )

    print(
        f"Budget: ₹{savings['budget']:,.0f}"
    )

    if savings["budget_difference"] >= 0:

        print(
            f"Savings: ₹{savings['budget_difference']:,.0f}"
        )

    else:

        print(
            f"Over Budget: "
            f"₹{abs(savings['budget_difference']):,.0f}"
        )

    print(
        f"Savings %: "
        f"{savings['savings_percentage']:.2f}%"
    )

    # -----------------------------------------------------
    # WHY THIS VENDOR?
    # -----------------------------------------------------

    print("\nWHY THIS VENDOR?")

    print("• Strongest overall procurement score")

    for bullet in summary["strength_bullets"]:
        print(f"• {bullet}")

    print(f"• {summary['risk_bullet']}")

    print(f"• {summary['financial_bullet']}")

    # -----------------------------------------------------
    # TRADE-OFF
    # -----------------------------------------------------

    print("\nKEY TRADE-OFF")

    print(summary["trade_off"])

    # -----------------------------------------------------
    # WHAT-IF
    # -----------------------------------------------------

    print("\nWHAT-IF INSIGHT")

    print(summary["whatif_insight"])