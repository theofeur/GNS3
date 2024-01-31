import json

def create_gns3_topology():
    
    Adjacence= [[0,0,1,0,0,0],
                [0,0,1,0,0,0],
                [1,1,0,1,0,0],
                [0,0,1,0,1,1],
                [0,0,0,1,0,0],
                [0,0,0,1,0,0]]
    
    
    NOMBRE_ROUTEUR_PAR_AS = len(Adjacence)//2
    numero_interface = 1
    
    topology = {
        "version": "2.0.0",
        "project_name": "petit_adressage_test",
        "topology": {
            "routeurs": []
            }
        }

    # Ajout des routeurs AS1 (R1, R2, R3) en Ripng
    nombre_lien=1
    for i in range(0, NOMBRE_ROUTEUR_PAR_AS):           
        router = {
                "informations": {
                    "name": f"R{i+1}",
                    "router_number": f"{i+1}",
                    "ASnumber": "1"
                },
                "config": {
                    "interfaces": {
                        "interface_0": {
                            "name": "Loopback0",
                            "type": "loopback",
                            "routing_protocole": "bgp",
                            "ipv6": f"2001:100:1:0::{i+1}/128"
                            
                        }
                    }         
                }
            }
        
        for j in range(0, NOMBRE_ROUTEUR_PAR_AS):
            if Adjacence[i][j]==1:
                nombre_interface= len(router["config"]["interfaces"])
                interface = f"interface_{nombre_interface}"
                info = {
                        "name": f"GigabitEthernet{nombre_interface}/0",
                        "type": "ethernet",
                        "location": "intra",
                        "neighbor": f"R{j+1}",
                        "routing_protocole": "ripng",
                        }
                if len(topology["topology"]["routeurs"])<j :
                    info["ipv6"]= f"2001:100:1:{nombre_lien}::{j+1}/64"
                    nombre_lien+=1
                else:
                    for z in range(1, len(topology["topology"]["routeurs"][j]["config"]["interfaces"])):
                        if topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["neighbor"]==f"R{i+1}":
                            substring = topology["topology"]["routeurs"][j]["config"]["interfaces"][f"interface_{z}"]["ipv6"][:-4]
                            info["ipv6"]=substring+f"{j+1}/64"

                router["config"]["interfaces"][interface]=info
            
        if i == NOMBRE_ROUTEUR_PAR_AS-1:
            interface = f"interface_{nombre_interface+1}"
            info = {
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


#def properties(i, protocole):
     