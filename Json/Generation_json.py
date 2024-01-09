import json

def create_gns3_topology():
    
    NOMBRE_ROUTEUR_PAR_AS = 3
    
    
    
    numero_interface = 1
    
    topology = {
        "version": "1.0.1.1",
        "project_name": "petit_adressage_test",
        "topology": {
            "routeurs": [],
            "links": []
        }
    }

    # Ajout des routeurs AS1 (R1, R2, R3) en Ripng
    for i in range(1, NOMBRE_ROUTEUR_PAR_AS+1):
        if i%2==0:
            numero_interface=2
        else:
            numero_interface=1
        if i==1:
            router = {
                "informations": {
                    "name": f"R{i}",
                    "x": i * 100,
                    "y": 100,
                    "type": "router",
                    "ASnumber": 1
                },
                "config": {
                    "interfaces": {
                        "interface1": {
                            "name": f"gigabitEthernet{i}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        }
                    }         
                }
        }
            
            
        elif i!=NOMBRE_ROUTEUR_PAR_AS:
            router = {
                "informations": {
                    "name": f"R{i}",
                    "x": i * 100,
                    "y": 100,
                    "type": "router",
                    "ASnumber": 1
                    },
                "config": {
                    "interfaces": {
                        "interface1": {
                            "name": f"gigabitEthernet{i-1}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i-1}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        },
                        "interface2": {
                            "name": f"gigabitEthernet{i}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        }
                    }
                }
            }
            
        elif i==NOMBRE_ROUTEUR_PAR_AS:
                router = {
                    "informations": {
                        "name": f"R{i}",
                        "x": i * 100,
                        "y": 100,
                        "type": "router",
                        "ASnumber": 1
                        },
                    "config": {
                        "interfaces": {
                            "interface1": {
                                "name": f"gigabitEthernet{i-1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:1:{i-1}::{numero_interface}/64",
                                "routing_protocole":"ripng"
                            },
                            "interface2": {
                                "name": f"gigabitEthernet{i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:3:1::1/64",
                                "routing_protocole":"bgp"
                        }
                    }
                }
            }     
            
            
            
            
        
        topology["topology"]["routeurs"].append(router)

    # Ajout des routeurs AS2 (R4, R5, R6) en OSPF
    for i in range(NOMBRE_ROUTEUR_PAR_AS+1, NOMBRE_ROUTEUR_PAR_AS*2+1):
        
        if i%2==0:
            numero_interface=1
        else:
            numero_interface=2
        
        
        if i==NOMBRE_ROUTEUR_PAR_AS+1:
            router = {
                    "informations": {
                        "name": f"R{i}",
                        "x": i * 100,
                        "y": 100,
                        "type": "router",
                        "ASnumber": 2
                        },
                    "config": {
                        "interfaces": {
                            "interface1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:3:1::2/64",
                                "routing_protocole":"bgp"
                            },
                            "interface2": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:1::{numero_interface}/64",
                                "routing_protocole": "ospf"
                        }
                    }
                }
            }
        
        elif i!=NOMBRE_ROUTEUR_PAR_AS*2:
            router = {
                    "informations": {
                        "name": f"R{i}",
                        "x": i * 100,
                        "y": 100,
                        "type": "router",
                        "ASnumber": 2
                        },
                    "config": {
                        "interfaces": {
                            "interface1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i-1}::{numero_interface}/64",
                                "routing_protocole":"ospf"
                            },
                            "interface2": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i}::{numero_interface}/64",
                                "routing_protocole": "ospf"
                        }
                    }
                }
            }
            
        elif i==NOMBRE_ROUTEUR_PAR_AS*2:
                router = {
                    "informations": {
                        "name": f"R{i}",
                        "x": i * 100,
                        "y": 100,
                        "type": "router",
                        "ASnumber": 2
                        },
                    "config": {
                        "interfaces": {
                            "interface1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i-1}::{numero_interface}/64",
                                "routing_protocole":"ospf"
                            }
                    }
                }
            } 
                
        topology["topology"]["routeurs"].append(router)

    # Connexion entre R3 et R4 en BGP
    link_bgp = {
        "nodes": [
            {"adapter_number": 0, "node_name": "R3"},
            {"adapter_number": 0, "node_name": "R4"}
        ],
        "label": "BGP Link",
        "link_type": "ethernet",
        "config": {"ipv4": True, "ipv6": True}
    }
    topology["topology"]["links"].append(link_bgp)

    # Connexion des routeurs au AS1 et AS2
    for i in range(1, 4):
        link_ripng = {
            "nodes": [
                {"adapter_number": 0, "node_name": f"R{i}"},
                {"adapter_number": 0, "node_name": "AS1"}
            ],
            "label": f"R{i}-AS1 Link",
            "link_type": "ethernet",
            "config": {"ipv4": True, "ipv6": True}
        }
        topology["topology"]["links"].append(link_ripng)

    for i in range(4, 7):
        link_ospf = {
            "nodes": [
                {"adapter_number": 0, "node_name": f"R{i}"},
                {"adapter_number": 0, "node_name": "AS2"}
            ],
            "label": f"R{i}-AS2 Link",
            "link_type": "ethernet",
            "config": {"ipv4": True, "ipv6": True}
        }
        topology["topology"]["links"].append(link_ospf)

    return topology

if __name__ == "__main__":
    gns3_topology = create_gns3_topology()
    
    with open("gns3_topology.json", "w") as json_file:
        json.dump(gns3_topology, json_file, indent=2)

    print("GNS3 topology JSON file created: gns3_topology.json")


#def properties(i, protocole):
     