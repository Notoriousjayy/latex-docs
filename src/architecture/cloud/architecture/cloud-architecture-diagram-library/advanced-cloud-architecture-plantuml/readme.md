# Advanced Cloud Architectures — PlantUML

14 chapter-oriented diagrams representing thirteen advanced cloud architecture patterns and a case study. These are interpretations of Chapter 14 rather than provider-specific system designs.

## Actual diagram sources

| Source | Topic |
|---|---|
| [14-01-hypervisor-clustering-heartbeat.puml](diagrams/14-01-hypervisor-clustering-heartbeat.puml) | Hypervisor clustering |
| [14-02-virtual-server-clustering-structural.puml](diagrams/14-02-virtual-server-clustering-structural.puml) | Virtual server clustering |
| [14-03-load-balanced-virtual-server-instances.puml](diagrams/14-03-load-balanced-virtual-server-instances.puml) | Load-balanced virtual servers |
| [14-04-nondisruptive-service-relocation.puml](diagrams/14-04-nondisruptive-service-relocation.puml) | Service relocation |
| [14-05-zero-downtime-active-failover-group.puml](diagrams/14-05-zero-downtime-active-failover-group.puml) | Zero downtime |
| [14-06-cloud-balancing-cross-cloud-routing.puml](diagrams/14-06-cloud-balancing-cross-cloud-routing.puml) | Cloud balancing |
| [14-07-resilient-disaster-recovery-premises.puml](diagrams/14-07-resilient-disaster-recovery-premises.puml) | Disaster recovery |
| [14-08-distributed-data-sovereignty-region.puml](diagrams/14-08-distributed-data-sovereignty-region.puml) | Data sovereignty |
| [14-09-resource-reservation-borrow-reclaim.puml](diagrams/14-09-resource-reservation-borrow-reclaim.puml) | Resource reservation |
| [14-10-dynamic-failure-detection-recovery.puml](diagrams/14-10-dynamic-failure-detection-recovery.puml) | Failure detection and recovery |
| [14-11-rapid-provisioning-engine-sequence-18.puml](diagrams/14-11-rapid-provisioning-engine-sequence-18.puml) | Rapid provisioning |
| [14-12-storage-workload-mgmt-lun-migration.puml](diagrams/14-12-storage-workload-mgmt-lun-migration.puml) | Storage workload management |
| [14-13-virtual-private-cloud-dedicated-slice.puml](diagrams/14-13-virtual-private-cloud-dedicated-slice.puml) | Virtual private cloud |
| [14-14-case-study-innovartus-role-player-cloud.puml](diagrams/14-14-case-study-innovartus-role-player-cloud.puml) | Case study |

## Review and render

Identify the architectural question, read the relevant source section, inspect the diagram and compare rendered output with the intent of the model. Retain optional mechanisms as optional, and record assumptions explicitly.

```bash
make render-plantuml
python3 tooling/scripts/plantuml_lint.py
```

The sources are under `diagrams/`, with rendered formats nearby. Historic [per-file compilation notes](validation/compile-commands.md) contain some former filenames; use the actual linked `.puml` names above and the canonical repository renderer. A clean render does not prove real-world resilience or cloud security.

## Related

[Parent diagram library](../readme.md)
