FROM nginx:1.27-alpine
COPY index.html /usr/share/nginx/html/index.html
COPY healthz /usr/share/nginx/html/healthz
