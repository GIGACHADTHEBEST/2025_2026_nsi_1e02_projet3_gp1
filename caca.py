def coup_bot(allumettes: int, max_prise: int = 3) -> int:
    modulo = max_prise + 1
    reste = allumettes % modulo
    return reste if reste != 0 else 1 


def jouer():
    allumettes = int(input("Nombre d'allumettes au départ : "))
    max_prise  = int(input("Max allumettes par tour (défaut 3) : ") or 3)

    tour = 0  # 0 = joueur, 1 = bot

    while allumettes > 0:
        print(f"\n Allumettes restantes : {allumettes}")

        if tour == 1:
            prise = coup_bot(allumettes, max_prise)
            print(f" Le bot prend : {prise}")
        else:
            while True:
                try:
                    prise = int(input(f"Combien prenez-vous ? (entre 1 et {min(max_prise, allumettes)} compris) : "))
                    if 1 <= prise <= min(max_prise, allumettes):
                        break
                    print("Invalide, réessayez.")
                except ValueError:
                    print("Entrez un entier.")

        allumettes -= prise #mise a jour

        if allumettes == 0:
            gagnant = ["Joueur", "Bot"][tour]
            print(f"\n {gagnant} a pris la dernière allumette --> {gagnant} GAGNE !")
            break

        tour = 1 - tour


if __name__ == "__main__":
    jouer()

