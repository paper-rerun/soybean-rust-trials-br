# Fungicide efficacy across seasons

Exploratory. Takes the national mean table of each cooperative-trial summary and asks how the control efficacy of the same product, at the same dose, changes from season to season.

- `series.csv`: every season from 2003/04 to 2025/26, the publication that holds its national summary, and whether it is already in the dataset. `status` is `in_dataset`, `to_transcribe` (publication found, not transcribed yet) or `to_find`.
- `efficacy_over_time.py`: builds the series and fits, for each product tested in 3 or more seasons, a straight line plus a season effect shared by all products, so a harder season does not count as a fall in each product.
- `efficacy_by_season.csv`, `efficacy_trends.csv`: its outputs, with the record ids behind every value.

## Adding a season

1. Transcribe the publication into `data/soybean_rust_trials.csv` with the same method and schema as the rest of the dataset.
2. In `series.csv`, set `status` to `in_dataset`, fill `doc_id`, and put in `mean_table` the label of the table with the mean efficacy over all sites (for example `Tabela 3`).
3. Run `python -I analysis/efficacy_over_time.py`.

## First results (5 seasons)

With 5 of the 23 seasons, 7 products were tested in at least 3 of them, all at an unchanged dose. All 7 lose efficacy. The steepest is azoxistrobina + benzovindiflupir (60 + 30 g a.i./ha): 76% control in 2015/16, 28% in 2022/23, about 7.8 points a year once the season effect is taken out. Strobilurin + triazole mixtures that started near 80% in 2009/10 fell by 3 to 5 points a year. These are 5 seasons and only the national means, so the trends are a first look, not a result; the full series is what would make them one.
