from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class Prediction:
    source: str
    market: str
    pick: str
    confidence: int = 60


@dataclass
class Fixture:
    league: str
    home: str
    away: str
    kickoff: str
    predictions: list[Prediction]
    notes: list[str]


def normalize_pick(market: str, pick: str) -> tuple[str, str]:
    m = market.strip().lower()
    p = pick.strip().lower()

    market_map = {
        "home win": "1X2", "draw": "1X2", "away win": "1X2", "1x2": "1X2",
        "btts": "BTTS", "both teams to score": "BTTS",
        "over/under": "Goals", "goals": "Goals", "over 1.5": "Goals", "over 2.5": "Goals",
        "double chance": "Double Chance", "dnb": "Draw No Bet", "draw no bet": "Draw No Bet",
    }
    normalized_market = market_map.get(m, market.strip())

    replacements = {
        "home": "Home Win", "home win": "Home Win", "1": "Home Win",
        "x": "Draw", "draw": "Draw",
        "away": "Away Win", "away win": "Away Win", "2": "Away Win",
        "yes": "BTTS Yes", "btts yes": "BTTS Yes",
        "no": "BTTS No", "btts no": "BTTS No",
        "over 1.5 goals": "Over 1.5", "over 1.5": "Over 1.5",
        "over 2.5 goals": "Over 2.5", "over 2.5": "Over 2.5",
        "under 2.5 goals": "Under 2.5", "under 2.5": "Under 2.5",
        "1x": "Home or Draw", "x2": "Away or Draw", "12": "Home or Away",
    }
    normalized_pick = replacements.get(p, pick.strip())
    return normalized_market, normalized_pick


def consensus(predictions: list[Prediction]) -> dict:
    if not predictions:
        return {"pick": "No Pick", "agreement": 0, "votes": 0, "sources": []}

    keys = []
    for pred in predictions:
        market, pick = normalize_pick(pred.market, pred.pick)
        keys.append((market, pick))

    counter = Counter(keys)
    (market, pick), votes = counter.most_common(1)[0]
    agreement = round((votes / len(predictions)) * 100)
    sources = [p.source for p in predictions if normalize_pick(p.market, p.pick) == (market, pick)]
    return {"market": market, "pick": pick, "agreement": agreement, "votes": votes, "sources": sources}


def detect_traps(fixture: Fixture, selected_pick: str, agreement: int) -> tuple[str, list[str]]:
    warnings: list[str] = []
    name = f"{fixture.home} vs {fixture.away}".lower()

    derby_keywords = ["milan", "roma", "manchester", "london", "madrid", "barcelona"]
    if any(k in name for k in derby_keywords) and selected_pick in ["Home Win", "Away Win"]:
        warnings.append("Derby/rivalry-style risk: avoid overconfidence on straight 1X2.")

    if agreement < 60:
        warnings.append("Weak prediction consensus across sources.")

    if selected_pick in ["Home Win", "Away Win"] and agreement < 75:
        warnings.append("Straight win pick is not strongly supported; consider safer market.")

    for note in fixture.notes:
        if any(word in note.lower() for word in ["injury", "rotation", "suspended", "fatigue", "odds drift"]):
            warnings.append(note)

    if len(warnings) >= 2:
        return "High", warnings
    if len(warnings) == 1:
        return "Medium", warnings
    return "Low", warnings


def score_pick(agreement: int, trap_risk: str) -> tuple[int, str]:
    penalty = {"Low": 0, "Medium": 10, "High": 25}.get(trap_risk, 0)
    score = max(1, min(95, agreement + 10 - penalty))
    if score >= 80:
        label = "High"
    elif score >= 65:
        label = "Medium"
    else:
        label = "Low"
    return score, label


def get_today_fixtures() -> list[Fixture]:
    """
    MVP sample data. Replace this later with API/prediction-site collectors.
    """
    return [
        Fixture(
            league="Premier League",
            home="Arsenal",
            away="Chelsea",
            kickoff="20:00",
            predictions=[
                Prediction("Source A", "Goals", "Over 1.5"),
                Prediction("Source B", "Over 1.5", "Over 1.5"),
                Prediction("Source C", "BTTS", "BTTS Yes"),
                Prediction("Source D", "Goals", "Over 1.5"),
            ],
            notes=[]
        ),
        Fixture(
            league="La Liga",
            home="Real Madrid",
            away="Sevilla",
            kickoff="22:00",
            predictions=[
                Prediction("Source A", "1X2", "Home Win"),
                Prediction("Source B", "Double Chance", "Home or Draw"),
                Prediction("Source C", "Goals", "Over 1.5"),
                Prediction("Source D", "1X2", "Home Win"),
            ],
            notes=["Possible low-odds accumulator trap on straight home win."]
        ),
    ]


def build_daily_report() -> tuple[str, str]:
    tz = ZoneInfo("Africa/Kampala")
    today = datetime.now(tz).strftime("%d %B %Y")
    fixtures = get_today_fixtures()

    subject = f"Betting Guru Daily Football Picks - {today}"
    lines = [
        "🤖 Betting Guru Daily Football Picks",
        f"Date: {today}",
        "",
        "Coverage target: major European leagues + UEFA competitions",
        "Note: MVP currently uses sample prediction inputs until live sources are connected.",
        "",
    ]

    if not fixtures:
        lines.append("No fixtures found for today.")
    else:
        current_league = None
        for i, fixture in enumerate(fixtures, start=1):
            if fixture.league != current_league:
                current_league = fixture.league
                lines.append(f"🏆 {current_league}")
                lines.append("")

            c = consensus(fixture.predictions)
            trap_risk, warnings = detect_traps(fixture, c["pick"], c["agreement"])
            score, label = score_pick(c["agreement"], trap_risk)
            sources = ", ".join(c["sources"])

            lines.extend([
                f"{i}. ⚽ {fixture.home} vs {fixture.away} ({fixture.kickoff})",
                f"Best Market: {c['pick']} ({c.get('market', 'Market')})",
                f"Confidence: {label} - {score}%",
                f"Consensus: {c['votes']}/{len(fixture.predictions)} sources agree ({c['agreement']}%)",
                f"Supporting Sources: {sources}",
                f"Trap Risk: {trap_risk}",
            ])
            if warnings:
                lines.append("Warnings:")
                for warning in warnings:
                    lines.append(f"- {warning}")
            else:
                lines.append("Warnings: No major trap detected.")
            lines.append("")

    lines.extend([
        "⚠️ Responsible Betting:",
        "Predictions are analysis only, not guaranteed outcomes. Bet responsibly and only what you can afford to lose.",
    ])
    return subject, "\n".join(lines)
