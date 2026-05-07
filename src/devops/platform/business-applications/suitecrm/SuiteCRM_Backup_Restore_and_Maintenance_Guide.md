# SuiteCRM Backup, Restore, and Maintenance Guide

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Purpose

This guide defines the operational backup, restore, and maintenance model for a self-hosted SuiteCRM deployment. SuiteCRM stores critical state in both the database and the filesystem; reliable recovery requires both.

## Backup Scope

| Asset | Why It Matters | Backup Method |
|---|---|---|
| Database | CRM records, metadata, users, roles, module data, configuration state. | `mysqldump`, `mariadb-dump`, physical backup, or managed DB snapshot. |
| Application files | SuiteCRM codebase, configuration, customizations, uploads, local extensions. | File archive or filesystem snapshot. |
| Uploads/documents | User-uploaded customer and business records. | Include in application file backup. |
| Config files | Site URL, database settings, trusted hosts, scheduler settings. | Include in file backup with restricted access. |
| Web server config | Vhost, TLS, rewrite behavior, headers. | Infrastructure-as-code or config backup. |
| Cron/systemd units | Scheduler execution model. | Config backup or infrastructure-as-code. |

## Backup Architecture

```text
SuiteCRM application host
  |-- application file backup
  |-- webserver/PHP config backup
  |-- scheduler config backup

Database host
  |-- logical dump or snapshot

Backup target
  |-- encrypted off-host storage
  |-- retention policy
  |-- restore-test environment
```

## Recommended Backup Schedule

| Environment | Database | Files | Retention | Restore Test |
|---|---|---|---|---|
| Production | Daily full + optional binlog/PITR | Daily | 30-90 days, business dependent | Monthly or after major change |
| Staging | Daily or weekly | Weekly | 14-30 days | Quarterly |
| Development | Optional | Optional | Minimal | As needed |

## Database Backup Example

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/srv/backups/suitecrm
DATE=$(date +%Y%m%d-%H%M%S)
DB_NAME=suitecrm
DB_USER=suitecrm_backup

mkdir -p "$BACKUP_DIR"

mysqldump --single-transaction --routines --triggers   --user="$DB_USER"   --password   "$DB_NAME"   | gzip > "$BACKUP_DIR/suitecrm-db-$DATE.sql.gz"

sha256sum "$BACKUP_DIR/suitecrm-db-$DATE.sql.gz" > "$BACKUP_DIR/suitecrm-db-$DATE.sql.gz.sha256"
```

Notes:

- Prefer a dedicated backup user with required read/lock privileges rather than the application user.
- Use `--single-transaction` for InnoDB tables to reduce locking impact.
- Store database backup passwords in a secure mechanism rather than inline scripts.

## File Backup Example

```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=/srv/backups/suitecrm
DATE=$(date +%Y%m%d-%H%M%S)
APP_DIR=/var/www/suitecrm

mkdir -p "$BACKUP_DIR"

tar --acls --xattrs -czf "$BACKUP_DIR/suitecrm-files-$DATE.tar.gz"   -C "$(dirname "$APP_DIR")" "$(basename "$APP_DIR")"

sha256sum "$BACKUP_DIR/suitecrm-files-$DATE.tar.gz" > "$BACKUP_DIR/suitecrm-files-$DATE.tar.gz.sha256"
```

Move artifacts off-host:

```bash
rclone copy /srv/backups/suitecrm remote:suitecrm-backups/$(hostname)/
# or use your approved object storage, SFTP, or backup platform
```

## Restore Procedure

### 1. Prepare restore host

```bash
sudo apt update
sudo apt install -y apache2 mariadb-server php php-cli php-common php-curl php-intl   php-gd php-mbstring php-mysql php-soap php-xml php-zip unzip
```

### 2. Restore files

```bash
sudo tar -xzf suitecrm-files-YYYYMMDD-HHMMSS.tar.gz -C /var/www
sudo chown -R www-data:www-data /var/www/suitecrm
cd /var/www/suitecrm
sudo find . -type d -exec chmod 2755 {} \;
sudo find . -type f -exec chmod 0644 {} \;
sudo chmod +x bin/console 2>/dev/null || true
```

### 3. Restore database

```bash
mysql -e "CREATE DATABASE suitecrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
gunzip -c suitecrm-db-YYYYMMDD-HHMMSS.sql.gz | mysql suitecrm
```

### 4. Reconnect configuration

- Validate database hostname, username, and password in SuiteCRM config.
- Validate `site_url` and trusted hosts for the restore hostname.
- Configure webserver document root to `/var/www/suitecrm/public`.
- Configure scheduler with the allowed non-root user.

### 5. Post-restore checks

```bash
curl -I https://restore-crm.example.com
sudo -u www-data ./bin/console list | head
sudo -u www-data ./bin/console schedulers:run -vvv
```

UI validation:

- Admin login works.
- Dashboard loads.
- Records are present.
- Uploads/documents open.
- Scheduled jobs run.
- Email settings are intact or safely disabled for restore testing.

## Maintenance Tasks

| Frequency | Task | Notes |
|---|---|---|
| Daily | Check backup job result and disk usage. | Alert on missing backup or failed upload. |
| Weekly | Review SuiteCRM, PHP, webserver, and OS security updates. | Patch non-production first. |
| Weekly | Review scheduler status and application logs. | Focus on fatal errors and repeated permission errors. |
| Monthly | Restore a recent backup into non-production. | Record time to restore and data integrity findings. |
| Quarterly | Review users, admin accounts, roles, and 2FA coverage. | Remove stale accounts. |
| Before upgrade | Take database and file backup, snapshot host if available. | Do not rely only on VM snapshot. |
| After upgrade | Reapply permissions, validate scheduler, validate web root, test login and core modules. | Capture evidence. |

## Backup Acceptance Criteria

A backup process is not considered production-ready until all of the following are true:

- Database backup completes on schedule.
- Application file backup completes on schedule.
- Backups are moved off-host.
- Backup artifacts are encrypted or stored in an encrypted target.
- Retention policy is implemented.
- A restore has been successfully tested.
- Restore steps are documented and repeatable by another operator.

## Maintenance Risk Register

| Risk | Mitigation |
|---|---|
| Database backup succeeds but uploads are missing. | Always pair DB backup with file backup. |
| Backup stored on same host is lost with host. | Copy backups off-host. |
| Scheduler silently fails after upgrade. | Include scheduler verification in post-upgrade checklist. |
| Wrong web root exposes application files. | Validate document root points to `public`. |
| Root-owned files cause runtime failures. | Never run scheduler as root; reapply ownership after maintenance. |
| Restore environment sends real emails. | Disable outbound mail or isolate restore environment during testing. |

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
