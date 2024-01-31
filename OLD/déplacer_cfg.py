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
    dynamips='C:\\Users\\gabir\\GNS3\\projects\\Net_Aut_Project_V2\\project-files\\dynamips'
    """chemins vers les répertoires possibles"""
    dests = [dynamips + '\\29598050-f4af-48f1-80ef-0b9e6e828f3f\\configs', dynamips + '\\6607d6b6-e7d0-4b19-bb2e-f10603ae01cf\\configs', dynamips + '\\bd5c103b-c96e-41a0-bebf-94e4418e057c\\configs', dynamips + '\\c95c3ace-5be1-42db-a3f8-29131802ba8b\\configs', dynamips + '\\e29a8fd8-473d-4aff-b733-3a325b8d097c\\configs', dynamips + '\\ec2a4221-8984-472b-b14c-6d1f3b5da48c\\configs' ]
    result=[]
    
    for k in range (1,7) :
        nom_fichier = f"i{k}_startup-config.cfg"
        rep_cible=trouve_repertoire_cible(dests, nom_fichier)
        result.append(rep_cible)
        """effacer le fichier qui est déjà dedans"""
        os.remove(rep_cible + f"\\i{k}_startup-config.cfg") 
    
    """à partir d'ici les répertoires configs sont vides et placés dans result dans le bon ordre"""
    for k in range (1,7) :
        shutil.copy(source + f"\\i{k}_startup-config.cfg", result[k-1])



