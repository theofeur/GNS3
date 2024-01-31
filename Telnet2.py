from gns3fy import Gns3Connector, Project 
from telnetlib import Telnet
import json
import time


def start_telnet(projet_name) :
    serveur = Gns3Connector("http://localhost:3080")
    projet = Project(name=projet_name,connector=serveur)
        
    projet.get()
    projet.open()

    noeuds = {}
    for noeud in projet.nodes : 
        noeuds[noeud.name] = Telnet(noeud.console_host,str(noeud.console))
    return noeuds

def commande(cmd,noeuds,routeur) :
    if type(cmd) == str :
        noeuds[routeur].write(bytes(cmd+"\r",encoding="ascii"))
    time.sleep(0.1)

def lire_fichier_json(fichier_json):
    with open(fichier_json, 'r') as fichier:
        contenu_json = json.load(fichier)
    return contenu_json

def main(contenu_variable,noeuds):
    
    for AS_dico in contenu_variable["topology"]["AS"] :
      for routeur in AS_dico["routeurs"]:
          
        config=routeur["config"]
        info=routeur["informations"]

        for clef,val in config["interfaces"].items():
            interfaces_utiles(noeuds,val["name"],config,info,AS_dico)       

        
        
    
def interfaces_utiles(noeuds,interface,config,info,AS_dico):

    name=info["name"]
    router_id=f"{info['router_number']}.{info['router_number']}.{info['router_number']}.{info['router_number']}"
    routing_protocole=AS_dico["AS_protocol"]

    commande("\r", noeuds, name)
    commande("\r", noeuds, name)
    
    commande("enable", noeuds, name)
    commande("conf t", noeuds, name)

    if routing_protocole=="ripng":
        commande("ipv6 unicast-routing", noeuds, name)
        commande("ipv6 router rip ripng", noeuds, name)
        commande("redistribute connected", noeuds, name)
    
    elif routing_protocole=="ospf":
        commande("ipv6 unicast-routing", noeuds, name)
        commande("ipv6 router ospf 200", noeuds, name)
        commande(f"router-id {router_id}", noeuds, name)

    commande("exit",noeuds,name)
    commande(f"interface {interface}",noeuds,name)
    commande("ipv6 enable",noeuds,name)
    lien=" "

    if interface=="Loopback0":
        ipv6=config["interfaces"]["interface_0"]["ipv6"]
        commande(f"ipv6 address {ipv6}",noeuds,name)
    
    elif interface=="FastEthernet0/0":
        ipv6=config["interfaces"]["interface_4"]["ipv6"]
        commande(f"ipv6 address {ipv6}",noeuds,name)
        lien=config["interfaces"][f"interface_4"]["location"]
        nom_interface="interface_4"
        
    else :
        for i in range (3):
            if interface==f"GigabitEthernet{i+1}/0":
                ipv6=config["interfaces"][f"interface_{i+1}"]["ipv6"]
                commande(f"ipv6 address {ipv6}",noeuds,name)
                lien=config["interfaces"][f"interface_{i+1}"]["location"]
                nom_interface=f"interface_{i+1}"

    commande("no shutdown", noeuds, name)

    if routing_protocole=="ripng" and (lien== "intra" or interface=="Loopback0"):  
        commande("ipv6 rip ripng enable", noeuds, name)               
    elif routing_protocole=="ospf": 
        commande("ipv6 ospf 200 area 1", noeuds, name)
        if interface!="Loopback0" and lien == "intra":
            commande(f"ipv6 ospf cost {config['interfaces'][nom_interface]['cost']}", noeuds, name)
  
        elif lien == "inter":
            commande("exit", noeuds, name)
            commande("ipv6 router ospf 200", noeuds, name)
            commande(f"passive-interface {interface}", noeuds, name)       

    commande("exit", noeuds, name)

    if interface=="Loopback0":
        bgp(contenu_variable,config,info,AS_dico,noeuds,name,router_id)

    else :
        commande(f"end", noeuds, name)
    

def bgp(contenu_variable,config,info,AS_dico,noeuds,name,router_id):
    
    AS_number=AS_dico['AS_number']
    ipv6_voisins=[]

    commande(f"router bgp {AS_number}", noeuds, name)
    commande(f"bgp router-id {router_id}", noeuds, name)
    commande("no bgp default ipv4-unicast", noeuds, name)
    
    
    for routeur in AS_dico["routeurs"]:
      if routeur["informations"]!=info :
        ipv6=routeur["config"]["interfaces"]["interface_0"]["ipv6"].split("/")[0]
        ipv6_voisins.append(ipv6)
        commande(f"neighbor {ipv6} remote-as {AS_number}", noeuds, name)
        commande(f"neighbor {ipv6} update-source Loopback0", noeuds, name)


    if info["border_router"]=="true":
        for interface in config["interfaces"].keys():
            if interface != "interface_0":   
                if config["interfaces"][interface]["location"]=="inter":  
                    for AS_tout in contenu_variable["topology"]["AS"] :
                        for routeur in AS_tout["routeurs"]:
                            if routeur["informations"]["name"]==config["interfaces"][interface]["neighbor"] :
                                for interface_inter in routeur['config']["interfaces"].keys() : 
                                    if interface_inter != "interface_0":   
                                        if routeur["config"]["interfaces"][interface_inter]["neighbor"]==info["name"]: 
                                            if routeur["config"]["interfaces"][interface_inter]["location"]=="inter" :
                                                ipv6=routeur["config"]["interfaces"][f"{interface_inter}"]["ipv6"].split("/")[0]
                                                ipv6_voisins.append(ipv6)
                                                commande(f"neighbor {ipv6} remote-as {AS_tout['AS_number']}",noeuds, name)       
                                            if routeur["config"]["interfaces"][interface_inter]["business"]=="client" :
                                                commande(f" neighbor {ipv6} route-map CLIENT_IN in \n",noeuds, name) 
                                            elif routeur["config"]["interfaces"][interface_inter]["business"]=="peer":
                                                commande(f" neighbor {ipv6} route-map PEER_IN in \n",noeuds,  name) 
                                                commande(f" neighbor {ipv6} route-map PP_OUT out\n",noeuds,   name)
                                            elif routeur["config"]["interfaces"][interface_inter]["business"]=="provider" :
                                                commande(f" neighbor {ipv6} route-map PROVIDER_IN in \n",noeuds,  name) 
                                                commande(f" neighbor {ipv6} route-map PP_OUT out\n",noeuds,   name)
    
    commande("address-family ipv6 unicast", noeuds, name)

    for addr in ipv6_voisins : 
        commande(f"neighbor {addr} activate", noeuds, name)
        commande(f"neighbor {addr} send-community", noeuds, name)

    if info["border_router"]=="true":
        commande(f"network {AS_dico['network'] } route-map SET_ADMIN", noeuds, name)

    commande(f"end", noeuds, name)

    if info["border_router"]=="true":
            
            commande(f"conf t", noeuds, name)
            commande(f"ipv6 route {AS_dico['network']} Null0", noeuds, name)
            commande("bgp community new-format", noeuds, name)
            commande("ip community-list 1 permit 1", noeuds, name)
            commande("ip community-list 2 permit 2", noeuds, name)
            commande("ip community-list 3 permit 3", noeuds, name)

            commande("route-map CLIENT_IN permit 10", noeuds, name)
            commande("set community 1", noeuds, name)
            commande("set local-preference 150", noeuds, name)
            commande("exit", noeuds, name)

            commande("route-map PEER_IN permit 10", noeuds, name)
            commande("set community 2", noeuds, name)
            commande("set local-preference 100", noeuds, name)
            commande("exit", noeuds, name)

            commande("route-map PROVIDER_IN permit 10", noeuds, name)
            commande("set community 13", noeuds, name)
            commande("set local-preference 50", noeuds, name)
            commande("exit", noeuds, name)

            commande("route-map SET_ADMIN permit 10", noeuds, name)
            commande("set community 4", noeuds, name)
            commande("exit", noeuds, name)

            commande("route-map PP_OUT permit 10", noeuds, name)
            commande("match community 1", noeuds, name)
            commande("match community 4", noeuds, name)
            commande("exit", noeuds, name)          
              
    
if __name__ == '__main__' :

    fichier_json = "petit_network.json"
    noeuds = start_telnet("test_telnet")
    contenu_variable = lire_fichier_json(fichier_json) 
    main(contenu_variable,noeuds)
    
