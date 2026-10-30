"""Control efficacy of each fungicide across the national cooperative trials, season by season.

The five national summaries in this dataset (2009/10, 2012/13, 2015/16, 2019/20, 2022/23) each
print one table with the mean control efficacy of every product over all trial sites. This script
takes those tables, matches the same active ingredients at the same dose across seasons, and
writes the series and a per-product trend.

Exploratory: efficacy also depends on how strong the epidemic was in each season, so a fall in one
product means more when the products tested alongside it fell less.

Usage: python -I efficacy_over_time.py
Writes efficacy_by_season.csv and efficacy_trends.csv next to this file. Needs pandas.
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data" / "soybean_rust_trials.csv"

# The national mean table of each summary
MEAN_TABLES = {
	"godoy2010-cooperativos-0910-ct80": "Tabela 3",
	"godoy2013-cooperativos-1213-ct99": "Tabela 3",
	"godoy2016-cooperativos-1516-ct119": "Tabela 3",
	"godoy2020-cooperativos-1920-ct160": "Tabela 5",
	"godoy2023-cooperativos-2223-ct195": "Tabela 6",
}


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


def season_start(season):
	return int(str(season)[:4])


def main():
	data = pd.read_csv(DATA, dtype=str)
	rows = []
	for doc, table in MEAN_TABLES.items():
		part = data[
			(data.doc_id == doc)
			& (data.table_or_figure == table)
			& (data.variable_standardized == "control_efficacy_pct")
			& data.active_ingredient_or_agent.notna()
		]
		for _, r in part.iterrows():
			rows.append({
				"season": r.season_or_year,
				"year": season_start(r.season_or_year),
				"ingredients": ingredients(r.active_ingredient_or_agent),
				"dose_g_ai_ha": dose(r.dose_and_unit),
				"efficacy_pct": float(r.value),
				"treatment_as_printed": r.treatment,
				"record_id": r.record_id,
			})
	series = pd.DataFrame(rows).sort_values(["ingredients", "dose_g_ai_ha", "year"])
	series.to_csv(HERE / "efficacy_by_season.csv", index=False)

	season_mean = series.groupby("year").efficacy_pct.mean()
	trends = []
	for (name, dose_g), g in series.groupby(["ingredients", "dose_g_ai_ha"]):
		g = g.groupby("year").efficacy_pct.mean()
		if len(g) < 3:
			continue
		years = pd.Series(g.index, index=g.index, dtype=float)
		slope = ((years - years.mean()) * (g - g.mean())).sum() / ((years - years.mean()) ** 2).sum()
		relative = g - season_mean.loc[g.index]
		rel_slope = ((years - years.mean()) * (relative - relative.mean())).sum() / ((years - years.mean()) ** 2).sum()
		trends.append({
			"ingredients": name,
			"dose_g_ai_ha": dose_g,
			"seasons": len(g),
			"first": f"{int(g.index[0])}: {g.iloc[0]:.0f}%",
			"last": f"{int(g.index[-1])}: {g.iloc[-1]:.0f}%",
			"change_pp_per_year": round(slope, 2),
			"change_vs_season_mean_pp_per_year": round(rel_slope, 2),
		})
	trends = pd.DataFrame(trends).sort_values("change_pp_per_year")
	trends.to_csv(HERE / "efficacy_trends.csv", index=False)
	print(trends.to_string(index=False))
	print()
	print("Mean efficacy of all products in each season:")
	print(season_mean.round(1).to_string())


if __name__ == "__main__":
	main()
