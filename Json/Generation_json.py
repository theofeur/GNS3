import json

def create_gns3_topology():
    topology = {
        "version": "1.0.0.0",
        "project_name": "petit_adressage_test",
        "topology": {
            "nodes": [],
            "links": []
        }
    }

    # Ajout des routeurs AS1 (R1, R2, R3) en Ripng
    for i in range(1, 4):
        router = {
            "name": f"R{i}",
            "x": i * 100,
            "y": 100,
            "symbol": "router",
            "node_type": "dynamips",
            "compute_id": "local",
            "symbol": "ROUTER",
            "label": f"AS1-R{i}",
            "properties": {
                "adapter_type": "virtio-net",
                "image": "qemu-img",
                "qemu_path": "/usr/bin/qemu-system-x86_64",
                "ram": 256,
                "hda_disk_image": "",
                "cdrom_image": "",
                "boot_priority": "c"
            }
        }
        topology["topology"]["nodes"].append(router)

    # Ajout des routeurs AS2 (R4, R5, R6) en OSPF
    for i in range(4, 7):
        router = {
            "name": f"R{i}",
            "x": (i - 3) * 100,
            "y": 300,
            "symbol": "router",
            "label": f"AS2-R{i}",
            "console": 5000 + i,
            "type": "qemu",
            "properties": {
                "adapter_type": "virtio-net",
                "image": "qemu-img",
                "qemu_path": "/usr/bin/qemu-system-x86_64",
                "ram": 256,
                "hda_disk_image": "",
                "cdrom_image": "",
                "boot_priority": "c"
            }
        }
        topology["topology"]["nodes"].append(router)

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
     