from gns3fy import Gns3Connector, Project  # Importation des modules nécessaires
from telnetlib import Telnet
import json
import time

# Fonction pour démarrer une connexion Telnet vers les noeuds du projet GNS3
def start_telnet(projet_name):
    serveur = Gns3Connector("http://localhost:3080")  # Connexion au serveur GNS3
    projet = Project(name=projet_name, connector=serveur)  # Sélection du projet par son nom
    
    projet.get()  # Récupération des informations du projet
    projet.open()  # Ouverture du projet dans GNS3

    noeuds = {}  # Dictionnaire pour stocker les connexions Telnet vers chaque noeud
    for noeud in projet.nodes:  # Parcours de chaque noeud dans le projet
        noeuds[noeud.name] = Telnet(noeud.console_host, str(noeud.console))  # Connexion Telnet à chaque noeud
    return noeuds

# Fonction pour envoyer une commande via Telnet à un routeur spécifique
def commande(cmd, noeuds, routeur):
    if type(cmd) == str:
        noeuds[routeur].write(bytes(cmd + "\r", encoding="ascii"))  # Envoi de la commande avec un retour à la ligne
    time.sleep(0.1)  # Pause pour laisser le temps au routeur de répondre

# Fonction pour lire un fichier JSON et le charger dans un dictionnaire Python
def lire_fichier_json(fichier_json):
    with open(fichier_json, 'r') as fichier:
        contenu_json = json.load(fichier)
    return contenu_json

# Fonction principale pour configurer les interfaces des routeurs en fonction du fichier JSON
def main(contenu_variable, noeuds):
    for AS_dico in contenu_variable["topology"]["AS"]:
        for routeur in AS_dico["routeurs"]:
            config = routeur["config"]
            info = routeur["informations"]

            for clef, val in config["interfaces"].items():
                interfaces_utiles(noeuds, val["name"], config, info, AS_dico)

# Fonction pour configurer les interfaces des routeurs
def interfaces_utiles(noeuds, interface, config, info, AS_dico):
    # Récupération des informations nécessaires
    name = info["name"]
    router_id = f"{info['router_number']}.{info['router_number']}.{info['router_number']}.{info['router_number']}"
    routing_protocole = AS_dico["AS_protocol"]

    # Envoi des commandes via Telnet pour configurer les interfaces
    commande("\r", noeuds, name)
    commande("\r", noeuds, name)
    commande("enable", noeuds, name)
    commande("conf t", noeuds, name)

    # Configuration spécifique selon le protocole de routage
    if routing_protocole == "ripng":
        # Configuration pour RIPng
        commande("ipv6 unicast-routing", noeuds, name)
        commande("ipv6 router rip ripng", noeuds, name)
        commande("redistribute connected", noeuds, name)
    elif routing_protocole == "ospf":
        # Configuration pour OSPF
        commande("ipv6 unicast-routing", noeuds, name)
        commande("ipv6 router ospf 200", noeuds, name)
        commande(f"router-id {router_id}", noeuds, name)

    # Configuration générale de l'interface
    commande("exit", noeuds, name)
    commande(f"interface {interface}", noeuds, name)
    commande("ipv6 enable", noeuds, name)
    lien = " "

    # Configuration spécifique selon le type d'interface
    if interface == "Loopback0":
        ipv6 = config["interfaces"]["interface_0"]["ipv6"]
        commande(f"ipv6 address {ipv6}", noeuds, name)
    elif interface == "FastEthernet0/0":
        ipv6 = config["interfaces"]["interface_4"]["ipv6"]
        commande(f"ipv6 address {ipv6}", noeuds, name)
        lien = config["interfaces"][f"interface_4"]["location"]
        nom_interface = "interface_4"
    else:
        for i in range(3):
            if interface == f"GigabitEthernet{i+1}/0":
                ipv6 = config["interfaces"][f"interface_{i+1}"]["ipv6"]
                commande(f"ipv6 address {ipv6}", noeuds, name)
                lien = config["interfaces"][f"interface_{i+1}"]["location"]
                nom_interface = f"interface_{i+1}"

    # Configuration de la liaison et activation de l'interface
    commande("no shutdown", noeuds, name)
    if routing_protocole == "ripng" and (lien == "intra" or interface == "Loopback0"):
        commande("ipv6 rip ripng enable", noeuds, name)
    elif routing_protocole == "ospf":
        commande("ipv6 ospf 200 area 1", noeuds, name)
        if interface != "Loopback0" and lien == "intra":
            commande(f"ipv6 ospf cost {config['interfaces'][nom_interface]['cost']}", noeuds, name)
        elif lien == "inter":
            commande("exit", noeuds, name)
            commande("ipv6 router ospf 200", noeuds, name)
            commande(f"passive-interface {interface}", noeuds, name)

    commande("exit", noeuds, name)

    # Configuration BGP pour l'interface Loopback0
    if interface == "Loopback0":
        bgp(contenu_variable, config, info, AS_dico, noeuds, name, router_id)
    else:
        commande(f"end", noeuds, name)

# Fonction pour configurer BGP
def bgp(contenu_variable, config, info, AS_dico, noeuds, name, router_id):
    AS_number = AS_dico['AS_number']
    ipv6_voisins = []

    # Configuration BGP de base
    commande(f"router bgp {AS_number}", noeuds, name)
    commande(f"bgp router-id {router_id}", noeuds, name)
    commande("no bgp default ipv4-unicast", noeuds, name)

    # Configuration des voisins BGP
    for routeur in AS_dico["routeurs"]:
        if routeur["informations"] != info:
            ipv6 = routeur["config"]["interfaces"]["interface_0"]["ipv6"].split("/")[0]
            ipv6_voisins.append(ipv6)
            commande(f"neighbor {ipv6} remote-as {AS_number}", noeuds, name)
            commande(f"neighbor {ipv6} update-source Loopback0", noeuds, name)

    # Configuration spécifique pour le routeur de bordure
    if info["border_router"] == "true":
        for interface in config["interfaces"].keys():
            if interface != "interface_0":
                if config["interfaces"][interface]["location"] == "inter":
                    for AS_tout in contenu_variable["topology"]["AS"]:
                        for routeur in AS_tout["routeurs"]:
                            if routeur["informations"]["name"] == config["interfaces"][interface]["neighbor"]:
                                for interface_inter in routeur['config']["interfaces"].keys():
                                    if interface_inter != "interface_0":
                                        if routeur["config"]["interfaces"][interface_inter]["neighbor"] == info[
                                            "name"]:
                                            if routeur["config"]["interfaces"][interface_inter]["location"] == "inter":
                                                ipv6 = routeur["config"]["interfaces"][f"{interface_inter}"][
                                                    "ipv6"].split("/")[0]
                                                ipv6_voisins.append(ipv6)
                                                commande(f"neighbor {ipv6} remote-as {AS_tout['AS_number']}", noeuds,
                                                         name)

    # Activation des voisins BGP et configuration additionnelle
    commande("address-family ipv6 unicast", noeuds, name)
    for addr in ipv6_voisins:
        commande(f"neighbor {addr} activate", noeuds, name)
        commande(f"neighbor {addr} send-community", noeuds, name)

    # Configuration spécifique pour le routeur de bordure
    if info["border_router"] == "true":
        for interface in config["interfaces"].keys():
            if interface != "interface_0":
                if config["interfaces"][interface]["location"] == "inter":
                    for AS_tout in contenu_variable["topology"]["AS"]:
                        for routeur in AS_tout["routeurs"]:
                            if routeur["informations"]["name"] == config["interfaces"][interface]["neighbor"]:
                                for interface_inter in routeur['config']["interfaces"].keys():
                                    if interface_inter != "interface_0":
                                        if routeur["config"]["interfaces"][interface_inter]["neighbor"] == info[
                                            "name"]:
                                            if routeur["config"]["interfaces"][interface_inter]["business"] == "client":
                                                commande(f" neighbor {ipv6} route-map CLIENT_IN in", noeuds, name)
                                            elif routeur["config"]["interfaces"][interface_inter]["business"] == "peer":
                                                commande(f" neighbor {ipv6} route-map PEER_IN in", noeuds, name)
                                                commande(f" neighbor {ipv6} route-map PP_OUT out", noeuds, name)
                                            elif routeur["config"]["interfaces"][interface_inter]["business"] == \
                                                    "provider":
                                                commande(f" neighbor {ipv6} route-map PROVIDER_IN in", noeuds, name)
                                                commande(f" neighbor {ipv6} route-map PP_OUT out", noeuds, name)

    # Configuration spécifique pour le routeur de bord
    if info["border_router"] == "true":
        commande(f"network {AS_dico['network'] } route-map SET_OWN", noeuds, name)
        commande(f"end", noeuds, name)

        # Configuration spécifique pour le routeur de bord
        commande(f"conf t", noeuds, name)
        commande(f"ipv6 route {AS_dico['network']} Null0", noeuds, name)
        commande("bgp community new-format", noeuds, name)
        for i in range(1, 5):
            commande(f"ip community-list {i} permit {i}", noeuds, name)

        commande("route-map CLIENT_IN permit 10", noeuds, name)
        commande("set community 1", noeuds, name)
        commande("set local-preference 150", noeuds, name)
        commande("exit", noeuds, name)

        commande("route-map PEER_IN permit 10", noeuds, name)
        commande("set community 2", noeuds, name)
        commande("set local-preference 100", noeuds, name)
        commande("exit", noeuds, name)

        commande("route-map PROVIDER_IN permit 10", noeuds, name)
        commande("set community 3", noeuds, name)
        commande("set local-preference 50", noeuds, name)
        commande("exit", noeuds, name)

        commande("route-map SET_OWN permit 10", noeuds, name)
        commande("set community 4", noeuds, name)
        commande("exit", noeuds, name)

        commande("route-map PP_OUT permit 10", noeuds, name)
        commande("match community 1", noeuds, name)
        commande("match community 4", noeuds, name)
        commande("exit", noeuds, name)

if __name__ == '__main__':
    fichier_json = "gns3_topology.json"  # Fichier JSON contenant la topologie GNS3
    noeuds = start_telnet("PROJET BIG AS TELLNET")  # Démarrage de la connexion Telnet
    contenu_variable = lire_fichier_json(fichier_json)  # Chargement du contenu JSON
    main(contenu_variable, noeuds)  # Exécution de la fonction principale
