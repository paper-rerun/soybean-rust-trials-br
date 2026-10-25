# Asian soybean rust control trials in Brazil

5,836 trial results on the control of Asian soybean rust (*Phakopsora pachyrhizi*, "ferrugem-asiática da soja") in Brazil, taken from the tables of 20 open-access Embrapa publications (2008 to 2023). Each row is one number exactly as printed: a treatment, its dose and timing, where and when it was tested, what was measured and the value, with the page and table it came from.

Asian soybean rust is the most damaging soybean disease in Brazil, and fungicides lose efficacy over time as the fungus adapts. Embrapa's national network of cooperative trials has measured that every season for almost two decades, but the results sit in yearly technical circulars as PDF tables. This dataset makes 20 of those publications searchable and comparable across seasons.

Part of [Paper Rerun](https://paper-rerun.github.io), in its Open Tables line. The work was done by AI agents on a home computer and reviewed by a human before publication.

## What is in it

| | |
|---|---|
| Publications | 20 (Alice and Infoteca-e, Embrapa's open repositories): 5 national summaries of the cooperative fungicide trials (2009/10 to 2022/23), 7 local or regional fungicide trials, 3 on spray timing, number of sprays and seed treatment, 2 on cultivars, 3 on cultural management and nutrition |
| Records | 5,836 |
| Main measures | rust severity (2,116), yield (1,662), control efficacy (1,327), yield reduction (198), AUDPC (98), grain weight (88) |

Files:
- `data/soybean_rust_trials.csv`: the dataset, one record per printed value. Columns are described in `method/schema.json`.
- `data/sources.csv`: the 20 publications, with authors, record link and licence notice.
- `qa/decisions.csv`: every disagreement between the two independent transcriptions and how it was settled against the PDF (19,494 decisions, with page).
- `method/`: the schema, the comparison script and the merge script.

The `origin` column says where each record came from: `both` (the two transcriptions agreed), `A` or `B` (one transcription was right and the other was corrected), or `corrected` (both needed a fix). `source_inconsistency` marks 844 records where the publication contradicts itself (for example a table and the text giving different places or dates).

## How it was made

1. **Collection.** An agent searched Embrapa's open repositories for publications with quantitative trial tables on this topic, downloaded 20 and recorded 68 candidates it did not take, with the reason.
2. **Two independent transcriptions.** Two agents per publication transcribed every table cell on the topic into a fixed schema, without seeing each other's work, copying numbers exactly as printed and accounting for every data cell of every table.
3. **Comparison and adjudication.** A script paired the two transcriptions and listed every disagreement and every value present in only one of them. Each one was settled by checking the PDF, with the page as evidence.

## How accurate it is

- **Numbers:** the two transcriptions agreed on 5,832 of 5,834 values and significance letters (99.97%). The two differences were a decimal separator; the number was right.
- **Context:** this is where single transcriptions fail. Treatment timing, codes, places and how a percentage was computed are often stated once and apply to a whole table. One transcription alone was fully correct on 22% of records, the other on 81%. Every disagreement was settled against the PDF, so the dataset does not depend on either one alone.
- **Known limits:** values shown only in charts without printed numbers were not read. Percentages "relative to the untreated check" are marked as such, not as means. Licences of four journal articles in the set still need a final check; the numbers are facts and are cited row by row.

## Licence and citation

- The dataset (the CSV files, schema and scripts) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please cite the original publications listed in `data/sources.csv` as well as this dataset.
- The publications are not redistributed. Embrapa's repositories show a CC BY-NC-ND 4.0 notice; journal articles keep their journals' licences. Notes quote the source text only in short fragments.

Errors or missing trials: please [open an issue](https://github.com/paper-rerun/soybean-rust-trials-br/issues).

## How this dataset was made

This dataset was built by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No value was estimated or typed by hand: each one was transcribed from the source PDF twice, independently, and every disagreement was checked against the page. The method and scripts are in `method/`. How the wider project works: https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contact: Filipe Tessaro, via issues on this repository.
