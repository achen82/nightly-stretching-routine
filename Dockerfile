# Nightly Stretching Routine — static web app served by nginx.
# The official nginx image is multi-arch (works on Raspberry Pi arm64/armv7 and x86).
FROM nginx:alpine

# The whole app is a single self-contained HTML file.
COPY index.html /usr/share/nginx/html/index.html

# Server block: serves the app and proxies /api/ to the state-store service.
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
