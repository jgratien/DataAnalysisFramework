# **Stage 2020 : Évaluation des base de donnée de type Série Temporelle**

* [Introduction](#introduction)
* [Installation des dépendances en commun](#installation-des-dépendances-en-commun)
* [Évaluation de MongoDB](#evaluation-de-mongodb)
* [Évaluation de InfluxDB](#evaluation-de-influxdb)

# Introduction



# Installation des dépendances en commun
### Pour installer `Anaconda3` : 
Télécharger le script (python 3.7) pour linux dans le [download page officiel](https://www.anaconda.com/distribution/#download-section). 
Exécuter le bash avec ligne commande : 
```bash
> sh Anaconda3-2019.03-Linux-x86_64.sh
```
Taper "yes" pour accepter la licence et préciser la location d'installation pour anaconda. 
Le script va modifier le contenu dans ~/.bashrc, donc il faut activer anaconda avec ligne command après l'installation:
```bash
> source ~/.bashrc
```
#### Tester anaconda
```bash
> conda list
```
### Pour installer `Kafka` : 
Télécharger l'archive et le désarchiver avec ligne commande suivante : 
```bash
> wget http://apache.crihan.fr/dist/kafka/2.4.1/kafka_2.12-2.4.1.tgz
> tar -xzfv kafka_2.12-2.4.1.tgz
```
Aller dans le répertoire `config` et configurer les fichiers.
* Dans le fichier `server.properties` : 
1. log.dirs=/home/ymo/local/var/kafka/logs 
2. zookeeper.connect=localhost:2181 (la porte par défaut est 2181, à modifier si besoin)
* Dans le fichier `zookeeper.properties` :
1. dataDir=/home/ymo/local/var/kafka/zookeeper
2. clientPort=2181 (la porte par défaut est 2181, à modifier si besoin)

#### Tester le service kafka
 - kafka zookeeper : 
```bash
> bin/zookeeper-server-start.sh config/zookeeper.properties
```
 - kafka service
```bash
> bin/kafka-server-start.sh config/server.properties
```
## Information du système global :
| Nom | Version |
| ---- | ----:|
| CentOS Linux | 7.7.1908|
| jre | 1.8.0_222-ea|
| python | 3.7.6 |

### Information des dépendances en commun :
 | Nom | Version |
| ---- | ----:|
| Anaconda3 | 2020.02 | 
| Kafka | 2.4.1 |
| jeager | 1.17.0 |

> `jeager` est une solution globale et faisable pour évaluer tous les types de bases de données. C'est une extension qui collabore avec les codes python et affiche les résultats dans un Web UI.
### Structure de la répertoire

    .
    ├── MongoDBNotebook         # Notebook fichiers pour tester la performance de mongoDB 
    ├── TimeSeriesTools         # Python fichiers pour les functions communs
    └── README.md


# Evaluation de MongoDB
> Cette partie montre les démarches pour tester six différentes opérations dans une mongo base. Les sources de données sont smartGrid et éolienne.  

## Installation et configuration
Télécharger et désarchiver le package de `mongoDB` pour Centos avec ligne commande : 
```
wget http://downloads.mongodb.org/linux/mongodb-linux-x86_64-rhel70-4.2.3.tgz
tar -xvfz mongodb-linux-x86_64-rhel70-4.2.3.tgz
```
Configurer le fichier mongodb.conf pour éviter le problème de privilège :
1. `path`: /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/logs/mongodb.log
2. `dbPath` : /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/data/db
3. `pidFilePath`: /work/weiy/local/var/run/mongodb/mongod.pid
4. `port`: 28018 
5. `authorization`: disabled

Installer le package `pymongo` (le client python pour mongoDB) avec ligne commande :
```
python -m pip install pymongo
```
>Pour vérifier les données dans mongoDB, [`mongo-compass`](https://www.mongodb.com/products/compass) est une GUI officielle qui permet des interactions avec mongoDB. 

## Connexion de mongodb
Ouvrir le terminal et aller dans le répertoire `bin` de mongodb.
Initialiser mongoDB selon le fichier de configuration avec ligne commande : 
```
./mongod --config mongodb.conf
```
Pour lancer mongo shell, utiliser ligne commande :
```
./mongo --port 28018
```
Pour lancer le service de mongodb, utiliser ligne commande :
```
./mongod --port 28018 --dbpath /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/data/db
```
Code exemple en python : 
```python
from pymongo import MongoClient,errors
client = MongoClient('localhost', 28018, serverSelectionTimeoutMS = 2000)
```
## Tester la performance

**Remarque** : Avant l’exécution du script, il faut d'abord lancer les services nécessaires :
 - kafka zookeeper : 
```bash
> bin/zookeeper-server-start.sh config/zookeeper.properties
```
 - kafka service
```bash
> bin/kafka-server-start.sh config/server.properties
```
 - mongoDB
```bash
> ./mongod --port 28018 --dbpath /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/data/db
```
 - jaeger
```bash
> ./jeager-all-in-one
```
 - mongo-compass (optionnel)
```bash
> ./mongo-compass
```


### Exécution des tests
Tous les fonctions de tests sont écrits dans le fichier `../TimeSeriesTools/mongodb_test.py`. Pour exécuter la fonction à tester, il faut utiliser les lignes commandes dans un terminal ou exécuter les cellules avec les paramètres d'entrée dans le fichier `../MongoDBNotebook/mongoDB_inference_test.ipynb` avec jupyter-notebook. 

Liste des paramètres d'entrée : 
 - `--query`: le string de la requête
   - valeur par défaut : '{"timestamp":{"$regex":"10:"}}'
 - `--value`: la requête des modifications des données sélectionnées
    - valeur par défaut : '{"$set":{"timestamp":"00/00/0000 00:00"}}
 - `--topic`: indiquer le nom du topic désiré
    - valeur par défaut : "eolienne_jour_1"
 - `--collection`: indiquer le nom de la collection désirée
    - valeur par défaut : "test_eolienne"
 - `--tracer`: indiquer le nom du tracer à initialiser
    - valeur par défaut : "mongodb_test_eolienne_1_jour"
 - `--function`: indiquer le nom de la fonction à tester, cet paramètre est **obligatoire**. 
 
Dans le script python il y a 6 fonctions de test à choisir :

- `test_insert_bulk` : Mesurer le temps pour insérer toutes les données collectées dans la base de donnée à la fois.
  - paramètres optionnels: `--topic`, `--collection`,`--tracer`
- `test_insert_one` : Mesurer le temps pour insérer toutes les données collectées dans la base de donnée ligne par ligne.
  - paramètres optionnels: `--topic`, `--collection`,`--tracer`
- `find_some_data` : Mesurer le temps pour trouver les données correspondantes à la requête dans la base de donnée.
  - paramètres optionnels: `--query`, `--collection`,`--tracer`
- `find_all_data` : Mesurer le temps pour lire toutes les données dans la base de donnée.
  - paramètres optionnels: `--collection`,`--tracer`
- `update_some_data` : Mesurer le temps pour modifier les données correspondantes à la requête dans la base de donnée.
  - paramètres optionnels: `--query`, `--value`, `--collection`,`--tracer`
- `update_all_data`: Mesurer le temps pour modifier toutes les données dans la base de donnée.
  - paramètres optionnels: `--query`, `--value`, `--collection`,`--tracer`
  
**Remarque** : Toutes les types des paramètres d'entrée sont string.

### Code exemple 

 
### Surveillance des tâches
Un span unique de tracer principal est initialisé avant le démarre de chaque fonction, ce span contient le temps d’exécution de la fonction, les tags et les logs.
Naviguer dans l'URL `http://localhost:16686/` (porte 16686 par defaut) pour acceder le Web UI de jaeger.
Choisir le nom de tracer à gauche et cliquer query pour trouver les informations dans le conteneur de ce tracer.

![test](/uploads/ea9513e752cfe4ba667e4475a813bdb9/test.png)





## Information des dépendances 
| Dépendances | Version |
| ------ | -----------: |
| mongoDB | rhel70-4.2.3 |
| pymongo | 3.0.1 |
| mongo-compass | 1.20.5 |


# Evaluation de InfluxDB

