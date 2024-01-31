import json

def create_gns3_topology():
    
    NOMBRE_ROUTEUR_PAR_AS = 3
    
    
    
    numero_interface = 1
    
    topology = {
        "version": "1.2.1",
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
                        "interface_1": {
                            "name": f"gigabitEthernet{i}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        },
                        "interface_2": {
                            "name": "loopback0",
                            "type": "loopback",
                            "ipv6": f"2001:100:1:3::{i}/128",
                            "routing_protocole": "bgp"
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
                        "interface_1": {
                            "name": f"gigabitEthernet{i-1}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i-1}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        },
                        "interface_2": {
                            "name": f"gigabitEthernet{i}/0",
                            "type": "ethernet",
                            "ipv6": f"2001:100:1:{i}::{numero_interface}/64",
                            "routing_protocole": "ripng"
                        },
                        "interface_3": {
                            "name": "loopback0",
                            "type": "loopback",
                            "ipv6": f"2001:100:1:3::{i}/128",
                            "routing_protocole": "bgp"
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
                            "interface_1": {
                                "name": f"gigabitEthernet{i-1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:1:{i-1}::{numero_interface}/64",
                                "routing_protocole":"ripng"
                            },
                            "interface_2": {
                                "name": f"gigabitEthernet{i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:3:1::1/64",
                                "routing_protocole":"bgp"
                            },
                            "interface_3": {
                                "name": "loopback0",
                                "type": "loopback",
                                "ipv6": f"2001:100:1:3::{i}/128",
                                "routing_protocole": "bgp"
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
                            "interface_1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:3:1::2/64",
                                "routing_protocole":"bgp"
                            },
                            "interface_2": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:1::{numero_interface}/64",
                                "routing_protocole": "ospf"
                            }, 
                            "interface_3": {
                                "name": "loopback0",
                                "type": "loopback",
                                "ipv6": f"2001:100:2:3::{i}/128",
                                "routing_protocole": "bgp"
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
                            "interface_1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i-1}::{numero_interface}/64",
                                "routing_protocole":"ospf"
                            },
                            "interface_2": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i}::{numero_interface}/64",
                                "routing_protocole": "ospf"
                            },
                            "interface_3": {
                                "name": "loopback0",
                                "type": "loopback",
                                "ipv6": f"2001:100:2:3::{i}/128",
                                "routing_protocole": "bgp"
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
                            "interface_1": {
                                "name": f"gigabitEthernet{NOMBRE_ROUTEUR_PAR_AS*2-i+1}/0",
                                "type": "ethernet",
                                "ipv6": f"2001:100:2:{-NOMBRE_ROUTEUR_PAR_AS+i-1}::{numero_interface}/64",
                                "routing_protocole":"ospf"
                            },
                            "interface_2": {
                                "name": "loopback0",
                                "type": "loopback",
                                "ipv6": f"2001:100:2:3::{i}/128",
                                "routing_protocole": "bgp"
                            }  
                        }
                    }
                } 
                
        topology["topology"]["routeurs"].append(router)

    # Connexion entre R3 et R4 en BGP
    link_bgp = {
        "nodes": {
            "node_name_1": f"R{NOMBRE_ROUTEUR_PAR_AS}",
            "node_name_2": f"R{NOMBRE_ROUTEUR_PAR_AS+1}"
        },
        "label": "AS1-AS2 Link",
        "label_type": "bgp",
        "link_type": "inter",
        "ASnumber_1": 1,
        "ASnumber_2": 2
    }
    topology["topology"]["links"].append(link_bgp)

    # Connexion des routeurs au AS1 et AS2
    for i in range(2, NOMBRE_ROUTEUR_PAR_AS+1):
        link_ripng = {
            "nodes": {
                "node_name_1": f"R{i-1}",
                "node_name_2": f"R{i}"
            },
            "label": "AS1 Link",
            "label_type": "ripng",
            "link_type": "intra",
            "ASnumber": 1
        }
        topology["topology"]["links"].append(link_ripng)

    for i in range(NOMBRE_ROUTEUR_PAR_AS+2, NOMBRE_ROUTEUR_PAR_AS*2+1):
        link_ospf = {
            "nodes":  {
                "node_name_1": f"R{i-1}",
                "node_name_2": f"R{i}"
            },
            "label": "AS2 Link",
            "label_type": "ospf",
            "link_type": "intra",
            "ASnumber": 2
        }
        topology["topology"]["links"].append(link_ospf)

    return topology

if __name__ == "__main__":
    gns3_topology = create_gns3_topology()
    
    with open("gns3_topology.json", "w") as json_file:
        json.dump(gns3_topology, json_file, indent=2)

    print("GNS3 topology JSON file created: gns3_topology.json")


#def properties(i, protocole):
     