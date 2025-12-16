# ===== STAGE 1: BUILD =====
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
# Если падает на install, можно добавить --legacy-peer-deps
RUN npm install 
COPY . .
RUN npm run build && ls -la /app/dist > /build-log.txt

# ===== STAGE 2: NGINX =====
FROM nginx:stable-alpine

# 1. Удаляем вообще ВСЁ из папки конфигов, чтобы не было конфликтов
RUN rm -rf /etc/nginx/conf.d/*

# 2. Удаляем дефолтный HTML
RUN rm -rf /usr/share/nginx/html/*

# 3. Копируем билд (React)
COPY --from=build /app/dist /usr/share/nginx/html

# 4. Копируем ваш конфиг
# Убедитесь, что файл nginx.conf лежит РЯДОМ с Dockerfile в папке проекта!
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 5. Исправляем права доступа (иногда Nginx не может прочитать файлы root-а)
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]