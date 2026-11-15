# BarCode Pro — Suite de Génération, Vérification & Traçabilité de Codes-Barres

Application web Full-Stack développée avec **Python (Flask)** et **JavaScript Vanilla**, conçue pour générer des codes-barres normalisés, vérifier leur authenticité et assurer le suivi des références produits dans un environnement **100 % autonome et sécurisé (Offline-First & Privacy-by-Design)**.

---

## Fonctionnalités clés

* **Génération multi-standards :** Prise en charge des normes industrielles **Code 128**, **EAN-13**, **EAN-8** et **UPC-A** via la bibliothèque `python-barcode`.
* **Exportation multi-formats & compression légère :** Conversion dynamique en mémoire vive avec **Pillow** vers les formats **PNG**, **JPG/JPEG** et **WebP** (fichiers ultra-légers de quelques kilo-octets sans perte de lisibilité laser).
* **Audit & Vérification d'intégrité :** Contrôle automatique de la longueur, du format et calcul de la clé de contrôle (*checksum*) pour détecter toute erreur de saisie.
* **Journal de traçabilité :** Historique local persistant associant chaque code généré au produit correspondant avec horodatage et copie rapide en un clic.
* **Architecture 100 % locale (Zéro CDN externe) :** Aucune dépendance externe (icônes Ionicons v2 et styles hébergés localement), garantissant la confidentialité totale des données produits et un fonctionnement hors-ligne.

---

## Stack Technique

* **Backend :** Python 3, Flask (API REST JSON), `python-barcode`, `Pillow`
* **Frontend :** HTML5 sémantique, CSS3 (Grid/Flexbox, design responsive), JavaScript (Fetch API)
* **Icônes :** Ionicons v2.0.0 (hébergement local)

---

## Structure du projet

```text
generateur_codebarre/
├── app.py                   # Serveur Flask, validation, génération d'images et API REST
├── requirements.txt         # Dépendances Python du projet
├── .gitignore               # Fichiers exclus du suivi Git
├── static/
│   ├── css/
│   │   └── style.css        # Feuille de style responsive
│   ├── js/
│   │   └── main.js          # Logique interactive et appels API asynchrones
│   └── libs/
│       └── ionicons/        # Bibliothèque d'icônes locale (CSS & Fonts)
└── templates/
    └── index.html           # Interface utilisateur principale
```

---

## Installation et exécution en local

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/glodyclaver-ui/Codes-Barres
   cd generateur-codebarre
   ```

2. **Installer les dépendances :**
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Lancer l'application :**
   ```bash
   python app.py
   ```

4. **Ouvrir dans le navigateur :**
   Accédez à l'adresse **`http://127.0.0.1:5000`**.

---

## Auteur

**Glodi-Placide Oleko Diomba**  
Développeur Web & Solutions Numériques
