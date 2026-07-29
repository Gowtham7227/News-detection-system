# ==============================================================================
# Production-ready Dockerfile for React/Vite Frontend
# ==============================================================================

# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install --frozen-lockfile || npm install

COPY . .

RUN npm run build

# Production runner stage with Nginx
FROM nginx:1.25-alpine AS runner

# Remove default nginx config and replace with our SPA + proxy config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
