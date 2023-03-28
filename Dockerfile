FROM node:14

RUN mkdir app
COPY . /app
WORKDIR /app

RUN yarn install

CMD [ "yarn", "deploy" ]
