# Fungicide efficacy across seasons

Exploratory. Takes the national mean table of each cooperative-trial summary and asks how the control efficacy of the same product, at the same dose, changes from season to season.

- `series.csv`: every season from 2003/04 to 2025/26, the publication that holds its national summary, its `doc_id` and the label of the mean table. `status` is `in_dataset` for 22 seasons and `not_published` for 2007/08 (see the caveats).
- `efficacy_over_time.py`: builds the series and fits, for each product tested in 3 or more seasons, a straight line plus a season effect shared by all products, so a harder season does not count as a fall in each product. Output in `efficacy_by_season.csv` and `efficacy_trends.csv`, with the record ids behind every value; printed summary in `run.txt`.
- `control_from_severity.py`: control computed as 100 x (1 - severity / check severity) for the three seasons whose mean table prints severity but no control column (2003/04, 2005/06, 2006/07). Output in `control_from_severity.csv` and `run_control_from_severity.txt`.
- `efficacy_over_time_original.py`: the version published with 5 seasons, kept to show what changed. Its output on the full data is in `*_original_script.csv` and `run_original_script.txt`.

Run from the repository root with `python -I analysis/efficacy_over_time.py` and `python -I analysis/control_from_severity.py` (both need pandas).

## What changed in the script for the full series

The 5-season script runs on the full data without errors, but gets four things wrong that only show up with all seasons. The current `efficacy_over_time.py` fixes them and checks the fixes with asserts before it runs:
- 2020/21 prints "picoxistrobina & ciproconazol", and the old script only split ingredients on "+", so that season dropped out;
- 2004/05 is written in English ("azoxystrobin", "tebuconazole") and matched nothing;
- 2008/09 has three control columns (all sites, sites without symptoms and sites with symptoms at the first spray). Only the first is the national mean; the old script averaged the three;
- the dose did not follow its ingredient when the names were sorted, so "tebuconazol + clorotalonil 125 + 1125" and "clorotalonil + tebuconazol 1125 + 125" were two products. This was already in the published 5-season output.

With the fixes: 19 seasons with printed control, 96 products, 31 tested in 3 or more seasons (7 in the first look).

## Results (22 of 23 seasons)

Per product, in percentage points of control per year, after the season effect (`efficacy_trends.csv`):
- **27 of the 31 products lose efficacy**, 18 of them by 2 points a year or more.
- **Site-specific only (24 products): median -4.1 a year, 23 of 24 falling.** The fastest are the strobilurin + triazole mixtures tested between 2008/09 and 2014/15: metconazol + piraclostrobina -11.3 (78% in 2009/10, 27% in 2013/14), azoxistrobina + flutriafol -11.2, epoxiconazol + piraclostrobina -8.2 (68% to 26% from 2008/09 to 2013/14), azoxistrobina + tebuconazol -8.0. Then the carboxamides: azoxistrobina + benzovindiflupir -6.9 (86% in 2013/14, 28% in 2022/23), benzovindiflupir + picoxistrobina -5.9, epoxiconazol + fluxapiroxade + piraclostrobina -5.1, fluxapiroxade + piraclostrobina -3.0, bixafem + protioconazol + trifloxistrobina -2.1.
- **With a multisite fungicide (clorotalonil or mancozebe, 7 products): median -0.1 a year**, from -2.3 to +2.3, 4 of 7 falling and 3 rising. All entered from 2015/16 on. Clorotalonil + tebuconazol (1,125 + 125 g a.i./ha) stayed between 58% and 71% in 9 seasons in a row, 2017/18 to 2025/26.
- **The triazoles fell before the 5-season series started.** From the control computed from severity, tebuconazol (100 g) was at 90% in 2003/04 and 2004/05, 77% in 2005/06, 62% in 2006/07, 42% in 2008/09 and 28% in 2009/10: about 60 points in 6 seasons, close to 10 a season. After that it stayed between 15% and 41% until it left the network in 2016/17. Azoxistrobina + ciproconazol fell in two steps: 90% in 2004/05, around 70% from 2006/07 to 2010/11, then down again from 2013/14 (46%) to 28% in 2017/18.

### Against the first look (5 seasons)

| Product | 5 seasons (pp/year) | Full series (pp/year) | Seasons | From / to |
|---|---:|---:|---:|---|
| azoxistrobina + benzovindiflupir (60 + 30) | -7.8 | -6.9 | 9 | 86% in 2013/14 / 28% in 2022/23 |
| azoxistrobina + ciproconazol (60 + 24) | -5.2 | -4.1 (-5.2 without 2004/05) | 11 | 90% in 2004/05 / 28% in 2017/18 |
| ciproconazol + picoxistrobina (24 + 60) | -3.4 | -2.9 | 12 | 81% in 2009/10 / 48% in 2020/21 |
| bixafem + protioconazol + trifloxistrobina | -2.8 | -2.1 | 11 | 80% in 2013/14 / 62% in 2023/24 |
| ciproconazol (30) | -1.2 | -1.6 | 8 | 39% in 2009/10 / 23% in 2016/17 |
| protioconazol + trifloxistrobina (70 + 60) | -1.0 | -1.3 | 11 | 78% in 2010/11 / 67% in 2020/21 |
| tebuconazol (100) | -0.5 | -4.1 (-2.1 without 2004/05) | 10 | 90% in 2004/05 / 18% in 2016/17 |

The first look holds: the 7 products still fall, in nearly the same order. Slopes got a little smaller with more points, as expected going from 3 seasons to 9 or 12. The exception is tebuconazol. With 5 seasons it looked stable because the series started in 2009/10, after the fall. A straight line is a poor fit for it: it fell fast and then stopped, it does not lose 4 points a year.

## Caveats

- **National means only.** Variation between sites is in the per-site annexes (2020/21 on) and is not used here. A fall in the mean can be a fall in one region.
- **Products leave the network when they fail, and new ones come in high.** Single triazoles left in 2016/17, the older mixtures around 2014/15. That cuts the tail of each curve.
- **The season effect is estimated from a changing set of products.** The 2004/05 effect (+13.7 points) rests on 3 products, and on its own it moves the tebuconazol slope from -2.1 to -4.1. There is a 3-year gap between 2004/05 and 2008/09.
- **The protocol changed.** Up to 2005/06, two fixed sprays (R2 and R5.1, or R3 and R5.1); from 2008/09 to 2016/17, the first at R1/R2 and then by interval; from 2018/19, the first at 45 to 50 days, before flowering, and four sprays in 13 of the 14 trials of 2023/24. Starting earlier and spraying more pushes control up, so the real loss of the long-running products may be larger than measured.
- **Stable multisite mixtures cover 4 to 9 seasons, from 2015/16.** Too early to say they do not lose efficacy; they had not lost it by 2025/26.
- **Control computed from severity** (2003/04, 2005/06, 2006/07) is derived, not printed, and does not go into the fit. On the 283 products of seasons that print both, it is within 2.1 points of the printed value (mean 0.3). In those three seasons the dose is printed only as commercial product per hectare, so products are matched by active ingredient, and two formulations of the same ingredient in one table count as their mean.
- **2007/08 is missing.** No national summary was found. Circular Técnica 69 cites the summaries of 2003/04, 2004/05 and 2006/07 and none for 2007/08, and the minutes of the 2008 meeting (Documentos 310) ask for the network trials to be resumed. So the network apparently did not run that season. This is an inference, not a confirmation.
- These are national means of trials, not field recommendations.

## Adding a season

1. Transcribe the publication into `data/soybean_rust_trials.csv` with the same method and schema as the rest of the dataset.
2. In `series.csv`, set `status` to `in_dataset`, fill `doc_id`, and put in `mean_table` the label of the table with the mean efficacy over all sites (for example `Tabela 3`).
3. Run `python -I analysis/efficacy_over_time.py`.
