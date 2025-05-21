FROM node:lts-alpine AS BUILD
WORKDIR /code
COPY ./frontend/package*.json ./
RUN npm install
COPY ./frontend .
RUN npm run build

FROM nginx
WORKDIR /app
COPY --from=BUILD /code/dist /app
COPY ./frontend/nginx.conf /etc/nginx/nginx.conf
EXPOSE 80