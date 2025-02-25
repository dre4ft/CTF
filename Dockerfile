# Utiliser une image de base Ubuntu
FROM ubuntu:latest

# Mettre à jour les paquets et installer les utilitaires de base
RUN apt-get update && apt-get install -y \
    apt-utils \
    curl \
    wget \
    vim \
    git \
    python3

# Installer Apache
RUN apt-get install -y apache2

# Installer PHP et les modules couramment utilisés
RUN apt-get install -y php libapache2-mod-php php-mysql php-cli php-curl php-gd php-mbstring php-xml php-zip

# Installer MySQL Server
RUN apt-get install -y mysql-server

# Configurer Apache pour qu'il démarre automatiquement
RUN update-rc.d apache2 defaults

# Exposer le port 80 (port par défaut d'Apache)
EXPOSE 80

# Démarrer Apache et MySQL lors du lancement du conteneur
CMD service mysql start && service apache2 start && tail -f /var/log/apache2/access.log


# Optionnel: Définir le répertoire de travail
WORKDIR /var/www/html/
