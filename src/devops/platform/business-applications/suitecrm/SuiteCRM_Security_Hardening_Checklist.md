# SuiteCRM Security Hardening Checklist

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Security Objective

Harden SuiteCRM by reducing the exposed attack surface, controlling administrative access, protecting the database and uploaded files, and ensuring recoverability. This checklist assumes a self-hosted SuiteCRM 8.x deployment.

## 1. Exposure and Network Controls

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Serve SuiteCRM only over HTTPS. | Use a valid certificate and redirect HTTP to HTTPS. |
| [ ] | Limit inbound ports. | Public: 80/443 only. Admin access: SSH from approved networks only. |
| [ ] | Do not expose database ports publicly. | Allow DB access only from the application host or private network. |
| [ ] | Place SuiteCRM behind a reverse proxy if central ingress is required. | Preserve correct host headers and test trusted-host behavior. |
| [ ] | Monitor web requests and errors. | Collect Apache/Nginx access/error logs and SuiteCRM logs. |

## 2. Web Root and File Exposure

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Point the web server document root to SuiteCRM's `public` folder. | Official guidance warns that exposing the full SuiteCRM folder can expose application files. |
| [ ] | Deny direct access to backup files, config files, logs, and temporary artifacts. | Keep backups outside the web root. |
| [ ] | Remove installer artifacts or restrict installer access after deployment. | Confirm no installer route remains publicly usable. |
| [ ] | Avoid world-writable permissions. | Use targeted ownership for web-server writable paths. |
| [ ] | Re-run permission checks after upgrades and restores. | Upgrades can change ownership or mode expectations. |

## 3. Authentication and Session Controls

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Enable 2FA for administrators. | SuiteCRM 8 supports user-profile 2FA enrollment and backup codes. |
| [ ] | Keep login throttling enabled. | SuiteCRM 8 defaults to throttling after 3 failed attempts. Tune only through approved configuration. |
| [ ] | Use named admin accounts. | Avoid shared administrator accounts except documented break-glass. |
| [ ] | Disable or rotate default/example credentials immediately. | Never leave demo or setup credentials active. |
| [ ] | Review roles and security groups. | Use least privilege for operational users. |

## 4. Trusted Host and URL Controls

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Configure `trusted_hosts` for production hostnames. | SuiteCRM 8.4.2+ includes host-header validation support. |
| [ ] | Set `site_url` to the canonical HTTPS URL. | Use the same URL users will enter in browsers. |
| [ ] | Test alternate Host headers. | Unexpected hostnames should not serve the application. |
| [ ] | Keep reverse proxy host-header behavior deterministic. | Avoid ambiguous proxy rewrites. |

Example trusted-host entry:

```php
$sugar_config['trusted_hosts'] = ['^crm\.example\.com$'];
```

## 5. Database Security

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Use a dedicated SuiteCRM database user. | Do not use root or a shared administrative DB account. |
| [ ] | Scope privileges to the SuiteCRM database. | Grant only what the application requires. |
| [ ] | Store credentials securely. | Restrict config file permissions and use approved secret handling. |
| [ ] | Back up database with encryption. | Validate restore, not just backup completion. |
| [ ] | Monitor failed DB connections and slow queries. | Useful for operational and security triage. |

## 6. PHP and Application Runtime

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Use only SuiteCRM-compatible PHP versions. | SuiteCRM 8.10.x lists PHP 8.2, 8.3, and 8.4. |
| [ ] | Disable display of PHP errors in production. | Log errors server-side. |
| [ ] | Configure SuiteCRM-recommended `error_reporting`. | Official webserver setup recommends suppressing notices/warnings/deprecated/strict output. |
| [ ] | Enable OPcache for production. | Improves performance and reduces runtime overhead. |
| [ ] | Patch PHP, web server, and OS packages. | Include emergency patch workflow. |

## 7. Scheduler Hardening

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Do not run scheduler as root. | SuiteCRM scheduler documentation explicitly discourages root. |
| [ ] | Ensure scheduler user is listed in allowed cron users. | Validate `config.php` after installation. |
| [ ] | Log scheduler output. | Capture failures and last-run status. |
| [ ] | Alert on stale scheduler execution. | Stale scheduler impacts workflows, email checks, and reports. |

## 8. Backup and Recovery Controls

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Back up database and application files. | Database-only backup is incomplete. |
| [ ] | Store backups off-host. | Protect against host loss or compromise. |
| [ ] | Encrypt backup artifacts. | Include key recovery process. |
| [ ] | Test restores on a schedule. | Record restoration time and issues. |
| [ ] | Restrict backup access. | Treat backups as sensitive customer and business data. |

## 9. Operational Monitoring

| Status | Control | Implementation Notes |
|---|---|---|
| [ ] | Monitor uptime and TLS certificate expiry. | Include alert thresholds. |
| [ ] | Monitor disk utilization. | Uploads, logs, and backups can fill disks. |
| [ ] | Monitor database health. | Track disk, connections, slow queries, and backup success. |
| [ ] | Monitor scheduler last run. | Workflows and email checks depend on it. |
| [ ] | Review logs after failed logins, 500 errors, or permission issues. | Keep logs centralized where feasible. |

## Security Go-Live Gate

Do not place SuiteCRM into production until all of the following are true:

- HTTPS is enabled and verified.
- Web root points to `public`.
- Admin 2FA is enabled.
- Login throttling is active.
- Trusted hosts are configured.
- Scheduler runs as non-root and is monitored.
- Database is not exposed publicly.
- Backups are off-host, encrypted, and restore-tested.

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
