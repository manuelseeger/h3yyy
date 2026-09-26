FROM nginx:1.27-alpine
COPY index.html /usr/share/nginx/html/index.html
ARG RELEASE_TAG=local
RUN printf '%s\n' "$RELEASE_TAG" > /usr/share/nginx/html/release.txt
