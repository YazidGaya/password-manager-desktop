from cryptography.fernet import Fernet

#Création de la clé (32 bits)
key = Fernet.generate_key()#
print(key)
fichCle =open("maCle.key","wb")
fichCle.write(key)
fichCle.close()
print("Clée crée")

ficheCle=open("maCle.key", "rb")
key=ficheCle.read()

f=Fernet(key)

fichierAchiffrer= open("mesInfo.txt", "rb")
aChiffrer=fichierAchiffrer.read()
fichierAchiffrer.close()

chiffre=f.encrypt(aChiffrer)

fichierChiffrement= open("mesInfoChiffrer.txt","wb")
fichierChiffrement.write(chiffre)
fichierChiffrement.close()



