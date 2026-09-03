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

            <a href="/calculatrice">
                <button>Calculatrice</button>
            </a>

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
