ARG ECR_REGISTRY
FROM ${ECR_REGISTRY}/node:20.11-alpine3.19 AS base

RUN apk add --no-cache tzdata

#RUN npm install -g npm@latest

ENV NEXT_TELEMETRY_DISABLED 1

FROM base as packages

WORKDIR /web

COPY package.json .

RUN npm install --frozen-lockfile


FROM base as builder
WORKDIR /web

ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

COPY --from=packages /web/ .
COPY . .

RUN npx update-browserslist-db@latest
RUN npm run build


FROM base as production

ENV PORT 3002

ENV TZ UTC
RUN ln -s /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone

RUN npm -g add pm2 && npm cache verify

WORKDIR /web
COPY --from=builder /web/public ./public
COPY --from=builder /web/.next/standalone ./
COPY --from=builder /web/.next/static ./.next/static

COPY docker/pm2.json ./pm2.json
COPY docker/entrypoint.sh /entrypoint.sh
RUN tr -d '\r' < /entrypoint.sh > /entrypoint-unix.sh && mv /entrypoint-unix.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 3002
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
