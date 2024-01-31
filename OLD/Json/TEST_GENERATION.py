import json
import requests

def import_topology_to_gns3(json_file_path, gns3_server, gns3_port):
    # Charger le fichier JSON
    with open(json_file_path, 'r') as json_file:
        topology_data = json.load(json_file)

    # Configuration de l'URL de l'API GNS3
    base_url = f"http://{gns3_server}:{gns3_port}/v2/projects"
    project_id = topology_data['project_id']
    project_url = f"{base_url}/{project_id}/topologies"
    print(project_url)

    # Création de la topologie sur le serveur GNS3
    response = requests.post(project_url, json=topology_data['topology'])
    
    if response.status_code == 201:
        print("La topologie a été importée avec succès dans GNS3.")
    else:
        print(f"Erreur lors de l'import de la topologie dans GNS3. Code de statut : {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Spécifiez le chemin du fichier JSON et les détails du serveur GNS3
    json_file_path = "gns3_topology.json"
    gns3_server = "localhost"
    gns3_port = "3080" 

    # Appel de la fonction pour importer la topologie dans GNS3
    import_topology_to_gns3(json_file_path, gns3_server, gns3_port)