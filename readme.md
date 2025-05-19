**Scenario :**

Voici **PseudoX**, le nouveau réseau social du moment, pas du tout inspiré d'un déjà existant.
Le problème : l'équipe de sécurité applicative est une équipe de stagiaires en stage de 3ᵉ, donc la sécurité, c'est pas leur fort.
Ils ont laissé une vulnérabilité critique permettant de **gagner accès** au serveur hébergeant le site.
Vous savez de source fiable qu'un mot de passe est stocké sur le serveur (c'est le flag), permettant d'accéder au portefeuille du CEO de PseudoX.
Votre objectif est de trouver ce mot de passe et de le tester avec le script `"cryptochecker.py"` pour se connecter au Wallet.

**Soyez fair-play** : ne lisez pas les différents fichiers et ne vous connectez pas directement au docker avec `"docker exec"`.
Pas de brute force nécessaire pour résoudre ce challenge.

L'unique indice que vous **aurez** est : **TOP 1 OWASP WEB**

---

**Créer l'image :**

```bash
docker build -t ctf .
```

**Créer le conteneur :**

```bash
docker run -d -p 6080:80 -p 6022:22 --name ctf_container ctf
```
