# **Stage 2020 : Évaluation des base de donnée de type Série Temporelle**

* [Introduction](#introduction)
* [Structure des répertoires](#structure-des-répertoires)
* [Installation des dépendances en commun](#installation-des-dépendances-en-commun)
* [Préparation des donnnées](#préparation-des-données)
* [Évaluation de MongoDB](#evaluation-de-mongodb)
* [Évaluation de InfluxDB](#evaluation-de-influxdb)

# Introduction


# Structure des répertoires

    .
    ├── MongoDBNotebook         # Notebook fichiers pour tester la performance de mongoDB 
    ├── TimeSeriesTools         # Python fichiers pour les functions communs
    └── README.md


# Installation des dépendances en commun

### Installer `Anaconda3` 
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
### Installer `kafka` 
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

Pour utiliser kafka dans script python, il faut installer le package `kafka-python` avec lignes commande suivante : 

```bash
> pip install kafka-python
```
**Remarque** : N'installer pas le package `kafka`, c'est l'ancienne version.

#### Tester le service kafka
 - kafka zookeeper : 
```bash
> bin/zookeeper-server-start.sh config/zookeeper.properties
```
 - kafka service
```bash
> bin/kafka-server-start.sh config/server.properties
```

#### Tester kafka-python 

```python
import kafka
from kafka import KafkaProducer, KafkaConsumer
```

### Installer `jaeger`
 `jeager` est un système de traçage distribué publié en open source par Uber Technologies. C'est une extension facile à installer et il est principalement utilisé pour l'optimisation des performances / latence. Vu que les bases de données nous allons
 
est une solution globale et faisable pour évaluer tous les types de bases de données. C'est une extension qui peut collaborer avec les codes python et affiche les résultats dans un Web UI. 
 
Télécharger l'archive pour linux dans la [page officiel](https://www.jaegertracing.io/download/) et désarchiver le package.

#### Installer le client python
Pour utiliser jaeger en python, faut installer son client python et sa dépendance avec la ligne commande suivante : 

```bash
pip install 
pip install opentracing-instrumentation
```


## Information du système global :
| Nom | Version |
| ---- | ----:|
| CentOS Linux | 7.7.1908|
| jre | 1.8.0_222-ea|
| python | 3.7.6 |
| openssl | 1.0.1e | 

### Information des dépendances en commun :
 | Nom | Version |
| ---- | ----:|
| Anaconda3 | 2020.02 | 
| kafka | 2.4.1 |
| kafka-python | 2.0.1 |
| jeager | 1.17.0 |
| jaeger-client | 4.3.0|
| opentracing-instrumentation | 3.2.1 |

# Préparation des données
Objective de cette partie est récoupérer les données viennent de différentes ressourceses, réparer les fichiers corruptible qui contient des données et les transférer dans les topic via kafka producer.

## Resources et formats des données
* smaritGrid
  - format des fichiers originaux : fichier .csv 
  - exemple des données originales : 
    | timestamp | tagname | value | quality | 
    | ---- | ----| ---- | ---- |
    | 01/01/2019 09:15:12 | CRY.CENTRALE_SOLAIRE.CRY_act_prod_pow | 1.000000000 | 100.0 |
  - nombre de colonne : 4
  
* fuites d'éolienne
  - format des fichiers originaux : fichier .xls
  > Les fichiers .xls d'origine sont corruptibles donc ils pouvent pas être utilisé directement. Utiliser le script `../TimeSeriesTool/recover_xls_files.py` pour générer les fichiers .csv corrects avant lire les données.
  - exemple des données originales : 
  
    | Heure | Temps écoulé | 4069 state | ... | HP_Delta_iCH4_2min | HP_Delta_iCH4_5min | 
    | ---- | ----| ---- | ---- | ---- | ---- |
    | 02/10/2019 09:11:02 | 0 | 1,010000	 | ... | 0,00 | 0,00 |
 
  - nombre de colonne : 51
* elements 
  - format des fichiers originaux : fichier .bson 
  
  > BSON, abréviation de Binary JSON, est une sérialisation codée en binaire de documents de type JSON. Ce type de fichier est utilisé    principalement comme stockage de données et format de transfert de données par le réseau dans la base de données MongoDB. C'est un format binaire permettant de représenter des structures de données simples et des tableaux associatifs.
Pour importer le fichier .bson dans une seule collection d'une base de MongoDB, utiliser la ligne commande suivante :
  ```bash
  > mongorestore --drop -d test -c elements /home/ymo/local/work-ref/data/elements/elements.bson
  ```
  Le résultat s'affiche dans la console :
  ```bash
  977448 objects found
  2020-03-20T11:07:50.564+0100    Creating index: { key: { _id: { $numberInt: "1" } }, name: "_id_", ns: "test.elements" }
  Error creating index test.elements: 73 err: "cannot write to 'test.system.indexes'"
  Aborted (core dumped)
  ```
  **Remarque** : Faut taper ce command directement dans un terminal, même si c'est un command seulement pour l'opération de MongoDB, ça fonctionne pas dans mongoshell.
  - exemple des données originales : 
  ```bash
  {
        "_id" : ObjectId("5d89cfd59c285126bb089f75"),
        "data" : {
                "Elements" : {
                        "NO" : 0,
                        "NO2" : 0,
                        "NH3" : 0,
                        "Soot" : 20.799999237060547,
                        "H2O" : null,
                        "O2" : null,
                        "counter" : 198
                },
                "Naneos" : {
                        "NaneosTime" : 0,
                        "ParticuleNumber" : 0,
                        "ChargerDiffusionCurrent" : 0,
                        "ChargerHighVoltage" : 0,
                        "ElectroMeterReading" : 0,
                        "ElectroMeterAmplitude" : 0,
                        "Temperature" : 0,
                        "RelativeHumidity" : 0,
                        "BarometricPressureInHousing" : 0,
                        "Status" : 0
                }
        }
        "updatedAt" : ISODate("2019-09-24T08:12:05.357Z"),
        "createdAt" : ISODate("2019-09-24T08:12:05.358Z")
   }
  ```
  - nombre de élément : 19

# Evaluation de MongoDB
> Cette partie montre les démarches pour tester six différentes opérations dans une mongo base. Les sources de données sont smartGrid et éolienne.  

## Installation et configuration
Télécharger et désarchiver le package de `mongoDB` pour Centos avec ligne commande : 
```
wget http://downloads.mongodb.org/linux/mongodb-linux-x86_64-rhel70-4.2.3.tgz
tar -xvfz mongodb-linux-x86_64-rhel70-4.2.3.tgz
```
Si mongodb est installé avec l'archive, il faut créer le fichier de configuration manuellement dans le répertoire `bin` et le nommer `mongodb.conf`.
Voici [format de fichier](https://github.com/mongodb/mongo/blob/master/rpm/mongod.conf).

Configurer le fichier mongodb.conf pour éviter le problème de privilège :
1. `path`: /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/logs/mongodb.log
2. `dbPath` : /work/weiy/local/mongodb-linux-x86_64-rhel70-4.2.3/bin/data/db
3. `pidFilePath`: /work/weiy/local/var/run/mongodb/mongod.pid
4. `port`: 28018 
5. `authorization`: disabled

### Installer mongodb client

Pour communiquer avec MongoDB en utilisant son protocole TCP par défaut sur le port 27017, il a besoin d'un client MongoDB.
Ouvrir un terminal et taper la ligne commande suivante:
```bash
> sudo apt install mongodb-clients
```

Vérifier l'installation : 

```bash
> mongo --version
```

### Installer le client python

Installer le package `pymongo` (le client python pour mongoDB) avec ligne commande :
```
python -m pip install pymongo
```
>Pour vérifier les données dans mongoDB, [`mongo-compass`](https://www.mongodb.com/products/compass) est une GUI officielle qui permet des interactions avec mongoDB. 

## Connexion de mongodb
Ouvrir le terminal et aller dans le répertoire `bin` de mongodb.
Lancer mongoDB selon le fichier de configuration avec ligne commande : 
```
./mongod --config mongodb.conf
```
Pour lancer mongo shell, utiliser ligne commande :
```
./mongo --port 28018
```
Pour lancer le service de mongodb sans fichier de configuration, utiliser ligne commande :
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
    - valeur par défaut : "eolienne_DT"
 - `--collection`: indiquer le nom de la collection désirée
    - valeur par défaut : "eolienne_DT"
 - `--tracer`: indiquer le nom du tracer à initialiser
    - valeur par défaut : "mongodb_test_eolienne_1_jour"
 - `--domain`: indiquer l'address du domaine pour connecter à la base de mongodb
    - valeur par défaut : "localhost"
 - `--port`: indiquer la porte pour connecter à la base de mongodb
    - valeur par défaut : "27017"
 - `--function`: indiquer le nom de la fonction à tester, il n'a pas de valeur par défaut donc cet paramètre est **obligatoire**. 

**Remarque** : 
- Sauf que le numéro de la porte est int, toutes les types des paramètres d'entrée sont string.
- Les paramètres suivantes sont optionnels pour toutes les functions : 
    - <--tracer>
    - <--collection>
    - <--domain>
    - <--port>

Dans le script python il y a 6 fonctions de test à choisir :

- `test_insert_bulk` : Mesurer le temps pour insérer toutes les données collectées dans la base de donnée à la fois.
  - paramètres optionnels: <--topic>
- `test_insert_one` : Mesurer le temps pour insérer toutes les données collectées dans la base de donnée ligne par ligne.
  - paramètres optionnels: <--topic>
- `find_some_data` : Mesurer le temps pour trouver les données correspondantes à la requête dans la base de donnée.
  - paramètres optionnels: <--query>
- `find_all_data` : Mesurer le temps pour lire toutes les données dans la base de donnée.

- `update_some_data` : Mesurer le temps pour modifier les données correspondantes à la requête dans la base de donnée.
  - paramètres optionnels: <--query>,<--value>
- `update_all_data`: Mesurer le temps pour modifier toutes les données dans la base de donnée.
  - paramètres optionnels: <--query>,<--value>
  
### Code exemple 
Pour récupérer toutes les données venant d'un topic de kafka, et mesurer le temps d'insertion ligne par ligne dans la base de mongodb, il faut préciser au minimun un paramètre : le nom de la function à tester. Les autres cinq paramètres sont optionnels dans cette function pour indiquer le source des données (c'est à dire lire les données dans quel topic), la destination des données (insérer les données dans quelle collection dans la base de données), le nom de tracer pour visualiser les informations détailles de cette opération, le domain et la porte pour connecter à la base de mongodb (ça dépend le fichier de configuration).
Dans le terminal : 

```bash
> python mongodb_test.py --function test_insert_one --topic "eolienne_DT" --collection "eolienne_DT" --domain "localhost" --port 27017 --tracer "test_insert_lines"
```
Dans le notebook :

```python
%run ../TimeSeriesTools/mongodb_test.py --function test_insert_one --topic "eolienne_DT" --collection "eolienne_DT" --domain "localhost" --port 27017 --tracer "test_insert_lines"
```

Pendant l'exécution du script, une ligne de données incorrecte est insérée pour tester la validation de données.
Une message s'affiche dans la console qui indique l'index de ligne et les champs des données invalides: 

```bash
line:  51288 , position:  0 , require  Heure
line:  51288 , position:  1 , require  Temps écoulé
line:  51288 , position:  12 , require  MWD Wind Speed
```
Après l'exécution du script, un tracer qui contient deux sous-span (un pour l'étape de la collection des données venant du topic, l'autre pour l'étape de l'insertion des donnnées) est signalé. Les informations et les barres intéractives sont ensuite disponibles sur wen UI de jeager (http://localhost:16686 par défaut).

```bash
Reporting span bb054b92a0316e58:16b5632098eb1b2:44a4e06b3541cefc:1 test_insert_lines.collect_data
Reporting span bb054b92a0316e58:d0fa76c1b3f2abed:44a4e06b3541cefc:1 test_insert_lines.insert_one
51289  documents inserted
Reporting span bb054b92a0316e58:44a4e06b3541cefc:0:1 test_insert_lines.test_line_insertion
```

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

## Installation et configuraion
#### En cas d'utiliser systèm Ubuntu, ajoutez le référentiel InfluxData avec les commandes suivantes:
```bash
> wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```
Installer InfluxDB directement avec sudo apt-get : 
```bash
sudo apt-get update && sudo apt-get install influxdb
```
#### En cas d'installer InfluxDB en utilisant l'archive :
Télécharger le package dans la [page officielle](https://portal.influxdata.com/downloads/) et le désarchiver : 

```bash
wget https://dl.influxdata.com/influxdb/releases/influxdb-1.7.10-static_linux_amd64.tar.gz
tar xvfz influxdb-1.7.10-static_linux_amd64.tar.gz
```
### Configurer le fichier de config
La location du fichier de config est `/etc/influxdb/influxdb.conf`.

Configurer les paramètres suivants: 

`meta`
- dir = "/home/ymo/local/var/influxdb/meta"
  
`data`
- dir = "/home/ymo/local/var/influxdb/data"
- wal-dir = "/home/ymo/local/var/influxdb/wal"

`http` : 
- enabled = true
- flux-enabled = true
- bind-address = ":8086"

### Tester l'installation de InfluxDB

Lancer InfluxDB selon le fichier de configuration avec command suivant:
```
> sudo influxd -config /etc/influxdb/influxdb.conf
```

### Installer le client python
Pour utiliser le client python de l'InfluxDB, il faut installer le package `influxdb` en utilisant la ligne commande suivante : 

```bash
> pip install influxdb

```


## Information des dépendances 
| Dépendances | Version |
| ------ | -----------: |
| InfluxDB | 1.7.0 |
| influxdb (client python) | 5.2.3 |
