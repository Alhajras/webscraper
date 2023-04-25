FROM node:19-alpine

WORKDIR /usr/src/app

COPY . .

# Have to remove those files otherwise there is an error installing packages
RUN rm package-lock.json
RUN rm -r node_modules

RUN npm install


EXPOSE 4200

CMD ["npm", "start"]
