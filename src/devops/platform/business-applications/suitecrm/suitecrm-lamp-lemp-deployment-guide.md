# SuiteCRM LAMP/LEMP Deployment Guide

> Default target: SuiteCRM 8.10.x on Linux with Apache 2.4, PHP 8.2-8.4, and MariaDB/MySQL using the official SuiteCRM 8.x installation model. Where this bundle discusses Nginx/LEMP, treat it as an operator pattern that must be validated against your environment; the current official SuiteCRM 8.10.x compatibility matrix centers Apache 2.4.

## Scope

This guide provides an implementation-ready deployment path for SuiteCRM 8.x. The LAMP path is the recommended default because SuiteCRM's official 8.10.x compatibility matrix lists Apache 2.4. The LEMP section is included as a validation pattern for operators who standardize on Nginx and PHP-FPM.

## Assumptions

- OS: Ubuntu or another Linux distribution supported by your operations team.
- SuiteCRM path: `/var/www/suitecrm`.
- Public hostname: `crm.example.com`.
- Web-server user: `www-data` on Ubuntu/Debian; adjust for your distribution.
- Database: MariaDB or MySQL version compatible with your SuiteCRM version.

## 1. Install Base Packages

### LAMP baseline

```bash
sudo apt update
sudo apt install -y apache2 mariadb-server unzip curl ca-certificates
sudo apt install -y php php-cli php-common php-curl php-intl php-gd php-mbstring \
  php-mysql php-soap php-xml php-zip php-opcache
sudo apt install -y php-imap php-ldap   # optional, only when required
```

Enable rewrite support:

```bash
sudo a2enmod rewrite headers ssl
sudo systemctl restart apache2
```

Confirm versions:

```bash
php -v
apache2 -v
mysql --version
php -m | egrep 'cli|curl|intl|gd|mbstring|mysqli|pdo_mysql|openssl|soap|xml|zip|imap|ldap'
```

## 2. Create Database and User

```sql
CREATE DATABASE suitecrm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'suitecrm'@'localhost' IDENTIFIED BY 'REPLACE_WITH_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON suitecrm.* TO 'suitecrm'@'localhost';
FLUSH PRIVILEGES;
```

Use a private database host if the DB is remote, and restrict access to the application host.

## 3. Place SuiteCRM Files

Download SuiteCRM from the official SuiteCRM download page and extract it to the application path.

```bash
sudo mkdir -p /var/www/suitecrm
sudo unzip SuiteCRM-8.x.x.zip -d /var/www/suitecrm
sudo chown -R www-data:www-data /var/www/suitecrm
cd /var/www/suitecrm
sudo find . -type d -exec chmod 2755 {} \;
sudo find . -type f -exec chmod 0644 {} \;
sudo chmod +x bin/console 2>/dev/null || true
```

## 4. Configure Apache Virtual Host

The official webserver setup guide recommends pointing the vhost to the `public` folder so that the full SuiteCRM application root is not exposed.

Create `/etc/apache2/sites-available/suitecrm.conf`:

```apache
<VirtualHost *:80>
    ServerName crm.example.com
    DocumentRoot /var/www/suitecrm/public

    <Directory /var/www/suitecrm/public>
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/suitecrm_error.log
    CustomLog ${APACHE_LOG_DIR}/suitecrm_access.log combined
</VirtualHost>
```

Enable the site:

```bash
sudo a2ensite suitecrm.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## 5. Configure HTTPS

Use your approved certificate process. A common public approach is Let's Encrypt via Certbot:

```bash
sudo apt install -y certbot python3-certbot-apache
sudo certbot --apache -d crm.example.com
```

Validate redirect behavior:

```bash
curl -I http://crm.example.com
curl -I https://crm.example.com
```

## 6. Configure PHP for Production

Edit the active PHP configuration for Apache or PHP-FPM. Typical production controls:

```ini
memory_limit = 256M
upload_max_filesize = 50M
post_max_size = 60M
max_execution_time = 300
display_errors = Off
log_errors = On
error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT & ~E_NOTICE & ~E_WARNING
```

Enable OPcache for production:

```ini
opcache.enable=1
opcache.memory_consumption=256
opcache.max_accelerated_files=20000
opcache.validate_timestamps=0
```

Restart the service:

```bash
sudo systemctl restart apache2
# or, with PHP-FPM:
sudo systemctl restart php8.3-fpm
```

## 7. Run the Installer

### UI installer

Open:

```text
https://crm.example.com
```

Follow the installer flow:

1. Confirm pre-install checks.
2. Enter database host, database name, database user, and password.
3. Set the canonical site URL.
4. Create the admin account.
5. Complete installation.

### CLI installer

Use the CLI method for repeatable deployments:

```bash
cd /var/www/suitecrm
sudo -u www-data ./bin/console suitecrm:app:install \
  -u "admin" \
  -p "REPLACE_WITH_ADMIN_PASSWORD" \
  -U "suitecrm" \
  -P "REPLACE_WITH_DB_PASSWORD" \
  -H "127.0.0.1" \
  -N "suitecrm" \
  -S "https://crm.example.com" \
  -d "no"
```

After installation, reapply permissions:

```bash
cd /var/www/suitecrm
sudo find . -type d -not -perm 2755 -exec chmod 2755 {} \;
sudo find . -type f -not -perm 0644 -exec chmod 0644 {} \;
sudo chown -R www-data:www-data .
sudo chmod +x bin/console 2>/dev/null || true
```

## 8. Configure Scheduler

Use the scheduler guidance in the dedicated Cron and Scheduler Operations Guide in this bundle. At minimum, configure cron or a systemd timer using an allowed non-root user and verify that scheduled jobs run.

## 9. LEMP Pattern - Validate Before Production

SuiteCRM's current official 8.10.x matrix lists Apache 2.4. If your environment requires Nginx, validate all routes, rewrites, uploads, API calls, and upgrade behavior before production.

Illustrative Nginx server block:

```nginx
server {
    listen 80;
    server_name crm.example.com;
    root /var/www/suitecrm/public;
    index index.php index.html;

    client_max_body_size 60m;

    location / {
        try_files $uri /index.php$is_args$args;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php8.3-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\. {
        deny all;
    }
}
```

Required validation:

- Home/login page loads.
- API routes do not return unexpected 404s.
- Static assets load from `public/dist`.
- Uploads work.
- Installer and post-install repair tasks work.
- Scheduler jobs run.
- Admin pages work.
- Logs do not show rewrite or permission failures.

## 10. Post-Deployment Verification

```bash
curl -I https://crm.example.com
sudo tail -n 100 /var/log/apache2/suitecrm_error.log
sudo -u www-data php -v
sudo -u www-data ./bin/console list | head
```

Verify in the UI:

- Admin login works.
- 2FA can be enabled for an admin user.
- System settings are accessible.
- Scheduler page shows expected job status.
- Email settings can be saved.
- A test record can be created and retrieved.

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



