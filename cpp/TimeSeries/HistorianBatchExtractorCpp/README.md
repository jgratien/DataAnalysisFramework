Historian Batch Extractor
=========================

Au sein d�IFPEN les donn�es issues des capteurs sont stock�es dans une base Historian. Celle-ci ne dispose toujours pas (version actuelle 5.5) d'API d'interrogation Web Service.
Il a donc �t� d�cid� d'extraire toutes les donn�es afin de les int�grer dans la base ChroniX du cluster Hadoop. Pour ce faire les solutions � base d'ODBC ne sont pas assez performantes ni fiables pour garantir un export complet.
L'id�e est donc de s'appuyer sur les API C Historian (sens�es �tre plus efficaces), dans un programme batch d'extraction. Ce programme �tant appel� depuis un programme Java (pour g�rer les stats, la base de donn�es des exports r�ussis et surtout la parall�lisation des traitements).

Structure du projet
-------------------

- compilers : solution et projets au sens visual studio + r�pertoires de compilation
- auxiliaries : r�pertoire des biblioth�ques compl�mentaires
	- log4cpp-1.1.3 : biblioth�que de log (parametrable et conviviale)
	- googletest : biblioth�que de tests automatis�s
- resources : documentation compl�mentaire, diagrammes UML, etc.
- hbe_exe : r�pertoire des sources (cpp et hpp) du programme
- hbe_tests : r�pertoire des sources des tests automatis�s

Gestion des sources
-------------------

Le projet est g�r� en version avec SVN : TODO


Pr�-requis
----------

Pour d�velopper historian batch extractor, il vous faudra avoir install� :
- Historian v5.5 : � demander � la DSI (JC Hunault)
- Visual Studio 2015 (min) : DSI ou Community version chez Microsoft
- CMake : <https://cmake.org/download/>


Gestion des logs
----------------

Les logs (param�trables)sont g�r�s par la biblioth�que <http://log4cpp.sourceforge.net/>. Une configuration par d�faut est r�alis�e, mais on peut la changer en fournissant un fichier `log4cpp.properties` via la commande :
```
MiscUtils::setLogFile("c:/test/log.properties");
```

Ensuite pour ajouter des logs, il faut r�cup�rer un logger (objet de l'api log4cpp classe `Category`) :
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

Pour obtenir plus d'info (nom du fichier et n� de ligne concern�), on peut s'appuyer sur la macro `LOG_MSG` :
```
log.debug(LOG_MSG("Improved message (with file name and line number"));
```

Dans le cas o� on veut simplement �crire une ligne, les macros suivantes permettent de se passer de la d�claration / instanciation du logger :
```
LOG_DEBUG("Simple use of logger / level DEBUG"); // => inclut LOG_MSG et est d�sactiv� en compilation Release
LOG_INFO("Simple use of logger / level INFO");
LOG_WARN("Simple use of logger / level WARN");
LOG_ERROR("Simple use of logger / level ERROR");
```

Tests automatis�s
-------------------

Les tests automatis�s s'appuient sur la biblioth�que googletest : <https://github.com/google/googletest>

Ils sont int�gr�s � Visual Studio (en natif � partir de la version 2017), via l'outil "Google Test Adapter" (disponible dans le VS MarketPlace => "Extensions et mises � jour").

Les tests ajout�s au projet `hbe_tests` sont automatiquement d�tect�s par l'outil "Google Test Adapter" et peuvent �tre lanc�s depuis celui-ci, ou en ex�cutant le programme `be_tests.exe` (on peut le lancer depuis VS : `Ctrl+F5` ou `F5`).

**IMPORTANT** : Pour que les tests puissent voir toutes les classes et m�thodes du programme batch extractor, il faut int�grer tous les sources du programme dans le projet de test (liens vers les fichiers).

Un test simple ressemble � ceci :

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

