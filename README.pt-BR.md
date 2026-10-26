# Ensaios de controle da ferrugem-asiática da soja no Brasil

English version: [README.md](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23631775.svg)](https://doi.org/10.5281/zenodo.23631775)

5.836 resultados de ensaios sobre o controle da ferrugem-asiática da soja (*Phakopsora pachyrhizi*) no Brasil, tirados das tabelas de 20 publicações de acesso aberto da Embrapa (2008 a 2023). Cada linha é um número exatamente como foi impresso: um tratamento, a dose e o momento de aplicação, onde e quando foi testado, o que foi medido e o valor, com a página e a tabela de onde saiu.

A ferrugem-asiática é a doença que mais causa dano à soja no Brasil, e os fungicidas perdem eficiência com o tempo, à medida que o fungo se adapta. A rede nacional de ensaios cooperativos da Embrapa mede isso a cada safra há quase duas décadas, mas os resultados ficam em circulares técnicas anuais, em tabelas de PDF. Este dataset torna 20 dessas publicações pesquisáveis e comparáveis entre safras.

Faz parte do [Paper Rerun](https://paper-rerun.github.io), na linha Open Tables. O trabalho foi feito por agentes de IA num computador doméstico e revisado por uma pessoa antes da publicação.

## O que tem

| | |
|---|---|
| Publicações | 20 (Alice e Infoteca-e, os repositórios abertos da Embrapa): 5 resumos nacionais dos ensaios cooperativos de fungicidas (2009/10 a 2022/23), 7 ensaios locais ou regionais de fungicidas, 3 sobre momento de aplicação, número de aplicações e tratamento de sementes, 2 sobre cultivares, 3 sobre manejo cultural e nutrição |
| Registros | 5.836 |
| Principais medidas | severidade da ferrugem (2.116), produtividade (1.662), eficiência de controle (1.327), redução de produtividade (198), AACPD (98), massa de grãos (88) |

Arquivos:
- `data/soybean_rust_trials.csv`: o dataset, um registro por valor impresso. As colunas estão descritas em `method/schema.json`.
- `data/sources.csv`: as 20 publicações, com autores, link do registro e aviso de licença.
- `qa/decisions.csv`: cada divergência entre as duas transcrições independentes e como ela foi resolvida conferindo o PDF (19.494 decisões, com a página).
- `method/`: o schema, o script de comparação e o script de junção.

A coluna `origin` diz de onde veio cada registro: `both` (as duas transcrições concordaram), `A` ou `B` (uma transcrição estava certa e a outra foi corrigida) ou `corrected` (as duas precisaram de correção). `source_inconsistency` marca 844 registros em que a publicação se contradiz (por exemplo, uma tabela e o texto dando locais ou datas diferentes).

### Principais colunas

O arquivo está em UTF-8, com vírgula separando as colunas. Local, safra, data de semeadura e cultivar estão em `location`, `season_or_year`, `sowing_date` e `cultivar`, no próprio registro.

- `doc_id`: identificador da publicação de origem. Liga o registro a `data/sources.csv` e é também o nome do PDF, sem a extensão.
- `page`: página do PDF contada a partir de 1 (a primeira página do arquivo é 1), e não o número impresso na página. O rótulo da tabela está em `table_or_figure`, como impresso ("Tabela 3", "Quadro 1"), ou `text` quando o número está no corpo do texto.
- `treatment`: nome do tratamento exatamente como aparece na linha ou no cabeçalho da tabela, com nomes de produto e marcas de rodapé.
- `treatment_type`: o fator que define a linha. `fungicide` é pulverização foliar só com fungicidas sítio-específicos (triazol, estrobilurina, carboxamida e misturas deles); `fungicide_with_multisite`, pulverização que inclui um multissítio (mancozebe, clorotalonil, oxicloreto de cobre); `spray_program`, linhas que diferem no momento ou no número de aplicações; `seed_treatment`, fungicida na semente; `genotype`, cultivar ou linhagem; `cultural`, época de semeadura, espaçamento, arranjo ou população de plantas; `biological`, produto biológico; `control`, testemunha sem fungicida; `combination`, célula de fatorial que cruza duas classes; `other`, o resto.
- `crop_stage`: estádio da soja como escrito ("R6", "R5.4"). `crop_stage_refers_to` diz se é o estádio da avaliação, da aplicação, da semeadura, da colheita ou da inoculação.
- `variable`: variável medida, exatamente como no cabeçalho ou na legenda, com o momento quando ele faz parte do cabeçalho ("Severidade (%) R6", "AACPD", "PCG (g)", "RP (%)").
- `variable_standardized`: a mesma variável numa lista fechada. As mais comuns são `severity_pct` (severidade da ferrugem em % de área foliar), `yield_kg_ha` (produtividade de grãos em kg/ha), `control_efficacy_pct` (% de controle impresso pelos autores, em relação à testemunha), `yield_reduction_pct` (redução de produtividade em %), `audpc` (AACPD) e `grain_weight_100_g` (massa de 100 grãos). A lista completa está em `method/schema.json`.
- `value_as_printed`: o número exatamente como impresso, sem a letra de significância ("2.941", "33,5").
- `value`: o mesmo número pronto para cálculo, com ponto decimal e sem separador de milhar ("2.941" vira 2941, "33,5" vira 33.5). Nada foi calculado, convertido ou arredondado.
- `unit`: unidade como impressa ou informada na legenda ("%", "kg/ha", "kg ha-1", "sc/ha", "R$/ha"). Vazia quando não há unidade impressa, como na AACPD.
- `statistic`: o que o número é: `mean` (média do tratamento ou média entre ensaios), `median`, `total`, `single_value` (uma parcela ou uma observação), `percentage_of_total` ou `other`. Os percentuais calculados pelos autores em relação à testemunha (eficiência de controle, redução de produtividade) estão como `other`, e não como média.
- `significance_letter`: letra(s) do teste de médias exatamente como impressas ("a", "AB", "a A", "bc"). Vazia quando não há.

## Como foi feito

1. **Coleta.** Um agente buscou nos repositórios abertos da Embrapa publicações com tabelas de ensaios quantitativos sobre o tema, baixou 20 e registrou outras 68 candidatas que não entraram, com o motivo.
2. **Duas transcrições independentes.** Dois agentes por publicação transcreveram cada célula de tabela sobre o tema num schema fixo, sem ver o trabalho um do outro, copiando os números exatamente como impressos e prestando contas de cada célula de dados de cada tabela.
3. **Comparação e arbitragem.** Um script pareou as duas transcrições e listou cada divergência e cada valor presente em só uma delas. Cada caso foi resolvido conferindo o PDF, com a página como evidência.

## Qual a precisão

- **Números:** as duas transcrições concordaram em 5.832 de 5.834 valores e letras de significância (99,97%). As duas diferenças eram o separador decimal; o número estava certo.
- **Contexto:** é aqui que uma transcrição só falha. Momento de aplicação, códigos dos tratamentos, locais e a forma como um percentual foi calculado muitas vezes aparecem uma vez só e valem para a tabela inteira. Sozinha, uma transcrição estava totalmente correta em 22% dos registros; a outra, em 81%. Cada divergência foi resolvida conferindo o PDF, então o dataset não depende de nenhuma das duas sozinha.
- **Limites conhecidos:** valores mostrados só em gráficos, sem número impresso, não foram lidos. Percentuais "em relação à testemunha" estão marcados como tal, e não como médias. As licenças de quatro artigos de periódico do conjunto ainda precisam de uma conferência final; os números são fatos e estão citados linha a linha.

## Licença e citação

- O dataset (os arquivos CSV, o schema e os scripts) é publicado sob a licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Por favor, cite as publicações originais listadas em `data/sources.csv` e também este dataset.
- As publicações não são redistribuídas. Os repositórios da Embrapa exibem um aviso CC BY-NC-ND 4.0; os artigos de periódico mantêm as licenças das revistas. As notas citam o texto original só em trechos curtos.

Erros ou ensaios que faltam: por favor, [abra uma issue](https://github.com/paper-rerun/soybean-rust-trials-br/issues).

## Como este dataset foi feito

Este dataset foi montado por agentes de IA (Claude, da Anthropic) num computador doméstico e revisado por uma pessoa antes da publicação. Nenhum valor foi estimado ou digitado à mão: cada um foi transcrito do PDF original duas vezes, de forma independente, e cada divergência foi conferida na página. O método e os scripts estão em `method/`. Como funciona o projeto como um todo (em inglês): https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contato: Filipe Tessaro, pelas issues deste repositório.
