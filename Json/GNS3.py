import json
import requests

# Informations GNS3
gns3_server_url = "http://localhost:3080"  # Remplacez par l'URL de votre serveur GNS3
project_id = "320547e5-bf62-4d8a-a9ac-c52f0877e71d"  # Remplacez par l'ID de votre projet GNS3

# Charger les configurations depuis le fichier JSON
with open('gns3_topology.json', 'r') as file:
    configurations = json.load(file)

# Créer les nodes dans GNS3
for node in configurations["nodes"]:
    response = requests.post(f"{gns3_server_url}/v2/projects/{project_id}/nodes", json=node)
    if response.status_code == 201:
        print(f"Node {node['name']} créé avec succès.")
    else:
        print(f"Erreur lors de la création du node {node['name']}. Code d'erreur :", response.status_code)
        print(response.text)

# Créer les liens entre les nodes
for link in configurations["links"]:
    response = requests.post(f"{gns3_server_url}/v2/projects/{project_id}/links", json=link)
    if response.status_code == 201:
        print(f"Lien entre {link['nodes'][0]} et {link['nodes'][1]} créé avec succès.")
    else:
        print(f"Erreur lors de la création du lien entre {link['nodes'][0]} et {link['nodes'][1]}. Code d'erreur :", response.status_code)
        print(response.text)
