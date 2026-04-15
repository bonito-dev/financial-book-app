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

    standard_categories = [
        "Earned Income",
        "Passive Income",
        "Business Income",
        "Investment Income",
        "Transfer Income",
        "Residual Income",
    ]

    rules = []

    # ── EARNED INCOME SPECIAL DEDUCTIONS (ordered) ──────────────
    # Tithe deducted FIRST (order 1) — 10% of gross
    rules.append(
        BudgetRule(
            income_category="Earned Income",
            category="Tithe",
            percentage=0.10,
            is_fixed=False,
            deduct_first=True,
            deduction_order=1,        # happens first
            valid_from=start_date,
            is_current=True
        )
    )

    # Fare topped up SECOND (order 2) — on 1st of each month
    rules.append(
        BudgetRule(
            income_category="Earned Income",
            category="Fare",
            is_fixed=False,
            deduct_first=True,
            deduction_order=2,        # happens after Tithe
            is_topup=True,
            topup_target=5000.0,      # top up to KES 5,000
            topup_day=1,              # triggers on 1st of month
            valid_from=start_date,
            is_current=True
        )
    )

    # ── STANDARD PERCENTAGE RULES ────────────────────────────────
    # Applied to remainder after deductions
    # Note: Tithe skipped here for Earned Income (already deducted above)
    standard_rules = [
        ("Food",               "Needs", 0.25),
        ("Housing",            "Needs", 0.15),
        ("Clothing",           "Needs", 0.10),
        ("Wants",              None,    0.20),
        ("Investment/Savings", None,    0.20),
        ("Tithe",              None,    0.10),  # applied to non-Earned categories
    ]

    for income_cat in standard_categories:
        for category, parent, pct in standard_rules:
            # Earned Income: skip Tithe here (handled above as deduct_first)
            # Earned Income: skip Fare here (handled above as topup)
            if income_cat == "Earned Income" and category in ("Tithe", "Fare"):
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

    # ── OTHER (30% Wants, no Tithe) ──────────────────────────────
    other_rules = [
        ("Food",               "Needs", 0.25),
        ("Housing",            "Needs", 0.15),
        ("Clothing",           "Needs", 0.10),
        ("Wants",              None,    0.30),  # 30% for Other
        ("Investment/Savings", None,    0.20),
        ("Tithe",              None,    0.00),  # not applied to Other
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