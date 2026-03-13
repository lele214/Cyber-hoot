# TP 5 : Tooling

De tête, quelle est la commande complète pour lancer l'application ?

Et si on avait juste à taper `start` par exemple ?

## `make`

`make` est à l'origine un outil de **compilation incrémentale** : il permet de ne recompiler que les fichiers qui ont changé depuis la dernière compilation. C'est particulièrement utile pour les langages compilés comme le C ou le C++.

`make` existe depuis 1976, est souvent installé par défaut sur quasiment tous les systèmes Unix/Linux/macOS.

Exemple d'un makefile :

```makefile
# make ne recompilera hello que si hello.c a changé
hello: hello.c
    gcc -o hello hello.c
```

Dans ce TP, nous utiliserons `make` uniquement en tant comme **command runner** — c'est-à-dire pour regrouper des commandes courantes sous des noms courts. Nous n'utilisons pas ses fonctionnalités de compilation incrémentale.

Son fichier de configuration (`Makefile`) est versionné avec le reste du code — tout le monde a les mêmes commandes, dans la même version.

### command runner

Un projet logiciel implique de nombreuses commandes répétitives : installer les dépendances, lancer l'application, exécuter les tests, formater le code, nettoyer les fichiers temporaires, etc.

Sans outil dédié, ces commandes sont soit mémorisées par chaque développeur, soit éparpillées dans un README ou dans des scripts à droite à gauche. C'est source d'erreurs (mauvaise option oubliée, ordre des étapes inversé) et de friction : chaque nouveau membre de l'équipe doit lire la documentation pour savoir comment lancer le projet.

Un **command runner** résout ce problème : il centralise toutes les commandes du projet dans un fichier versionné, et permet de les exécuter avec une commande courte et mémorisable.

```bash
# Au lieu de :
uv run uvicorn src.web:app --reload --host 0.0.0.0 --port=8000

# On écrit simplement :
make run-dev
```

### Exemple : Makefile pour un projet C Hello World

Voir `examples/makefile/Makefile` pour un exemple minimal de Makefile dans le contexte d'un projet C.

Questions :

- lancer une premiere fois la commande `make build`, que se passe-t-il ?
- lancer `make build` une deuxieme fois, que remarquez-vous ?
- lancer `make` sans argument, que remarquez-vous ?
- existe-t-il une commande `make` pour lister toutes les recipes disponibles ?

### Exercice 1

- en vous inspirant de `examples/makefile/Makefile`, créer un makefile a la racine du projet avec une commande pour lancer le projet
- en option, rajouter une commande pour nettoyer le projet (supprimer le venv et les fichiers temporaires)
- en option, rajouter une option pour installer les dépendances de dev
- comment éviter que si un utilisateur écrive `make` sans argument que cela ne lance une commande involontairement ?

Lisez le blogpost suivant pour un exemple de Makefile intéressant <https://tech.davis-hansson.com/p/make/>

Modifier votre makefile grâce à ces nouveaux exemples.

(Je vous conseille de ne pas vous embeter avec le `.RECIPEPREFIX` pour le moment)

### Explication du Makefile du projet

```makefile
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
```

- `SHELL := bash` — force l'utilisation de bash (au lieu de `/bin/sh` par défaut)
- `.ONESHELL:` — exécute toutes les lignes d'une recette dans le même shell (sinon chaque ligne est un shell séparé, ce qui empêche les variables d'être partagées)
- `.SHELLFLAGS := -eu -o pipefail -c` — active le mode strict : `-e` stoppe en cas d'erreur, `-u` échoue sur les variables indéfinies, `-o pipefail` propage les erreurs dans les pipes

```makefile
.PHONY: install
install: ## Install prod dependencies
    uv sync --locked
```

- `.PHONY` déclare que la cible n'est pas un fichier — sans ça, si un fichier `install` existait dans le dossier, `make` ne lancerait pas la commande
- `## Install prod dependencies` est une convention pour générer automatiquement avec `make help`

---

### Les limites de `make` comme command runner

`make` a été conçu pour la compilation, pas pour lancer des commandes.

- **Les variables d'environnement** : `make` ne charge pas automatiquement un fichier `.env`. Il faut rajouter du code pour importer un `.env` ou exporter manuellement les variables.
- **Les arguments** : passer des arguments à une recette est peu intuitif — on utilise des variables `make new-migrate NAME=ma_migration` plutôt qu'une syntaxe naturelle.
- **`.PHONY`** : déclarer chaque cible comme `.PHONY` est verbeux et facile à oublier.
- **Le mode strict** : par défaut, `make` continue même si une commande échoue — il faut configurer explicitement bash en mode strict.

Un résumé des inconvénients de `make` : <https://github.com/casey/just#what-are-the-idiosyncrasies-of-make-that-just-avoids>

## `just`

`just` : <https://github.com/casey/just>, une alternative à `make`, écrite en rust

### Avantages de `just` par rapport à `make`

- **Arguments natifs** : les recettes acceptent des paramètres directement — `just new-migrate ma_migration` au lieu de `make new-migrate NAME=ma_migration`
- **Chargement automatique du `.env`** : `just` charge le fichier `.env` du projet automatiquement (avec `set dotenv-load`)
- **Pas de `.PHONY`** : toutes les recettes sont "phony" par défaut — pas de déclaration à oublier
- **Espaces ou tabulations** : indifférent à l'indentation, fini les bugs de tabulation
- **Mode strict par défaut** : `just` utilise `sh -u` par défaut et stoppe à la première erreur
- **`just --list`** : liste toutes les recettes avec leurs descriptions, sans configuration supplémentaire, ou magie noire
- **Syntaxe plus lisible** : commentaires `#` simples, pas de `##` ou de `awk` pour générer l'aide

Installation :

<https://github.com/casey/just#packages>

Exercice :

Faire un `justfile` identique au `Makefile`

Exemples :

- <https://tduyng.medium.com/justfile-became-my-favorite-task-runner-7a89e3f45d9a>
- <https://github.com/fixie-ai/fixie-examples/blob/main/Justfile>

## Gestion de projet python

Jusqu'ici on utilisait `pip`, en combinaison avec un environnement virtuel, avec un fichier texte `requirements.txt` qui liste les dépendances requises et leurs versions.

Les limitations de ce système se font vite ressentir.

- Ne pas oublier de `pip freeze` après chaque installation d'une dépendance
- Comment faire en sorte d'installer uniquement les dépendances requises en production ? Par exemple `pytest`, une dependance pour lancer des tests, n'est pas necessaire en prod mais est necessaire pour dev.
- Si j'utilise `flask` version 3.1.2 et que Flask décide de modifier cette version en la supprimant et en poussant une version avec le meme numéro mais du code différent, comment le détecter ?
- Il faut que chaque developpeur pense bien à créer un environnement virtuel. Comment s'assurer que chaque developpeur utilise la meme version de python ?
- Alice installe les dependances le 23 fevrier. Bob installe les dependances le 3 mars. Vis a vis du fichier `requirements.txt` ils ont bien les memes versions mais ils observent quand meme des comportements différents. Pourquoi ?

On peut surement tenter de gérer chaque limitation avec de la documentation, mais la liste reste longue.

### Gestionnaires de dépendances et d'environnements

Pour palier à toutes ces problématiques, il est courant d'utiliser un gestionnaire de dépendance et d'environnement.

Il en existe plusieurs, récents comme anciens.

- `pipenv`
- `poetry`
- `uv`

Pour votre culture je vous invite à essayer `pipenv` et `poetry`, mais pour la suite, nous utiliserons `uv`.

### `uv`

Depuis 2023, la société `Astral` a complètement transformer l'écosystème python avec des outils dev-friendly et beaucoup plus rapides que les tools existants. La rapidité est largement dûe au fait qu'ils sont développés en rust.

`uv` est donc un gestionnaire de dépendance et d'environnement python.

```bash
Usage: uv [OPTIONS] <COMMAND>

Commands:
  auth     Manage authentication
  run      Run a command or script
  init     Create a new project
  add      Add dependencies to the project
  remove   Remove dependencies from the project
  version  Read or update the project's version
  sync     Update the project's environment
  lock     Update the project's lockfile
  export   Export the project's lockfile to an alternate format
  tree     Display the project's dependency tree
  format   Format Python code in the project
  tool     Run and install commands provided by Python packages
  python   Manage Python versions and installations
  pip      Manage Python packages with a pip-compatible interface
  venv     Create a virtual environment
  build    Build Python packages into source distributions and wheels
  publish  Upload distributions to an index
  cache    Manage uv's cache
  self     Manage the uv executable
  help     Display documentation for a command
```

L'avantage de `uv` est qu'il est distribué sous forme de binaire, indépendant donc de quelque version de python installé sur le système. Cette autonomie lui permet de pouvoir gérer plus facilement les installations de python.

Par exemple, sur un ubuntu 20 avec python 3.8 natif, il est possible avec `uv` d'installer python3.12 pour un projet, et python3.10 pour un autre sans que cela ne vienne perturber le système.

Installer `uv` : <https://docs.astral.sh/uv/getting-started/installation/>

Dans un terminal dans ce projet, lancer `uv init --bare`.

### `pyproject.toml`

On remarquera la création d'un fichier `pyproject.toml` !

Le fichier `pyproject.toml` a été introduit par la [PEP 518](https://peps.python.org/pep-0518/) en **2016**, complétée par la [PEP 517](https://peps.python.org/pep-0517/) pour standardiser les systèmes de build, puis par la [PEP 621](https://peps.python.org/pep-0621/) en 2020 pour normaliser les métadonnées de projet.

Il remplace les anciens fichiers `setup.py` et `setup.cfg`.

**Ses avantages :**

- **Format standard** : un seul fichier pour toute la configuration du projet (dépendances, outils, build)
- **Déclaratif** : pas de code Python exécutable, plus sûr et prévisible
- **Interopérable** : compatible avec tous les outils modernes (`pip`, `uv`, `ruff`, `pytest`, `mypy`…)
- **Lisible** : syntaxe TOML claire et structurée

Plus d'infos sur ce fichier ici : <https://packaging.python.org/en/latest/guides/writing-pyproject-toml/>

---

Contenu de notre fichier `pyproject.toml` :

```toml
[project]
name = "app"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []
```

On remarque le champ `requires-python` qui indique la version (ou les versions) de python à utiliser pour le projet ; dans notre cas, les versions de python supérieures ou égales à 3.13.

Et le champ `dependencies` qui pour l'instant est un tableau vide.

Executer `uv add flask` et re-regarder le contenu du `pyproject.toml`.

```toml
...
dependencies = [
    "flask>=3.1.3",
]
```

On voit que le fichier a été automatiquement modifié pour contenir maintenant la dépendance `flask` en version supérieure ou égale à `3.1.3`.

On remarque aussi la création d'un fichier `uv.lock`.

```toml
version = 1
revision = 3
requires-python = ">=3.13"

[[package]]
name = "app"
version = "0.1.0"
source = { virtual = "." }
dependencies = [
    { name = "flask" },
]

[package.metadata]
requires-dist = [{ name = "flask", specifier = ">=3.1.3" }]

[[package]]
name = "blinker"
version = "1.9.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/packages/21/28/9b3f50ce0e048515135495f198351908d99540d69bfdc8c1d15b73dc55ce/blinker-1.9.0.tar.gz", hash = "sha256:b4ce2265a7abece45e7cc896e98dbebe6cead56bcf805a3d23136d145f5445bf", size = 22460, upload-time = "2024-11-08T17:25:47.436Z" }
wheels = [
    { url = "https://files.pythonhosted.org/packages/10/cb/f2ad4230dc2eb1a74edf38f1a38b9b52277f75bef262d8908e60d957e13c/blinker-1.9.0-py3-none-any.whl", hash = "sha256:ba0efaa9080b619ff2f3459d1d500c57bddea4a6b424b60a91141db6fd2f08bc", size = 8458, upload-time = "2024-11-08T17:25:46.184Z" },
]
```

Le fichier `uv.lock` est un **lockfile** généré automatiquement par `uv`. Il enregistre les versions **exactes** de toutes les dépendances installées — y compris les dépendances indirectes (les dépendances des dépendances), aussi appelées dépendances transitives.

Plusieurs avantages à avoir ce fichier :

- **Reproductibilité** : on peut installer exactement les mêmes versions de toutes les dépendances, ce qui permet d'éviter d'avoir des delta entre des développeurs ou dans la CI et ne pas avoir à entendre le fameux "chez moi ça marche"
- **Sécurité** : chaque paquet est accompagné d'un hash cryptographique (`sha256`) qui vérifie l'intégrité du fichier téléchargé
- **Traçabilité** : on voit précisément d'où vient chaque paquet (URL de téléchargement, version de wheel ou de sdist)

Au final:

- `pyproject.toml` déclare les dépendances avec des contraintes souples (`flask>=3.1.3`)
- `uv.lock` fixe les versions exactes (`blinker==1.9.0`, `flask==3.1.3`…)
- Ce fichier doit être **commité dans git** pour garantir des environnements identiques
- Il ne doit **jamais être modifié à la main** — `uv` le gère automatiquement

Executer `uv add alembic` et constate que alembic est rajouté au `pyproject.toml`

Ajoutons maintenant `ruff` avec la commande `uv add ruff --dev`.

Que constatons-nous dans le fichier `pyproject.toml` ?

```toml
...
[dependency-groups]
dev = [
    "ruff>=0.15.4",
]
```

Une nouvelle section est apparue, `dependency-groups` avec une liste `dev`. Cela correspond simplement à la liste des dépendances necessaires lors du developpement de l'app. C'est un nom arbitraire.

Lancer `uv add httpx --group blablabla` et vous verrez un nouveau groupe nommé `blablabla`.

Annuler cet ajout avec `uv remove httpx --group blablabla`.

L'intérêt d'avoir des groupes est de séparer les dépendances pour n'installer que le strict nécessaire.

Généralement on retrouve toujours les dépendances principales, obligatoires pour le fonctionnement de notre application. Et les deps de `dev` pour coder.

Pour finir, rajoutons `alembic` avec `uv add alembic`.

## ruff

Nous venons d'installer `ruff` en tant que dépendance de `dev`.

A quoi sert `ruff` ?

> Ruff is a Python linter and code formatter.

### Linter + formatter : c'est quoi ?

Un **linter** analyse statiquement le code (sans l'exécuter) pour détecter des problèmes :

- erreurs probables (`if x = 1:` au lieu de `if x == 1:`)
- code mort (variables déclarées mais jamais utilisées)
- mauvaises pratiques (`except:` trop large, imports inutilisés)
- non-respect des conventions de style (PEP 8 en Python)

Par exemple dans le code suivant, la variable `result` est crée mais jamais utilisée. `ruff` soulèvera ce problème.

```python
def add(a, b):
    result = a + b
    return a + b
```

Un **formatter** reformate automatiquement le code pour qu'il respecte un style uniforme — indentation, longueur de lignes, guillemets, espaces autour des opérateurs, etc. Contrairement au linter, il ne détecte pas de bugs : il réécrit le code pour qu'il soit homogène.

```python
# Avant formatter
x=1+2
my_list=[1,2,      3]

# Après formatter
x = 1 + 2
my_list = [1, 2, 3]
```

`ruff` combine les deux en un seul outil.

Pour votre culture, `ruff` remplace plusieurs outils : `flake8`, `isort`, `pyupgrade` et `black`.

## ty

Lancer `uv add ty --dev`

> Python type checker and language server

### Un type checker : c'est quoi ?

Python est un langage dynamiquement typé : les types ne sont vérifiés qu'à l'exécution. Mais depuis Python 3.5, on peut ajouter des **annotations de type** qui permettent à un outil de détecter des bugs avant l'éxécution du code.

Par exemple pour le code suivant ...

```python
def greet(name: str) -> str:
    return "Hello, " + name

greet(42)
```

... sans type checker, on ne decouvrirait que notre code plante uniquement lorsqu'on le lancerait ; dans le pire des cas, en production, si on a mal testé notre code.

```python
TypeError: can only concatenate str (not "int") to str
```

Ici, `ty` signalera une erreur : `int` n'est pas un `str`.

### Language server : c'est quoi ?

Un **language server** est un programme qui tourne en arrière-plan et communique avec votre éditeur (VSCode, Neovim, etc.) via le protocole [LSP](https://microsoft.github.io/language-server-protocol/). Il fournit :

- l'autocomplétion intelligente
- la navigation vers la définition d'une fonction
- la documentation au survol
- le surlignage des erreurs en temps réel

`ty` embarque un language server : en le configurant dans VSCode, vous obtenez la vérification de types en temps réel dans l'éditeur, sans avoir à lancer une commande manuellement.

## `.vscode`

Le dossier `.vscode/` contient la configuration VSCode **propre au projet**. Ces fichiers sont versionnés avec le code et partagés avec toute l'équipe/communauté. Cela garantit que tout le monde travaille avec les mêmes outils et la même configuration.

### `extensions.json` — extensions recommandées

Ce fichier liste les extensions VSCode recommandées pour le projet. Quand 1 dev ouvre le projet pour la première fois, VSCode lui propose de les installer automatiquement.

```json
{
  "recommendations": [
    "astral-sh.ty",         // type checker ty
    "charliermarsh.ruff",   // linter/formatter ruff
    "ms-python.python",     // support Python de base
    ...
  ]
}
```

Cela évite d'avoir à documenter manuellement "merci d'installer extension X et Y" dans le README.

### `settings.json` — configuration de l'espace de travail

Ce fichier surcharge les préférences utilisateur pour ce projet uniquement. Les configurations clés ici :

- **Formatters par langage** : ruff pour Python, prettier pour JS/TS/JSON, shell-format pour les scripts shell
- **Actions à la sauvegarde** : `formatOnSave` est configuré sur `true` ce qui permet une auto-organisation des imports, suppression des imports inutilisés — tout se fait automatiquement à chaque `Ctrl+S`
- **Environnement Python** : l'interpréteur pointe sur `.venv/bin/python` (le virtualenv géré par `uv`), et le terminal active automatiquement le venv
- **Tests** : pytest est configuré avec le dossier `tests/` comme cible

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  }
}
```
