# Data Systems

Data-platform documentation — AI/ML, streaming, and other system-level
data infrastructure topics. Currently sparse; structured in anticipation
of growth.

## Scope

**Belongs here:**
- LLM adoption and AI/ML system stories (`ai-ml/llm/`).
- Streaming-platform material (`streaming/kafka/`).
- Future: warehouses, lakes, lineage, contracts.

**Does not belong here:**
- Application-level data persistence patterns — see `../architecture/views-and-beyond/style-catalogs/module/data-model-style/`.
- Database security topics — see `../security/`.

## Contents

| Child | Purpose |
|---|---|
| `ai-ml/llm/` | LLM adoption user stories and AI/ML platform docs. |
| `streaming/kafka/` | Kafka adoption and platform user stories. |

## Conventions

- New AI/ML topics get their own folder under `ai-ml/<topic>/`.
- New streaming systems get their own folder under `streaming/<system>/`.
- Singleton folders are fine; this domain is intentionally
  forward-structured.

## Building

```bash
make build-category-data-systems
```

## Related

- `../README.md`
- Future expansion targets: warehouses, OLAP, data contracts.



