import os
import shutil

"""fonction qui retourne le répertoire où se trouve le fichier 'nom_fichier_déjà_dedans' parmis les répertoires dans la liste dests """
def trouve_repertoire_cible(dests, nom_fichier_déjà_dedans):
    for repertoire in dests :
        if nom_fichier_déjà_dedans in os.listdir(repertoire):
            return repertoire
    return None

if __name__=="__main__":
    """chemin vers répertoire contenant les fichiers cfg à déplacer"""
    source = 'C:\\Users\\gabir\\OneDrive\\Documents\\Répertoire_essai'
    """chemin vers dynamips"""
    dynamips='C:\\Users\\gabir\\GNS3\\projects\\Net_Aut_Project_V2\\project-files\\dynamips\\'
    dests=[]
    result=[]
    nb_routeurs = 6
    
    for repertoire in os.listdir(dynamips) : 
        if os.path.isdir(dynamips + repertoire)==True :
            dests.append(dynamips + "\\" + repertoire + '\\configs')
    
    if len(dests)==0 :
        print("dests est vide zebi")

    for k in range (1,nb_routeurs+1) :
        nom_fichier = f"i{k}_startup-config.cfg"
        rep_cible=trouve_repertoire_cible(dests, nom_fichier)
        result.append(rep_cible)
        """effacer le fichier qui est déjà dedans"""
        os.remove(rep_cible + f"\\i{k}_startup-config.cfg") 
    
    """à partir d'ici les répertoires configs sont vides et placés dans result dans le bon ordre"""
    for k in range (1,nb_routeurs+1) :
        shutil.copy(source + f"\\i{k}_startup-config.cfg", result[k-1])



