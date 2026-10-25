# Compare the two independent transcriptions (A/*.json and B/*.json, schema v2: {records, tables})
# Output: method/diff.csv, or method/diff_<doc_id>.csv when doc ids are given, with every field
# disagreement and every record present on one side only
# Copied from spodoptera-milho/blind/compare.py; changed only the paths, the {records, tables}
# loading and the compared fields (schema v2 split location/affiliation and n_or_reps)
#
# Matching: records are grouped by (doc_id, page, table_or_figure). Inside a group each A/B pair
# gets a score from treatment, variable and position tokens (numbers, dates) plus small bonuses
# for same value and same crop_stage; pairs are taken greedily from the best score down.
# The value is only a tie-breaker, so a wrong value in A still pairs with the right cell in B
#
# Usage: python compare.py [doc_id ...]   (paths are relative to this file)
import csv
import difflib
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A_DIR = os.path.join(ROOT, "A")
B_DIR = os.path.join(ROOT, "B")

# value first (compare_pair treats it apart); then every value-bearing or context field of schema v2.
# doc_id, page and table_or_figure are the group key; notes is free text and is not compared
COMPARED_FIELDS = ["value", "unit", "significance_letter", "statistic", "statistic_stated", "is_marginal",
	"treatment", "treatment_code", "treatment_type", "variable", "variable_standardized",
	"trial_label", "location", "affiliation", "season_or_year", "sowing_date", "cultivar",
	"crop_stage", "crop_stage_refers_to", "active_ingredient_or_agent", "dose_and_unit", "dose_source_page",
	"application_method", "application_stages", "n_applications", "n_reps", "design_notes", "source_inconsistency"]
MIN_PAIR_SCORE = 3.0


def norm(text):
	if text is None:
		return ""
	text = unicodedata.normalize("NFKD", str(text))
	text = "".join(ch for ch in text if not unicodedata.combining(ch))
	text = text.lower().replace("±", " pm ")
	return re.sub(r"[^a-z0-9]+", " ", text).strip()


def norm_unit(text):
	# kg/ha, Kg ha-1 and kg.ha-1 are the same unit
	text = norm(text).replace(" 1", " ")
	return re.sub(r"\s+", "", text)


def number_tokens(text):
	return set(re.findall(r"\d+(?:[.,]\d+)?", text or ""))


def similarity(a, b):
	a, b = norm(a), norm(b)
	if not a and not b:
		return 1.0
	if a == b:
		return 1.0
	tokens_a, tokens_b = set(a.split()), set(b.split())
	jaccard = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))
	ratio = difflib.SequenceMatcher(None, a, b).ratio()
	return max(jaccard, ratio)


def position_text(record):
	return " ".join(str(record.get(k) or "") for k in ("treatment", "variable", "crop_stage", "trial_label", "cultivar"))


def pair_score(a, b):
	score = 3.0 * similarity(a["treatment"], b["treatment"])
	score += 3.0 * similarity(a["variable"], b["variable"])
	numbers_a, numbers_b = number_tokens(position_text(a)), number_tokens(position_text(b))
	if numbers_a or numbers_b:
		score += 2.0 * len(numbers_a & numbers_b) / max(1, len(numbers_a | numbers_b))
	else:
		score += 2.0
	if norm(a["treatment"]) == norm(b["treatment"]):
		score += 1.0
	# Schema v2 treatment_code: the annex rows print only the code (TRAT 3), so one side may write
	# "3" and the other the name from the products table; the same printed code is strong evidence
	if norm(a.get("treatment_code")) and norm(a.get("treatment_code")) == norm(b.get("treatment_code")):
		score += 3.0
	if a.get("value") == b.get("value"):
		score += 0.75
	if norm(a.get("crop_stage")) == norm(b.get("crop_stage")):
		score += 0.25
	return score


def text_field_differs(field, value_a, value_b):
	if field == "unit":
		return norm_unit(value_a) != norm_unit(value_b)
	return norm(value_a) != norm(value_b)


def site_number(record):
	# Cooperative circulars print one small table per site inside the same annex page ("3. Fundação MS"),
	# all with the same TRAT 1..15 rows, so the site number in trial_label is part of the group key
	# A separator ";" or " - " goes between the protocol name and the site ("Protocolo X - 1. Desafios agro")
	match = re.search(r"(?:^|; | - )(\d+)\. ", record.get("trial_label") or "")
	return int(match.group(1)) if match else 0


def load(directory, name):
	with open(os.path.join(directory, name), encoding="utf-8") as handle:
		data = json.load(handle)
	# Schema v2 wraps the records in {records, tables}
	return data["records"] if isinstance(data, dict) else data


def compare_pair(a, b):
	rows = []
	value_a, value_b = a.get("value"), b.get("value")
	printed_a, printed_b = (a.get("value_as_printed") or "").strip(), (b.get("value_as_printed") or "").strip()
	if value_a != value_b:
		rows.append(("value", value_a, value_b, printed_a, printed_b))
	elif printed_a.replace(" ", "") != printed_b.replace(" ", ""):
		rows.append(("value_as_printed", value_a, value_b, printed_a, printed_b))
	for field in COMPARED_FIELDS[1:]:
		if text_field_differs(field, a.get(field), b.get(field)):
			rows.append((field, a.get(field), b.get(field), printed_a, printed_b))
	return rows


def kind_of(field, value_a, value_b):
	if field in ("value", "value_as_printed", "significance_letter"):
		return "value_mismatch" if field != "significance_letter" else "letter_mismatch"
	if value_a in (None, "") or value_b in (None, ""):
		return "null_vs_text"
	if number_tokens(str(value_a)) != number_tokens(str(value_b)):
		return "numbers_differ"
	return "wording"


def main(doc_ids):
	if doc_ids:
		names = [doc_id + ".json" for doc_id in doc_ids]
		out_path = os.path.join(HERE, "diff_%s.csv" % "_".join(doc_ids)) if len(doc_ids) == 1 else os.path.join(HERE, "diff_selected.csv")
	else:
		names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(A_DIR, "*.json")) if os.path.exists(os.path.join(B_DIR, os.path.basename(p))))
		out_path = os.path.join(HERE, "diff.csv")
	header = ["diff_id", "doc_id", "page", "table_or_figure", "kind", "field", "a_index", "b_index",
		"treatment_a", "treatment_b", "variable_a", "variable_b", "a_value", "b_value",
		"value_as_printed_a", "value_as_printed_b", "match_score"]
	out_rows = []
	totals = {"a": 0, "b": 0, "pairs": 0}
	for name in names:
		records_a = load(A_DIR, name)
		records_b = load(B_DIR, name)
		totals["a"] += len(records_a)
		totals["b"] += len(records_b)
		groups = {}
		for side, records in (("a", records_a), ("b", records_b)):
			for index, record in enumerate(records):
				key = (record["page"], norm(record["table_or_figure"]), site_number(record))
				groups.setdefault(key, {"a": [], "b": []})[side].append(index)
		for key in sorted(groups, key=lambda k: (k[0], k[1])):
			indexes_a, indexes_b = groups[key]["a"], groups[key]["b"]
			candidates = []
			for ia in indexes_a:
				for ib in indexes_b:
					score = pair_score(records_a[ia], records_b[ib])
					if score >= MIN_PAIR_SCORE:
						candidates.append((score, ia, ib))
			# Best pairs first; ties keep file order so parallel tables line up
			candidates.sort(key=lambda c: (-c[0], c[1], c[2]))
			used_a, used_b, pairs = set(), set(), []
			for score, ia, ib in candidates:
				if ia in used_a or ib in used_b:
					continue
				used_a.add(ia)
				used_b.add(ib)
				pairs.append((score, ia, ib))
			totals["pairs"] += len(pairs)
			for score, ia, ib in sorted(pairs, key=lambda p: p[1]):
				a, b = records_a[ia], records_b[ib]
				for field, value_a, value_b, printed_a, printed_b in compare_pair(a, b):
					out_rows.append([name[:-5], a["page"], a["table_or_figure"], kind_of(field, value_a, value_b), field,
						ia, ib, a["treatment"], b["treatment"], a["variable"], b["variable"], value_a, value_b,
						printed_a, printed_b, round(score, 2)])
			for ia in indexes_a:
				if ia not in used_a:
					a = records_a[ia]
					out_rows.append([name[:-5], a["page"], a["table_or_figure"], "only_in_A", "record", ia, "",
						a["treatment"], "", a["variable"], "", a["value"], "", a["value_as_printed"], "", ""])
			for ib in indexes_b:
				if ib not in used_b:
					b = records_b[ib]
					out_rows.append([name[:-5], b["page"], b["table_or_figure"], "only_in_B", "record", "", ib,
						"", b["treatment"], "", b["variable"], "", b["value"], "", b["value_as_printed"], ""])
	with open(out_path, "w", encoding="utf-8", newline="") as handle:
		writer = csv.writer(handle)
		writer.writerow(header)
		for number, row in enumerate(out_rows, 1):
			writer.writerow(["D%04d" % number] + row)
	print("A records %d, B records %d, matched pairs %d, diff rows %d" % (totals["a"], totals["b"], totals["pairs"], len(out_rows)))


def self_check():
	assert norm_unit("Kg ha-1") == norm_unit("kg/ha")
	assert norm("Labóratório") == "laboratorio"
	assert number_tokens("Aug,7 (4)") == {"7", "4"}
	assert site_number({"trial_label": "Experimento com fungicidas registrados; 18. Fundação Mato Grosso"}) == 18
	assert site_number({"trial_label": "Protocolo FUNGICIDAS REGISTRADOS - 1. Desafios agro, Chapadão do Sul, MS"}) == 1
	assert site_number({"trial_label": "19. TAGRO"}) == 19 and site_number({"trial_label": None}) == 0
	a = {"treatment": "Untreated", "variable": "Infestation Aug,7 (4)", "crop_stage": None, "value": 1.0}
	b_right = {"treatment": "Untreated", "variable": "Infestation (mean) Aug,7 (4)", "crop_stage": None, "value": 2.0}
	b_wrong = {"treatment": "Untreated", "variable": "Infestation (mean) Aug,9 (6)", "crop_stage": None, "value": 1.0}
	assert pair_score(a, b_right) > pair_score(a, b_wrong)


if __name__ == "__main__":
	self_check()
	if "--check" not in sys.argv:
		main([arg for arg in sys.argv[1:] if not arg.startswith("--")])
