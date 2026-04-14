from app.database import SessionLocal
import app.models
from app.models.budget_rules import BudgetRule
from datetime import date

def seed_budget_rules():
    db = SessionLocal()

    existing = db.query(BudgetRule).first()
    if existing:
        print("⚠️  Budget rules already seeded. Skipping.")
        db.close()
        return

    start_date = date(2026, 1, 1)

    # Income categories that follow the standard rule set
    standard_categories = [
        "Earned Income",
        "Passive Income",
        "Business Income",
        "Investment Income",
        "Transfer Income",
        "Residual Income",
    ]

    rules = []

    # ── EARNED INCOME (Fare deducted first) ─────────────────────
    rules.append(
        BudgetRule(income_category="Earned Income", category="Fare",
                   is_fixed=True, fixed_amount=5000.0,
                   deduct_first=True,                   # deducted before anything else
                   valid_from=start_date, is_current=True)
    )

    # ── STANDARD RULES (applied to all 6 non-Other categories) ──
    standard_rules = [
        ("Food",                "Needs", 0.25),
        ("Housing",             "Needs", 0.15),
        ("Clothing",            "Needs", 0.10),
        ("Wants",               None,    0.20),
        ("Investment/Savings",  None,    0.20),
        ("Tithe",               None,    0.10),
    ]

    for income_cat in standard_categories:
        for category, parent, pct in standard_rules:
            # Earned Income already has Fare — skip adding a zero Fare rule
            if income_cat == "Earned Income" and category == "Fare":
                continue
            rules.append(
                BudgetRule(
                    income_category=income_cat,
                    category=category,
                    parent_category=parent,
                    percentage=pct,
                    is_fixed=False,
                    deduct_first=False,
                    valid_from=start_date,
                    is_current=True
                )
            )

    # ── OTHER (modified rules — more Wants, no Tithe) ────────────
    other_rules = [
        ("Food",                "Needs", 0.25),
        ("Housing",             "Needs", 0.15),
        ("Clothing",            "Needs", 0.10),
        ("Wants",               None,    0.30),  # 30% instead of 20%
        ("Investment/Savings",  None,    0.20),
        ("Tithe",               None,    0.00),  # not applied to Other
    ]

    for category, parent, pct in other_rules:
        rules.append(
            BudgetRule(
                income_category="Other",
                category=category,
                parent_category=parent,
                percentage=pct,
                is_fixed=False,
                deduct_first=False,
                valid_from=start_date,
                is_current=True
            )
        )

    db.add_all(rules)
    db.commit()
    print(f"✅ {len(rules)} budget rules seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_budget_rules()