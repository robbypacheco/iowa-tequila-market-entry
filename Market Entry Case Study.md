# Iowa tequila market entry in 2021

## Why, what, who, and how

**Why.** In this fictional supplier engagement, I am the demand forecast analyst reviewing the Iowa market at year-end 2021. The decision is where to qualify a first retail pilot and what evidence I need before committing inventory. My experience buying for restaurants and retail informs how I assess assortment fit and buying access. My planning experience informs how I would size the pilot and track reorders.

**What.** Iowa Class E retailers recorded $428.12M in spirits wholesale purchases. Tequila accounted for $34.58M, or 8.08%, ranking fifth of nine analytical groups. Tequila purchase dollars rose 6.2% in Q4 compared with Q3, while the overall market rose 10.1%. Tequila's share fell 0.29 percentage points on unrounded values. The quarterly comparison provides context for movement within 2021. It does not establish a recurring seasonal pattern.

**Who.** Start with Hy-Vee in Carroll (store 2593), Costco #1325 in Davenport (5666), and Hy-Vee in Urbandale (2663). All three already purchase tequila and rank in the top quartile by total spirits spend. Their tequila mix trails the 8.08% statewide benchmark. Two locations are under the same banner, so verify whether assortment decisions are centralized before treating them as independent opportunities.

**How.** Qualify buying access, shelf position, price tier, case pack, lead time, and expected reorder cadence. Ask buyers for store-level point-of-sale and on-hand data. Use those inputs to estimate first orders separately from replenishment, then compare actual weekly depletion and orders with the pilot plan. Track in-stock rate, reorder intervals, and forecast bias before expanding. The benchmark gap ranks outreach priority. It is not incremental supplier revenue, a volume forecast, or a sales target.

## The five-second test

Show **Market overview** for five seconds, then hide it. Ask the reader what market is being sized, how large tequila is in that market, and what to do next. The headline gives the action. The top-left cards show tequila’s scale and quarter-over-quarter context. The monthly chart uses gold columns for bottles purchased (left axis) and a burgundy line for wholesale sales (right axis). December led on both measures with 161,213 bottles and $3.42M in wholesale sales. **Accounts and methods** gives readers the shortlist, pilot checks, extraction workflow, and metric definitions when they are ready to inspect the decision.

## Metric definitions

| Metric | Definition |
| --- | --- |
| Wholesale sales | Sum of the source `sale_dollars` field for the selected order lines. This is the recorded value of retailer orders, not checkout revenue, brand revenue, or consumer demand. |
| Tequila wholesale sales | Wholesale sales for the source categories `100% Agave Tequila` and `Mixto Tequila`. Mezcal is grouped under Specialty & other. |
| Tequila share | Tequila wholesale dollars divided by all recorded spirits wholesale dollars for the same period and population. |
| Bottles purchased | Sum of `bottles_sold` on tequila order lines, across bottle sizes. |
| Quarter-over-quarter context | Q4 divided by Q3 minus one for dollar measures. For share, subtract Q3 share from Q4 share and express the result in percentage points. |
| Account screen | Store-level spirits spend at or above the 75th-percentile cutoff ($194,543.99), at least $10,000 in tequila purchases, and tequila share below the statewide benchmark. 245 of 1,948 stores passed. |
| Dollar gap to the state mix | Store spirits dollars × statewide tequila share − observed store tequila dollars. Rank descending. Use store ID as a deterministic tiebreaker. |

## Source and reproducibility

I filtered the Kaggle archive to calendar 2021 and retained all recorded spirits groups in the denominator. The 2,622,712 retained order lines match the State of Iowa's published row count. The category, month, and store aggregates reconcile to $428,123,535.40. The tequila slice reconciles to $34,584,491.25 and 1,616,872 bottles. The published row count is a coverage check, rather than a row-by-row equivalence check.

Download the archive from Kaggle. Run the commands from the project folder using Python 3. The JSON preserves the monthly aggregates, original category-to-group mapping, and the shortlisted account inputs. The Power BI model embeds the reviewed snapshot, so opening the saved report does not require the raw archive.

```text
python build_market_data.py "Iowa Liquor Sales (Jan 2021-Jan 2022).csv.zip" Iowa_Market_Entry_2021.json
python build_market_report.py
```

Source: Gabriel Ramos, *Updated Iowa Liquor Sales*, Kaggle, CC BY 4.0. This project filters, groups, and aggregates the source records. [Kaggle dataset](https://www.kaggle.com/datasets/gabrielramos87/iowa-sales-liquor-jan-2021jan-2022) · [State of Iowa data catalog](https://data.iowa.gov/catalog/dataset/1258) · [CC BY 4.0 license](https://creativecommons.org/licenses/by/4.0/)
