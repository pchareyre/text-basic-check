"""
Generate a French frequency dictionary for SymSpell.

This creates a basic French dictionary with common words and their frequencies.
Format: word frequency (space-separated)
"""

# Common French words with estimated frequencies
# Format: (word, frequency)
FRENCH_WORDS = [
    # Greetings and common expressions
    ("bonjour", 85000), ("bonsoir", 70000), ("salut", 65000), ("merci", 80000),
    ("pardon", 45000), ("excusez", 42000), ("s'il", 65000), ("vous", 130000),
    ("plaît", 55000), ("oui", 90000), ("non", 88000), ("peut-être", 77000),
    
    # Articles
    ("le", 500000), ("la", 400000), ("les", 350000), ("un", 300000), ("une", 280000),
    ("des", 250000), ("du", 200000), ("de", 450000), ("l", 180000),
    
    # Pronouns
    ("je", 200000), ("tu", 150000), ("il", 180000), ("elle", 170000),
    ("nous", 140000), ("vous", 130000), ("ils", 120000), ("elles", 110000),
    ("ce", 100000), ("ça", 90000), ("cela", 80000), ("qui", 150000), ("que", 140000),
    ("quoi", 70000), ("où", 65000), ("dont", 60000),
    
    # Common verbs
    ("être", 200000), ("avoir", 190000), ("faire", 180000), ("dire", 170000),
    ("aller", 160000), ("voir", 150000), ("savoir", 140000), ("pouvoir", 130000),
    ("vouloir", 120000), ("venir", 110000), ("devoir", 100000), ("prendre", 95000),
    ("donner", 90000), ("trouver", 85000), ("passer", 80000), ("mettre", 75000),
    ("parler", 70000), ("aimer", 68000), ("arriver", 66000), ("croire", 64000),
    ("demander", 62000), ("rester", 60000), ("répondre", 58000), ("laisser", 56000),
    ("penser", 54000), ("appeler", 52000), ("continuer", 50000), ("tenir", 48000),
    ("porter", 46000), ("paraître", 44000), ("connaître", 42000), ("commencer", 40000),
    ("chercher", 38000), ("comprendre", 36000), ("entendre", 34000), ("rendre", 32000),
    ("devenir", 30000), ("écrire", 28000), ("lire", 26000), ("suivre", 24000),
    ("servir", 22000), ("vivre", 20000), ("sortir", 19000), ("partir", 18000),
    ("mourir", 17000), ("ouvrir", 16000), ("sentir", 15000), ("courir", 14000),
    
    # Conjugated forms (present tense)
    ("suis", 80000), ("es", 75000), ("est", 150000), ("sommes", 60000),
    ("êtes", 55000), ("sont", 120000),
    ("ai", 90000), ("as", 85000), ("a", 140000), ("avons", 70000),
    ("avez", 65000), ("ont", 110000),
    ("fais", 60000), ("fait", 95000), ("faisons", 45000), ("faites", 42000),
    ("font", 80000),
    ("dis", 55000), ("dit", 90000), ("disons", 40000), ("dites", 38000),
    ("disent", 70000),
    ("vais", 75000), ("vas", 70000), ("va", 120000), ("allons", 60000),
    ("allez", 58000), ("vont", 95000),
    
    # Common adjectives
    ("bon", 60000), ("bonne", 58000), ("grand", 56000), ("grande", 54000),
    ("petit", 52000), ("petite", 50000), ("nouveau", 48000), ("nouvelle", 46000),
    ("vieux", 44000), ("vieille", 42000), ("jeune", 40000), ("autre", 65000),
    ("même", 63000), ("tel", 38000), ("telle", 36000), ("tout", 85000),
    ("toute", 75000), ("tous", 70000), ("toutes", 68000), ("premier", 45000),
    ("première", 43000), ("dernier", 41000), ("dernière", 39000), ("seul", 55000),
    ("seule", 53000), ("propre", 37000), ("long", 35000), ("longue", 33000),
    ("beau", 50000), ("belle", 48000), ("gros", 32000), ("grosse", 30000),
    ("mauvais", 31000), ("mauvaise", 29000), ("haut", 34000), ("haute", 32000),
    ("bas", 31000), ("basse", 29000), ("français", 55000), ("française", 53000),
    
    # Common nouns
    ("homme", 70000), ("femme", 68000), ("enfant", 66000), ("personne", 64000),
    ("monde", 62000), ("vie", 60000), ("jour", 58000), ("temps", 56000),
    ("chose", 54000), ("main", 52000), ("œil", 50000), ("yeux", 48000),
    ("tête", 46000), ("cœur", 44000), ("fois", 55000), ("part", 42000),
    ("lieu", 40000), ("année", 53000), ("mois", 38000), ("heure", 36000),
    ("minute", 34000), ("seconde", 32000), ("moment", 45000), ("point", 41000),
    ("cas", 39000), ("façon", 37000), ("manière", 35000), ("question", 43000),
    ("raison", 33000), ("idée", 40000), ("côté", 31000), ("façade", 18000),
    ("porte", 38000), ("fenêtre", 36000), ("rue", 42000), ("ville", 47000),
    ("pays", 49000), ("terre", 35000), ("maison", 44000), ("chambre", 33000),
    ("ami", 41000), ("père", 46000), ("mère", 45000), ("fils", 39000),
    ("fille", 43000), ("frère", 37000), ("sœur", 36000), ("famille", 42000),
    ("nom", 38000), ("mot", 40000), ("voix", 34000), ("eau", 37000),
    ("feu", 29000), ("air", 35000), ("terre", 35000), ("soleil", 32000),
    ("lune", 28000), ("étoile", 27000), ("mer", 33000), ("montagne", 30000),
    ("arbre", 31000), ("fleur", 28000), ("jardin", 29000), ("forêt", 27000),
    
    # Prepositions and conjunctions
    ("à", 400000), ("dans", 250000), ("pour", 240000), ("avec", 230000),
    ("sur", 220000), ("par", 210000), ("sans", 180000), ("sous", 160000),
    ("entre", 150000), ("vers", 140000), ("chez", 130000), ("depuis", 120000),
    ("pendant", 110000), ("avant", 100000), ("après", 95000), ("devant", 85000),
    ("derrière", 80000), ("contre", 75000), ("parmi", 70000), ("selon", 68000),
    ("et", 450000), ("ou", 200000), ("mais", 190000), ("donc", 170000),
    ("or", 150000), ("ni", 140000), ("car", 130000), ("comme", 160000),
    ("si", 180000), ("quand", 120000), ("lorsque", 90000), ("puisque", 85000),
    ("parce", 100000), ("bien", 95000), ("alors", 110000), ("ainsi", 88000),
    
    # Adverbs
    ("pas", 180000), ("plus", 170000), ("très", 160000), ("trop", 140000),
    ("bien", 135000), ("mal", 125000), ("peu", 120000), ("beaucoup", 115000),
    ("encore", 110000), ("déjà", 105000), ("toujours", 100000), ("jamais", 95000),
    ("souvent", 90000), ("parfois", 85000), ("maintenant", 82000), ("ici", 80000),
    ("là", 130000), ("hier", 75000), ("aujourd", 78000), ("demain", 72000),
    ("tard", 70000), ("tôt", 68000), ("vite", 66000), ("lentement", 52000),
    ("ensemble", 64000), ("seulement", 76000), ("aussi", 115000), ("même", 90000),
    ("vraiment", 74000), ("certainement", 50000), ("probablement", 48000),
    ("peut-être", 77000), ("peut", 110000), ("être", 200000),
    
    # Numbers
    ("un", 300000), ("deux", 120000), ("trois", 100000), ("quatre", 90000),
    ("cinq", 80000), ("six", 70000), ("sept", 60000), ("huit", 55000),
    ("neuf", 50000), ("dix", 65000), ("cent", 58000), ("mille", 53000),
    ("million", 35000), ("milliard", 25000), ("premier", 45000), ("second", 40000),
    ("deuxième", 43000), ("troisième", 38000), ("dernier", 41000),
    
    # Common expressions
    ("aujourd'hui", 78000), ("c'est", 150000), ("il", 180000), ("y", 125000),
    ("s'il", 65000), ("n'est", 70000), ("d'un", 72000), ("d'une", 70000),
    ("qu'il", 68000), ("qu'elle", 65000), ("j'ai", 80000), ("n'ai", 45000),
    ("qu'est-ce", 55000), ("est-ce", 60000), ("n'y", 42000),
    
    # Professional/modern words
    ("travail", 52000), ("bureau", 48000), ("entreprise", 45000), ("projet", 47000),
    ("équipe", 43000), ("client", 44000), ("service", 46000), ("produit", 42000),
    ("système", 41000), ("programme", 40000), ("ordinateur", 39000), ("internet", 38000),
    ("site", 37000), ("page", 36000), ("document", 38000), ("fichier", 35000),
    ("données", 36000), ("information", 40000), ("communication", 37000),
    ("problème", 48000), ("solution", 44000), ("résultat", 41000), ("objectif", 39000),
]

def generate_french_dictionary():
    """Generate French frequency dictionary file."""
    output_file = "dictionaries/frequency_dictionary_fr_25000.txt"
    
    print(f"Generating French dictionary: {output_file}")
    print(f"Total words: {len(FRENCH_WORDS)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for word, frequency in sorted(FRENCH_WORDS, key=lambda x: x[1], reverse=True):
            f.write(f"{word} {frequency}\n")
    
    print(f"✓ French dictionary created with {len(FRENCH_WORDS)} words")
    print(f"  File: {output_file}")

if __name__ == "__main__":
    generate_french_dictionary()
