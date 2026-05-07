# SuiteCRM Implementation Checklist

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Checklist Use

Use this checklist as the deployment work plan. Mark each item as Done, Blocked, or Not Applicable. Capture evidence for production deployments, including command output, screenshots of installer status, backup logs, and restore-test notes.

## Phase 1 - Planning

| Status | Task | Evidence |
|---|---|---|
| [ ] | Select SuiteCRM version and confirm the official compatibility matrix. | Version selected and compatibility link captured. |
| [ ] | Choose LAMP as the default supported stack unless a validated LEMP pattern is required. | Architecture decision recorded. |
| [ ] | Define hostname, site URL, DNS record, and TLS certificate approach. | DNS/TLS plan documented. |
| [ ] | Define database engine and version. | MariaDB/MySQL version documented. |
| [ ] | Define backup retention, off-host target, and restore RPO/RTO expectations. | Backup standard approved. |
| [ ] | Define admin user model, 2FA expectation, and break-glass process. | Access model documented. |

## Phase 2 - Host Provisioning

| Status | Task | Evidence |
|---|---|---|
| [ ] | Provision Linux host or VM. | Hostname and inventory record. |
| [ ] | Apply OS updates. | Patch command output. |
| [ ] | Configure host firewall to allow only required ports. | Firewall rules exported. |
| [ ] | Create an application or deployment user if separate from web-server user. | User/group record. |
| [ ] | Configure NTP/time sync. | `timedatectl` output. |
| [ ] | Configure log rotation. | Logrotate policy or system logs. |

## Phase 3 - Runtime Stack

| Status | Task | Evidence |
|---|---|---|
| [ ] | Install Apache 2.4, PHP, and database packages matching SuiteCRM compatibility. | Package versions. |
| [ ] | Install required PHP modules: cli, curl, common, intl, json, gd, mbstring, mysqli, pdo_mysql, openssl, soap, xml, zip. | `php -m` output. |
| [ ] | Install optional PHP modules if required: imap, ldap. | `php -m` output and use case. |
| [ ] | Enable Apache rewrite support. | Apache module status. |
| [ ] | Configure PHP settings, including memory/upload limits and error reporting. | PHP config diff. |
| [ ] | Enable OPcache for production after testing. | OPcache configuration. |

## Phase 4 - SuiteCRM Files

| Status | Task | Evidence |
|---|---|---|
| [ ] | Download SuiteCRM from the official SuiteCRM download source. | Release/version artifact. |
| [ ] | Extract files to `/var/www/suitecrm` or approved application path. | Directory listing. |
| [ ] | Set web server vhost `DocumentRoot` to `/var/www/suitecrm/public`. | Vhost file. |
| [ ] | Set file and directory permissions using the approved web-server user. | `find`/`stat` sample output. |
| [ ] | Confirm that application root files outside `public` are not web-exposed. | Browser test or webserver config review. |

## Phase 5 - Database

| Status | Task | Evidence |
|---|---|---|
| [ ] | Create SuiteCRM database. | SQL command or DB admin ticket. |
| [ ] | Create SuiteCRM database user with least privilege for that database. | Grants output. |
| [ ] | Store credentials using the approved secret-handling process. | Secret vault reference or controlled config location. |
| [ ] | Confirm DB connectivity from application host. | Connection test output. |

## Phase 6 - Installer

| Status | Task | Evidence |
|---|---|---|
| [ ] | Run the UI installer or CLI installer. | Installer screenshot or CLI output. |
| [ ] | Enter site URL exactly as users will access it. | Config review. |
| [ ] | Configure admin username/password through the installer. | Account created; password not recorded in evidence. |
| [ ] | Resolve installer pre-check failures. | Pre-check status. |
| [ ] | Reapply permissions after installation. | Permission command output. |

## Phase 7 - Scheduler and Background Jobs

| Status | Task | Evidence |
|---|---|---|
| [ ] | Confirm scheduler command for the installed SuiteCRM version. | Command documented. |
| [ ] | Ensure scheduler user is allowed in SuiteCRM configuration. | Config check. |
| [ ] | Configure cron or systemd timer. | Crontab or timer unit. |
| [ ] | Verify scheduled jobs execute. | Last-run timestamp and log entry. |
| [ ] | Confirm email import/workflows/report jobs behave as expected. | Functional test evidence. |

## Phase 8 - Security Hardening

| Status | Task | Evidence |
|---|---|---|
| [ ] | Enable HTTPS and redirect HTTP to HTTPS. | TLS test. |
| [ ] | Configure trusted hosts for production hostname. | Config review. |
| [ ] | Keep login throttling enabled or tune approved values. | `.env.local` or config review. |
| [ ] | Enable 2FA for administrators. | Admin-profile screenshot without secrets. |
| [ ] | Lock down database network access. | Security group/firewall rules. |
| [ ] | Confirm sensitive files are not downloadable. | Web test. |
| [ ] | Configure security headers at web tier where compatible. | Header scan. |

## Phase 9 - Backup, Monitoring, and Operations

| Status | Task | Evidence |
|---|---|---|
| [ ] | Configure database backups. | Backup log. |
| [ ] | Configure application file backups. | Backup log. |
| [ ] | Move backups off-host and encrypt artifacts. | Storage proof. |
| [ ] | Perform restore test into non-production environment. | Restore record. |
| [ ] | Monitor web server, PHP, database, disk, and scheduler. | Monitoring dashboard. |
| [ ] | Document patch and upgrade process. | Operations runbook. |

## Go-Live Criteria

- Installation and pre-checks complete.
- HTTPS works and HTTP redirects safely.
- Admin 2FA is configured.
- Scheduler is running and observable.
- Backups are complete and restore-tested.
- Operators know where logs, backups, scheduler status, and SuiteCRM config are located.

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
