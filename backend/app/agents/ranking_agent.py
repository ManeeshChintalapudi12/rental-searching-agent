from app.models import Recommendation, RentalListing


class RankingAgent:
    """Computes transparent deal scores from provider facts."""

    def run(self, listings: list[RentalListing]) -> list[Recommendation]:
        if not listings:
            return []
        lowest = min(item.total_price.amount for item in listings)
        recommendations = []
        for item in listings:
            price_score = 60 * (lowest / max(item.total_price.amount, 1))
            rating_score = 30 * (item.rating / 5)
            fee_score = 10 * (1 - min(item.mandatory_fees.amount / max(item.total_price.amount, 1), 1))
            score = round(min(price_score + rating_score + fee_score, 100), 1)
            recommendations.append(Recommendation(
                listing_id=item.id,
                reason=f"${item.total_price.amount:,.0f} verified total, {item.rating}/5 rating, and {len(item.features)} matched features.",
                verified_total=item.total_price,
                deal_score=score,
            ))
        return sorted(recommendations, key=lambda item: item.deal_score, reverse=True)[:3]
