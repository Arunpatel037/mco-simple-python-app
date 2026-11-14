FROM docker.io/nginxinc/nginx-unprivileged:1.29-alpine

# Install OS updates, then switch back to the image's non-root user.
USER root
RUN apk upgrade --no-cache
USER 101

ENV BACKEND_URL=http://mco-simple-python-app-backend:8000

# nginx turns files in /etc/nginx/templates into config at startup.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY index.html styles.css app.js /usr/share/nginx/html/

EXPOSE 8080
