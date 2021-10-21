FROM node:latest

WORKDIR /web

COPY package.json .

COPY .env .

RUN yarn install

COPY ./public/ /web/public/ 

COPY ./src/ /web/src/ 

CMD [ "yarn", "start"]