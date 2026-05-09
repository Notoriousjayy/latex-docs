# Advanced Cloud Architecture - PlantUML Diagram Set

## Purpose

This diagram set provides original PlantUML representations of the thirteen advanced cloud architectures and the case study described in **Chapter 14: Advanced Cloud Architectures**. Each diagram captures the architecture's purpose, primary actors, mechanisms, and runtime flow as described in the source. The diagrams are intentionally faithful to the source's terminology and stated mechanisms; no external technologies, vendor names, or unstated implementation details are introduced.

## Source Document

- File: `14_Chapter_14_Advanced_Cloud_Architectures.pdf`
- Chapter: 14, Sections 14.1 - 14.14

## Diagram Inventory

| # | File | Architecture | Diagram Type |
|---|---|---|---|
| 01 | `01_hypervisor_clustering.puml` | Hypervisor Clustering | Sequence |
| 02 | `02_virtual_server_clustering.puml` | Virtual Server Clustering | Deployment |
| 03 | `03_load_balanced_virtual_server_instances.puml` | Load-Balanced Virtual Server Instances | Sequence |
| 04 | `04_nondisruptive_service_relocation.puml` | Nondisruptive Service Relocation | Sequence |
| 05 | `05_zero_downtime.puml` | Zero Downtime | Deployment |
| 06 | `06_cloud_balancing.puml` | Cloud Balancing | Component |
| 07 | `07_resilient_disaster_recovery.puml` | Resilient Disaster Recovery | Deployment |
| 08 | `08_distributed_data_sovereignty.puml` | Distributed Data Sovereignty | Deployment |
| 09 | `09_resource_reservation.puml` | Resource Reservation | Activity |
| 10 | `10_dynamic_failure_detection_and_recovery.puml` | Dynamic Failure Detection and Recovery | Activity |
| 11 | `11_rapid_provisioning.puml` | Rapid Provisioning | Sequence |
| 12 | `12_storage_workload_management.puml` | Storage Workload Management | Sequence |
| 13 | `13_virtual_private_cloud.puml` | Virtual Private Cloud | Deployment |
| 14 | `14_case_study_example.puml` | Case Study (Innovartus Cloud Balancing) | Component |

## Compiling

See `validation/compile_commands.md`. In short:

    java -jar plantuml.jar -tpng diagrams/*.puml
    java -jar plantuml.jar -tsvg diagrams/*.puml

Each `.puml` file is self-contained and compiles independently. No `!include` directives are used.

## Validation

The full set has been validated against `plantuml` (version 1.2020.02 on OpenJDK 21) producing both PNG and SVG output without errors or warnings.

## Ambiguity Notes

Where the source describes qualitative behavior without naming a specific component, that behavior is represented in the diagram with a labelled note. Specific examples:

- **14.4 Nondisruptive Service Relocation** - The source defines two virtual-server migration modes (local/non-shared storage vs. shared remote storage). Both are represented in a single note rather than as separate flow branches because the source does not give different overall sequencing for them.
- **14.6 Cloud Balancing** - The source notes that resource replication "may need" to be incorporated when manual cross-cloud synchronization is not possible. This conditional is preserved as a note.
- **14.10 Dynamic Failure Detection and Recovery** - The four recovery steps shown follow the example policy in Figure 14.25 verbatim. The number and content of steps are policy-driven and may vary in practice; the diagram preserves the exact policy from the source.
- **14.11 Rapid Provisioning** - The numbered sequence follows the 18-step description in the source. The "deployment engine" is treated as a function of the rapid provisioning engine, consistent with the source's narrative.
- **14.13 Virtual Private Cloud** - The source mentions a dedicated physical link as an alternative to VPN; this is preserved as a note.

## Originality

These diagrams are original PlantUML interpretations based only on the source document. They are not visual reproductions of the figures in the chapter. They preserve the source's terminology, stated mechanisms, sequence logic, and stated constraints (including the explicit conflict between Nondisruptive Service Relocation and the direct I/O access architecture). They add no inferred implementation technologies (no AWS, Azure, GCP, Kubernetes, Terraform, ServiceNow, or any other tooling).



