"""Build the local Power BI project from verified 2021 market aggregates."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = "Iowa Tequila Market Entry Portfolio"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/"
REPORT_SCHEMA = SCHEMA + "item/report/definition/"
PAGE = "81e20151fe6b4c879021"
METHOD_PAGE = "56d65dbcdf044a78a6f2"
FONT = "Times New Roman"
NAVY, IVORY, WINE, GOLD, SLATE = "#142738", "#F6F0E6", "#762F44", "#C4A168", "#45596A"


def write(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def table(name, columns, rows, measures, sort_column=None):
    m_types = {"string": "text", "int64": "number", "decimal": "number"}
    model_columns = [
        {"name": label, "sourceColumn": label, "dataType": dtype, "summarizeBy": "none"}
        for label, dtype in columns
    ]
    if sort_column:
        model_columns[0]["sortByColumn"] = sort_column
        model_columns[1]["isHidden"] = True
    header = ", ".join(f'#"{label}" = {m_types[dtype]}' for label, dtype in columns)
    values = ",\n    ".join("{" + ", ".join(json.dumps(v, ensure_ascii=False) for v in row) + "}" for row in rows)
    return {
        "name": name, "columns": model_columns, "measures": measures,
        "partitions": [{"name": name, "mode": "import", "source": {
            "type": "m", "expression": f"#table(type table [{header}], {{\n    {values}\n}})"
        }}],
    }


def amount(cents):
    return f"${cents / 100_000_000:,.2f}M"


def literal(value):
    return {"expr": {"Literal": {"Value": value}}}


def fill(color):
    return {"solid": {"color": literal(f"'{color}'")}}


def text(lines, background=None):
    paragraphs = [
        {"textRuns": [{"value": value, "textStyle": {
            "fontFamily": FONT, "fontSize": f"{size}px", "color": color,
            "fontWeight": "bold" if bold else "normal",
        }}], "horizontalTextAlignment": "left"}
        for value, size, color, bold in lines
    ]
    props = {"show": literal("false")} if background is None else {
        "show": literal("true"), "color": fill(background), "transparency": literal("0D")
    }
    return {
        "visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
        "visualContainerObjects": {"background": [{"properties": props}]},
    }


def chart(kind, title, entity, category, measure, descending=False, *, line_measure=None):
    def field(field_kind, label):
        return {field_kind: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": label}}

    def projection(field_kind, label):
        return {"field": field(field_kind, label), "queryRef": f"{entity}.{label}",
                "nativeQueryRef": label, "active": True}

    value_axis = {"showAxisTitle": literal("false"), "labelFontFamily": literal(f"'{FONT}'")}
    if descending:
        value_axis["end"] = literal("160000000D")

    visual = {
        "visualType": kind,
        "query": {"queryState": {
            "Category": {"projections": [projection("Column", category)]},
            "Y": {"projections": [projection("Measure", measure)]},
        }, "sortDefinition": {"sort": [{
            "field": field("Measure", measure) if descending else field("Column", category),
            "direction": "Descending" if descending else "Ascending",
        }]}},
        "objects": {
            "categoryAxis": [{"properties": {"showAxisTitle": literal("false"), "labelFontFamily": literal(f"'{FONT}'")}}],
            "valueAxis": [{"properties": value_axis}],
            "dataPoint": [{"properties": {"defaultColor": fill(WINE if kind == "columnChart" else NAVY)}}],
            "labels": [{"properties": {
                "show": literal("true"), "labelPosition": literal("'OutsideEnd'"),
                "labelDisplayUnits": literal("1000000D" if descending else "1000D"),
                "labelPrecision": literal("1D" if descending else "0D"),
                "fontSize": literal("12D"), "fontFamily": literal(f"'{FONT}'"), "color": fill(NAVY),
            }}],
        },
        "visualContainerObjects": {"title": [{"properties": {
            "show": literal("true"), "text": literal(f"'{title}'"), "fontSize": literal("17D"),
            "fontFamily": literal(f"'{FONT}'"), "fontColor": fill(NAVY),
        }}]},
    }
    if line_measure:
        visual["query"]["queryState"]["Y2"] = {"projections": [projection("Measure", line_measure)]}
        value_axis.update({
            "start": literal("0D"), "end": literal("200000D"),
            "secShow": literal("true"), "secShowAxisTitle": literal("false"),
            "secStart": literal("0D"), "secEnd": literal("4000000D"),
            "secLabelDisplayUnits": literal("1000000D"), "secLabelPrecision": literal("0D"),
            "secLabelColor": fill(WINE), "secFontFamily": literal(f"'{FONT}'"),
        })
        objects = visual["objects"]
        objects["dataPoint"] = [
            {"properties": {"defaultColor": fill(GOLD)}},
            {"selector": {"metadata": f"{entity}.{measure}"}, "properties": {"fill": fill(GOLD)}},
            {"selector": {"metadata": f"{entity}.{line_measure}"}, "properties": {"fill": fill(WINE)}},
        ]
        objects["legend"] = [{"properties": {
            "show": literal("true"), "position": literal("'Top'"),
            "showTitle": literal("false"), "fontFamily": literal(f"'{FONT}'"), "fontSize": literal("12D"),
        }}]
        objects["lineStyles"] = [{"properties": {"strokeWidth": literal("3D")}}]
        objects["labels"][0]["properties"].update({
            "labelPosition": literal("'InsideCenter'"), "labelDensity": literal("100D"),
            "enableBackground": literal("false"), "fontSize": literal("10D"),
        })
        objects["labels"].append({
            "selector": {"metadata": f"{entity}.{line_measure}"},
            "properties": {
                "show": literal("true"), "labelPosition": literal("'Above'"),
                "labelDisplayUnits": literal("1000000D"), "labelPrecision": literal("2D"),
                "color": fill(WINE),
            },
        })
    return visual


def build():
    data = json.loads((ROOT / "Iowa_Market_Entry_2021.json").read_text(encoding="utf-8"))
    model_dir = ROOT / f"{PROJECT}.SemanticModel"
    report_dir = ROOT / f"{PROJECT}.Report"
    definition = report_dir / "definition"
    write(ROOT / f"{PROJECT}.pbip", {
        "version": "1.0", "artifacts": [{"report": {"path": report_dir.name}}],
        "settings": {"enableAutoRecovery": True},
    })
    write(report_dir / "definition.pbir", {
        "$schema": SCHEMA + "item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": f"../{model_dir.name}"}},
    })
    write(model_dir / "definition.pbism", {
        "$schema": SCHEMA + "item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "1.0", "settings": {},
    })
    month_labels = "JAN FEB MAR APRIL MAY JUN JULY AUG SEP OCT NOV DEC".split()
    months = [[month_labels[m - 1], m, bottles, teq / 100, total / 100]
              for m, bottles, teq, total in data["months"]]
    groups = [[label, cents / 100] for label, cents in data["families"].items()]
    monthly = table("Monthly Purchases", [
        ("Month", "string"), ("Month Number", "int64"), ("Bottle Quantity", "int64"),
        ("Tequila Dollars", "decimal"), ("Market Dollars", "decimal"),
    ], months, [
        {"name": "Bottles Purchased", "expression": "SUM('Monthly Purchases'[Bottle Quantity])",
         "formatString": "#,0"},
        {"name": "Wholesale Sales", "expression": "SUM('Monthly Purchases'[Tequila Dollars])",
         "formatString": "$#,0"},
    ], "Month Number")
    market = table("Spirits Market", [("Spirits Group", "string"), ("Wholesale Dollars", "decimal")],
                   groups, [{"name": "Wholesale Value", "expression": "SUM('Spirits Market'[Wholesale Dollars])",
                             "formatString": "$#,0"}])
    write(model_dir / "model.bim", {
        "name": PROJECT, "compatibilityLevel": 1600, "model": {
            "culture": "en-US", "sourceQueryCulture": "en-US",
            "defaultPowerBIDataSourceVersion": "powerBI_V3", "tables": [monthly, market],
        },
    })
    base = "CY25SU12"
    theme = "IowaMarketEntry.json"
    theme_versions = {"visual": "2.5.0", "report": "3.1.0", "page": "2.3.0"}
    write(report_dir / "StaticResources" / "RegisteredResources" / theme, {
        "name": "Iowa Market Entry", "dataColors": [WINE, NAVY, GOLD, "#23655D", SLATE],
        "background": IVORY, "foreground": NAVY, "tableAccent": WINE,
        "textClasses": {name: {"fontFace": FONT, "color": NAVY} for name in ("title", "header", "label", "callout")},
    })
    write(definition / "version.json", {"$schema": REPORT_SCHEMA + "versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    write(definition / "report.json", {
        "$schema": REPORT_SCHEMA + "report/3.1.0/schema.json",
        "themeCollection": {
            "baseTheme": {"name": base, "reportVersionAtImport": theme_versions, "type": "SharedResources"},
            "customTheme": {"name": theme, "reportVersionAtImport": theme_versions, "type": "RegisteredResources"},
        },
        "resourcePackages": [
            {"name": "SharedResources", "type": "SharedResources",
             "items": [{"name": base, "path": f"BaseThemes/{base}.json", "type": "BaseTheme"}]},
            {"name": "RegisteredResources", "type": "RegisteredResources",
             "items": [{"name": theme, "path": theme, "type": "CustomTheme"}]},
        ],
    })
    write(definition / "pages" / "pages.json", {
        "$schema": REPORT_SCHEMA + "pagesMetadata/1.0.0/schema.json",
        "pageOrder": [PAGE, METHOD_PAGE], "activePageName": PAGE,
    })
    for page_id, display_name in [(PAGE, "Market overview"), (METHOD_PAGE, "Accounts and methods")]:
        write(definition / "pages" / page_id / "page.json", {
            "$schema": REPORT_SCHEMA + "page/2.0.0/schema.json", "name": page_id,
            "displayName": display_name, "displayOption": "FitToPage", "width": 1440, "height": 810,
        })

    def visual(index, x, y, width, height, body, *, page_id=PAGE):
        name = f"{page_id[:12]}{index:08x}"
        write(definition / "pages" / page_id / "visuals" / name / "visual.json", {
            "$schema": REPORT_SCHEMA + "visualContainer/2.5.0/schema.json", "name": name,
            "position": {"x": x, "y": y, "width": width, "height": height, "z": 1000 * index, "tabOrder": 1000 * index},
            "visual": body,
        })

    annual_market = sum(data["families"].values())
    annual_tequila = data["families"]["Tequila"]
    share = annual_tequila / annual_market
    q3_tequila = sum(month[2] for month in data["months"][6:9])
    q4_tequila = sum(month[2] for month in data["months"][9:])
    q3_market = sum(month[3] for month in data["months"][6:9])
    q4_market = sum(month[3] for month in data["months"][9:])
    q4_share_change = (q4_tequila / q4_market - q3_tequila / q3_market) * 100
    visual(1, 26, 25, 1388, 100, text([
        ("Iowa tequila market entry  |  2021", 41, NAVY, True),
        ("Tequila ranked fifth. Qualify three high-volume retailers for a pilot.", 25, WINE, True),
    ]))
    cards = [
        (amount(annual_tequila), "Tequila wholesale sales", f"Q4 {q4_tequila / q3_tequila - 1:+.1%} vs Q3"),
        (f"{share:.2%}", "Tequila share of Iowa spirits sales", f"Q4 {q4_share_change:+.2f} percentage points vs Q3"),
        (amount(annual_market), "Iowa spirits wholesale sales", f"Q4 {q4_market / q3_market - 1:+.1%} vs Q3"),
    ]
    for index, (number, label, detail) in enumerate(cards):
        visual(2 + index, 26 + index * 465, 145, 450, 128, text([
            (number, 38, WINE, True), (label, 22, NAVY, True), (detail, 19, SLATE, False),
        ], IVORY))
    visual(5, 26, 311, 630, 385, chart("barChart", "Wholesale sales by spirits group", "Spirits Market", "Spirits Group", "Wholesale Value", True))
    visual(6, 681, 311, 732, 385, chart(
        "lineClusteredColumnComboChart", "Monthly tequila purchases and wholesale sales",
        "Monthly Purchases", "Month", "Bottles Purchased", line_measure="Wholesale Sales",
    ))
    visual(7, 26, 728, 1388, 62, text([
        ("Scope  •  Calendar 2021 wholesale orders by Iowa Class E retailers. Monthly chart shows tequila only.", 17, SLATE, False),
        ("Accounts and methods  →  Retailer shortlist, pilot checks, extraction, and metric definitions", 17, WINE, True),
    ]))

    visual(1, 26, 25, 1388, 100, text([
        ("Accounts and methods", 41, NAVY, True),
        ("Year-end 2021  •  Retail pilot for a fictional tequila supplier", 24, WINE, True),
    ]), page_id=METHOD_PAGE)
    target_lines = [("Three stores to qualify", 27, WINE, True)]
    for _, store, name, city, total, tequila in data["targets"]:
        label = name.split(" / ")[0]
        target_lines.append((f"{label}, {city}  ·  {amount(total)} spirits  ·  {tequila / total:.2%} tequila", 21, NAVY, False))
    target_lines.extend([
        (f"Screen  •  Top-quartile spirits spend, ≥$10K in tequila and mix below {share:.2%}.", 19, SLATE, False),
        ("Rank  •  Store spirits dollars × statewide tequila share − store tequila dollars.", 19, SLATE, False),
    ])
    visual(2, 26, 145, 680, 240, text(target_lines, IVORY), page_id=METHOD_PAGE)
    visual(3, 728, 145, 685, 240, text([
        ("From qualification to pilot", 27, WINE, True),
        ("Confirm who controls the assortment. Two stores are Hy-Vee.", 21, NAVY, False),
        ("Check shelf fit, price tier, case packs and lead time with buyers.", 21, NAVY, False),
        ("Request point-of-sale and on-hand data before sizing orders.", 21, NAVY, False),
        ("Plan first orders and replenishment separately. Track reorders and", 19, SLATE, False),
        ("forecast bias before expanding.", 19, SLATE, False),
    ], IVORY), page_id=METHOD_PAGE)
    visual(4, 26, 419, 680, 256, text([
        ("Source and extraction", 27, WINE, True),
        ("Kaggle archive → filter to calendar 2021 → group spirits categories", 21, NAVY, False),
        ("→ aggregate by month, category group and store → Power BI", 21, NAVY, False),
        ("2,622,712 order lines matched Iowa’s published row count.", 19, SLATE, False),
        (f"All three sets of aggregates reconcile to {amount(annual_market)}.", 19, SLATE, False),
    ]), page_id=METHOD_PAGE)
    visual(5, 728, 419, 685, 256, text([
        ("How to read the metrics", 27, WINE, True),
        ("Wholesale sales  •  Sum of the source field Sale Dollars.", 21, NAVY, False),
        ("Tequila share  •  Tequila dollars ÷ all recorded spirits dollars.", 21, NAVY, False),
        ("Bottles  •  Sum of Bottles Sold for tequila across bottle sizes.", 21, NAVY, False),
        ("Quarterly context  •  Q4 vs Q3. Share change is in percentage points.", 19, SLATE, False),
        ("These orders measure retailer purchases from the state.", 19, SLATE, False),
    ]), page_id=METHOD_PAGE)
    visual(6, 26, 722, 1388, 60, text([
        ("Source  •  Iowa Alcohol Operations Bureau via Gabriel Ramos on Kaggle (CC BY 4.0).", 17, SLATE, False),
        ("The case study documents the source links, category mapping, and reproducibility steps.", 17, SLATE, False),
    ]), page_id=METHOD_PAGE)


if __name__ == "__main__":
    build()
