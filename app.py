from flask import Flask, render_template_string, request
import json
import os
import sqlite3
import psycopg2

app = Flask(__name__)


def connexion_base():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    return sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "codes.db")
    )


class CurseurCompatible:
    def __init__(self, connexion):
        self.connexion = connexion
        self.est_postgres = bool(os.environ.get("DATABASE_URL"))
        self.curseur = connexion.cursor()

    def execute(self, requete, parametres=None):
        if self.est_postgres:
            requete = requete.replace("?", "%s")

        if parametres is None:
            return self.curseur.execute(requete)

        return self.curseur.execute(requete, parametres)

    def fetchone(self):
        return self.curseur.fetchone()

    def fetchall(self):
        return self.curseur.fetchall()


def initialiser_base():
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            description TEXT NOT NULL
        )
    """)

    connexion.commit()
    connexion.close()


def importer_codes():
    with open(
        os.path.join(os.path.dirname(__file__), "codes.json"),
        "r",
        encoding="utf-8"
    ) as fichier:
        codes = json.load(fichier)

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    for code, description in codes.items():
        code = code.strip()

        curseur.execute(
            "SELECT code FROM codes WHERE LOWER(TRIM(code)) = LOWER(?)",
            (code,)
        )

        if curseur.fetchone() is None:
            curseur.execute(
                "INSERT INTO codes (code, description) VALUES (?, ?)",
                (code, description)
            )

    connexion.commit()
    connexion.close()


initialiser_base()
importer_codes()


@app.route("/")
def accueil():
    return """
    <html>
        <head>
            <title>Mon Appli</title>

            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #cfe8ff;
                }

                a {
                    text-decoration: none;
                }

                h1 {
                    font-size: 32px;
                    margin-top: 40px;
                }

                p {
                    font-size: 20px;
                    margin-bottom: 30px;
                }

                button {
                    display: block;
                    width: 90%;
                    max-width: 400px;
                    height: 60px;
                    margin: 15px auto;
                    font-size: 22px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #fff4b8;
                }
            </style>

        </head>

        <body>

            <h1>MON OUTIL</h1>

            <p>Bienvenue dans mon application !</p>

            <a href="/codes-erreurs">
                <button>Codes erreurs</button>
            </a>

            <a href="/clients">
                <button>Clients</button>
            </a>
            
            <!--
            <a href="/calculatrice">
                <button>Calculatrice</button>
            </a>
            -->

        </body>
    </html>
    """


@app.route("/calculatrice")
def calculatrice():
    return """
    <html>
        <head>
            <title>Calculatrice</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">


            <style>
                button {
                    width: 70px;
                    height: 50px;
                    padding: 0;
                    margin: 3px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;

                }

                #ecran {
                    display: block;
                    margin: 20px auto;
                    width: 250px;
                    height: 50px;
                    font-size: 30px;
                    text-align: right;
                    box-sizing: border-box;
                }

                #calculatrice {
                    text-align: center;
                }

                body {
                    background-color: #f8d7da;
                }

            </style>
        </head>

        <script>

            let premierNombre = 0;
            let operateur = "";

            function ajouter(nombre) {
                let ecran = document.getElementById("ecran");

                if (nombre === "," && ecran.value.includes(",")) {
                    return;
                }

                if (ecran.value === "0" && nombre !== ",") {
                    ecran.value = nombre;
                } else {
                    ecran.value += nombre;
                }
            }

            function effacer() {
                let ecran = document.getElementById("ecran");
                ecran.value = "0";
            }

            function supprimer() {
                let ecran = document.getElementById("ecran");

                if (ecran.value.length > 1) {
                    ecran.value = ecran.value.slice(0, -1);
                } else {
                    ecran.value = "0";
                }
            }    

            function operation(op) {
                let ecran = document.getElementById("ecran");

                premierNombre = Number(ecran.value);
                operateur = op;
                ecran.value = ecran.value + op;
            }

            function calculer() {
                let ecran = document.getElementById("ecran");
                let calcul = ecran.value.replace("×", "*").replace(",", ".");

                try {
                    ecran.value = eval(calcul).toString().replace(".", ",");
                } catch {
                    ecran.value = "Erreur";
                }
            }


        </script>

        <body>
            <div id="calculatrice">
                <h1>Calculatrice</h1>
                <a href="/"><button>← Accueil</button></a>

                <input type="text" id="ecran" value="0" readonly>

                <br><br>

                <button onclick="ajouter('7')">7</button>
                <button onclick="ajouter('8')">8</button>
                <button onclick="ajouter('9')">9</button>

                <br>

                <button onclick="ajouter('4')">4</button>
                <button onclick="ajouter('5')">5</button>
                <button onclick="ajouter('6')">6</button>

                <br>

                <button onclick="ajouter('1')">1</button>
                <button onclick="ajouter('2')">2</button>
                <button onclick="ajouter('3')">3</button>

                <br>

                <button onclick="ajouter(',')">,</button>
                <button onclick="ajouter('0')">0</button>
                <button onclick="calculer()">=</button>

                <br><br>

                <button onclick="operation('+')">+</button>
                <button onclick="operation('-')">-</button>
                <button onclick="operation('*')">×</button>


                <br>

                <button onclick="operation('/')">÷</button>    
                <button onclick="supprimer()">⌫</button>
                <button onclick="effacer()">C</button>

            </div>
        </body>
    </html>
    """



@app.route("/modifier-code/<code>", methods=["GET", "POST"])
def modifier_code(code):
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute(
        "SELECT code, description FROM codes WHERE code = ?",
        (code,)
    )

    resultat = curseur.fetchone()

    connexion.close()

    if resultat is None:
        return "Code inconnu."

    description_actuelle = resultat[1]

    if request.method == "POST":
        description = request.form["description"]

        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)

        curseur.execute(
            "UPDATE codes SET description = ? WHERE code = ?",
            (description, code)
        )

        connexion.commit()
        connexion.close()

        return f'<script>window.location.href="/voir-code/{code}";</script>'

    return render_template_string("""
    <html>
        <head>
            <title>Modifier le code {{ code }}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                }

                textarea {
                    width: 90%;
                    max-width: 500px;
                    height: 180px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                button {
                    width: 150px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }
            </style>
        </head>

        <body>

            <h1>Modifier le code {{ code }}</h1>

            <form method="POST">

                <textarea name="description">{{ description }}</textarea>

                <br>

                <button type="submit">Enregistrer</button>

            </form>

            <a href="/voir-code/{{ code }}">
                <button>← Annuler</button>
            </a>

        </body>
    </html>
    """, code=code, description=description_actuelle)



@app.route("/supprimer-code/<code>", methods=["POST"])
def supprimer_code(code):
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute(
        "DELETE FROM codes WHERE code = ?",
        (code,)
    )

    connexion.commit()
    connexion.close()

    return '<script>window.location.href="/liste-codes";</script>'



@app.route("/voir-code/<code>")
def voir_code(code):
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute("SELECT code, description FROM codes")
    codes = dict(curseur.fetchall())

    connexion.close()

    
    if code.lower() not in [c.lower() for c in codes]:
        return "Code inconnu."

    code_reel = next(c for c in codes if c.lower() == code.lower())
    description = codes[code_reel]

    return render_template_string("""
    <html>
        <head>
            <title>Code {{ code }}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                }

                .description {
                    width: 90%;
                    max-width: 500px;
                    margin: 30px auto;
                    padding: 20px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 20px;
                }

                button {
                    width: 130px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }
            </style>
        </head>

        <body>

            <h1>Code {{ code }}</h1>

            <div class="description">
                {{ description }}
            </div>

            <a href="/liste-codes">
                <button>← Retour</button>
            </a>

            <br>

            <a href="/modifier-code/{{ code }}">
                <button>Modifier</button>
            </a>

            <form method="POST" action="/supprimer-code/{{ code }}" style="display: inline;" onsubmit="return confirm('Voulez-vous vraiment supprimer le code {{ code }} ?');">
                <button type="submit">Supprimer</button>
            </form>

        </body>
    </html>
    """, code=code, description=description)



@app.route("/liste-codes")
def liste_codes():
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute("SELECT code, description FROM codes")
    codes = dict(curseur.fetchall())

    connexion.close()

    liste = ""

    codes_tries = sorted(
        codes,
        key=lambda code: (
            0 if code.replace(" ", "").isdigit() else 1,
            int(code.replace(" ", "")) if code.replace(" ", "").isdigit() else code.lower()
        )
    )

    for code in codes_tries:
        liste += f"""
        <a href="/voir-code/{code}" style="text-decoration: none; color: black;">
            <div class="code">
                {code}
            </div>
        </a>
        """

    return render_template_string("""
    <html>
        <head>
            <title>Liste des codes</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                }

                button {
                    width: 120px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

                .code {
                    width: 90%;
                    max-width: 400px;
                    margin: 8px auto;
                    padding: 15px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: bold;
                }
            </style>
        </head>

        <body>

            <h1>Liste des codes</h1>

            <a href="/codes-erreurs">
                <button>← Retour</button>
            </a>

            <br><br>

            {{ liste | safe }}

        </body>
    </html>
    """, liste=liste)



@app.route("/ajouter-code", methods=["GET", "POST"])
def ajouter_code():
    if request.method == "POST":
        donnees = request.get_json()

        code = donnees["code"]
        description = donnees["description"]

        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)

        curseur.execute("SELECT code FROM codes WHERE code = ?", (code,))

        if curseur.fetchone():
            connexion.close()
            return {"success": False, "message": "Code déjà ajouté."}

        curseur.execute(
            "INSERT INTO codes (code, description) VALUES (?, ?)",
            (code, description)
        )

        connexion.commit()
        connexion.close()

        return {"success": True, "message": "Code ajouté avec succès."}

    return """
    <html>
        <head>
            <title>Ajouter un code</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                }

                input, textarea {
                    width: 90%;
                    max-width: 400px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 10px;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                input {
                    height: 50px;
                }

                textarea {
                    height: 150px;
                    resize: vertical;
                }

                button {
                    width: 180px;
                    height: 50px;
                    margin: 10px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                }
            </style>
        </head>

        <body>

            <h1>Ajouter un code</h1>

            <a href="/codes-erreurs">
                <button>← Retour</button>
            </a>

            <br>

            <input
                type="text"
                id="nouveauCode"
                placeholder="Numéro du code"
                inputmode="numeric"
            >

            <br>

            <textarea
                id="description"
                placeholder="Description du code"
            ></textarea>

            <br>

            <button onclick="ajouter()">Valider</button>

            <script>

                function ajouter() {
                    let code = document.getElementById("nouveauCode").value;
                    let description = document.getElementById("description").value;

                    if (code === "" || description === "") {
                        alert("Merci de remplir les deux champs.");
                        return;
                    }

                    fetch("/ajouter-code", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            code: code,
                            description: description
                        })
                    })
                    .then(async response => {
                        if (!response.ok) {
                            throw new Error("Erreur serveur : " + response.status);
                        }

                        return response.json();
                    })
                    .then(resultat => {
                        alert(resultat.message);

                        if (resultat.success) {
                            window.location.href = "/codes-erreurs";
                        }
                    })
                    .catch(erreur => {
                        alert("Une erreur est survenue : " + erreur.message);
                    });
                }
    
            </script>

        </body>
    </html>
    """


@app.route("/codes-erreurs")
def codes_erreurs():
    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute("SELECT code, description FROM codes")
    codes = dict(curseur.fetchall())

    connexion.close()
    return render_template_string("""
    <html>
        <head>
            <title>Codes erreurs</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                }

                button {
                    width: 70px;
                    height: 50px;
                    padding: 0;
                    margin: 3px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;

                }

                #recherche {
                    width: 250px;
                    height: 50px;
                    font-size: 25px;
                    text-align: center;
                    box-sizing: border-box;
                    margin: 20px 5px;
                }

                #resultat {
                    margin: 20px auto;
                    width: 90%;
                    max-width: 500px;
                    font-size: 20px;
                }
            </style>
        </head>

        <body>

            <h1>Codes erreurs</h1>

            <a href="/">
                <button>← Accueil</button>
            </a>

            <a href="/ajouter-code">
                <button>Ajouter un code</button>
            </a>

            <a href="/liste-codes">
                <button>Liste codes</button>
            </a>

            <br>

            <input
                type="text"
                id="recherche"
                placeholder="Code erreur"
                inputmode="numeric"
                maxlength="7"
            >

            <button onclick="chercher()">🔍</button>

            <div id="resultat"></div>

            <script>
                let codes = {{ codes | tojson }};
                

                function chercher() {
                    let recherche = document.getElementById("recherche").value;
                    let resultat = document.getElementById("resultat");

                    if (codes[recherche]) {
                        resultat.innerHTML = "<strong>Code " + recherche + "</strong><br><br>" + codes[recherche];
                    } else {
                        resultat.innerHTML = "Code inconnu.";
                    }
                }

                document.getElementById("recherche").addEventListener("keydown", function(event) {
                    if (event.key === "Enter") {
                        chercher();
                    }
                });

            </script>

        </body>
    </html>
    """, codes=codes)



# ============================================================
# CLIENTS / VEHICULES / INFORMATIONS
# ============================================================


# ------------------------------------------------------------
# CREATION DES TABLES
# ------------------------------------------------------------

def creer_tables_clients():

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            nom TEXT NOT NULL
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS vehicules (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            nom TEXT NOT NULL
        )
    """)

    # Nouvelle table pour les informations.
    # Elle permet d'avoir autant d'informations que nécessaire
    # pour chaque véhicule.
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS infos_vehicules (
            id INTEGER PRIMARY KEY,
            vehicule_id INTEGER NOT NULL,
            titre TEXT NOT NULL,
            valeur TEXT NOT NULL
        )
    """)

    connexion.commit()
    connexion.close()


creer_tables_clients()


# ============================================================
# PAGE PRINCIPALE DES CLIENTS
# ============================================================

@app.route("/clients")
def clients():

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)

    curseur.execute(
        "SELECT id, nom FROM clients ORDER BY nom"
    )

    liste_clients = curseur.fetchall()

    connexion.close()

    return render_template_string("""
    <html>

        <head>

            <title>Clients</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    margin: 0;
                    padding: 20px;
                }

                button {
                    width: 180px;
                    min-height: 50px;
                    margin: 5px;
                    padding: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

                .client {
                    width: 90%;
                    max-width: 400px;
                    margin: 8px auto;
                    padding: 15px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: bold;
                }

                a {
                    text-decoration: none;
                    color: black;
                }

            </style>

        </head>


        <body>

            <h1>Clients</h1>


            <a href="/">
                <button>← Accueil</button>
            </a>

            <br>


            <a href="/ajouter-client">
                <button>Ajouter un client</button>
            </a>


            <br><br>


            {% if liste_clients %}

                {% for client in liste_clients %}

                    <a href="/client/{{ client[0] }}">

                        <div class="client">
                            {{ client[1] }}
                        </div>

                    </a>

                {% endfor %}

            {% else %}

                <p>Aucun client enregistré.</p>

            {% endif %}


        </body>

    </html>
    """, liste_clients=liste_clients)


# ============================================================
# AJOUTER UN CLIENT
# ============================================================

@app.route("/ajouter-client", methods=["GET", "POST"])
def ajouter_client():

    if request.method == "POST":

        nom = request.form["nom"].strip()

        if nom == "":
            return """
            <script>
                alert("Merci de renseigner le nom du client.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        # Vérification si le client existe déjà
        curseur.execute(
            """
            SELECT id
            FROM clients
            WHERE LOWER(TRIM(nom)) = LOWER(TRIM(?))
            """,
            (nom,)
        )

        client_existant = curseur.fetchone()


        if client_existant:

            connexion.close()

            return """
            <script>
                alert("Ce client est déjà ajouté.");
                window.location.href="/clients";
            </script>
            """


        # Création d'un nouvel ID compatible
        # SQLite + PostgreSQL
        curseur.execute(
            "SELECT MAX(id) FROM clients"
        )

        dernier_id = curseur.fetchone()[0]

        if dernier_id is None:
            nouvel_id = 1
        else:
            nouvel_id = dernier_id + 1


        curseur.execute(
            """
            INSERT INTO clients (id, nom)
            VALUES (?, ?)
            """,
            (nouvel_id, nom)
        )


        connexion.commit()
        connexion.close()


        return """
        <script>
            window.location.href="/clients";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Ajouter un client</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input {
                    width: 90%;
                    max-width: 400px;
                    height: 50px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                button {
                    width: 180px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Ajouter un client</h1>


            <form method="POST">

                <input
                    type="text"
                    name="nom"
                    placeholder="Nom du client"
                    required
                    autofocus
                >

                <br>

                <button type="submit">
                    Ajouter
                </button>

            </form>


            <br>


            <a href="/clients">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """)


# ============================================================
# PAGE D'UN CLIENT
# ============================================================

@app.route("/client/<int:client_id>")
def client(client_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT id, nom
        FROM clients
        WHERE id = ?
        """,
        (client_id,)
    )

    client_selectionne = curseur.fetchone()


    if client_selectionne is None:

        connexion.close()

        return "Client inconnu."


    curseur.execute(
        """
        SELECT id, nom
        FROM vehicules
        WHERE client_id = ?
        ORDER BY nom
        """,
        (client_id,)
    )

    liste_vehicules = curseur.fetchall()


    connexion.close()


    return render_template_string("""
    <html>

        <head>

            <title>{{ nom }}</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                button {
                    width: 190px;
                    min-height: 50px;
                    margin: 5px;
                    padding: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

                .vehicule {
                    width: 90%;
                    max-width: 400px;
                    margin: 8px auto;
                    padding: 15px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: bold;
                }

                a {
                    text-decoration: none;
                    color: black;
                }

            </style>

        </head>


        <body>

            <h1>{{ nom }}</h1>


            <a href="/">
                <button>← Accueil</button>
            </a>

            <br>


            <a href="/clients">
                <button>← Clients</button>
            </a>

            <br><br>


            <a href="/ajouter-vehicule/{{ client_id }}">
                <button>Ajouter un véhicule</button>
            </a>


            <br><br>


            {% if liste_vehicules %}

                {% for vehicule in liste_vehicules %}

                    <a href="/vehicule/{{ vehicule[0] }}">

                        <div class="vehicule">
                            {{ vehicule[1] }}
                        </div>

                    </a>

                {% endfor %}

            {% else %}

                <p>Aucun véhicule enregistré.</p>

            {% endif %}


            <br><br>


            <a href="/modifier-client/{{ client_id }}">
                <button>Modifier le client</button>
            </a>


            <br>


            <form
                method="POST"
                action="/supprimer-client/{{ client_id }}"
                onsubmit="return confirm('Voulez-vous vraiment supprimer ce client et tous ses véhicules ?');"
                style="display: inline;"
            >

                <button type="submit">
                    Supprimer le client
                </button>

            </form>


        </body>

    </html>
    """,
    nom=client_selectionne[1],
    client_id=client_id,
    liste_vehicules=liste_vehicules)


# ============================================================
# MODIFIER UN CLIENT
# ============================================================

@app.route("/modifier-client/<int:client_id>", methods=["GET", "POST"])
def modifier_client(client_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT nom
        FROM clients
        WHERE id = ?
        """,
        (client_id,)
    )

    client_selectionne = curseur.fetchone()


    connexion.close()


    if client_selectionne is None:
        return "Client inconnu."


    if request.method == "POST":

        nom = request.form["nom"].strip()


        if nom == "":
            return """
            <script>
                alert("Merci de renseigner le nom du client.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        # Vérifie qu'un autre client ne possède pas déjà ce nom
        curseur.execute(
            """
            SELECT id
            FROM clients
            WHERE LOWER(TRIM(nom)) = LOWER(TRIM(?))
            AND id != ?
            """,
            (nom, client_id)
        )

        autre_client = curseur.fetchone()


        if autre_client:

            connexion.close()

            return """
            <script>
                alert("Ce client est déjà ajouté.");
                window.history.back();
            </script>
            """


        curseur.execute(
            """
            UPDATE clients
            SET nom = ?
            WHERE id = ?
            """,
            (nom, client_id)
        )


        connexion.commit()
        connexion.close()


        return f"""
        <script>
            window.location.href="/client/{client_id}";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Modifier le client</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input {
                    width: 90%;
                    max-width: 400px;
                    height: 50px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                button {
                    width: 190px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Modifier le client</h1>


            <form method="POST">

                <input
                    type="text"
                    name="nom"
                    value="{{ nom }}"
                    required
                    autofocus
                >

                <br>

                <button type="submit">
                    Enregistrer
                </button>

            </form>


            <br>


            <a href="/client/{{ client_id }}">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """,
    nom=client_selectionne[0],
    client_id=client_id)


# ============================================================
# SUPPRIMER UN CLIENT
# ============================================================

@app.route("/supprimer-client/<int:client_id>", methods=["POST"])
def supprimer_client(client_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    # Récupération des véhicules du client
    curseur.execute(
        """
        SELECT id
        FROM vehicules
        WHERE client_id = ?
        """,
        (client_id,)
    )

    vehicules = curseur.fetchall()


    # Suppression des informations de chaque véhicule
    for vehicule in vehicules:

        curseur.execute(
            """
            DELETE FROM infos_vehicules
            WHERE vehicule_id = ?
            """,
            (vehicule[0],)
        )


    # Suppression des véhicules
    curseur.execute(
        """
        DELETE FROM vehicules
        WHERE client_id = ?
        """,
        (client_id,)
    )


    # Suppression du client
    curseur.execute(
        """
        DELETE FROM clients
        WHERE id = ?
        """,
        (client_id,)
    )


    connexion.commit()
    connexion.close()


    return """
    <script>
        window.location.href="/clients";
    </script>
    """


# ============================================================
# AJOUTER UN VEHICULE
# ============================================================

@app.route("/ajouter-vehicule/<int:client_id>", methods=["GET", "POST"])
def ajouter_vehicule(client_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT nom
        FROM clients
        WHERE id = ?
        """,
        (client_id,)
    )

    client_selectionne = curseur.fetchone()


    connexion.close()


    if client_selectionne is None:
        return "Client inconnu."


    if request.method == "POST":

        nom = request.form["nom"].strip()


        if nom == "":
            return """
            <script>
                alert("Merci de renseigner le nom du véhicule.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        # Vérifie si ce véhicule existe déjà pour ce client
        curseur.execute(
            """
            SELECT id
            FROM vehicules
            WHERE client_id = ?
            AND LOWER(TRIM(nom)) = LOWER(TRIM(?))
            """,
            (client_id, nom)
        )

        vehicule_existant = curseur.fetchone()


        if vehicule_existant:

            connexion.close()

            return """
            <script>
                alert("Ce véhicule est déjà ajouté pour ce client.");
                window.history.back();
            </script>
            """


        # Génération d'un ID compatible
        curseur.execute(
            "SELECT MAX(id) FROM vehicules"
        )

        dernier_id = curseur.fetchone()[0]


        if dernier_id is None:
            nouvel_id = 1
        else:
            nouvel_id = dernier_id + 1


        curseur.execute(
            """
            INSERT INTO vehicules (id, client_id, nom)
            VALUES (?, ?, ?)
            """,
            (nouvel_id, client_id, nom)
        )


        connexion.commit()
        connexion.close()


        return f"""
        <script>
            window.location.href="/client/{client_id}";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Ajouter un véhicule</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input {
                    width: 90%;
                    max-width: 400px;
                    height: 50px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                button {
                    width: 200px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Ajouter un véhicule</h1>


            <p>Client : <strong>{{ client_nom }}</strong></p>


            <form method="POST">

                <input
                    type="text"
                    name="nom"
                    placeholder="Nom du véhicule"
                    required
                    autofocus
                >

                <br>

                <button type="submit">
                    Ajouter
                </button>

            </form>


            <br>


            <a href="/client/{{ client_id }}">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """,
    client_nom=client_selectionne[0],
    client_id=client_id)


# ============================================================
# PAGE D'UN VEHICULE
# ============================================================

@app.route("/vehicule/<int:vehicule_id>")
def vehicule(vehicule_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT
            vehicules.id,
            vehicules.nom,
            clients.id,
            clients.nom
        FROM vehicules
        JOIN clients
            ON clients.id = vehicules.client_id
        WHERE vehicules.id = ?
        """,
        (vehicule_id,)
    )

    vehicule_selectionne = curseur.fetchone()


    if vehicule_selectionne is None:

        connexion.close()

        return "Véhicule inconnu."


    curseur.execute(
        """
        SELECT id, titre, valeur
        FROM infos_vehicules
        WHERE vehicule_id = ?
        ORDER BY titre
        """,
        (vehicule_id,)
    )

    informations = curseur.fetchall()


    connexion.close()


    return render_template_string("""
    <html>

        <head>

            <title>{{ nom }}</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                button {
                    width: 200px;
                    min-height: 50px;
                    margin: 5px;
                    padding: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

                .information {
                    width: 90%;
                    max-width: 500px;
                    margin: 10px auto;
                    padding: 18px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 20px;
                }

                .titre {
                    font-weight: bold;
                    font-size: 21px;
                }

                .valeur {
                    margin-top: 10px;
                }

                a {
                    text-decoration: none;
                    color: black;
                }

            </style>

        </head>


        <body>

            <h1>{{ nom }}</h1>


            <a href="/">
                <button>← Accueil</button>
            </a>

            <br>


            <a href="/client/{{ client_id }}">
                <button>← {{ client_nom }}</button>
            </a>


            <br><br>


            <a href="/ajouter-info/{{ vehicule_id }}">
                <button>Ajouter une information</button>
            </a>


            <br><br>


            {% if informations %}

                {% for information in informations %}

                    <a href="/info/{{ information[0] }}">

                        <div class="information">

                            <div class="titre">
                                {{ information[1] }}
                            </div>

                            <div class="valeur">
                                {{ information[2] }}
                            </div>

                        </div>

                    </a>

                {% endfor %}

            {% else %}

                <p>Aucune information enregistrée.</p>

            {% endif %}


            <br>


            <a href="/modifier-vehicule/{{ vehicule_id }}">
                <button>Modifier le véhicule</button>
            </a>


            <br>


            <form
                method="POST"
                action="/supprimer-vehicule/{{ vehicule_id }}"
                onsubmit="return confirm('Voulez-vous vraiment supprimer ce véhicule et toutes ses informations ?');"
                style="display: inline;"
            >

                <button type="submit">
                    Supprimer le véhicule
                </button>

            </form>


        </body>

    </html>
    """,
    nom=vehicule_selectionne[1],
    vehicule_id=vehicule_selectionne[0],
    client_id=vehicule_selectionne[2],
    client_nom=vehicule_selectionne[3],
    informations=informations)


# ============================================================
# AJOUTER UNE INFORMATION
# ============================================================

@app.route("/ajouter-info/<int:vehicule_id>", methods=["GET", "POST"])
def ajouter_info(vehicule_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT nom, client_id
        FROM vehicules
        WHERE id = ?
        """,
        (vehicule_id,)
    )

    vehicule_selectionne = curseur.fetchone()


    connexion.close()


    if vehicule_selectionne is None:
        return "Véhicule inconnu."


    if request.method == "POST":

        titre = request.form["titre"].strip()
        valeur = request.form["valeur"].strip()


        if titre == "" or valeur == "":

            return """
            <script>
                alert("Merci de remplir les deux champs.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        # Génération d'un ID compatible
        curseur.execute(
            "SELECT MAX(id) FROM infos_vehicules"
        )

        dernier_id = curseur.fetchone()[0]


        if dernier_id is None:
            nouvel_id = 1
        else:
            nouvel_id = dernier_id + 1


        curseur.execute(
            """
            INSERT INTO infos_vehicules
            (id, vehicule_id, titre, valeur)
            VALUES (?, ?, ?, ?)
            """,
            (nouvel_id, vehicule_id, titre, valeur)
        )


        connexion.commit()
        connexion.close()


        return f"""
        <script>
            window.location.href="/vehicule/{vehicule_id}";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Ajouter une information</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input, textarea {
                    width: 90%;
                    max-width: 400px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 10px;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                input {
                    height: 50px;
                }

                textarea {
                    height: 150px;
                    resize: vertical;
                }

                button {
                    width: 200px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Ajouter une information</h1>


            <p>
                Véhicule :
                <strong>{{ vehicule_nom }}</strong>
            </p>


            <form method="POST">


                <input
                    type="text"
                    name="titre"
                    placeholder="Titre (ex : N° série)"
                    required
                    autofocus
                >


                <br>


                <textarea
                    name="valeur"
                    placeholder="Valeur de l'information"
                    required
                ></textarea>


                <br>


                <button type="submit">
                    Enregistrer
                </button>


            </form>


            <br>


            <a href="/vehicule/{{ vehicule_id }}">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """,
    vehicule_nom=vehicule_selectionne[0],
    vehicule_id=vehicule_id)


# ============================================================
# PAGE D'UNE INFORMATION
# ============================================================

@app.route("/info/<int:info_id>")
def voir_info(info_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT
            infos_vehicules.id,
            infos_vehicules.titre,
            infos_vehicules.valeur,
            vehicules.id,
            vehicules.nom,
            clients.id,
            clients.nom
        FROM infos_vehicules
        JOIN vehicules
            ON vehicules.id = infos_vehicules.vehicule_id
        JOIN clients
            ON clients.id = vehicules.client_id
        WHERE infos_vehicules.id = ?
        """,
        (info_id,)
    )

    information = curseur.fetchone()


    connexion.close()


    if information is None:
        return "Information inconnue."


    return render_template_string("""
    <html>

        <head>

            <title>{{ titre }}</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                .information {
                    width: 90%;
                    max-width: 500px;
                    margin: 30px auto;
                    padding: 25px;
                    box-sizing: border-box;
                    background-color: white;
                    border-radius: 10px;
                    font-size: 21px;
                }

                .titre {
                    font-weight: bold;
                    font-size: 25px;
                    margin-bottom: 20px;
                }

                button {
                    width: 200px;
                    min-height: 50px;
                    margin: 5px;
                    padding: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>{{ titre }}</h1>


            <div class="information">

                <div class="titre">
                    {{ titre }}
                </div>

                <div>
                    {{ valeur }}
                </div>

            </div>


            <a href="/vehicule/{{ vehicule_id }}">
                <button>← {{ vehicule_nom }}</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


            <br><br>


            <a href="/modifier-info/{{ info_id }}">
                <button>Modifier l'information</button>
            </a>


            <br>


            <form
                method="POST"
                action="/supprimer-info/{{ info_id }}"
                onsubmit="return confirm('Voulez-vous vraiment supprimer cette information ?');"
                style="display: inline;"
            >

                <button type="submit">
                    Supprimer l'information
                </button>

            </form>


        </body>

    </html>
    """,
    titre=information[1],
    valeur=information[2],
    info_id=information[0],
    vehicule_id=information[3],
    vehicule_nom=information[4])


# ============================================================
# MODIFIER UNE INFORMATION
# ============================================================

@app.route("/modifier-info/<int:info_id>", methods=["GET", "POST"])
def modifier_info(info_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT
            infos_vehicules.titre,
            infos_vehicules.valeur,
            vehicules.id,
            vehicules.nom
        FROM infos_vehicules
        JOIN vehicules
            ON vehicules.id = infos_vehicules.vehicule_id
        WHERE infos_vehicules.id = ?
        """,
        (info_id,)
    )

    information = curseur.fetchone()


    connexion.close()


    if information is None:
        return "Information inconnue."


    if request.method == "POST":

        titre = request.form["titre"].strip()
        valeur = request.form["valeur"].strip()


        if titre == "" or valeur == "":

            return """
            <script>
                alert("Merci de remplir les deux champs.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        curseur.execute(
            """
            UPDATE infos_vehicules
            SET titre = ?, valeur = ?
            WHERE id = ?
            """,
            (titre, valeur, info_id)
        )


        connexion.commit()
        connexion.close()


        return f"""
        <script>
            window.location.href="/info/{info_id}";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Modifier l'information</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input, textarea {
                    width: 90%;
                    max-width: 400px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 10px;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                input {
                    height: 50px;
                }

                textarea {
                    height: 150px;
                    resize: vertical;
                }

                button {
                    width: 210px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Modifier l'information</h1>


            <form method="POST">


                <input
                    type="text"
                    name="titre"
                    value="{{ titre }}"
                    required
                >


                <br>


                <textarea
                    name="valeur"
                    required
                >{{ valeur }}</textarea>


                <br>


                <button type="submit">
                    Enregistrer
                </button>


            </form>


            <br>


            <a href="/info/{{ info_id }}">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """,
    titre=information[0],
    valeur=information[1],
    info_id=info_id)


# ============================================================
# SUPPRIMER UNE INFORMATION
# ============================================================

@app.route("/supprimer-info/<int:info_id>", methods=["POST"])
def supprimer_info(info_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT vehicule_id
        FROM infos_vehicules
        WHERE id = ?
        """,
        (info_id,)
    )

    information = curseur.fetchone()


    if information is None:

        connexion.close()

        return "Information inconnue."


    vehicule_id = information[0]


    curseur.execute(
        """
        DELETE FROM infos_vehicules
        WHERE id = ?
        """,
        (info_id,)
    )


    connexion.commit()
    connexion.close()


    return f"""
    <script>
        window.location.href="/vehicule/{vehicule_id}";
    </script>
    """


# ============================================================
# MODIFIER UN VEHICULE
# ============================================================

@app.route("/modifier-vehicule/<int:vehicule_id>", methods=["GET", "POST"])
def modifier_vehicule(vehicule_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT nom, client_id
        FROM vehicules
        WHERE id = ?
        """,
        (vehicule_id,)
    )

    vehicule_selectionne = curseur.fetchone()


    connexion.close()


    if vehicule_selectionne is None:
        return "Véhicule inconnu."


    if request.method == "POST":

        nom = request.form["nom"].strip()


        if nom == "":
            return """
            <script>
                alert("Merci de renseigner le nom du véhicule.");
                window.history.back();
            </script>
            """


        connexion = connexion_base()
        curseur = CurseurCompatible(connexion)


        # Vérifie si un autre véhicule du même client porte déjà ce nom
        curseur.execute(
            """
            SELECT id
            FROM vehicules
            WHERE client_id = ?
            AND LOWER(TRIM(nom)) = LOWER(TRIM(?))
            AND id != ?
            """,
            (vehicule_selectionne[1], nom, vehicule_id)
        )

        autre_vehicule = curseur.fetchone()


        if autre_vehicule:

            connexion.close()

            return """
            <script>
                alert("Ce véhicule est déjà ajouté pour ce client.");
                window.history.back();
            </script>
            """


        curseur.execute(
            """
            UPDATE vehicules
            SET nom = ?
            WHERE id = ?
            """,
            (nom, vehicule_id)
        )


        connexion.commit()
        connexion.close()


        return f"""
        <script>
            window.location.href="/vehicule/{vehicule_id}";
        </script>
        """


    return render_template_string("""
    <html>

        <head>

            <title>Modifier le véhicule</title>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1.0">

            <style>

                body {
                    text-align: center;
                    font-family: Arial, sans-serif;
                    background-color: #e0e0e0;
                    padding: 20px;
                }

                input {
                    width: 90%;
                    max-width: 400px;
                    height: 50px;
                    box-sizing: border-box;
                    font-size: 20px;
                    padding: 10px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border: 1px solid #999;
                }

                button {
                    width: 200px;
                    height: 50px;
                    margin: 5px;
                    font-size: 18px;
                    border-radius: 10px;
                    border: none;
                    cursor: pointer;
                    background-color: #cfe8ff;
                }

            </style>

        </head>


        <body>

            <h1>Modifier le véhicule</h1>


            <form method="POST">

                <input
                    type="text"
                    name="nom"
                    value="{{ nom }}"
                    required
                    autofocus
                >

                <br>

                <button type="submit">
                    Enregistrer
                </button>

            </form>


            <br>


            <a href="/vehicule/{{ vehicule_id }}">
                <button>← Retour</button>
            </a>


            <br>


            <a href="/">
                <button>← Accueil</button>
            </a>


        </body>

    </html>
    """,
    nom=vehicule_selectionne[0],
    vehicule_id=vehicule_id)


# ============================================================
# SUPPRIMER UN VEHICULE
# ============================================================

@app.route("/supprimer-vehicule/<int:vehicule_id>", methods=["POST"])
def supprimer_vehicule(vehicule_id):

    connexion = connexion_base()
    curseur = CurseurCompatible(connexion)


    curseur.execute(
        """
        SELECT client_id
        FROM vehicules
        WHERE id = ?
        """,
        (vehicule_id,)
    )

    vehicule_selectionne = curseur.fetchone()


    if vehicule_selectionne is None:

        connexion.close()

        return "Véhicule inconnu."


    client_id = vehicule_selectionne[0]


    # Suppression des informations
    curseur.execute(
        """
        DELETE FROM infos_vehicules
        WHERE vehicule_id = ?
        """,
        (vehicule_id,)
    )


    # Suppression du véhicule
    curseur.execute(
        """
        DELETE FROM vehicules
        WHERE id = ?
        """,
        (vehicule_id,)
    )


    connexion.commit()
    connexion.close()


    return f"""
    <script>
        window.location.href="/client/{client_id}";
    </script>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
