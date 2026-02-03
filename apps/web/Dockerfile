FROM node:20-alpine AS deps
WORKDIR /app/apps/web
COPY apps/web/package.json /app/apps/web/package.json
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /app/apps/web
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY --from=deps /app/apps/web/node_modules /app/apps/web/node_modules
COPY apps/web /app/apps/web
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app/apps/web
ENV NODE_ENV=production
COPY --from=builder /app/apps/web/.next/standalone /app/apps/web
COPY --from=builder /app/apps/web/.next/static /app/apps/web/.next/static
COPY --from=builder /app/apps/web/public /app/apps/web/public
EXPOSE 3000
CMD ["node", "server.js"]
