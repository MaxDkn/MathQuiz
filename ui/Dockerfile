# Étape 1 : Image de développement
FROM node:20 AS dev

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
# Copier tout le projet
COPY . .  

EXPOSE 3000

CMD ["npm", "start"]

#  ------------------PRODUCTION------------------
# Étape 1 : Build de l'application React
#  FROM node:20 AS build

#  WORKDIR /app
#  COPY package.json package-lock.json ./
#  RUN npm install
#  COPY . .
#  RUN npm run build

# Étape 2 : Serveur Nginx pour servir les fichiers statiques
#  FROM nginx:alpine

# Copie du build React vers Nginx
#  COPY --from=build /app/build /usr/share/nginx/html

# Copie de la configuration Nginx personnalisée
#  COPY nginx.conf /etc/nginx/conf.d/default.conf

#  EXPOSE 80

#  CMD ["nginx", "-g", "daemon off;"]