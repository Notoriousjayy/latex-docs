# Enterprise Architecture

Enterprise-level references spanning business operations and IT service-management systems. Use them to connect stakeholder concerns, business capabilities and technology implementation.

## Collections

| Collection | Purpose |
|---|---|
| [Business operations](business-operations/readme.md) | Small-business operating model, management guides and controls. |
| [ITSM and CMDB](itsm-cmdb/) | IT service-management and configuration-management architecture, including GLPI/iTop. |

## Workflow

1. Establish business capabilities, processes and required service outcomes.
2. Describe systems, owners, interfaces, dependencies and control requirements.
3. Record significant decisions through the [ADR templates](../decisions/readme.md) and link to evidence.

## Build

```bash
make preflight
make build-category-architecture
```

These commands compile documentation, not enterprise systems.

## Related

[Architecture catalog](../readme.md) · [Startup documents](../../startups/readme.md)
