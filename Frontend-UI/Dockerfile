# =========================================
# Stage 1: Build the React/Vite application
# =========================================

FROM node:24-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files first
# This allows Docker to cache npm dependencies
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the Vite application
RUN npm run build


# =========================================
# Stage 2: Serve the application with Nginx
# =========================================

FROM nginx:alpine

# Remove the default Nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy our Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the production build from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx listens on port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]