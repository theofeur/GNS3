import json

def create_gns3_topology():
    
    # Indiquez l'adjacence des différents routeurs
    Adjacence= [[0,0,1,0,0,0],
                [0,0,1,0,0,0],
                [1,1,0,1,0,0],
                [0,0,1,0,1,1],
                [0,0,0,1,0,0],
                [0,0,0,1,0,0]]
    
    # On définit qu'il y autant de routeur d'un as à l'autre
    NOMBRE_ROUTEUR_PAR_AS = len(Adjacence)//2
    
    # On commence le json par des détails du projet
    topology = {
        "version": "2.0.0",
        "project_name": "petit_adressage_test",
        "topology": {
            "routeurs": []
            }
        }

    # On ajoute les routeurs de l'AS1 en Ripng
    
    # La variable "nombre_lien" sert pour l'adressage. Elle est réinitialisée à 1 à chaque changement d'AS
    nombre_lien=1
    
    # On va créer le dictionnaire de chaque routeur de l'AS1, avec chaques informations importantes pour les programmes
    for i in range(0, NOMBRE_ROUTEUR_PAR_AS):           
        router = {
                "informations": {
                    "name": f"R{i+1}",
                    "router_number": f"{i+1}",
                    "ASnumber": "1"
                },
                "config": {
                    "interfaces": {
                        # L'interface 0 sera toujours l'interface de loopback, le protocole sera toujours bgp (ibgp)
                        "interface_0": {
                            "name": "Loopback0",
                            "type": "loopback",
                            "routing_protocole": "bgp",
                            "ipv6": f"2001:100:1:0::{i+1}/128"
                            
                        }
                    }         
                }
            }
        
        # On va se déplacer dans la matrice d'adjacence et ajouter les interfaces 1 à 1
        for j in range(0, NOMBRE_ROUTEUR_PAR_AS):
            
            # S'il y a un "1" dans la matrice d'adjacence, cela signifie qu'il y a un lien entre 2 routeurs, dans ce cas:
            if Adjacence[i][j]==1:
                # On définit une variable "nombre_interface" qui va servir à indiquer une interface non-utilisée
                nombre_interface= len(router["config"]["interfaces"])
                interface = f"interface_{nombre_interface}"
                # On rajoute les informations de l'interface. La clé "location" indique qu'on est à l'interieur d'une même AS
                info = {
                        "name": f"GigabitEthernet{nombre_interface}/0",
                        "type": "ethernet",
                        "location": "intra",
                        "neighbor": f"R{j+1}",
                        "routing_protocole": "ripng",
                        }
                
                # Ce "if" permet de gérer l'adressage. Si le lien avec le voisin n'a pas encore été établi, on génère un adressage
                if len(topology["topology"]["routeurs"])<j :
                    info["ipv6"]= f"2001:100:1:{nombre_lien}::{j+1}/64"
                    nombre_lien+=1
                # Sinon, on récupère l'adressage du lien établi puis on le modifie pour assurer qu'on n'ait pas les mêmes adresses
                else:
                    # Ici, on se déplace dans les différents interfaces du voisin dont le lien a déjà été établi 
                    for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])):
                        # On cherche l'interface pour trouver celui qui correspond au routeur que l'on est en train de traiter
                        if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                            # On récupère toute l'adresse sauf la fin
                            substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"][:-4]
                            # On modifie la fin pour avoir un bon adressage
                            info["ipv6"]=substring+f"{j+1}/64"

                router["config"]["interfaces"][interface]=info
        
        # Si l'on est dans le dernier router de l'AS, on suppose que notre routeur est un routeur de bordure, dans ce cas:    
        if i == NOMBRE_ROUTEUR_PAR_AS-1:
            # On rajoute une interface, puis que le routeur de bordure est automatiquement voisin du routeur de bordure de l'AS 2
            interface = f"interface_{nombre_interface+1}"
            info = {
                # On y indique toutes les informations dont on a besoin.
                    "name": f"GigabitEthernet{nombre_interface+1}/0",
                    "type": "ethernet",
                    "location": "inter",
                    "neighbor": f"R{NOMBRE_ROUTEUR_PAR_AS+1}",
                    "routing_protocole": "bgp",
                    "ipv6": f"2001:100:3:1::{NOMBRE_ROUTEUR_PAR_AS+1}/64"
                }
            router["config"]["interfaces"][interface]=info
                
        topology["topology"]["routeurs"].append(router)



    nombre_lien=1
    
    # Ajout des routeurs AS2 (R4, R5, R6) en OSPF
    for i in range(NOMBRE_ROUTEUR_PAR_AS, NOMBRE_ROUTEUR_PAR_AS*2):           
        router = {
                "informations": {
                    "name": f"R{i+1}",
                    "router_number": f"{i+1}",
                    "ASnumber": "2"
                },
                "config": {
                    "interfaces": {
                        "interface_0": {
                            "name": "Loopback0",
                            "type": "loopback",
                            "routing_protocole": "bgp",
                            "ipv6": f"2001:100:2:0::{i+1}/128"
                            
                        }
                    }         
                }
            }
        
        for j in range(NOMBRE_ROUTEUR_PAR_AS, NOMBRE_ROUTEUR_PAR_AS*2):
            if Adjacence[i][j]==1:
                nombre_interface= len(router["config"]["interfaces"])
                interface = f"interface_{nombre_interface}"
                info = {
                        "name": f"GigabitEthernet{nombre_interface}/0",
                        "type": "ethernet",
                        "location": "intra",
                        "neighbor": f"R{j+1}",
                        "routing_protocole": "ospf",
                        }
                if len(topology["topology"]["routeurs"])<j :
                    info["ipv6"]= f"2001:100:2:{nombre_lien}::{j+1}/64"
                    nombre_lien+=1
                else:
                    for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])):
                        if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                            substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"][:-4]
                            info["ipv6"]=substring+f"{j+1}/64"

                router["config"]["interfaces"][interface]=info
            
        if i == NOMBRE_ROUTEUR_PAR_AS:
            interface = f"interface_{nombre_interface+1}"
            info = {
                    "name": f"GigabitEthernet{nombre_interface+1}/0",
                    "type": "ethernet",
                    "location": "inter",
                    "neighbor": f"R{NOMBRE_ROUTEUR_PAR_AS}",
                    "routing_protocole": "bgp",
                    "ipv6": f"2001:100:3:1::{NOMBRE_ROUTEUR_PAR_AS}/64"
                }
            router["config"]["interfaces"][interface]=info
                
        topology["topology"]["routeurs"].append(router)
    return topology

if __name__ == "__main__":
    gns3_topology = create_gns3_topology()
    
    with open("gns3_topology.json", "w") as json_file:
        json.dump(gns3_topology, json_file, indent=2)

    print("GNS3 topology JSON file created: gns3_topology.json")

     