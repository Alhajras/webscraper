FROM node:19-alpine

WORKDIR /usr/src/app

COPY . .

RUN rm package-lock.json
RUN rm -r node_modules

RUN npm install


EXPOSE 4200

CMD ["npm", "start"]
