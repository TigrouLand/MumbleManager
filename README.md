# MumbleManager

MumbleManager est un outil permettant de gérer les clients connectés sur un serveur vocal Mumble.
Pour l'heure, celui-ci communique par le biais d'une base de données MongoDB.

## Installation

### Configuration Mumble
Rendez-vous dans le fichier de configuration de votre serveur vocal Mumble. Premièrement, définissez sur quelle interface réseau Ice doit écouter. En l'occurence, cette configuration écoutera sur l'interface loopback `127.0.0.1` sur le port `6502`. Ces valeurs sont bien entendue modifiables. 
```
ice="tcp -h 127.0.0.1 -p 6502"
```
Dans un second temps, il est **fortement recommandé** de définir des identifiants de connexion pour sécuriser l'accès à la gestion de votre serveur vocal Mumble. Par principe, cette étape devient **obligatoire** si Ice écoute sur une interface réseau publique, accessible sans restriction depuis l'extérieur.
```
icesecretread=
icesecretwrite=
```
### Installation MumbleManager
Premièrement, vous devez installer Python 3 ainsi que PIP 3. Généralement disponibles dans les dépôts des principaux systèmes d'exploitations Linux, il vous suffit d'exécuter cette commande avec votre gestionnaire de paquet : `apt install python3 python3-pip`. Le paquet `apt install libbz2-dev` sera de même requis pour la suite.

Ensuite, clonez ce dépôt avec Git, via la commande `git clone https://github.com/TigrouLand/MumbleManager.git`. Rendez-vous dans le répertoire `MumbleManager`, et exécutez la commande suivante afin d'installer les modules Python nécessaires : `pip3 install Ice` et `pip3 install zeroc-ice`.

### Configuration MumbleManager
La configuration de MumbleManager s'effectue exclusivement via les variables d'environnement :
* `ICE_KEY` : identifiants que vous avez défini dans la première étape
* `ICE_PROXY` : adresse proxy de Ice (exemple : `Meta:tcp -h 127.0.0.1 -p 6502` - notez le préfixe `Meta:`)
* `ICE_CALLBACK` : adresse d'écoute de retour (exemple : `tcp -h 127.0.0.1`)