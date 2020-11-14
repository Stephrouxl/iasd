# iasd

## En local :
lancer `airflow webserver &` et `airflow scheduler &`
et sur le navigateur : localhost:8080

Quand met un nouveau .py ici par exemple code.py (qui charge le dataset iris) dans /dags, vérifier que celui ci apparait dans airflow en local (c'est le nom qui est à l'intérieur du dags qui s'affiche, pas le nom du fichier)

## En remote :
lancer une instance
activer : `source ~/my_app/env/bin/activate`
puis lancer `airflow webserver &` et `airflow scheduler &`

Lorsqu'on push sur github, le .py apparait dans le airflow remote (ip publique:8080)
