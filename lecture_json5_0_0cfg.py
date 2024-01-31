import json

# Chemin vers le fichier JSON
fichier_json = "giga_big_network.json"

# Fonction pour lire le fichier JSON et renvoyer son contenu
def lire_fichier_json(fichier_json):
    with open(fichier_json, 'r') as fichier:
        contenu_json = json.load(fichier)
    return contenu_json

def creer_fichier_cfg(ecrire_tot):
    i=1
    for ecrire in ecrire_tot : 
        with open(f"i{i}_startup-config.cfg", "w") as fichier:
            fichier.write(ecrire)
            i+=1

def creer_cfg(contenu_variable,header):

    ecrire_tot=[]
    for AS_dico in contenu_variable["topology"]["AS"] :
      for routeur in AS_dico["routeurs"]:
          
          ecrire=header[0]+f"hostname {routeur['informations']['name']}"+header[1]+"!\n!\n!\n"
          config=routeur["config"]
          info=routeur["informations"]

          for clef,val in config["interfaces"].items():
              ecrire+=interfaces_utiles(val["name"],config,AS_dico)

          ecrire+=bgp(contenu_variable,config,info,AS_dico,header)
          ecrire+=header[3]
          ecrire_tot.append(ecrire)
      
    creer_fichier_cfg(ecrire_tot)
    
def interfaces_utiles(interface,config,AS_dico):

    texte=f"interface {interface} \n no ip address \n"
    lien=" "

    if interface=="Loopback0": #Pour la loopback en RIP rajouter qqc pour l'activer voir sur internet
        ipv6=config["interfaces"]["interface_0"]["ipv6"]
        texte+=" ipv6 address "+ipv6+"\n"
    
    elif interface=="FastEthernet0/0":
        ipv6=config["interfaces"]["interface_4"]["ipv6"] #Faire un truc pour interface FastEthernet
        lien=config["interfaces"][f"interface_4"]["location"]
        texte+=" duplex full"+ "\n"+" ipv6 address "+ipv6+ "\n"
        nom_interface="interface_4"
        
    else :
        texte+=" negotiation auto \n"
        for i in range (3):
            if interface==f"GigabitEthernet{i+1}/0":
                lien=config["interfaces"][f"interface_{i+1}"]["location"]
                texte+=" ipv6 address "+config["interfaces"][f"interface_{i+1}"]["ipv6"]+ "\n"
                nom_interface=f"interface_{i+1}"

                
    routing_protocole=AS_dico["AS_protocol"]

    texte+=" ipv6 enable"
    if routing_protocole=="ripng" and (lien== "intra" or interface=="Loopback0"):  
        texte+="\n ipv6 rip ripng enable"                 
    elif routing_protocole=="ospf": 
        texte+="\n ipv6 ospf 200 area 1"
        if interface!="Loopback0" and lien == "intra":
            texte+=f"\n ipv6 ospf cost {config['interfaces'][nom_interface]['cost']}"

    
    texte+="\n!\n"
    return texte 

def bgp(contenu_variable,config,info,AS_dico,header):
    
    router_id=f"{info['router_number']}.{info['router_number']}.{info['router_number']}.{info['router_number']}"
    AS=AS_dico['AS_number']
    ipv6_voisins=[]
    texte=f"router bgp {AS} \n bgp router-id {router_id}\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
    texte2=""
    
    for routeur in AS_dico["routeurs"]:
      if routeur["informations"]!=info :
        ipv6=routeur["config"]["interfaces"]["interface_0"]["ipv6"].split("/")[0]
        ipv6_voisins.append(ipv6)
        texte+= f" neighbor {ipv6} remote-as {AS} \n neighbor {ipv6} update-source Loopback0 \n"

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
                                              interface_passive=interface
                                              ipv6=routeur["config"]["interfaces"][f"{interface_inter}"]["ipv6"].split("/")[0]
                                              ipv6_voisins.append(ipv6)
                                              texte+= f"  neighbor {ipv6} remote-as {AS_tout['AS_number']} \n"
                                          if routeur["config"]["interfaces"][interface_inter]["business"]=="client" :
                                                      texte2 += f" neighbor {ipv6} route-map CLIENT_IN in \n"
                                          elif routeur["config"]["interfaces"][interface_inter]["business"]=="peer":
                                              texte2 += f"  neighbor {ipv6} route-map PEER_IN in \n"
                                              texte2 += f"  neighbor {ipv6} route-map PP_OUT out \n"
                                          elif routeur["config"]["interfaces"][interface_inter]["business"]=="provider" :
                                              texte2 += f"  neighbor {ipv6} route-map PROVIDER_IN in \n"
                                              texte2 += f"  neighbor {ipv6} route-map PP_OUT out \n"

    
    texte+=" ! \n address-family ipv4 \n exit-address-family \n ! \n address-family ipv6 \n"

    if info["border_router"]=="true":
        texte += f"  network {AS_dico['network']} route-map SET_ADMIN\n"

    for addr in ipv6_voisins : 
        texte += f"  neighbor {addr} activate \n"
        texte += f"  neighbor {addr} send-community \n"
    texte += texte2

    texte+=" exit-address-family \n"
    
    texte+=header[2]

    if info["border_router"]=="true":
            texte+=f"ipv6 route {AS_dico['network']} Null0 \n"

    if AS_dico["AS_protocol"]=="ospf":
        texte +=f"ipv6 router ospf 200 \n router-id {router_id} \n"
        if info["border_router"]=="true":
            texte+=f" passive-interface {config['interfaces'][interface_passive]['name']}"

    else : 
        texte +="ipv6 router rip ripng \n redistribute connected \n"

    if info["border_router"]=="true":

        texte+="\n!\nip bgp community new-format\nip community-list 1 permit 1\nip community-list 2 permit 2\nip community-list 3 permit 3 \n!\n"
        texte+="route-map CLIENT_IN permit 10\n set community 1\n set local-preference 150\n!\n"
        texte+="route-map PEER_IN permit 10\n set community 2\n set local-preference 100\n!\n"
        texte+="route-map PROVIDER_IN permit 10\n set community 3\n set local-preference 50\n!\n"
        texte+="route-map SET_ADMIN permit 10\n match community 4\n!\n"
        texte+="route-map PP_OUT permit 10\n match community 1\n match community 4\n!\n"

    return texte

# Appel de la fonction pour lire le fichier JSON
contenu_variable = lire_fichier_json(fichier_json)

header=["""version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
""","""
boot-start-marker
boot-end-marker
no aaa new-model
no ip icmp rate-limit unreachable
ip cef
no ip domain lookup
ipv6 unicast-routing
ipv6 cef
multilink bundle-name authenticated
ip tcp synwait-time 5
""","""!
ip forward-protocol nd
no ip http server
no ip http secure-server
!
""","""!
control-plane
line con 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line aux 0
 exec-timeout 0 0
 privilege level 15
 logging synchronous
 stopbits 1
line vty 0 4
 login
end
!
"""]

creer_cfg(contenu_variable,header)
