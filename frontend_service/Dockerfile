FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./

RUN npm install 
COPY . .
RUN npm run build

FROM nginx:stable-alpine

RUN rm -rf /etc/nginx/conf.d/*

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]