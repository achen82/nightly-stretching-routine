# Nightly Stretching Routine — static web app served by nginx.
# The official nginx image is multi-arch (works on Raspberry Pi arm64/armv7 and x86).
FROM nginx:alpine

# The whole app is a single self-contained HTML file.
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
