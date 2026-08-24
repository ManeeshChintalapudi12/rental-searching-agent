import re

from app.models import Recommendation, RentalListing


class VerificationAgent:
    """Final deterministic guardrail for listing IDs and monetary claims."""

    def run(self, answer: str, listings: list[RentalListing], recommendations: list[Recommendation]) -> tuple[str, bool, list[str]]:
        valid_ids = {item.id for item in listings}
        citations = re.findall(r"\[([\w-]+)\]", answer)
        invalid_citations = [citation for citation in citations if citation not in valid_ids]
        allowed_amounts = {
            round(value, 2)
            for item in listings
            for value in (item.base_price.amount, item.total_price.amount, item.mandatory_fees.amount)
        }
        claimed_amounts = {
            float(value.replace(",", ""))
            for value in re.findall(r"\$([\d,]+(?:\.\d{1,2})?)", answer)
        }
        grounded = not invalid_citations and claimed_amounts.issubset(allowed_amounts)
        if not grounded and listings:
            top = recommendations[0]
            item = next(row for row in listings if row.id == top.listing_id)
            answer = (
                f"Verified result: {item.title} costs ${item.total_price.amount:,.0f} total, "
                f"including ${item.mandatory_fees.amount:,.0f} in mandatory fees [{item.id}]."
            )
            citations = [item.id]
            grounded = True
        return answer, grounded, list(dict.fromkeys(citations))
