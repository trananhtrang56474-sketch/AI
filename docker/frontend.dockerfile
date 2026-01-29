# === 构建阶段 ===
FROM node:22-alpine AS build-stage

WORKDIR /app

# 👇 变化：加上 frontend/ 前缀
COPY frontend/package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

# 👇 变化：只拷贝 frontend 代码
COPY frontend/ .
RUN npm run build

# === 部署阶段 ===
FROM nginx:stable-alpine AS production-stage

COPY --from=build-stage /app/dist /usr/share/nginx/html

# 👇 变化：nginx.conf 现在就在 deploy 目录下（当前上下文），所以直接 COPY
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]