FROM node:20-alpine

# Install dependencies
RUN apk add --no-cache libc6-compat curl

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (use npm install since no lock file)
RUN npm install

# Copy application code
COPY . .

# Generate Prisma client
RUN npx prisma generate

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["npm", "run", "dev"]
