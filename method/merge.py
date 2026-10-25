# Merge the adjudicated documents into dataset.csv and qa/decisions.csv, and print the round numbers for RODADA.md
# Usage: python method/merge.py   (paths are relative to the ferrugem-soja folder)
import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPARED_FIELD_COUNT = 28  # COMPARED_FIELDS in method/compare.py, value and value_as_printed count as one
MAX_QUOTE_WORDS = 15
LICENSE_REPOSITORY = "CC BY-NC-ND 4.0 (aviso geral do repositório {repo}, não é licença do item)"

# Quotes in notes: 'x', "x", ‘x’, “x”. The single quote must not touch a letter, so "B's" is not a quote
QUOTE_PATTERN = re.compile(r"(?<![\w])'([^']{3,}?)'(?![\w])|\"([^\"]{3,}?)\"|‘([^’]+)’|“([^”]+)”")

# Decision rows that are not about a record field
NON_RECORD_KINDS = {"inventory", "inventory_only_in_A", "only_in_A", "only_in_B", "checked_no_diff"}

# Column names that mean the same thing in different adjudicators' files
DECISION_COLUMN_RENAMES = {"page_evidence": "evidence_page", "treatment_a": "treatment", "variable_a": "variable"}


def ShortenQuote(match):
	quoted_text = next(group for group in match.groups() if group)
	words = quoted_text.split()
	if len(words) <= MAX_QUOTE_WORDS:
		return match.group(0)
	# Keep the start and the end, where the number usually is
	shortened = " ".join(words[:7]) + " (...) " + " ".join(words[-6:])
	opening, closing = match.group(0)[0], match.group(0)[-1]
	return opening + shortened + closing


def ShortenNotes(notes):
	if not notes:
		return notes
	return QUOTE_PATTERN.sub(ShortenQuote, notes)


def BuildCitation(document):
	authors = "; ".join(document["authors"]).rstrip(".")
	title = document["title"].rstrip(".")
	return f"{authors}. {title}. {document['citation']} Disponível em: {document['record_url']}"


def BuildLicense(document):
	license_text = LICENSE_REPOSITORY.format(repo=document["repository"])
	if document.get("publisher_copyright_in_pdf"):
		license_text += "; o PDF imprime: " + " / ".join(document["publisher_copyright_in_pdf"])
	return license_text


def DecisionIds(record):
	for key in ("decision_ids", "adjudication_ids", "adjudication"):
		ids = record.get(key)
		if isinstance(ids, list):
			return "; ".join(str(each_id) for each_id in ids)
		if isinstance(ids, str):
			return ids
	return ""


def RecordKey(row, side_index_column):
	index = (row.get(side_index_column) or "").strip()
	if index:
		return ("index", index)
	# godoy2008 has no a_index/b_index; the printed cell identifies the record
	return ("cell", row.get("page"), row.get("table_or_figure"), row.get("treatment_code"), row.get("treatment"), row.get("variable"))


def IsRecordFieldRow(row):
	if row.get("kind") in NON_RECORD_KINDS:
		return False
	field = row.get("field") or ""
	if field.startswith("tables") or field == "notes":
		return False
	if row.get("diff_id", "").startswith("T") or row.get("decision_id", "").startswith("T"):
		return False
	return True


def main():
	schema = json.load(open(os.path.join(ROOT, "schema.json"), encoding="utf-8"))
	record_fields = schema["$defs"]["record"]["required"]
	sources = json.load(open(os.path.join(ROOT, "sources.json"), encoding="utf-8"))
	documents_by_id = {document["id"]: document for document in sources["documents"]}

	dataset_rows = []
	stats = defaultdict(dict)
	shortened_notes = 0
	for adjudicated_path in sorted(glob.glob(os.path.join(ROOT, "adjudicated", "*.json"))):
		doc_id = os.path.basename(adjudicated_path)[:-5]
		document = documents_by_id[doc_id]
		records = json.load(open(adjudicated_path, encoding="utf-8"))["records"]
		citation, license_text = BuildCitation(document), BuildLicense(document)
		for record_number, record in enumerate(records, start=1):
			# Every schema field must be there, and the record must belong to this document
			assert all(field in record for field in record_fields), (doc_id, record_number)
			assert record["doc_id"] == doc_id
			row = {"record_id": f"{doc_id}#{record_number:04d}"}
			for field in record_fields:
				row[field] = record[field]
			new_notes = ShortenNotes(record["notes"])
			if new_notes != record["notes"]:
				shortened_notes += 1
			row["notes"] = new_notes
			# source_inconsistency also quotes the text; same limit
			row["source_inconsistency"] = ShortenNotes(record["source_inconsistency"])
			row["origin"] = record.get("origin")
			row["decision_ids"] = DecisionIds(record)
			row["citation"] = citation
			row["license"] = license_text
			dataset_rows.append(row)
		stats[doc_id]["final"] = len(records)

	columns = ["record_id"] + record_fields + ["origin", "decision_ids", "citation", "license"]
	with open(os.path.join(ROOT, "dataset.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=columns)
		writer.writeheader()
		for row in dataset_rows:
			writer.writerow({key: ("" if value is None else value) for key, value in row.items()})

	# Concatenate the decision files, union of columns, with the few renamed columns aligned
	decision_rows = []
	decision_columns = ["source_file"]
	for decisions_path in sorted(glob.glob(os.path.join(ROOT, "adjudicated", "*_decisions.csv"))):
		for row in csv.DictReader(open(decisions_path, encoding="utf-8-sig", newline="")):
			row = {DECISION_COLUMN_RENAMES.get(key, key): value for key, value in row.items()}
			row["source_file"] = "adjudicated/" + os.path.basename(decisions_path)
			for key in row:
				if key not in decision_columns:
					decision_columns.append(key)
			decision_rows.append(row)
	os.makedirs(os.path.join(ROOT, "qa"), exist_ok=True)
	with open(os.path.join(ROOT, "qa", "decisions.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=decision_columns)
		writer.writeheader()
		writer.writerows(decision_rows)

	# Per side: field errors, records with a wrong field, records present
	for doc_id in stats:
		a_records = json.load(open(os.path.join(ROOT, "A", doc_id + ".json"), encoding="utf-8"))["records"]
		b_records = json.load(open(os.path.join(ROOT, "B", doc_id + ".json"), encoding="utf-8"))["records"]
		stats[doc_id]["a_records"], stats[doc_id]["b_records"] = len(a_records), len(b_records)
		a_wrong_records, b_wrong_records = set(), set()
		a_field_errors = b_field_errors = 0
		diff_rows_on_pairs = 0
		for row in decision_rows:
			if row["doc_id"] != doc_id or not IsRecordFieldRow(row):
				continue
			diff_rows_on_pairs += 1
			if row["decision"] == "B_right":
				a_field_errors += 1
				a_wrong_records.add(RecordKey(row, "a_index"))
			elif row["decision"] == "A_right":
				b_field_errors += 1
				b_wrong_records.add(RecordKey(row, "b_index"))
		stats[doc_id].update(a_field_errors=a_field_errors, b_field_errors=b_field_errors,
			a_wrong_records=len(a_wrong_records), b_wrong_records=len(b_wrong_records), diff_rows=diff_rows_on_pairs)

	# Required base: final records minus the optional text records kept from one side only (godoy2023, 2 from A)
	optional_kept = {"godoy2023-cooperativos-2223-ct195": 2}
	totals = Counter()
	print("doc_id;final;A;B;A_field_err;B_field_err;A_wrong_rec;B_wrong_rec")
	for doc_id, doc_stats in sorted(stats.items()):
		required = doc_stats["final"] - optional_kept.get(doc_id, 0)
		a_required = min(doc_stats["a_records"], required)
		b_required = min(doc_stats["b_records"], required)
		totals.update(final=doc_stats["final"], required=required, a_present=a_required, b_present=b_required,
			a_field_errors=doc_stats["a_field_errors"], b_field_errors=doc_stats["b_field_errors"],
			a_wrong_records=doc_stats["a_wrong_records"], b_wrong_records=doc_stats["b_wrong_records"],
			diff_rows=doc_stats["diff_rows"], a_records=doc_stats["a_records"], b_records=doc_stats["b_records"])
		print(f"{doc_id};{doc_stats['final']};{doc_stats['a_records']};{doc_stats['b_records']};{doc_stats['a_field_errors']};"
			f"{doc_stats['b_field_errors']};{doc_stats['a_wrong_records']};{doc_stats['b_wrong_records']}")
	print(dict(totals))
	print("shortened notes:", shortened_notes)
	print("decision rows:", len(decision_rows), Counter(row["decision"] for row in decision_rows))
	print("origin:", Counter(row["origin"] for row in dataset_rows))
	print("variable_standardized:", Counter(row["variable_standardized"] for row in dataset_rows).most_common())
	print("treatment_type:", Counter(row["treatment_type"] for row in dataset_rows).most_common())
	print("statistic:", Counter(row["statistic"] for row in dataset_rows).most_common())
	for field in ("crop_stage", "dose_and_unit", "season_or_year", "sowing_date", "location", "cultivar", "n_reps", "significance_letter", "application_stages", "affiliation", "trial_label"):
		empty = sum(1 for row in dataset_rows if row[field] in (None, ""))
		print(f"null {field}: {empty} ({100 * empty / len(dataset_rows):.1f}%)")
	print("source_inconsistency filled:", sum(1 for row in dataset_rows if row["source_inconsistency"]))
	print("from text:", sum(1 for row in dataset_rows if row["table_or_figure"] == "text"))

	# Self-check: the dataset holds every adjudicated record once, and no note quote is longer than the limit
	assert len(dataset_rows) == sum(doc_stats["final"] for doc_stats in stats.values())
	assert len({row["record_id"] for row in dataset_rows}) == len(dataset_rows)
	for row in dataset_rows:
		for match in QUOTE_PATTERN.finditer((row["notes"] or "") + " " + (row["source_inconsistency"] or "")):
			assert len(next(group for group in match.groups() if group).split()) <= MAX_QUOTE_WORDS


if __name__ == "__main__":
	main()
