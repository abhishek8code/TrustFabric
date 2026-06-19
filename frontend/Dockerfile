FROM node:20-alpine
WORKDIR /app
COPY package.json tsconfig.json vite.config.ts tailwind.config.js postcss.config.js index.html ./
COPY src ./src
RUN npm install
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
