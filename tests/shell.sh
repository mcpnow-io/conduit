#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive
export TZ=UTC

apt update
apt dist-upgrade -y
apt autoremove --purge -y
apt clean

apt-get install -y \
    curl \
    software-properties-common \
    ca-certificates \
    lsb-release \
    git \
    nginx \
    php-cli \
    php-fpm \
    php-mysql \
    php-mysqli \
    php-mbstring \
    php-iconv \
    php-curl \
    php-gd \
    php-zip \
    mysql-client \
    mysql-server \
    nano

cd /opt

git clone https://github.com/phorgeit/arcanist.git
git clone https://github.com/phorgeit/phorge.git

git config --system --add safe.directory /opt/arcanist
git config --system --add safe.directory /opt/phorge

useradd -m -s /bin/bash phorge
usermod -a -G www-data phorge

chown -R phorge:phorge /opt/phorge
chown -R phorge:phorge /opt/arcanist

cat > /etc/nginx/sites-available/phorge <<EOF
server {
    listen 80;
    server_name phorge.local;
    root /opt/phorge/webroot;

    location / {
        index index.php;
        rewrite ^/(.*)\$ /index.php?__path__=/\$1 last;
    }

    location /index.php {
        fastcgi_pass unix:/var/run/php/php8.3-fpm.sock;
        fastcgi_index index.php;

        fastcgi_param REDIRECT_STATUS 200;

        fastcgi_param SCRIPT_FILENAME \$document_root\$fastcgi_script_name;
        fastcgi_param QUERY_STRING \$query_string;
        fastcgi_param REQUEST_METHOD \$request_method;
        fastcgi_param CONTENT_TYPE \$content_type;
        fastcgi_param CONTENT_LENGTH \$content_length;
        fastcgi_param SCRIPT_NAME \$fastcgi_script_name;
        fastcgi_param GATEWAY_INTERFACE CGI/1.1;
        fastcgi_param SERVER_SOFTWARE nginx/\$nginx_version;
        fastcgi_param REMOTE_ADDR \$remote_addr;
    }

    error_log /var/log/nginx/phorge_error.log;
    access_log /var/log/nginx/phorge_access.log;
}
EOF

ln -sf /etc/nginx/sites-available/phorge /etc/nginx/sites-enabled/phorge
rm -f /etc/nginx/sites-enabled/default

usermod -d /var/lib/mysql/ mysql
service mysql start

until mysqladmin ping >/dev/null 2>&1; do
    echo "Waiting for MySQL to be ready..."
    sleep 1
done

mysql mysql -e "CREATE USER IF NOT EXISTS 'phorge'@'localhost' IDENTIFIED BY 'Passw0rd';"
mysql mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'phorge'@'localhost';"
mysql mysql -e "FLUSH PRIVILEGES;"

# Do note that you need to manual copy init_phabricator into container
# cp init_phabricator /opt/phorge/bin/init_phabricator
# chmod +x /opt/phorge/bin/init_phabricator

cd /opt/phorge
./bin/config set mysql.host localhost
./bin/config set mysql.user phorge
./bin/config set mysql.pass Passw0rd
./bin/storage upgrade --force

service nginx restart
