FROM node:18.16.1-bullseye

ENV NODE_ENV $NODE_ENV

WORKDIR /usr/src/app

RUN chown node:node ./

USER node

RUN mkdir -p vue

COPY --from=project_root --chown=node:node vue/public ./vue/public
COPY --chown=node:node ./src ./vue/src

COPY --from=project_root --chown=node:node babel.config.js jsconfig.json package.json package-lock.json vue.config.js ./

RUN npm ci && npm cache clean --force

RUN npm run build

COPY --chown=node:node --chmod=775 ./entrypoint.sh ./

ARG NODE_ENV=production

ENTRYPOINT ["./entrypoint.sh"]
