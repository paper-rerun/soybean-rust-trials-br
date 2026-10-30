"""Control efficacy of each fungicide across the national cooperative trials, season by season.

Each national summary prints one table with the mean control efficacy of every product over all
trial sites. series.csv lists every season, which publication holds it, and, once the publication
is in the dataset, its doc_id and the label of that table. This script takes those tables, matches
the same active ingredients at the same dose across seasons, and fits for each product a straight
line over the seasons it was tested.

Efficacy also depends on how strong the epidemic was in a season. The model separates the two:
efficacy = product level + product trend x (year - product's mean year) + season effect, with the
season effects averaging zero. It is fitted by alternating least squares, so a season in which
every product did worse does not show up as a fall in each product.

Usage: python -I efficacy_over_time.py
Writes efficacy_by_season.csv and efficacy_trends.csv next to this file. Needs pandas.
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data" / "soybean_rust_trials.csv"
SERIES = HERE / "series.csv"
MIN_SEASONS = 3
ITERATIONS = 200


def ingredients(text):
	"""'azoxistrobina + ciproconazol' -> 'azoxistrobina + ciproconazol', in a fixed order."""
	parts = [re.sub(r"\d+$", "", p.strip().lower()) for p in str(text).split("+")]
	return " + ".join(sorted(p for p in parts if p))


def dose(text):
	"""Grams of active ingredient per hectare, as printed before 'g i.a.' ('60 + 24')."""
	match = re.search(r"([\d.,]+(?:\s*\+\s*[\d.,]+)*)\s*g\s*i\.\s*a\.", str(text))
	if not match:
		return ""
	return " + ".join(p.strip().replace(".", "").replace(",", ".") for p in match.group(1).split("+"))


def load_series():
	data = pd.read_csv(DATA, dtype=str)
	seasons = pd.read_csv(SERIES, dtype=str).fillna("")
	rows = []
	for _, s in seasons[(seasons.doc_id != "") & (seasons.mean_table != "")].iterrows():
		part = data[
			(data.doc_id == s.doc_id)
			& (data.table_or_figure == s.mean_table)
			& (data.variable_standardized == "control_efficacy_pct")
			& data.active_ingredient_or_agent.notna()
		]
		for _, r in part.iterrows():
			rows.append({
				"season": s.season,
				"year": int(s.season[:4]),
				"product": f"{ingredients(r.active_ingredient_or_agent)} ({dose(r.dose_and_unit) or 'dose not printed'} g a.i./ha)",
				"efficacy_pct": float(r.value),
				"treatment_as_printed": r.treatment,
				"record_id": r.record_id,
			})
	series = pd.DataFrame(rows)
	# A product printed twice in one table (two formulations) counts once, as their mean
	return series.groupby(["product", "season", "year"], as_index=False).agg(
		efficacy_pct=("efficacy_pct", "mean"), record_ids=("record_id", "; ".join))


def slope(x, y):
	x = x - x.mean()
	return (x * (y - y.mean())).sum() / (x ** 2).sum() if (x ** 2).sum() else 0.0


def fit(series):
	"""Per-product line plus a season effect, by alternating least squares."""
	tracked = series.groupby("product").filter(lambda g: len(g) >= MIN_SEASONS).copy()
	season_effect = pd.Series(0.0, index=sorted(tracked.year.unique()))
	for _ in range(ITERATIONS):
		tracked["adjusted"] = tracked.efficacy_pct - tracked.year.map(season_effect)
		lines = {p: (g.adjusted.mean(), slope(g.year, g.adjusted), g.year.mean()) for p, g in tracked.groupby("product")}
		tracked["line"] = [lines[p][0] + lines[p][1] * (y - lines[p][2]) for p, y in zip(tracked["product"], tracked.year)]
		new_effect = (tracked.efficacy_pct - tracked.line).groupby(tracked.year).mean()
		new_effect -= new_effect.mean()
		if (new_effect - season_effect).abs().max() < 1e-9:
			break
		season_effect = new_effect
	return tracked, lines, season_effect


def main():
	series = load_series()
	series.sort_values(["product", "year"]).to_csv(HERE / "efficacy_by_season.csv", index=False)
	tracked, lines, season_effect = fit(series)

	trends = []
	for product, g in tracked.groupby("product"):
		g = g.sort_values("year")
		trends.append({
			"product": product,
			"seasons": len(g),
			"first": f"{g.season.iloc[0]}: {g.efficacy_pct.iloc[0]:.0f}%",
			"last": f"{g.season.iloc[-1]}: {g.efficacy_pct.iloc[-1]:.0f}%",
			"raw_change_pp_per_year": round(slope(g.year, g.efficacy_pct), 2),
			"season_adjusted_change_pp_per_year": round(lines[product][1], 2),
		})
	trends = pd.DataFrame(trends).sort_values("season_adjusted_change_pp_per_year")
	trends.to_csv(HERE / "efficacy_trends.csv", index=False)

	print(f"{series.season.nunique()} seasons, {series['product'].nunique()} products, {len(trends)} tested in {MIN_SEASONS}+ seasons\n")
	print(trends.to_string(index=False))
	print("\nSeason effect (pp, all products together; negative = harder season):")
	print(season_effect.round(1).to_string())


if __name__ == "__main__":
	main()
