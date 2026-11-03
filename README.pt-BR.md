# Ensaios de controle da ferrugem-asiática da soja no Brasil

English version: [README.md](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23631775.svg)](https://doi.org/10.5281/zenodo.23631775)

17.845 resultados de ensaios sobre o controle da ferrugem-asiática da soja (*Phakopsora pachyrhizi*) no Brasil, tirados das tabelas de 37 publicações de acesso aberto da Embrapa (2005 a 2026). Cada linha é um número exatamente como foi impresso: um tratamento, a dose e o momento de aplicação, onde e quando foi testado, o que foi medido e o valor, com a página e a tabela de onde saiu.

A ferrugem-asiática é a doença que mais causa dano à soja no Brasil, e os fungicidas perdem eficiência com o tempo, à medida que o fungo se adapta. A rede nacional de ensaios cooperativos da Embrapa mede isso a cada safra desde 2003/04, mas os resultados ficam em circulares técnicas anuais, em tabelas de PDF. Este dataset reúne o resumo nacional de 22 das 23 safras de 2003/04 a 2025/26, então dá para acompanhar o mesmo produto ao longo de duas décadas. A safra que falta é a 2007/08: não foi achado resumo nacional, e a reunião da rede de 2008 pediu que os ensaios fossem retomados, então a rede aparentemente não rodou naquela safra.

Faz parte do [Paper Rerun](https://paper-rerun.github.io), na linha Open Tables. O trabalho foi feito por agentes de IA num computador doméstico e revisado por uma pessoa antes da publicação.

## O que tem

| | |
|---|---|
| Publicações | 37 (Alice e Infoteca-e, os repositórios abertos da Embrapa): 22 resumos nacionais dos ensaios cooperativos de fungicidas (2003/04 a 2025/26, todas as safras menos 2007/08), 7 ensaios locais ou regionais de fungicidas, 3 sobre momento de aplicação, número de aplicações e tratamento de sementes, 2 sobre cultivares, 3 sobre manejo cultural e nutrição |
| Registros | 17.845 |
| Principais medidas | severidade da ferrugem (6.343), produtividade (4.890), eficiência de controle (4.315), redução de produtividade (641), AACPD (98), massa de grãos (88) |

Arquivos:
- `data/soybean_rust_trials.csv`: o dataset, um registro por valor impresso. As colunas estão descritas em `method/schema.json`.
- `data/sources.csv`: as 37 publicações, com autores, link do registro e aviso de licença.
- `qa/decisions.csv`: cada divergência entre as duas transcrições independentes e como ela foi resolvida conferindo o PDF (46.812 decisões, com a página).
- `method/`: o schema, o script de comparação e o script de junção. O schema agora é a v2.1: o formato de transcrição ganhou, por tabela, uma declaração do contexto que a tabela passa aos registros (momento de aplicação, local, número de aplicações etc.). As colunas dos registros não mudaram.
- `analysis/`: a série de eficácia ao longo das safras, ver abaixo.

A coluna `origin` diz de onde veio cada registro: `both` (as duas transcrições concordaram), `A` ou `B` (uma transcrição estava certa e a outra foi corrigida) ou `corrected` (as duas precisaram de correção). `source_inconsistency` marca 4.017 registros em que a publicação se contradiz (por exemplo, uma tabela e o texto dando locais, datas ou doses diferentes).

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

## Eficácia ao longo do tempo

A pasta `analysis/` acompanha a eficiência de controle do mesmo produto, na mesma dose, pelas tabelas de médias nacionais, descontando o efeito da safra, para que uma safra difícil não conte como queda de todos os produtos. Com 22 safras, 31 produtos foram testados em 3 ou mais delas.

- Os 7 produtos do primeiro olhar (5 safras) continuam perdendo eficácia, quase na mesma ordem. No total, 27 dos 31 produtos caem.
- O tebuconazol (100 g i.a./ha) foi de 90% de controle em 2003/04 para 28% em 2009/10, uns 10 pontos por safra, e depois ficou num piso de 15% a 40% até sair da rede em 2016/17.
- A azoxistrobina + benzovindiflupir (60 + 30 g) foi de 86% em 2013/14 para 28% em 2022/23.
- As misturas com fungicida multissítio (clorotalonil, mancozebe), testadas desde 2015/16, não mostram perda até agora: mediana de -0,1 ponto por ano em 7 produtos. Clorotalonil + tebuconazol ficou entre 58% e 71% por 9 safras.

São médias nacionais de ensaios, não recomendação de campo. Produto sai da rede quando falha, o protocolo de aplicação mudou ao longo dos anos e as misturas com multissítio cobrem só de 4 a 9 safras. Os cuidados e a tabela completa estão em `analysis/README.md` (em inglês).

## Como foi feito

1. **Coleta.** Um agente buscou nos repositórios abertos da Embrapa publicações com tabelas de ensaios quantitativos sobre o tema, baixou 20 e registrou outras 68 candidatas que não entraram, com o motivo. Uma segunda busca, pelas safras que faltavam dos ensaios cooperativos, achou mais 17 resumos nacionais.
2. **Duas transcrições independentes.** Dois agentes por publicação transcreveram cada célula de tabela sobre o tema num schema fixo, sem ver o trabalho um do outro, copiando os números exatamente como impressos e prestando contas de cada célula de dados de cada tabela.
3. **Comparação e arbitragem.** Um script pareou as duas transcrições e listou cada divergência e cada valor presente em só uma delas. Cada caso foi resolvido conferindo o PDF, com a página como evidência.

## Qual a precisão

- **Releitura cega (novembro de 2026):** um terceiro leitor, sem ver o dado publicado, leu de novo no PDF 100 registros sorteados deste dataset: nenhum tinha erro. Nos 13 datasets do Open Tables (1.297 registros) a taxa foi de 1,5 erro de valor e 10 de contexto por mil registros, e nenhum número foi lido errado ([detalhes, em inglês](https://github.com/paper-rerun/paper-rerun/blob/main/measurements/blind-reread-2026-11.md)).
- **Números:** nas 20 primeiras publicações, as duas transcrições concordaram em 5.832 de 5.834 valores e letras de significância (99,97%); as duas diferenças eram o separador decimal e o número estava certo. Nos 17 resumos que entraram depois, nenhum número foi lido errado em 12.003 pares.
- **Contexto:** é aqui que uma transcrição só falha. Momento de aplicação, códigos dos tratamentos, locais e a forma como um percentual foi calculado muitas vezes aparecem uma vez só e valem para a tabela inteira. Nas 20 primeiras publicações, sozinha, uma transcrição estava totalmente correta em 22% dos registros; a outra, em 81%. Nos 17 resumos que entraram depois, 64,3% e 83,3%. A maior parte dessa diferença vem de quatro cascatas de contexto, uma regra lida errado por documento e repetida numa tabela grande; sem elas, 91,3% e 97,2%. Cada divergência foi resolvida conferindo o PDF, então o dataset não depende de nenhuma das duas sozinha.
- **Limites conhecidos:** valores mostrados só em gráficos, sem número impresso, não foram lidos. Percentuais "em relação à testemunha" estão marcados como tal, e não como médias. 1.156 registros têm `variable_standardized` = `other`; 998 deles são notas de fitotoxicidade e 94 são outras doenças (mancha-alvo e doenças de final de ciclo) do resumo de 2024/25, que o vocabulário ainda não tem como nomear. As licenças de quatro artigos de periódico do conjunto ainda precisam de uma conferência final; os números são fatos e estão citados linha a linha.

## Licença e citação

- O dataset (os arquivos CSV, o schema e os scripts) é publicado sob a licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Por favor, cite as publicações originais listadas em `data/sources.csv` e também este dataset.
- As publicações não são redistribuídas. Os repositórios da Embrapa exibem um aviso CC BY-NC-ND 4.0; os artigos de periódico mantêm as licenças das revistas. Cinco dos resumos nacionais (Documentos 251, 266 e 272, Circulares Técnicas 206 e 219) imprimem "Todos os direitos reservados", e o Comunicado Técnico de 2025/26 imprime CC BY 4.0; o aviso de cada um está em `data/sources.csv`. As notas citam o texto original só em trechos curtos.

Erros ou ensaios que faltam: por favor, [abra uma issue](https://github.com/paper-rerun/soybean-rust-trials-br/issues).

## Como este dataset foi feito

Este dataset foi montado por agentes de IA (Claude, da Anthropic) num computador doméstico e revisado por uma pessoa antes da publicação. Nenhum valor foi estimado ou digitado à mão: cada um foi transcrito do PDF original duas vezes, de forma independente, e cada divergência foi conferida na página. O método e os scripts estão em `method/`. Como funciona o projeto como um todo (em inglês): https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md

Contato: Filipe Tessaro, pelas issues deste repositório.
