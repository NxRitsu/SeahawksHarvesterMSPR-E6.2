## 🌐 Présentation du Projet

### 🎯 Objectif du Projet "Seahawks Monitoring"

La société "NFL IT" souhaite améliorer son efficacité opérationnelle en concevant une solution de maintenance à distance. Le projet vise à collecter des informations techniques et à assurer la maintenance à distance des réseaux locaux des franchises de la NFL.

### Seahawks Harvester

Effectue un scan réseau du réseau local du client.
Fournis un tableau de bord avec des informations telles que:
* L'adresse IP locale
* Le nombre de machines connectées en LAN
* Affichage du dernier scan réseau (machines + ports)
* Latence de l’accès à Internet
  
Cette application créée un fichier XML comprenant toutes les inforamtions du dernier scan réseau, ce fichier XML est ensuite envoyé sur le serveur voulu via sFTP.
Présenté sous forme d’une application graphique Python déployée sur un environnement Debian 12.
 
## 🚀 Comment utiliser l’Application Seahawks Harvester ?

⚠️ Uniquemnent sous Windows & Python 3.12 ⚠️

1. Télécharger les fichiers :

```
git clone https://github.com/NxRitsu/SeahawksHarvesterMSPR-E6.2
```

2. Exécuter la commande suivante :
```
pip install python-nmap ping3 psutil pysftp
```
Cela va alors télécharger tout les modules python nécessaire au bon fonctionnement

3. Générer une paire de clés SSH :
```
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
```
```
ssh-copy-id -i ~/.ssh/id_rsa.pub <user_ssh>@<adresse_ip>
```

4. Exécutez cette commande pour lancer l'application graphique Python :

```
python3 Harvester.py
```
Il est aussi possible de créer un fichier "Harvester.bat" permettant d'avoir un raccourci sur le bureau : 

```
@ECHO OFF
cd <emplacement du script>
python3 Harvester.py
pause
```

Cela ouvrira l’application graphique Python, affichant l'adresse IP locale avec un bouton permettant d’effectuer le scan réseau.

En cliquant sur le bouton, le scan se lance, affichant le résultat du scan réseau ainsi que la latence WAN.
