FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt update && apt dist-upgrade -y && apt autoremove --purge -y && apt clean

RUN apt-get install -y \
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

RUN echo "[mysqld]" > /etc/mysql/conf.d/docker.cnf && \
    echo "skip-host-cache" >> /etc/mysql/conf.d/docker.cnf && \
    echo "skip-name-resolve" >> /etc/mysql/conf.d/docker.cnf && \
    echo "bind-address = 0.0.0.0" >> /etc/mysql/conf.d/docker.cnf && \
    echo "user = mysql" >> /etc/mysql/conf.d/docker.cnf && \
    echo "socket = /var/run/mysqld/mysqld.sock" >> /etc/mysql/conf.d/docker.cnf

RUN mkdir -p /var/run/mysqld && \
    chown mysql:mysql /var/run/mysqld && \
    chmod 755 /var/run/mysqld

WORKDIR /opt

RUN git clone https://github.com/phorgeit/arcanist.git && \
    git clone https://github.com/phorgeit/phorge.git

RUN git config --system --add safe.directory /opt/arcanist && \
    git config --system --add safe.directory /opt/phorge

RUN useradd -m -s /bin/bash phorge && \
    usermod -a -G www-data phorge

# RUN mkdir -p /var/repo && \
#     mkdir -p /var/log/phorge && \
#     chown -R phorge:phorge /var/repo && \
#     chown -R phorge:phorge /var/log/phorge

RUN chown -R phorge:phorge /opt/phorge && \
    chown -R phorge:phorge /opt/arcanist

COPY <<EOF /etc/nginx/sites-available/phorge
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

RUN ln -s /etc/nginx/sites-available/phorge /etc/nginx/sites-enabled/ && \
    rm -f /etc/nginx/sites-enabled/default

RUN usermod -d /var/lib/mysql/ mysql

RUN service mysql start && \
    until mysqladmin ping >/dev/null 2>&1; do \
        echo "Waiting for MySQL to be ready..."; \
        sleep 1; \
    done && \
    mysql mysql -e "CREATE USER IF NOT EXISTS 'phorge'@'localhost' IDENTIFIED BY 'Passw0rd';" && \
    mysql mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'phorge'@'localhost';" && \
    mysql mysql -e "FLUSH PRIVILEGES;" && \
    service mysql stop

RUN service mysql start && \
    until mysqladmin ping >/dev/null 2>&1; do \
        echo "Waiting for MySQL to be ready..."; \
        sleep 1; \
    done && \
    cd /opt/phorge && \
    ./bin/config set mysql.host localhost && \
    ./bin/config set mysql.user phorge && \
    ./bin/config set mysql.pass Passw0rd && \
    ./bin/storage upgrade --force && \
    service mysql stop

COPY init_phabricator /opt/phorge/bin/init_phabricator
RUN chmod +x /opt/phorge/bin/init_phabricator

RUN service mysql start && \
    until mysqladmin ping >/dev/null 2>&1; do \
        echo "Waiting for MySQL to be ready..."; \
        sleep 1; \
    done && \
    cd /opt/phorge && \
    ./bin/init_phabricator bootstrap --username admin --email admin@example.com > /tmp/bootstrap_output.txt 2>&1 && \
    grep "API Token:" /tmp/bootstrap_output.txt | cut -d' ' -f3 > /opt/phorge/api_token.txt && \
    cat /tmp/bootstrap_output.txt && \
    echo "API Token saved to /opt/phorge/api_token.txt" && \
    service mysql stop

COPY <<EOF /usr/local/bin/start-phorge.sh
#!/bin/bash

# Ensure MySQL directory permissions
chown -R mysql:mysql /var/lib/mysql
chown -R mysql:mysql /var/log/mysql
chown -R mysql:mysql /var/run/mysqld

# Start MySQL
service mysql start

until mysqladmin ping >/dev/null 2>&1; do
    echo "Waiting for MySQL to be ready..."
    sleep 1
done

chmod 755 /var/run/mysqld
chmod 666 /var/run/mysqld/mysqld.sock

usermod -a -G mysql www-data

mysql -u phorge -pPassw0rd -e "SELECT 1;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "MySQL connection test failed, recreating user..."
    mysql -u root -e "DROP USER IF EXISTS 'phorge'@'localhost';"
    mysql -u root -e "CREATE USER 'phorge'@'localhost' IDENTIFIED BY 'Passw0rd';"
    mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'phorge'@'localhost';"
    mysql -u root -e "FLUSH PRIVILEGES;"
fi

service php8.3-fpm start

echo "========================================="
echo "Phorge is starting up..."
echo "Admin credentials:"
echo "Username: admin"
echo "Email: admin@example.com"
if [ -f /opt/phorge/api_token.txt ]; then
    echo "API Token: $(cat /opt/phorge/api_token.txt)"
else
    echo "API Token: Check /tmp/bootstrap_output.txt for details"
fi
echo "========================================="

nginx -g 'daemon off;'
EOF

RUN chmod +x /usr/local/bin/start-phorge.sh

RUN echo "#!/bin/bash" > /usr/local/bin/get-api-token.sh && \
    echo "if [ -f /opt/phorge/api_token.txt ]; then" >> /usr/local/bin/get-api-token.sh && \
    echo "  cat /opt/phorge/api_token.txt" >> /usr/local/bin/get-api-token.sh && \
    echo "else" >> /usr/local/bin/get-api-token.sh && \
    echo "  echo 'API token file not found. Check bootstrap output:'" >> /usr/local/bin/get-api-token.sh && \
    echo "  if [ -f /tmp/bootstrap_output.txt ]; then" >> /usr/local/bin/get-api-token.sh && \
    echo "    grep 'API Token:' /tmp/bootstrap_output.txt || echo 'No API token found in bootstrap output'" >> /usr/local/bin/get-api-token.sh && \
    echo "  else" >> /usr/local/bin/get-api-token.sh && \
    echo "    echo 'Bootstrap output not found'" >> /usr/local/bin/get-api-token.sh && \
    echo "  fi" >> /usr/local/bin/get-api-token.sh && \
    echo "fi" >> /usr/local/bin/get-api-token.sh && \
    chmod +x /usr/local/bin/get-api-token.sh

RUN if [ -f /opt/phorge/api_token.txt ]; then \
    echo "export PHORGE_API_TOKEN=$(cat /opt/phorge/api_token.txt)" >> /etc/environment; \
    fi

EXPOSE 80 443 22

USER root

RUN echo "#!/bin/bash" > /usr/local/bin/setup-phorge.sh && \
    echo "echo 'Phorge has been pre-configured during Docker build!'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'MySQL databases, user, and storage schema are already set up.'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'Access Phorge at http://localhost (if port 80 is mapped)'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo ''" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'Admin User Information:'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'Username: admin'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'Email: admin@example.com'" >> /usr/local/bin/setup-phorge.sh && \
    echo "if [ -f /opt/phorge/api_token.txt ]; then" >> /usr/local/bin/setup-phorge.sh && \
    echo "  echo \"API Token: \$(cat /opt/phorge/api_token.txt)\"" >> /usr/local/bin/setup-phorge.sh && \
    echo "else" >> /usr/local/bin/setup-phorge.sh && \
    echo "  echo 'API Token: Not available (check bootstrap output)'" >> /usr/local/bin/setup-phorge.sh && \
    echo "fi" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo ''" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo 'If you need to reconfigure, you can run:'" >> /usr/local/bin/setup-phorge.sh && \
    echo "echo '  docker exec -it <container> /opt/phorge/bin/config set <key> <value>'" >> /usr/local/bin/setup-phorge.sh && \
    chmod +x /usr/local/bin/setup-phorge.sh

CMD ["/usr/local/bin/start-phorge.sh"]