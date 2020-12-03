FROM node:14

WORKDIR /web

COPY package.json .

RUN ls

RUN yarn install

COPY ./src/ /web/src/

COPY ./public/ /web/public/

EXPOSE 3000

CMD [ "yarn", "start" ]