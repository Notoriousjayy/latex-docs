# Specialized Cloud Architectures - PlantUML Diagram Set

This package contains a complete set of PlantUML diagrams for the sixteen
specialized cloud architectures described in Chapter 15, *Specialized Cloud
Architectures*. Each diagram is built directly from the source document and
follows a consistent, professional style suitable for technical reference,
review, and reuse.

## Contents

| #  | File                                                  | Architecture                                                  | Diagram type                          | Primary message                                                                                         | Source section |
|----|-------------------------------------------------------|---------------------------------------------------------------|---------------------------------------|----------------------------------------------------------------------------------------------------------|----------------|
| 01 | `01_direct_io_access.puml`                            | Direct I/O Access                                             | Component (with state notes)          | Virtual server bypasses the hypervisor and reaches the physical I/O card directly to overcome bottlenecks. | 15.1           |
| 02 | `02_direct_lun_access.puml`                           | Direct LUN Access                                             | Component / deployment                | Virtual servers reach a shared RAW block-based LUN through a physical HBA via raw device mapping.        | 15.2           |
| 03 | `03_dynamic_data_normalization.puml`                  | Dynamic Data Normalization                                    | Activity (workflow)                   | A de-duplication system hashes incoming blocks and replaces redundant blocks with pointers.              | 15.3           |
| 04 | `04_elastic_network_capacity.puml`                    | Elastic Network Capacity                                      | Activity with swimlanes               | Listener + automation engine dynamically allocate ports / bandwidth from a network resource pool.        | 15.4           |
| 05 | `05_cross_storage_device_vertical_tiering.puml`       | Cross-Storage Device Vertical Tiering                         | Activity with swimlanes               | LUNs scale up across devices via live migration; consumers are never disconnected.                       | 15.5           |
| 06 | `06_intra_storage_device_vertical_data_tiering.puml`  | Intra-Storage Device Vertical Data Tiering                    | Component (with workflow note)        | LUNs migrate between graded disk tiers inside a single cloud storage device.                             | 15.6           |
| 07 | `07_load_balanced_virtual_switches.puml`              | Load-Balanced Virtual Switches                                | Component / deployment                | Multiple physical uplinks (NIC team) distribute traffic to remove single-uplink bottlenecks.             | 15.7           |
| 08 | `08_multipath_resource_access.puml`                   | Multipath Resource Access                                     | Component (with state note)           | Alternative paths and a multipathing system keep the IT resource reachable on any single-path failure.   | 15.8           |
| 09 | `09_persistent_virtual_network_configuration.puml`    | Persistent Virtual Network Configuration                      | Component (with migration arrow)      | A centralized virtual switch + VIM replicate config so migrated VMs keep network connectivity.           | 15.9           |
| 10 | `10_redundant_physical_connection_virtual_servers.puml` | Redundant Physical Connection for Virtual Servers           | Activity (failover state machine)     | Standby uplink takes over transparently when the primary uplink fails, then yields back on recovery.     | 15.10          |
| 11 | `11_storage_maintenance_window.puml`                  | Storage Maintenance Window                                    | Activity with swimlanes               | Live storage migration redirects consumers to a secondary device for the duration of maintenance.        | 15.11          |
| 12 | `12_edge_computing.puml`                              | Edge Computing                                                | Deployment topology                   | Edge environments place lower-end processing closer to each consumer location while heavier work stays in the cloud. | 15.12 |
| 13 | `13_fog_computing.puml`                               | Fog Computing                                                 | Deployment topology                   | A fog layer sits between many edges and the cloud, relaying and triaging data flows.                     | 15.13          |
| 14 | `14_virtual_data_abstraction.puml`                    | Virtual Data Abstraction                                      | Component                             | A data virtualization layer exposes a single uniform API over disparate data sources.                    | 15.14          |
| 15 | `15_metacloud.puml`                                   | Metacloud                                                     | Component                             | A central control layer abstracts management, operations, security, and governance across clouds.        | 15.15          |
| 16 | `16_federated_cloud_application.puml`                 | Federated Cloud Application                                   | Deployment                            | Application services are placed across clouds where each placement is most advantageous.                 | 15.16          |
|    | `index_specialized_cloud_architectures.puml`          | Index / overview                                              | Grouping diagram                      | Groups all 16 architectures by major concern (storage access, tiering & migration, network capacity & resilience, distributed processing, abstraction & federation). | Ch. 15 |

## Style and conventions

All diagrams share a single visual style:

- Off-white canvas, no shadows, rounded corners.
- Components in light blue, nodes (physical hardware) in light orange, databases / storage in light green, clouds in light purple.
- Decision diamonds in light orange.
- Direct, short labels (1–3 words wherever practical).
- Notes used only where they add clarifying context drawn from the source.
- Numbered step references inside notes match the figure step numbers in the source document.

## Compiling

Every file is a complete, self-contained PlantUML document delimited by
`@startuml` and `@enduml`. To render:

```
plantuml -tpng *.puml
plantuml -tsvg *.puml
```

PlantUML 1.2024.x or later is recommended.

## Notes on ambiguity / explicit assumptions

The source document's prose plus its labeled figures gave enough information
to render every architecture without inventing mechanisms. The following minor
modeling choices are worth flagging:

- **15.1 Direct I/O Access** - The source presents this as a three-state
  progression (Figures 15.1 / 15.2 / 15.3). To keep one clear dominant message
  per file, the three states are consolidated into one component diagram: both
  the via-hypervisor path and the direct path are shown, and the sequence of
  events (1)–(4) is preserved in adjacent notes.
- **15.6 Intra-Storage Device Vertical Data Tiering** - Source figures span
  Figures 15.14–15.17. The component diagram captures the structure, and the
  side note carries the figure-numbered workflow steps (1)–(9) so traceability
  is preserved without splitting into multiple files.
- **15.7 Load-Balanced Virtual Switches** - The source mentions the *Load
  Balancer* mechanism but does not specify its exact placement relative to the
  virtual switch and NIC team. The diagram shows it as the component that
  performs link aggregation between the virtual switch and the uplink NICs,
  consistent with the source description ("link aggregation can be executed to
  balance the traffic").
- **15.8 Multipath Resource Access** - The numbered workflow (1)–(7) is shown
  as a single annotated structural diagram (rather than a separate sequence
  diagram) because the source's two figures both describe the same physical
  topology under different conditions; splitting the figure would have added
  visual cost without adding information.
- **15.11 Storage Maintenance Window** - Spans Figures 15.31–15.37. The
  end-to-end flow is captured in a single swimlaned activity diagram covering
  pre-migration, live migration, maintenance, restore, and resumption.
- **15.16 Federated Cloud Application** - The exact inter-service topology in
  Figure 15.42 is illustrative; the diagram preserves the source's three-cloud
  layout and the same set of services (A, B, C, D, E, AI Service A, Logging
  Service A) and shows representative connections among them.

No cloud-provider-specific services were introduced. All mechanisms named in
the diagrams (Cloud Usage Monitor, Logical Network Perimeter, Pay-Per-Use
Monitor, Resource Replication, Audit Monitor, Failover System, Hypervisor,
Virtual Server, Cloud Storage Device, Load Balancer, Storage Service Gateway,
Storage Management Program, LUN Migration, Live Storage Migration, Automated
Scaling Listener, Intelligent Automation Engine, VIM, Centralized Virtual
Switch, Data Virtualization Layer) come directly from the source document.



