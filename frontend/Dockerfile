# --- Build stage ---
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Baked in at build time. Leave empty so requests go to the same origin ("/api/..."),
# which nginx (below) reverse-proxies to the backend container.
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

# --- Runtime stage ---
FROM nginx:alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 127.0.0.1, not localhost: this image's busybox wget resolves "localhost" to the IPv6
# loopback (::1) first and doesn't fall back to IPv4, but nginx only binds 0.0.0.0 -- that
# made the healthcheck report unhealthy despite the server actually serving requests fine.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
