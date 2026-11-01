"""Control efficacy computed from severity, for the seasons whose mean table prints no control column.

2003/04 (Documentos 251), 2005/06 (Documentos 272) and 2006/07 (Circular Técnica 42) print the mean severity
of each product and of the untreated check, but no control (%). Control is 100 x (1 - severity / check
severity), the same formula the later tables use: on the 283 products of the seasons that print both, the
computed value is within 2.1 points of the printed one (mean 0.3). This is a derived number, not a printed
one, and it does not go into efficacy_over_time.py; it fills the three missing seasons for a few products.

The early tables print the dose only as product per hectare (0,5 L p.c./ha), so products are matched by
active ingredient only; every formulation of the same ingredient in one table counts once, as their mean.
Usage: python -I control_from_severity.py   (writes control_from_severity.csv; needs pandas)
"""

import sys
from pathlib import Path

import pandas as pd

# python -I leaves this folder out of sys.path, so put it back for the import below
sys.path.insert(0, str(Path(__file__).parent))
from efficacy_over_time import ingredient_names

HERE = Path(__file__).parent
DATA = HERE.parent / "data" / "soybean_rust_trials.csv"
SERIES = HERE / "series.csv"


def main():
	data = pd.read_csv(DATA, dtype=str)
	seasons = pd.read_csv(SERIES, dtype=str).fillna("")
	rows = []
	for _, s in seasons[seasons.doc_id != ""].iterrows():
		for table in s.mean_table.split("; "):
			severity = data[(data.doc_id == s.doc_id) & (data.table_or_figure.str.upper() == table.upper())
				& (data.variable_standardized == "severity_pct") 
				# Sites without or with symptoms at the first spray are subsets of the all-sites column
				& ~data.trial_label.fillna("").str.contains("Sem sintomas|Com sintomas")]
			check = severity[severity.treatment_type == "control"]
			if len(check) != 1:
				continue
			check_severity = float(check.value.iloc[0])
			for _, r in severity[severity.active_ingredient_or_agent.notna()].iterrows():
				rows.append({"season": s.season, "table": table, "ingredients": " + ".join(sorted(ingredient_names(r.active_ingredient_or_agent))),
					"control_pct_computed": round(100 * (1 - float(r.value) / check_severity), 1), "severity": float(r.value),
					"check_severity": check_severity, "treatment_as_printed": r.treatment, "record_id": r.record_id})
	table = pd.DataFrame(rows)
	table = table.groupby(["ingredients", "season"], as_index=False).agg(control_pct_computed=("control_pct_computed", "mean"),
		n_formulations=("record_id", "size"), record_ids=("record_id", "; ".join))
	table["control_pct_computed"] = table.control_pct_computed.round(1)
	table.to_csv(HERE / "control_from_severity.csv", index=False)
	for ingredients in ("tebuconazol", "azoxistrobina + ciproconazol", "ciproconazol + trifloxistrobina", "ciproconazol", "epoxiconazol + piraclostrobina"):
		g = table[table.ingredients == ingredients]
		print(f"{ingredients}: " + "  ".join(f"{season} {value:.0f}" for season, value in zip(g.season, g.control_pct_computed)))


if __name__ == "__main__":
	main()
