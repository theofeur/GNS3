import json

def create_gns3_topology():
    
    # Indiquez l'adjacence des différents routeurs
    Adjacence= [[0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
                [1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
                [0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,1,1,0,1,1,0,0,0,0,0,0,0,0,0],
                [0,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0],
                [0,0,0,1,1,0,0,0,1,0,0,0,0,0,"client",0],
                [0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,"peer"],
                [0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0],
                [0,0,0,0,0,0,0,1,1,0,1,1,0,0,0,0],
                [0,0,0,0,0,0,0,1,1,1,0,0,1,0,0,0],
                [0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0],
                [0,0,0,0,0,0,"provider",0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,"peer",0,0,0,0,0,0,0,0]]
    
    # Vous pouvez rajouter la communitie que vous souhaitez entre guillemets. Par défaut, les routeurs de bordures auront un business "admin"
    # Rajouter le terme "client" à la 6eme ligne 15eme colonne signifira que le routeur 6 sera client pour le routeur 15
    
    
    # Indiquez les différents protocoles de vos AS
    AS_PROTOCOLS = ["ripng","ospf","ripng","ripng"]

    
    # Indiquez le nombre de routeur dans chaque AS
    NOMBRE_ROUTEUR_PAR_AS = [7,7,1,1]

    

    
    
    ####################################################################################
    Total_router=0
    for i in range (0, len(NOMBRE_ROUTEUR_PAR_AS)):
        Total_router+=NOMBRE_ROUTEUR_PAR_AS[i]


    # On vérifie dans un premier temps que la matrice d'adjacence et le nombre de routeur sont correspondants.
    if(Total_router != len(Adjacence)):
        print("Erreur de correspondance entre la matrice d'adjacence et les nombres de routeurs")
        return
    elif(len(AS_PROTOCOLS) != len(NOMBRE_ROUTEUR_PAR_AS)):
        print("Erreur de tableau entre le nombre d'AS et le nombre de routeur par AS")
        return
    else:
        # On commence le json par des détails du projet
        topology = {
            "version": "4.2.1",
            "project_name": "petit_adressage_test",
            "topology": {
                "AS":[{} for _ in range(len(AS_PROTOCOLS))]
            }
        }

        
        # Cette variable sert à l'adressage et évite les répétitions des sous-réseaux inter-AS
        nombre_routeur_bordure=1
        # Cette variable compte le nombre de routeur au fil des boucles à travers les AS
        compteur_routeur=0
        
        
        # On fait une boucle pour toutes les AS
        for AS in range(0,len(AS_PROTOCOLS)):

            # Ces 2 variables permettent de calculer le nombre de routeur AVANT et APRES le nombre de routeur de l'AS étudié. Cela sert lors de l'assignation des voisins.
            routeur_avant=0
            routeur_apres=0
            
            if(AS==0):
                routeur_avant=0
                routeur_apres=Total_router-NOMBRE_ROUTEUR_PAR_AS[0]
            elif(AS==len(AS_PROTOCOLS)-1):
                routeur_apres=0
                routeur_avant=Total_router-NOMBRE_ROUTEUR_PAR_AS[AS]
            else:
                for i in range(0,AS):
                    routeur_avant+=NOMBRE_ROUTEUR_PAR_AS[i]
                for i in range(AS+1,len(NOMBRE_ROUTEUR_PAR_AS)):
                    routeur_apres+=NOMBRE_ROUTEUR_PAR_AS[i]
            nombre_lien=1
            
            # On indique les différentes informations de l'AS
            ASInformation = {"AS_number": f"{AS+1}",
                            "AS_protocol":  AS_PROTOCOLS[AS],
                            "network": f"2001:100:{AS+1}::/48",
                            "routeurs": [],
                            }
            topology["topology"]["AS"][AS]=ASInformation
            
            # Désormais, on fait une boucle sur tout les routeurs de l'AS
            for i in range (0, NOMBRE_ROUTEUR_PAR_AS[AS]):  
                is_a_border_router = False 
                compteur_routeur+=1   
                
                # On indique les différentes informations du routeur   
                router = {
                        "informations": {
                            "name": f"R{compteur_routeur}",
                            "router_number": f"{compteur_routeur}",
                        },
                        "config": {
                            "interfaces": {
                                # L'interface 0 sera toujours l'interface de loopback, le protocole sera toujours bgp (ibgp)
                                "interface_0": {
                                    "name": "Loopback0",
                                    "ipv6": f"2001:100:{AS+1}:0::{compteur_routeur}/128"
                                    
                                }
                            }         
                        }
                    }
                
                # On va se déplacer dans la matrice d'adjacence et ajouter les interfaces 1 à 1
                for j in range(0, len(Adjacence)):
                    
                    # Dans un premier temps, on test si la case est de type int
                    if type(Adjacence[routeur_avant+i][j])==int:
                        # S'il y a autre chose qu'un 0 dans la matrice d'adjacence, cela signifie qu'il y a un lien entre 2 routeurs, dans ce cas:
                        if Adjacence[routeur_avant+i][j]!=0:
                            # On définit une variable "nombre_interface" qui va servir à indiquer une interface non-utilisée
                            nombre_interface= len(router["config"]["interfaces"])
                            interface = f"interface_{nombre_interface}"
                            
                            # Si les voisins étudiés sont inférieurs au nombre de routeur par AS, cela signifie qu'on est encore dans l'AS.
                            if(routeur_avant <= j < Total_router-routeur_apres):
                            # On rajoute les informations de l'interface. La clé "location" indique qu'on est à l'interieur d'une même AS
                                if nombre_interface==4:
                                    # Par défaut, on indique que l'interface "4" sera toujours un FastEthernet pour garder une cohérence avec GNS3. Bien sur, ce chiffre est modifiable
                                    info = {
                                            "name": "FastEthernet0/0",
                                            "location": "intra",
                                            "neighbor": f"R{j+1}",
                                            }
                                else:
                                    info = {
                                            "name": f"GigabitEthernet{nombre_interface}/0",
                                            "location": "intra",
                                            "neighbor": f"R{j+1}",
                                            }
                                # Si le protocole de l'interface est ospf, on rajoute une information sur la métrique du lien, que l'on initialise à 1. Cette valeur sera changeable manuellement.
                                if(AS_PROTOCOLS[AS]=="ospf"):
                                    if(Adjacence[routeur_avant+i][j]==1):
                                        info["cost"]=1
                                    else: 
                                        info["cost"]=Adjacence[routeur_avant+i][j]
                                
                                # Ce "if" permet de gérer l'adressage. Si le lien avec le voisin n'a pas encore été établi, on génère un adressage
                                if compteur_routeur-1<j :
                                    info["ipv6"]= f"2001:100:{AS+1}:{nombre_lien}::{j+1}/64"
                                    nombre_lien+=1
                                # Sinon, on récupère l'adressage du lien établi puis on le modifie pour assurer qu'on n'ait pas les mêmes adresses
                                else:
                                    
                                    # Ici, on se déplace dans les différents interfaces du voisin dont le lien a déjà été établi    
                                    for z in range(1, len(topology["topology"]["AS"][AS]["routeurs"][j-routeur_avant]["config"]["interfaces"])):
                                        # On cherche l'interface pour trouver celui qui correspond au routeur que l'on est en train de traiter
                                        if topology["topology"]["AS"][AS]["routeurs"][j-routeur_avant]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{routeur_avant+i+1}":
                                            # On récupère toute l'adresse sauf la fin
                                            substring = topology["topology"]["AS"][AS]["routeurs"][j-routeur_avant]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                            # On modifie la fin pour avoir un bon adressage
                                            info["ipv6"]=substring[0]+f":{j+1}/64"
                            
                            # Si le voisin n'est pas dans l'AS, alors le routeur est automatiquement un routeur de bordure
                            else:
                                is_a_border_router = True
                                
                                if nombre_interface==4:
                                    
                                    info = {
                                            "name": "FastEthernet0/0",
                                            "location": "inter",
                                            "neighbor": f"R{j+1}",
                                            "business": "admin"
                                            }
                                else:
                                    info = {
                                            "name": f"GigabitEthernet{nombre_interface}/0",
                                            "location": "inter",
                                            "neighbor": f"R{j+1}",
                                            "business": "admin"
                                            }
                                
                                # Ce "if" permet de gérer l'adressage. Si le lien avec le voisin n'a pas encore été établi, on génère un adressage
                                if compteur_routeur-1<j :
                                    info["ipv6"]= f"2001:100:0:{nombre_routeur_bordure}::{j+1}/64"
                                    # Ici, on indique qu'on a un nouveau lien inter-AS, pour ne pas se tromper lors de l'adressage
                                    nombre_routeur_bordure+=1
                                # Sinon, on récupère l'adressage du lien établi puis on le modifie pour assurer qu'on n'ait pas les mêmes adresses
                                else:
                                    # Ici, on se déplace dans les différents interfaces du voisin dont le lien a déjà été établi 
                                    compteur_routeur_as_voisin=0
                                    
                                    # Cette boucle permet de compter le nombre de routeur qu'on a déjà traversé pour garder une cohérence au fil des AS
                                    for x in range(0, len(NOMBRE_ROUTEUR_PAR_AS)):
                                        compteur_routeur_as_voisin+=NOMBRE_ROUTEUR_PAR_AS[x]
                                        if j<compteur_routeur_as_voisin:
                                            ASVoisin=x
                                            compteur_routeur_as_voisin-=NOMBRE_ROUTEUR_PAR_AS[x]
                                            break
                                    for z in range(1, len(topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"])):
                                        # On cherche l'interface pour trouver celui qui correspond au routeur que l'on est en train de traiter
                                        if topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{routeur_avant+i+1}":
                                            # On récupère toute l'adresse sauf la fin
                                            substring = topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                            # On modifie la fin pour avoir un bon adressage
                                            info["ipv6"]=substring[0]+f":{j+1}/64"

                            router["config"]["interfaces"][interface]=info
                            
                    # Si le type n'est pas int, alors on test si le type est string        
                    elif type(Adjacence[routeur_avant+i][j])==str:     
                        # Dans ce cas, on est normalement sur un routeur de bordure      
                        # On définit une variable "nombre_interface" qui va servir à indiquer une interface non-utilisée
                            nombre_interface= len(router["config"]["interfaces"])
                            interface = f"interface_{nombre_interface}"
                            
                            # Si les voisins étudiés sont inférieurs au nombre de routeur par AS, cela signifie qu'on est encore dans l'AS.
                            if(routeur_avant <= j < Total_router-routeur_apres):
                                # Il y a donc une erreur
                                print("Erreur: community dans un routeur intra-AS")
                            
                            # Si le voisin n'est pas dans l'AS, alors le routeur est automatiquement un routeur de bordure
                            else:
                                is_a_border_router = True
                                
                                if nombre_interface==4:
                                    
                                    info = {
                                            "name": "FastEthernet0/0",
                                            "location": "inter",
                                            "neighbor": f"R{j+1}",
                                            }
                                else:
                                    info = {
                                            "name": f"GigabitEthernet{nombre_interface}/0",
                                            "location": "inter",
                                            "neighbor": f"R{j+1}",
                                            "business": Adjacence[routeur_avant+i][j]
                                            }
                                
                                # Ce "if" permet de gérer l'adressage. Si le lien avec le voisin n'a pas encore été établi, on génère un adressage
                                if compteur_routeur-1<j :
                                    info["ipv6"]= f"2001:100:0:{nombre_routeur_bordure}::{j+1}/64"
                                    # Ici, on indique qu'on a un nouveau lien inter-AS, pour ne pas se tromper lors de l'adressage
                                    nombre_routeur_bordure+=1
                                # Sinon, on récupère l'adressage du lien établi puis on le modifie pour assurer qu'on n'ait pas les mêmes adresses
                                else:
                                    # Ici, on se déplace dans les différents interfaces du voisin dont le lien a déjà été établi 
                                    compteur_routeur_as_voisin=0
                                    for x in range(0, len(NOMBRE_ROUTEUR_PAR_AS)):
                                        compteur_routeur_as_voisin+=NOMBRE_ROUTEUR_PAR_AS[x]
                                        if j<compteur_routeur_as_voisin:
                                            ASVoisin=x
                                            compteur_routeur_as_voisin-=NOMBRE_ROUTEUR_PAR_AS[x]
                                            break
                                    for z in range(1, len(topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"])):
                                        # On cherche l'interface pour trouver celui qui correspond au routeur que l'on est en train de traiter
                                        if topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{routeur_avant+i+1}":
                                            # On récupère toute l'adresse sauf la fin
                                            substring = topology["topology"]["AS"][ASVoisin]["routeurs"][j-compteur_routeur_as_voisin]["config"]["interfaces"][f"interface_{z}"]["ipv6"].rsplit(":",1)
                                            # On modifie la fin pour avoir un bon adressage
                                            info["ipv6"]=substring[0]+f":{j+1}/64"

                            router["config"]["interfaces"][interface]=info
                        
                    else:
                        print("Erreur: format dans la matrice d'adjacence")
                        return ""
                                
                if (is_a_border_router == True):
                    router["informations"]["border_router"]= "true"
                else:
                    router["informations"]["border_router"]="false"       
                        
                topology["topology"]["AS"][AS]["routeurs"].append(router)
        
    return topology   
        
        
        
        
        

if __name__ == "__main__":
    gns3_topology = create_gns3_topology()
    
    with open("gns3_topology.json", "w") as json_file:
        json.dump(gns3_topology, json_file, indent=2)

    print("Fichier généré: gns3_topology.json")

     
