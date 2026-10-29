# Small Business Core Systems

A reusable operating model for essential business functions. **The tracked handouts are `.tex` sources**, not prebuilt PDFs; the diagrams have a tracked `.puml` source and rendered assets.

## Source inventory

| Guide | Source |
|---|---|
| Business operating model | [Core systems operating model](small-business-core-systems/small-business-core-systems-operating-model.tex) |
| Marketing and lead generation | [Marketing system](small-business-core-systems/marketing-and-lead-generation-system.tex) |
| Sales and conversion | [Sales system](small-business-core-systems/sales-and-lead-conversion-system.tex) |
| Delivery and fulfillment | [Operations system](small-business-core-systems/operations-and-fulfillment-system.tex) |
| Finance | [Financial management](small-business-core-systems/financial-management-system.tex) |
| Administration and IT security | [Administration and IT security](small-business-core-systems/administration-and-it-security-system.tex) |
| HR and people management | [HR system](small-business-core-systems/hr-and-people-management-system.tex) |
| Leadership and strategy | [Leadership system](small-business-core-systems/leadership-and-strategy-system.tex) |
| SOPs and tools | [SOP and tooling](small-business-core-systems/sop-and-tooling-layer-guide.tex) |
| KPIs and improvement | [Continuous improvement](small-business-core-systems/kpi-and-continuous-improvement-layer.tex) |
| Delivery plan | [Implementation checklist](small-business-core-systems/impl-checklist.tex) |

## Architecture model

The canonical diagram is [small-business-core-systems-operating-model.puml](small-business-core-systems/small-business-core-systems-operating-model.puml); rendered [PNG](small-business-core-systems/png/), [SVG](small-business-core-systems/svg/) and [JPG](small-business-core-systems/jpg/) are available for inspection.

## How to apply

1. Identify the service model, customer, regulatory environment and operational boundaries.
2. Tailor each functional guide to the business and assign owners.
3. Map workflows, handoffs, controls and KPIs; document trade-offs and review authority.
4. Use the checklist to record implementation status backed by evidence.

## Build

```bash
make preflight
make build-category-architecture
make render-plantuml
make publish
```

Run from the repository root. `make publish` stages generated PDFs under `public/pdfs/architecture/enterprise/business-operations/`. The sources are templates and models, not a certification or proof of adopted controls.

## Related

[Enterprise architecture](../readme.md) · [Startup sources](../../../startups/README.md)
