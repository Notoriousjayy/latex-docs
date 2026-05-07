# SuiteCRM Cron and Scheduler Operations Guide

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Purpose

SuiteCRM relies on scheduled background jobs for workflows, email checks, report generation, indexing, and other recurring operations. A successful web installation is incomplete until the scheduler runs reliably and is monitored.

## Operating Principles

1. Run SuiteCRM scheduler as an approved application or web-server user, not as root.
2. Confirm the user is allowed by SuiteCRM scheduler configuration.
3. Capture scheduler output in logs.
4. Monitor last-run timestamps and alert on stale execution.
5. Treat scheduler failure as an application incident because it can silently break workflows and email processing.

## SuiteCRM 8 Scheduler Model

SuiteCRM 8 scheduler documentation states that users listed in `allowed_cron_users` in the SuiteCRM `config.php` are permitted to execute `./bin/console schedulers:run`. Users not listed will cause the script to terminate. The installer normally adds the current web-server user, but operators should verify this explicitly.

## Pre-Checks

```bash
cd /var/www/suitecrm
id www-data
sudo -u www-data php -v
sudo -u www-data ./bin/console list | grep schedulers || true
```

Check SuiteCRM configuration for allowed cron users:

```bash
grep -R "allowed_cron_users" -n config.php public/legacy/config.php public/legacy/config_override.php 2>/dev/null
```

If the user is not listed, update the approved SuiteCRM configuration location according to your version and change-management process.

## Cron Option

Edit the web-server/application user's crontab:

```bash
sudo crontab -u www-data -e
```

Add a scheduler entry:

```cron
* * * * * cd /var/www/suitecrm && ./bin/console schedulers:run >> /var/log/suitecrm-scheduler.log 2>&1
```

Secure the log file:

```bash
sudo touch /var/log/suitecrm-scheduler.log
sudo chown www-data:adm /var/log/suitecrm-scheduler.log
sudo chmod 0640 /var/log/suitecrm-scheduler.log
```

## Systemd Timer Option

Use systemd timers where your operations standard prefers unit-based scheduling.

Create `/etc/systemd/system/suitecrm-scheduler.service`:

```ini
[Unit]
Description=Run SuiteCRM scheduler

[Service]
Type=oneshot
User=www-data
Group=www-data
WorkingDirectory=/var/www/suitecrm
ExecStart=/var/www/suitecrm/bin/console schedulers:run
```

Create `/etc/systemd/system/suitecrm-scheduler.timer`:

```ini
[Unit]
Description=Run SuiteCRM scheduler every minute

[Timer]
OnBootSec=60
OnUnitActiveSec=60
AccuracySec=10
Unit=suitecrm-scheduler.service

[Install]
WantedBy=timers.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now suitecrm-scheduler.timer
sudo systemctl list-timers | grep suitecrm
```

## Verification Procedure

1. Run the scheduler manually as the intended user.

```bash
cd /var/www/suitecrm
sudo -u www-data ./bin/console schedulers:run -vvv
```

2. Check the scheduler log.

```bash
sudo tail -n 100 /var/log/suitecrm-scheduler.log
# or systemd
journalctl -u suitecrm-scheduler.service -n 100 --no-pager
```

3. Check the SuiteCRM Admin > Schedulers page for last-run values.
4. Validate at least one scheduled function, such as an email check, workflow, report, or indexing job.
5. Confirm no root-owned files were created by scheduler execution.

```bash
cd /var/www/suitecrm
sudo find . -user root | head
```

## Scheduler Job Categories

| Category | Example Impact if Scheduler Fails | Operational Signal |
|---|---|---|
| Workflows | Automations do not trigger. | Workflow status stale, business process delays. |
| Email checks/imports | Incoming mail not imported; reminders delayed. | Email jobs stale, users report missing records. |
| Reports | Scheduled reports not generated. | Report delivery gaps. |
| Indexing/search | Search results stale or incomplete. | Indexing job errors or stale search behavior. |
| Maintenance jobs | Cleanup or queued work not completed. | Growing queues, disk growth, log noise. |

## Monitoring Requirements

| Signal | Recommended Alert |
|---|---|
| Timer/cron execution failure | Alert after two consecutive failures. |
| Scheduler last-run timestamp stale | Alert if older than 5-10 minutes for every-minute scheduler. |
| Log contains fatal PHP error | Alert immediately. |
| Scheduler creates root-owned files | Alert and repair permissions. |
| Disk usage above threshold | Alert before upload/log/cache space is exhausted. |

## Troubleshooting

### Symptom: Scheduler exits immediately

Likely causes:

- Running as a user not listed in `allowed_cron_users`.
- Wrong working directory.
- Missing executable permission on `bin/console`.
- PHP CLI version differs from web runtime.

Actions:

```bash
whoami
pwd
php -v
ls -l bin/console
grep -R "allowed_cron_users" -n . 2>/dev/null | head
```

### Symptom: Jobs run manually but not on schedule

Likely causes:

- Crontab installed for wrong user.
- Systemd timer disabled.
- PATH/environment differs from shell.
- Log path not writable.

Actions:

```bash
sudo crontab -u www-data -l
systemctl status suitecrm-scheduler.timer suitecrm-scheduler.service
journalctl -u suitecrm-scheduler.service -n 50 --no-pager
```

### Symptom: File permission problems after scheduler runs

Likely causes:

- Scheduler was run once as root.
- Application files extracted with wrong owner.
- Mixed deployment and runtime user model.

Actions:

```bash
cd /var/www/suitecrm
sudo chown -R www-data:www-data .
sudo find . -type d -exec chmod 2755 {} \;
sudo find . -type f -exec chmod 0644 {} \;
sudo chmod +x bin/console 2>/dev/null || true
```

## Operational Runbook

| Frequency | Task |
|---|---|
| Daily | Review scheduler failures, backup success, and disk usage. |
| Weekly | Confirm last-run values for critical scheduled jobs. |
| Monthly | Restore a recent backup to a non-production environment. |
| After upgrades | Revalidate scheduler command, allowed user, permissions, and last-run status. |

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
