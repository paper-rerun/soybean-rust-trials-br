# Asian soybean rust control trials in Brazil

Versão em português: [README.pt-BR.md](README.pt-BR.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23631775.svg)](https://doi.org/10.5281/zenodo.23631775)

17,845 trial results on the control of Asian soybean rust (*Phakopsora pachyrhizi*, "ferrugem-asiática da soja") in Brazil, taken from the tables of 37 open-access Embrapa publications (2005 to 2026). Each row is one number exactly as printed: a treatment, its dose and timing, where and when it was tested, what was measured and the value, with the page and table it came from.

Asian soybean rust is the most damaging soybean disease in Brazil, and fungicides lose efficacy over time as the fungus adapts. Embrapa's national network of cooperative trials has measured that every season since 2003/04, but the results sit in yearly technical circulars as PDF tables. This dataset holds the national summary of 22 of the 23 seasons from 2003/04 to 2025/26, so the same product can be followed across two decades. The missing season is 2007/08: no national summary was found, and the 2008 network meeting asked for the trials to be resumed, so the network apparently did not run that season.

Part of [Paper Rerun](https://paper-rerun.github.io), in its Open Tables line. The work was done by AI agents on a home computer and reviewed by a human before publication.

## What is in it

| | |
|---|---|
| Publications | 37 (Alice and Infoteca-e, Embrapa's open repositories): 22 national summaries of the cooperative fungicide trials (2003/04 to 2025/26, all seasons but 2007/08), 7 local or regional fungicide trials, 3 on spray timing, number of sprays and seed treatment, 2 on cultivars, 3 on cultural management and nutrition |
| Records | 17,845 |
| Main measures | rust severity (6,343), yield (4,890), control efficacy (4,315), yield reduction (641), AUDPC (98), grain weight (88) |

Files:
- `data/soybean_rust_trials.csv`: the dataset, one record per printed value. Columns are described in `method/schema.json`.
- `data/sources.csv`: the 37 publications, with authors, record link and licence notice.
- `qa/decisions.csv`: every disagreement between the two independent transcriptions and how it was settled against the PDF (46,812 decisions, with page).
- `method/`: the schema, the comparison script and the merge script. The schema is now v2.1: the transcription format gained a per-table declaration of the context a table passes to its records (timing, place, number of sprays and so on). The record columns did not change.
- `analysis/`: the efficacy series across seasons, see below.

The `origin` column says where each record came from: `both` (the two transcriptions agreed), `A` or `B` (one transcription was right and the other was corrected), or `corrected` (both needed a fix). `source_inconsistency` marks 4,017 records where the publication contradicts itself (for example a table and the text giving different places, dates or doses).

## Efficacy over time

`analysis/` follows the control efficacy of the same product, at the same dose, through the national mean tables, with a season effect taken out so a hard season does not count as a fall in every product. With 22 seasons, 31 products were tested in 3 or more of them.

- The 7 products of the first look (5 seasons) keep losing efficacy, in nearly the same order. Overall, 27 of the 31 products fall.
- Tebuconazol (100 g a.i./ha) went from 90% control in 2003/04 to 28% in 2009/10, about 10 points a season, then stayed at a floor of 15% to 40% until it left the network in 2016/17.
- Azoxistrobina + benzovindiflupir (60 + 30 g) went from 86% in 2013/14 to 28% in 2022/23.
- Mixtures with a multisite fungicide (clorotalonil, mancozebe), tested since 2015/16, show no loss so far: median -0.1 points a year over 7 products. Clorotalonil + tebuconazol stayed between 58% and 71% for 9 seasons.

These are national means of trials, not field recommendations. Products leave the network when they fail, the spray protocol changed over the years, and the multisite mixtures cover 4 to 9 seasons only. The caveats and the full table are in `analysis/README.md`.

## How it was made

1. **Collection.** An agent searched Embrapa's open repositories for publications with quantitative trial tables on this topic, downloaded 20 and recorded 68 candidates it did not take, with the reason. A second search for the remaining seasons of the cooperative trials found 17 more national summaries.
2. **Two independent transcriptions.** Two agents per publication transcribed every table cell on the topic into a fixed schema, without seeing each other's work, copying numbers exactly as printed and accounting for every data cell of every table.
3. **Comparison and adjudication.** A script paired the two transcriptions and listed every disagreement and every value present in only one of them. Each one was settled by checking the PDF, with the page as evidence.

## How accurate it is

- **Blind reread (November 2026):** a third reader, blind to the published data, read 100 random records of this dataset again from the PDF: none of them had an error. Across the 13 Open Tables datasets (1,297 records) the rate was 1.5 value errors and 10 context errors per 1,000 records, and no number was misread ([details](https://github.com/paper-rerun/paper-rerun/blob/main/measurements/blind-reread-2026-11.md)).
- **Numbers:** in the first 20 publications the two transcriptions agreed on 5,832 of 5,834 values and significance letters (99.97%); the two differences were a decimal separator and the number was right. In the 17 summaries added later, no number was misread in 12,003 pairs.
- **Context:** this is where single transcriptions fail. Treatment timing, codes, places and how a percentage was computed are often stated once and apply to a whole table. In the first 20 publications one transcription alone was fully correct on 22% of records, the other on 81%. In the 17 summaries added later, 64.3% and 83.3%. Most of that gap comes from four context cascades, one wrong rule per document repeated across a large table; without them, 91.3% and 97.2%. Every disagreement was settled against the PDF, so the dataset does not depend on either one alone.
- **Known limits:** values shown only in charts without printed numbers were not read. Percentages "relative to the untreated check" are marked as such, not as means. 1,156 records have `variable_standardized` = `other`; 998 of them are phytotoxicity scores and 94 are other diseases (target spot and late-season leaf diseases) from the 2024/25 summary, which the vocabulary has no term for yet. Licences of four journal articles in the set still need a final check; the numbers are facts and are cited row by row.

## Licence and citation

- The dataset (the CSV files, schema and scripts) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please cite the original publications listed in `data/sources.csv` as well as this dataset.
- The publications are not redistributed. Embrapa's repositories show a CC BY-NC-ND 4.0 notice; journal articles keep their journals' licences. Five of the national summaries (Documentos 251, 266 and 272, Circulares Técnicas 206 and 219) print "Todos os direitos reservados", and the 2025/26 Comunicado Técnico prints CC BY 4.0; each notice is in `data/sources.csv`. Notes quote the source text only in short fragments.

Errors or missing trials: please [open an issue](https://github.com/paper-rerun/soybean-rust-trials-br/issues).

## How this dataset was made

This dataset was built by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No value was estimated or typed by hand: each one was transcribed from the source PDF twice, independently, and every disagreement was checked against the page. The method and scripts are in `method/`. How the wider project works: https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contact: Filipe Tessaro, via issues on this repository.
