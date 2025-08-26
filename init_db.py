# app/init_db.py
# Ce script initialise la base de données en créant les tables définies dans les modèles ORM.
# Il doit être exécuté une seule fois au démarrage du projet (ou après modification des modèles).
#Executer avec python3 app/init_db.py


from app.database import engine, Base

# Ajouter cet import pour qu'on enregistre les classes User, Robot, UserRobot…
import app.models

def init_models():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_models()
    print("Tables créées avec succès.")
