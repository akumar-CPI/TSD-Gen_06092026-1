# iFlow → Technical Specification Document generator

Generates a Word (.docx) Technical Specification Document from an SAP
Integration Suite (Cloud Integration) iFlow package, matching the
FICOPROC TSD template's exact table format.

## How it works

1. **Push** an iFlow export zip into `iflows/` in this repo.
2. The GitHub Actions workflow detects the new/changed zip, runs the
   pipeline, and commits the resulting `.docx` into `docs/generated-tsd/`.
3. Pipeline = two scripts:
   - `scripts/parse_iflow.py` — unzips the package, parses the `.iflw`
     BPMN2 XML, and extracts every pallet-function element, adapter,
     participant, and process, along with all `ifl:property` key/value
     pairs.
   - `scripts/generate_tsd.py` — reads that JSON and renders the
     `.docx` using the field layouts in `scripts/schema_map.py`.

## Document structure (numbered, matches your template)

```
1. Participants
2. Process Overview
   2.1 Integration Process
   2.2 Local Integration Process
3. Pallet Function Details
   3.1 Content Modifier      <- one heading per TYPE, all instances'
       [table: Set Order Headers]     tables stacked directly underneath,
       [table: Set Retry Headers]     no "Instance 1/2" labels - each
       [table: Format Error]          table's own Name row identifies it
   3.2 Groovy Script
   3.3 Router
   ...
4. Connectivity
   4.1 HTTP Receiver
   4.2 HTTPS Sender
   ...
```

A pallet function type with zero occurrences in the iFlow gets **no
section at all**. A type that occurs but has no schema entry yet still
gets a numbered heading (so it's never silently missing) with a
**Name-only table** — never a raw property dump.

## Template-only fields — no "extra properties" dumping

**Only fields defined in `schema_map.py` are ever rendered.** There is
no fallback that dumps every extracted property. This was a deliberate
change after finding the previous "show everything" approach was
pulling in internal CPI plumbing (component version numbers, SWCV ids,
`cmdVariantUri`, protocol version strings) that never appears in the
CPI UI and isn't part of the template. If a property isn't listed in a
schema entry, it simply doesn't show up — full stop.

## Correctness: real export vs. best-effort

SAP CPI reuses the same internal `activityType` for several visually
distinct pallet functions and disambiguates them with a secondary
property. Missing this was the root cause of "Content Modifier showing
up as Content Enricher" — both share `activityType="Enricher"`; the
real distinguishing signal is whether a `bodyType` property is present
(Content Modifier has one, the legacy Content Enricher doesn't).
`parse_iflow.py`'s `resolve_pallet_type()` is the single place this
disambiguation happens now, verified against a real production iFlow
export:

| Shared `activityType` | Disambiguated by | Resolves to |
|---|---|---|
| `Enricher` | presence of `bodyType` | Content Modifier / Content Enricher |
| `Script` | `subActivityType` | Groovy Script / Java Script |
| `Mapping` | `subActivityType` | XSLT / Message / Operation Mapping |
| `DBstorage` | `operation` | Get / Select / Write / Delete / Persist |
| `Splitter` | `splitType` | General / Iterating Splitter |
| `ProcessCallElement` | `subActivityType` (exact match `"loopingprocess"` — a substring check would wrongly match `"nonloopingprocess"` too, which was a bug caught during testing) | Process Call / Looping Process Call |
| `ExclusiveGateway` | n/a | Router |

Every entry in `PALLET_SCHEMAS` / `ADAPTER_SCHEMAS` in `scripts/schema_map.py`
carries a `"verified": True/False` flag:
- **`True`** — property names were checked against a real production
  `.iflw` export (either one you shared or a real open-source SAP CPI
  iFlow used for testing). Trust these.
- **`False`** — best-effort from general SAP CPI documentation/community
  knowledge, not yet confirmed against a real export. These are
  reasonable starting points but double-check them against your own
  iFlow before trusting the output — the property key names or the
  raw stored values (e.g. `"local"` vs `"Global"`) may not match.

Also fixed: the adapter `direction` property is stored **lowercase**
(`direction`) in real exports, not `Direction` — the parser now checks
both, preferring lowercase.

## Field-spec language (`schema_map.py`)

- `"PropKey"` — plain value, shown as-is.
- `"__NAME__"` — the element's own name.
- `{"bool": "PropKey"}` — a single ☑/☐ with no text next to it, for
  plain on/off template fields (e.g. "Delete On Completion ☐").
- `{"prop": "PropKey", "checkbox": ["OptA", "OptB"]}` — every option
  shown with a box, checked when the raw value textually matches.
- `{"prop": "PropKey", "checkbox": {"rawvalue": "Display Label"}}` —
  same, but maps the raw *stored* value to the *displayed* label. Use
  this whenever they differ (very common — e.g. CPI stores Data Store
  visibility as `"local"`/`"global"`, the template shows "Integration
  Flow"/"Global").
- `["PropKeyA", "PropKeyB"]` — tries each key in order, first non-empty
  wins. Used where the same concept is stored under different keys
  across adapter versions (e.g. HTTP Receiver's URL is `Address` in
  some exports, `httpAddressWithoutQuery` in others — both are real).

## Nested "table inside a property" values

CPI stores Content Modifier's Message Header / Exchange Property
entries as a *single* property whose value is itself a small escaped
XML document (`<row><cell id='Action'>Create</cell>...</row><row>...`).
`generate_tsd.py` detects this, re-parses it, and renders it as its
own proper multi-column table — Action / Name / Type / Datatype /
Value / Default — matching the template, right under the step's main
table.

## Try it locally

```bash
pip install python-docx
python scripts/parse_iflow.py path/to/YourIFlow.zip parsed.json
python scripts/generate_tsd.py parsed.json YourIFlow_TSD.docx
```

## Extending coverage

Adding a pallet function or adapter type that isn't covered yet, or
correcting a `"verified": False` entry once you've checked it against
your own export, is just editing the dict in `schema_map.py` — no
other code changes needed. If you find a step type showing up as a
bare Name-only table, check `parsed.json` for its `resolved_type` and
raw `properties`, then add a matching entry.
