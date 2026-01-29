# === 构建阶段 ===
FROM node:18-alpine AS build-stage

WORKDIR /app

# 1. 直接把所有前端代码拷进去 (不管有没有混入 node_modules)
COPY frontend/ .

# 🔥🔥 核心大招：强制删除可能拷进去的 Windows 依赖 🔥🔥
# 这一步能确保环境绝对干净！
RUN rm -rf node_modules package-lock.json

# 2. 重新安装纯净的 Linux 依赖
RUN npm install --registry=https://registry.npmmirror.com

# 3. 开始打包
RUN npm run build || (echo "❌ npm build failed" && exit 1)

# === 部署阶段 (保持不变) ===
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]