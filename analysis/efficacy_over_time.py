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

Changed for the full series (ferrugem-soja-serie, 2026-11-01); the publico-soja version runs next to it as
efficacy_over_time_original.py, with its outputs on the same data in *_original_script.csv:
- the ingredient list also splits on '&' (2020/21 prints 'picoxistrobina & ciproconazol') and old or
  English spellings take the name the recent circulars use (2004/05 prints 'azoxystrobin', 'tebuconazole');
- each dose goes with its ingredient before sorting, so 'tebuconazol + clorotalonil 125 + 1125' and
  'clorotalonil + tebuconazol 1125 + 125' are the same product;
- the columns for sites sprayed without or with symptoms (2008/09, trial_label 'Sem sintomas' and
  'Com sintomas') are left out; only the all-sites column (Todos) is the national mean.
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data" / "soybean_rust_trials.csv"
SERIES = HERE / "series.csv"
MIN_SEASONS = 3
ITERATIONS = 200


# Spellings of the older and English-language summaries, to the name the recent circulars print
SAME_INGREDIENT = {
	"azoxystrobin": "azoxistrobina", "ciproconazole": "ciproconazol", "epoxiconazole": "epoxiconazol",
	"propiconazole": "propiconazol", "prothioconazol": "protioconazol", "protioconazole": "protioconazol",
	"prothioconazole": "protioconazol", "tebuconazole": "tebuconazol", "tetraconazole": "tetraconazol",
	"trifloxystrobin": "trifloxistrobina", "pyraclostrobin": "piraclostrobina", "difenoconazole": "difenoconazol",
	"fluquinconazole": "fluquinconazol", "metconazole": "metconazol", "myclobutanil": "miclobutanil",
	"bixafen": "bixafem", "fluxapyroxad": "fluxapiroxade", "fluxapiroxad": "fluxapiroxade",
	"benzovindiflupyr": "benzovindiflupir", "impirfluxan": "impirfluxam", "carbendazin": "carbendazim",
}


def ingredient_names(text):
	parts = [re.sub(r"\d+$", "", p.strip().lower()) for p in re.split(r"[+&]", str(text))]
	return [SAME_INGREDIENT.get(p, p) for p in parts if p]


def dose_parts(text):
	"""Grams of active ingredient per hectare, as printed before 'g i.a.' (['60', '24'])."""
	match = re.search(r"([\d.,]+(?:\s*[+&]\s*[\d.,]+)*)\s*g\s*i\.\s*a\.", str(text))
	if not match:
		return []
	return [p.strip().replace(".", "").replace(",", ".") for p in re.split(r"[+&]", match.group(1))]


def product_label(ingredient_text, dose_text):
	"""'tebuconazol + clorotalonil', '125 + 1125 g i.a./ha' -> 'clorotalonil + tebuconazol (1125 + 125 g a.i./ha)'."""
	names, doses = ingredient_names(ingredient_text), dose_parts(dose_text)
	if len(doses) == len(names):
		pairs = sorted(zip(names, doses))
		names, doses = [name for name, _ in pairs], [each_dose for _, each_dose in pairs]
	else:
		names = sorted(names)
	return f"{' + '.join(names)} ({' + '.join(doses) or 'dose not printed'} g a.i./ha)"


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
			# Sites without or with symptoms at the first spray are subsets; the all-sites column is the national mean
			& ~data.trial_label.fillna("").isin(["Sem sintomas", "Com sintomas"])
		]
		for _, r in part.iterrows():
			rows.append({
				"season": s.season,
				"year": int(s.season[:4]),
				"product": product_label(r.active_ingredient_or_agent, r.dose_and_unit),
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
	# The full-series fixes: dose follows its ingredient, '&' splits, English spellings match
	assert product_label("tebuconazol + clorotalonil", "125 + 1125 g i.a./ha") == product_label("clorotalonil + tebuconazol", "1.125 + 125 g i.a./ha") == "clorotalonil + tebuconazol (1125 + 125 g a.i./ha)"
	assert product_label("picoxistrobina & ciproconazol", "60 & 24 g i.a./ha") == product_label("picoxistrobina + ciproconazol1", "60 + 24 g i.a. ha-1")
	assert product_label("azoxystrobin + ciproconazole", "60 + 24 g i.a./ha") == product_label("azoxistrobina + ciproconazol", "60 + 24 g i.a./ha")
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
