# Create the container from the alpine nginx image
FROM nginx:alpine

# Copy the web client application into nginx
COPY dist/client.tar.gz /usr/share/nginx/html/

# Copy src code
COPY server/ /root/

# Copy the respective nginx configuration files
COPY build/nginx.conf /etc/nginx/

# Copy the start.sh into docker
COPY build/start.sh /root/

# Install required software
RUN apk update && \
    apk upgrade && \
    apk add --no-cache python3 && \
    apk add --no-cache py3-pip && \
    apk add --no-cache build-base python3-dev libffi-dev && \
    pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir wheel && \
    pip3 install --no-cache-dir boto3 && \
    pip3 install --no-cache-dir requests && \
    pip3 install --no-cache-dir pymysql && \
    pip3 install --no-cache-dir DBUtils && \
    pip3 install --no-cache-dir webauthn==0.4.7 && \
    pip3 install --no-cache-dir bcrypt && \
    pip3 install --no-cache-dir pyotp && \
    pip3 install --no-cache-dir flask && \
    pip3 install --no-cache-dir flask_cors && \
    pip3 install --no-cache-dir flask_jwt_extended && \
    pip3 install --no-cache-dir flask_compress && \
    pip3 install --no-cache-dir schedule && \
    pip3 install --no-cache-dir stripe && \
    pip3 install --no-cache-dir gunicorn && \
    pip3 install --no-cache-dir sentry-sdk[flask] && \
    tar -zxf /usr/share/nginx/html/client.tar.gz -C /usr/share/nginx/html/ && \
    mv /usr/share/nginx/html/client/* /usr/share/nginx/html/ && \
    rm -rf /usr/share/nginx/html/client* && \
    rm -rf /root/server.conf && \
    chown -R root:root /usr/share/nginx/html/ && \
    chown -R root:nginx /root && \
    chmod 750 /root && \
    chmod +x /root/start.sh && \
    find /usr/share/nginx/html -type d -print0 | xargs -0 chmod 755 && \
    find /usr/share/nginx/html -type f -print0 | xargs -0 chmod 644

# Start nginx and keep the process from backgrounding and the container from quitting
CMD ["/root/start.sh"]