import json

def create_gns3_topology():
    
    # Indiquez l'adjacence des différents routeurs
    Adjacence= [[0,1,0,0,0,0,0,0,0,0,0,0,0],
                [1,0,1,0,0,0,0,0,0,0,0,0,0],
                [0,1,0,1,1,1,0,0,0,0,0,0,0],
                [0,0,1,0,1,1,0,0,0,0,0,0,0],
                [0,0,1,1,0,0,1,0,0,0,0,0,0],
                [0,0,1,1,0,0,0,1,0,0,0,0,0],
                [0,0,0,0,1,0,0,0,1,1,0,0,0],
                [0,0,0,0,0,1,0,0,1,1,0,0,0],
                [0,0,0,0,0,0,1,1,0,1,1,0,0],
                [0,0,0,0,0,0,1,1,1,0,0,1,0],
                [0,0,0,0,0,0,0,0,1,0,0,1,1],
                [0,0,0,0,0,0,0,0,0,1,1,0,1],
                [0,0,0,0,0,0,0,0,0,0,1,1,0]]
    
    # Indiquez les différents protocoles de vos AS
    AS1_PROTOCOL= "ripng"
    AS2_PROTOCOL= "ospf"
    
    # Indiquez le nombre de routeur dans chaque AS
    NOMBRE_ROUTEUR_AS1 = 6
    NOMBRE_ROUTEUR_AS2 = 7

    if(NOMBRE_ROUTEUR_AS1 + NOMBRE_ROUTEUR_AS2 != len(Adjacence)):
        print("Erreur de correspondance entre la matrice d'adjacence et les nombres de routeurs")
        return
    else:

        # On commence le json par des détails du projet
        topology = {
            "version": "2.2.1",
            "project_name": "petit_adressage_test",
            "topology": {
                "routeurs": []
                }
            }

        # On ajoute les routeurs de l'AS1 en Ripng
        
            # La variable "nombre_lien" sert pour l'adressage. Elle est réinitialisée à 1 à chaque changement d'AS.
            # La variable "nombre_routeur_bordure" sert également pour l'adressage. Elle définit le nombre de sous-réseau dans la liaison des AS
        nombre_lien=1
        nombre_routeur_bordure=1
        
        # On va créer le dictionnaire de chaque routeur de l'AS1, avec chaques informations importantes pour les programmes   
        for i in range(0, NOMBRE_ROUTEUR_AS1):    
            # On initialise un booleen pour savoir si le routeur est un routeur de bordure. Si oui, on le rajoutera dans l'information du routeur
            is_a_border_router = False       
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
            for j in range(0, len(Adjacence)):
                
                # S'il y a un "1" dans la matrice d'adjacence, cela signifie qu'il y a un lien entre 2 routeurs, dans ce cas:
                if Adjacence[i][j]==1:
                    # On définit une variable "nombre_interface" qui va servir à indiquer une interface non-utilisée
                    nombre_interface= len(router["config"]["interfaces"])
                    interface = f"interface_{nombre_interface}"
                    
                    # Si les voisins étudiés sont inférieurs au nombre de routeur par AS, cela signifie qu'on est encore dans l'AS.
                    if(j<NOMBRE_ROUTEUR_AS1):
                    # On rajoute les informations de l'interface. La clé "location" indique qu'on est à l'interieur d'une même AS
                        info = {
                                "name": f"GigabitEthernet{nombre_interface}/0",
                                "type": "ethernet",
                                "location": "intra",
                                "neighbor": f"R{j+1}",
                                "routing_protocole": AS1_PROTOCOL,
                                }
                        
                        # Si le protocole de l'interface est ospf, on rajoute une information sur la métrique du lien, que l'on initialise à 100. Cette valeur sera changeable manuellement.
                        if(info["routing_protocole"]=="ospf"):
                            info["cost"]=100
                        
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
                                    substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                    # On modifie la fin pour avoir un bon adressage
                                    info["ipv6"]=substring[0]+f":{j+1}/64"
                    
                    # Si le voisin n'est pas dans l'AS, alors le routeur est automatiquement un routeur de bordure
                    else:
                        is_a_border_router = True
                        info = {
                    # On y indique donc toutes les informations dont on a besoin.
                        "name": f"GigabitEthernet{nombre_interface+1}/0",
                        "type": "ethernet",
                        "location": "inter",
                        "neighbor": f"R{j+1}",
                        "routing_protocole": "bgp",
                        }
                        
                        # Ce "if" permet de gérer l'adressage. Si le lien avec le voisin n'a pas encore été établi, on génère un adressage
                        if len(topology["topology"]["routeurs"])<j :
                            info["ipv6"]= f"2001:100:3:{nombre_routeur_bordure}::{j+1}/64"
                            # Ici, on indique qu'on a un nouveau lien inter-AS, pour ne pas se tromper lors de l'adressage
                            nombre_routeur_bordure+=1
                        # Sinon, on récupère l'adressage du lien établi puis on le modifie pour assurer qu'on n'ait pas les mêmes adresses
                        else:
                            # Ici, on se déplace dans les différents interfaces du voisin dont le lien a déjà été établi 
                            for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])-1):
                                # On cherche l'interface pour trouver celui qui correspond au routeur que l'on est en train de traiter
                                if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                                    # On récupère toute l'adresse sauf la fin
                                    substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                    # On modifie la fin pour avoir un bon adressage
                                    info["ipv6"]=substring[0]+f":{j+1}/64"

                    router["config"]["interfaces"][interface]=info
            if (is_a_border_router == True):
                router["informations"]["border_router"]= "true"
            else:
                router["informations"]["border_router"]="false"       
                    
            topology["topology"]["routeurs"].append(router)


        nombre_lien=1
        
        #  De la même manière, on ajoute les routeurs de l'AS 2. Le principe est sensiblement le même, les informations sont simplement modifiées.
        for i in range(NOMBRE_ROUTEUR_AS1, NOMBRE_ROUTEUR_AS2+NOMBRE_ROUTEUR_AS1):  
            is_a_border_router = False            
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
            
            for j in range(0, len(Adjacence)):
                if Adjacence[i][j]==1:
                    
                    nombre_interface= len(router["config"]["interfaces"])
                    interface = f"interface_{nombre_interface}"
                    if(j>=NOMBRE_ROUTEUR_AS1):
                        info = {
                                "name": f"GigabitEthernet{nombre_interface}/0",
                                "type": "ethernet",
                                "location": "intra",
                                "neighbor": f"R{j+1}",
                                "routing_protocole": AS2_PROTOCOL,
                                }
                        if(info["routing_protocole"]=="ospf"):
                            info["cost"]=100
                        if len(topology["topology"]["routeurs"])<j :
                            info["ipv6"]= f"2001:100:2:{nombre_lien}::{j+1}/64"
                            nombre_lien+=1
                        else:
                            for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])):
                                if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                                    substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                    info["ipv6"]=substring[0]+f":{j+1}/64"
                                        
                    else:
                            is_a_border_router = True
                            info = {
                            "name": f"GigabitEthernet{nombre_interface+1}/0",
                            "type": "ethernet",
                            "location": "inter",
                            "neighbor": f"R{j+1}",
                            "routing_protocole": "bgp",
                            }
                            
                            if len(topology["topology"]["routeurs"])<j :
                                info["ipv6"]= f"2001:100:3:{nombre_routeur_bordure}::{j+1}/64"
                                nombre_routeur_bordure+=1
                            else:
                                for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])):
                                    if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                                        substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                        info["ipv6"]=substring[0]+f":{j+1}/64"   

                    router["config"]["interfaces"][interface]=info
                    
            if (is_a_border_router == True):
                router["informations"]["border_router"]= "true"
            else:
                router["informations"]["border_router"]="false"  
                
            topology["topology"]["routeurs"].append(router)
            
        return topology

if __name__ == "__main__":
    gns3_topology = create_gns3_topology()
    
    with open("gns3_topology.json", "w") as json_file:
        json.dump(gns3_topology, json_file, indent=2)

    print("Fichier généré: gns3_topology.json")

     