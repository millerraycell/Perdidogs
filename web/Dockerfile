FROM node:14

WORKDIR /web

COPY package.json .

COPY yarn.lock .

RUN yarn install

ADD public/ /web/public

ADD src/ /web/src

RUN ls

EXPOSE 3000

CMD [ "yarn", "start" ]