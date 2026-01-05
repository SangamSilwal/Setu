# Use Node.js 20-alpine as the base image
FROM node:20-alpine AS base

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /app

# Copy package.json and pnpm-lock.yaml
COPY Frontend/package.json Frontend/pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy the rest of the frontend code
COPY Frontend/ .

# Set environment variables for build
ENV NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Build the Next.js application
RUN pnpm build

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["pnpm", "start"]
