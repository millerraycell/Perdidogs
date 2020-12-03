FROM node:14

WORKDIR /web

COPY package.json .

RUN yarn install

COPY src/ .

COPY public/ .

CMD [ "yarn", "start" ]

EXPOSE 3000

