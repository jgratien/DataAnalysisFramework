Historian Batch Extractor
=========================

Au sein d’IFPEN les données issues des capteurs sont stockées dans une base Historian. Celle-ci ne dispose toujours pas (version actuelle 5.5) d'API d'interrogation Web Service.
Il a donc été décidé d'extraire toutes les données afin de les intégrer dans la base ChroniX du cluster Hadoop. Pour ce faire les solutions à base d'ODBC ne sont pas assez performantes ni fiables pour garantir un export complet.
L'idée est donc de s'appuyer sur les API C Historian (sensées être plus efficaces), dans un programme batch d'extraction. Ce programme étant appelé depuis un programme Java (pour gérer les stats, la base de données des exports réussis et surtout la parallélisation des traitements).

Structure du projet
-------------------

- compilers : solution et projets au sens visual studio + répertoires de compilation
- auxiliaries : répertoire des bibliothèques complémentaires
	- log4cpp-1.1.3 : bibliothèque de log (parametrable et conviviale)
	- googletest : bibliothèque de tests automatisés
- resources : documentation complémentaire, diagrammes UML, etc.
- hbe_exe : répertoire des sources (cpp et hpp) du programme
- hbe_tests : répertoire des sources des tests automatisés

Gestion des sources
-------------------

Le projet est géré en version avec SVN : TODO


Pré-requis
----------

Pour développer historian batch extractor, il vous faudra avoir installé :
- Historian v5.5 : à demander à la DSI (JC Hunault)
- Visual Studio 2015 (min) : DSI ou Community version chez Microsoft
- CMake : <https://cmake.org/download/>


Gestion des logs
----------------

Les logs (paramétrables)sont gérés par la bibliothèque <http://log4cpp.sourceforge.net/>. Une configuration par défaut est réalisée, mais on peut la changer en fournissant un fichier `log4cpp.properties` via la commande :
```
MiscUtils::setLogFile("c:/test/log.properties");
```

Ensuite pour ajouter des logs, il faut récupérer un logger (objet de l'api log4cpp classe `Category`) :
```
LOG log = LOG_CREATE;
```

Puis de logguer en choisissant le niveau (DEBUG, INFO, WARN, ERROR, ...) via l'utilisation de la bonne fonction :
```
log.debug("Running extractor");
...
log.info("Successfull extraction");
...
log.error("Error met !!!")
```

Pour obtenir plus d'info (nom du fichier et n° de ligne concerné), on peut s'appuyer sur la macro `LOG_MSG` :
```
log.debug(LOG_MSG("Improved message (with file name and line number"));
```

Dans le cas où on veut simplement écrire une ligne, les macros suivantes permettent de se passer de la déclaration / instanciation du logger :
```
LOG_DEBUG("Simple use of logger / level DEBUG"); // => inclut LOG_MSG et est désactivé en compilation Release
LOG_INFO("Simple use of logger / level INFO");
LOG_WARN("Simple use of logger / level WARN");
LOG_ERROR("Simple use of logger / level ERROR");
```

Tests automatisés
-------------------

Les tests automatisés s'appuient sur la bibliothèque googletest : <https://github.com/google/googletest>

Ils sont intégrés à Visual Studio (en natif à partir de la version 2017), via l'outil "Google Test Adapter" (disponible dans le VS MarketPlace => "Extensions et mises à jour").

Les tests ajoutés au projet `hbe_tests` sont automatiquement détectés par l'outil "Google Test Adapter" et peuvent être lancés depuis celui-ci, ou en exécutant le programme `be_tests.exe` (on peut le lancer depuis VS : `Ctrl+F5` ou `F5`).

**IMPORTANT** : Pour que les tests puissent voir toutes les classes et méthodes du programme batch extractor, il faut intégrer tous les sources du programme dans le projet de test (liens vers les fichiers).

Un test simple ressemble à ceci :

```
#include "gtest/gtest.h"
#include "batch_extractor.hpp"

#include "misc.hpp"

namespace historian
{
	TEST(MiscTests, ToEpoch)
	{
		LOG_INFO("start of toEpoch test");
		EXPECT_EQ(MiscUtils::toEpoch(2019, 9, 11, 17, 53, 15), 1568217195);
		LOG_INFO("end of toEpoch test");
	}
}
```

Pour plus d'information sur l'api googletest :
- <https://github.com/google/googletest/blob/master/googletest/README.md>
- <https://www.ibm.com/developerworks/aix/library/au-googletestingframework.html>

