FROM node:18-alpine
WORKDIR /app

COPY . .
RUN npm install

# Provide your GCP service account JSON key (keyfile.json) via Docker context or bind-mount
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/keyfile.json

EXPOSE 3001
CMD ["node", "gcs-server.js"]
FROM node:18-alpine as build
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build"]
