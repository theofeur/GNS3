from gns3fy import Gns3Connector, Project 
from telnetlib import Telnet


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


if __name__ == '__main__' :
    noeuds = start_telnet("projet_essai_telnet")
    commande("en", noeuds, "R1")
    commande("conf t", noeuds, "R1")
    commande("int GigabitEthernet 1/0", noeuds, "R1")
    commande("ipv6 enable", noeuds, "R1")
    commande("ipv6 address 2001:100:1:1::1/64", noeuds, "R1")
    commande("no shutdown", noeuds, "R1")