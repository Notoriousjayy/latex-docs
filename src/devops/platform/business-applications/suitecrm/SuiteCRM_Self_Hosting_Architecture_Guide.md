# SuiteCRM Self-Hosting Architecture Guide

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Purpose

This guide defines a production-oriented self-hosting architecture for SuiteCRM. It is intended for small-business and internal-platform deployments that need clear ownership, repeatable operations, secure defaults, and a maintainable upgrade path.

## Reference Architecture

SuiteCRM is a PHP CRM application deployed behind a web server, backed by a relational database, and supported by scheduled background processing. The uploaded SuiteCRM repository snapshot confirms application entry points and runtime components such as `index.php`, `install.php`, `cron.php`, `run_job.php`, `Api/`, `Api/V8/`, `include/`, `custom/`, and module directories. The deployment model should therefore protect the application root, expose only the intended public web entry point, and explicitly operate the scheduler.

```text
Users / Admins
    |
    v
DNS + HTTPS endpoint
    |
    v
Reverse proxy / web server
    |  - terminates TLS or forwards to TLS terminator
    |  - serves SuiteCRM public web root
    |  - permits URL rewrites required by API routes
    v
PHP runtime
    |  - SuiteCRM application code
    |  - PHP extensions and OPcache/APCu where approved
    v
Database service
    |  - MariaDB or MySQL
    |  - least-privilege SuiteCRM database user
    v
Persistent storage
    |  - uploaded files
    |  - cache/runtime directories
    |  - logs

Scheduler host/process
    |  - cron or systemd timer
    |  - runs SuiteCRM scheduler as an allowed non-root user
    v
SuiteCRM scheduled jobs
    |  - email checks
    |  - workflows
    |  - reports
    |  - search indexing

Backup/monitoring layer
    |  - database dumps or physical backups
    |  - application file backups
    |  - log monitoring
    |  - restore tests
```

## Core Components

| Component | Recommended Responsibility | Notes |
|---|---|---|
| Linux host | Provides the OS baseline, firewall, package lifecycle, filesystem ownership, and monitoring agent. | Use a supported Linux distribution with a documented patch cadence. |
| Web server | Serves the SuiteCRM `public` directory, enables URL rewrites, and enforces HTTPS. | Apache 2.4 is the official compatibility-matrix web server for SuiteCRM 8.10.x. |
| PHP runtime | Executes SuiteCRM. | Use the SuiteCRM-compatible PHP version for the selected release. For 8.10.x, use PHP 8.2, 8.3, or 8.4. |
| Database | Stores CRM records, metadata, users, configuration, and module data. | For 8.10.x, SuiteCRM lists MariaDB 10.6/10.11/11.4/11.8 or MySQL 8.0/8.4. |
| Persistent files | Stores uploads, cache, customizations, logs, and application state. | Back up both the database and the application file tree. |
| Scheduler | Executes SuiteCRM background jobs. | Do not run as root. Use a web-server/application user listed in SuiteCRM's allowed cron users. |
| Mail integration | Sends notifications and imports inbound mail where configured. | Validate SMTP/OAuth and scheduled email import behavior. |
| Backup system | Produces recoverable database and file backups. | Restore testing is the acceptance criterion, not backup-job success alone. |

## Deployment Topologies

### Topology A: Single-Node Small Business Deployment

Use one VM for Apache/PHP, database, scheduler, and local backups staged to object storage or another host.

Best for:

- Pilot environments
- Small teams
- Low administrative overhead
- Simple operational ownership

Key risks:

- Single point of failure
- Local backups may fail with the host
- Database and web workload contend for CPU, memory, and disk I/O

Minimum controls:

- Off-host backups
- HTTPS-only access
- Firewall limited to 80/443 and admin access
- Non-root scheduler execution
- Restore test after implementation

### Topology B: Split Application and Database

Use one or more application hosts and a separate database host or managed database service.

Best for:

- Moderate user volume
- Stronger backup and recovery expectations
- Better database isolation

Key controls:

- Restrict database port to application hosts only
- Use a least-privilege database user
- Encrypt backup artifacts
- Monitor database latency and slow queries

### Topology C: Reverse Proxy + Internal App Host

Use a public reverse proxy or load balancer in front of an internal SuiteCRM application host.

Best for:

- Environments with central TLS management
- Shared ingress patterns
- Future high availability

Key controls:

- Preserve correct host headers
- Configure SuiteCRM trusted hosts
- Ensure the public site URL matches the served URL
- Forward client IPs safely if logs and rate limits depend on them

## Security Boundary Model

| Boundary | Required Control |
|---|---|
| Internet to web tier | HTTPS, firewall, rate limiting, patched web server, no direct database exposure. |
| Web tier to PHP/application | Only the public web root should be exposed. Do not serve the full SuiteCRM root as the web root. |
| Application to database | Private network path, least-privilege DB user, no shared administrative credentials. |
| Scheduler to application | Run scheduler as an allowed non-root user and monitor last-run status. |
| Operators to host | SSH key access, sudo auditing, MFA where available, restricted source IPs. |

## Runtime Data Flow

1. User requests arrive through DNS and HTTPS.
2. The web server serves SuiteCRM from the `public` directory and passes PHP requests to PHP-FPM or mod_php, depending on stack design.
3. SuiteCRM reads/writes CRM records in MariaDB/MySQL.
4. Uploaded documents, cache, logs, and customizations are written to the application filesystem.
5. The scheduler runs recurring background jobs such as workflow processing, email checks, report generation, and indexing.
6. Backup jobs capture database state and file state and move encrypted artifacts off-host.

## Architecture Decisions

| Decision | Recommendation | Rationale |
|---|---|---|
| SuiteCRM major version | Use SuiteCRM 8.x for new deployments unless you have a SuiteCRM 7 dependency. | Current 8.x docs provide the target architecture and installer flow. |
| Web server | Prefer Apache 2.4 for strict official compatibility alignment. | SuiteCRM 8.10.x compatibility matrix lists Apache 2.4. |
| Web root | Point the vhost to SuiteCRM's `public` folder. | Official webserver guidance warns that pointing at the SuiteCRM folder can expose files. |
| Scheduler user | Use web-server/application user, never root. | SuiteCRM scheduler controls allowed cron users and explicitly discourages root. |
| Backup scope | Back up database plus application file tree. | Database-only backups miss uploads, customizations, configuration, and local state. |
| Performance | Enable OPcache in production after validation. | SuiteCRM performance guidance recommends OPcache for production. |

## Acceptance Criteria

- SuiteCRM is reachable over HTTPS at the final production hostname.
- The web server document root points to the SuiteCRM `public` directory.
- SuiteCRM installer pre-checks pass or approved warnings are documented.
- Database user is scoped to the SuiteCRM database only.
- Scheduler runs successfully and last-run timestamps update.
- Trusted hosts are configured for the production hostname.
- Login throttling remains enabled or is explicitly tuned.
- At least one administrator account has 2FA enabled.
- Database and application-file backups complete and a restore test has been performed.

## Source Basis

This artifact is based on the following source set:

- SuiteCRM 8.x Compatibility Matrix: https://docs.suitecrm.com/8.x/admin/compatibility-matrix/
- SuiteCRM 8.x Webserver Setup Guide: https://docs.suitecrm.com/8.x/admin/installation-guide/webserver-setup-guide/
- SuiteCRM 8.x Downloading & Installing: https://docs.suitecrm.com/8.x/admin/installation-guide/downloading-installing/
- SuiteCRM 8.x Running the UI Installer: https://docs.suitecrm.com/8.x/admin/installation-guide/running-the-ui-installer/
- SuiteCRM 8.x Running the CLI Installer: https://docs.suitecrm.com/8.x/admin/installation-guide/running-the-cli-installer/
- SuiteCRM 8.x Schedulers: https://docs.suitecrm.com/8.x/admin/administration-panel/schedulers/
- SuiteCRM 8.x Performance: https://docs.suitecrm.com/8.x/admin/installation-guide/performance/
- SuiteCRM 8.x Login Throttling Configuration: https://docs.suitecrm.com/8.x/admin/configuration/login-throttling-configuration/
- SuiteCRM 8.x Trusted Hosts Configuration: https://docs.suitecrm.com/8.x/admin/configuration/trusted-hosts-configuration/
- SuiteCRM 8.x Two-Factor Authentication: https://docs.suitecrm.com/8.x/features/two-factor/two-factor/
- Uploaded SuiteCRM repository snapshot supplied in this chat.
