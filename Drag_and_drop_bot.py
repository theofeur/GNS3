import os
import shutil

#fonction qui retourne le répertoire où se trouve le fichier 'nom_fichier_déjà_dedans' parmis les répertoires dans la liste dests 
def trouve_repertoire_cible(dests, nom_fichier_déjà_dedans):
    for repertoire in dests :
        if nom_fichier_déjà_dedans in os.listdir(repertoire):
            return repertoire
    return None

if __name__=="__main__":
    #chemin vers répertoire contenant les fichiers cfg à déplacer
    source = 'C:\\Users\\theoa\\Documents\\GitHub'
    #chemin vers dynamips\ du projet
    dynamips='C:\\Users\\theoa\\Documents\\GitHub\\GNS3\\GNS3 Overlay\\PROJET BIG AS\\project-files\\dynamips\\'
    dests=[]
    result=[]
    nb_routeurs = 18
    
    #on sélectionne seulement les répertoires dans dynamips (on exclu les fichiers) et on les ajoute à dests[]
    for repertoire in os.listdir(dynamips) : 
        if os.path.isdir(dynamips + repertoire)==True :
            dests.append(dynamips + "\\" + repertoire + '\\configs')
    
    if len(dests)==0 :
        print("Aucun répertoire trouvé dans dynamips.")

    for k in range (1,nb_routeurs+1) :
        nom_fichier = f"i{k}_startup-config.cfg"
        #pour chaque routeur n°k on cherche son dossier 
        rep_cible=trouve_repertoire_cible(dests, nom_fichier)
        #on ajoute ce dossier à resulr[] et on efface le fichier qui est déjà dedans
        result.append(rep_cible)
        os.remove(rep_cible + f"\\i{k}_startup-config.cfg") 
    
    #à partir d'ici les répertoires configs sont vides et placés dans result dans le bon ordre, on copie les fichiers 
    for k in range (1,nb_routeurs+1) :
        shutil.copy(source + f"\\i{k}_startup-config.cfg", result[k-1])
