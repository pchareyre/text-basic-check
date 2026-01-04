"""
Generate French test corpus for benchmarking spell checker performance.

This script generates:
1. corpus_ortho_syntax_ground_truth_fr.txt - 500 correct French sentences
2. corpus_ortho_errors_only_fr.txt - sentences with orthographic errors only
3. corpus_ortho_syntax_errors_both_fr.txt - sentences with both orthographic and syntax errors
"""

import random
from typing import List, Tuple


# Base vocabulary for generating French sentences
SUBJECTS = [
    "Le chat", "Un chien", "L'étudiant", "Mon ami", "Le professeur",
    "Un scientifique", "L'ingénieur", "Un médecin", "Le programmeur", "Un écrivain",
    "L'artiste", "Un musicien", "L'athlète", "Un chercheur", "Le directeur",
    "Un chef", "Le pilote", "Une infirmière", "L'architecte", "Un avocat",
    "Le professeur", "Un journaliste", "Le photographe", "Un designer", "Le comptable"
]

VERBS = [
    "court", "marche", "étudie", "lit", "écrit",
    "joue", "enseigne", "apprend", "crée", "construit",
    "analyse", "développe", "gère", "organise", "conçoit",
    "cuisine", "conduit", "explore", "découvre", "invente",
    "publie", "présente", "investigue", "implémente", "optimise"
]

OBJECTS = [
    "le livre", "un projet", "le rapport", "une solution", "le problème",
    "un programme", "le système", "un modèle", "la base", "un site",
    "l'application", "un framework", "l'algorithme", "un document", "la présentation",
    "une recette", "le véhicule", "une carte", "l'expérience", "une théorie",
    "l'article", "une photographie", "le design", "un plan", "le budget"
]

ADVERBS = [
    "rapidement", "soigneusement", "efficacement", "complètement", "successivement",
    "diligemment", "précisément", "professionnellement", "créativement", "systématiquement",
    "constamment", "effectivement", "rapidement", "méticuleusement", "habilement",
    "gracieusement", "confidemment", "patiemment", "enthusiastement", "stratégiquement"
]

PREPOSITIONS = [
    "le matin", "le soir", "pendant la journée", "le lundi",
    "au bureau", "à la maison", "à la bibliothèque", "à l'école",
    "avec dévouement", "par la pratique", "en étudiant", "avec patience",
    "pour l'amélioration", "sans hésitation", "avec précision", "en planifiant",
    "en détail", "avec soin", "par l'analyse", "en testant"
]

# Common French orthographic errors (letter substitutions, omissions, insertions)
ORTHO_ERROR_PATTERNS = {
    'a': ['e', 'o'],
    'e': ['a', 'é', 'è'],
    'é': ['e', 'è'],
    'è': ['e', 'é'],
    'i': ['e', 'y'],
    'o': ['a', 'u'],
    'u': ['o', 'i'],
    'c': ['k', 's', 'ç'],
    'ç': ['c', 's'],
    'k': ['c', 'qu'],
    's': ['c', 'z', 'ss'],
    'z': ['s'],
    'f': ['ph', 'v'],
    'v': ['f', 'w'],
    'b': ['p'],
    'p': ['b'],
    'd': ['t'],
    't': ['d'],
    'g': ['j', 'gu'],
    'j': ['g'],
    'n': ['m'],
    'm': ['n', 'mm'],
}


def generate_sentence() -> str:
    """Generate a grammatically correct French sentence."""
    subject = random.choice(SUBJECTS)
    verb = random.choice(VERBS)
    obj = random.choice(OBJECTS)
    
    # 60% chance to add an adverb
    if random.random() < 0.6:
        adverb = random.choice(ADVERBS)
        # 50% chance to place adverb before or after verb
        if random.random() < 0.5:
            verb_phrase = f"{adverb} {verb}"
        else:
            verb_phrase = f"{verb} {adverb}"
    else:
        verb_phrase = verb
    
    # 50% chance to add a prepositional phrase
    if random.random() < 0.5:
        prep_phrase = random.choice(PREPOSITIONS)
        sentence = f"{subject} {verb_phrase} {obj} {prep_phrase}."
    else:
        sentence = f"{subject} {verb_phrase} {obj}."
    
    return sentence


def introduce_ortho_error(word: str) -> str:
    """Introduce a random orthographic error in a French word."""
    if len(word) < 3:
        return word
    
    error_type = random.choice(['substitute', 'omit', 'duplicate', 'transpose'])
    
    if error_type == 'substitute':
        # Replace a character with a similar one
        pos = random.randint(0, len(word) - 1)
        char = word[pos].lower()
        if char in ORTHO_ERROR_PATTERNS:
            replacement = random.choice(ORTHO_ERROR_PATTERNS[char])
            # Preserve case
            if word[pos].isupper():
                replacement = replacement.upper() if len(replacement) == 1 else replacement.capitalize()
            word = word[:pos] + replacement + word[pos+1:]
    
    elif error_type == 'omit':
        # Remove a character (not first or last)
        if len(word) > 3:
            pos = random.randint(1, len(word) - 2)
            word = word[:pos] + word[pos+1:]
    
    elif error_type == 'duplicate':
        # Duplicate a character
        pos = random.randint(0, len(word) - 1)
        word = word[:pos] + word[pos] + word[pos:]
    
    elif error_type == 'transpose':
        # Swap two adjacent characters
        if len(word) > 2:
            pos = random.randint(0, len(word) - 2)
            word = word[:pos] + word[pos+1] + word[pos] + word[pos+2:]
    
    return word


def introduce_syntax_error(sentence: str) -> str:
    """Introduce a syntax error in a French sentence."""
    words = sentence.split()
    
    error_type = random.choice(['missing_article', 'wrong_verb_form', 'extra_word'])
    
    if error_type == 'missing_article' and len(words) > 2:
        # Remove an article (le, la, les, un, une, des, l')
        for i, word in enumerate(words):
            if word.lower() in ['le', 'la', 'les', 'un', 'une', 'des', "l'"]:
                words.pop(i)
                break
    
    elif error_type == 'wrong_verb_form' and len(words) > 2:
        # Change verb form (e.g., "court" -> "cour" or add extra 's')
        for i, word in enumerate(words):
            if word.endswith('t') and len(word) > 2:
                words[i] = word[:-1]
                break
            elif not word.endswith('s') and len(word) > 2:
                words[i] = word + 's'
                break
    
    elif error_type == 'extra_word':
        # Duplicate a word
        pos = random.randint(1, len(words) - 2)
        words.insert(pos, words[pos])
    
    return ' '.join(words)


def add_ortho_errors_to_sentence(sentence: str, error_rate: float = 0.3) -> str:
    """Add orthographic errors to a French sentence."""
    words = sentence.split()
    result = []
    
    for word in words:
        # Don't modify punctuation-only tokens
        if word.strip('.,!?;:') == '':
            result.append(word)
            continue
        
        # Extract punctuation
        punct = ''
        if word and word[-1] in '.,!?;:':
            punct = word[-1]
            word = word[:-1]
        
        # Introduce error with given probability
        if random.random() < error_rate and len(word) > 2:
            word = introduce_ortho_error(word)
        
        result.append(word + punct)
    
    return ' '.join(result)


def generate_corpus(num_sentences: int = 500) -> Tuple[List[str], List[str], List[str]]:
    """
    Generate three corpus files:
    1. Ground truth (correct sentences)
    2. Orthographic errors only
    3. Both orthographic and syntax errors
    """
    ground_truth = []
    ortho_only = []
    ortho_syntax_both = []
    
    random.seed(42)  # For reproducibility
    
    for _ in range(num_sentences):
        # Generate correct sentence
        correct = generate_sentence()
        ground_truth.append(correct)
        
        # Generate sentence with orthographic errors
        with_ortho = add_ortho_errors_to_sentence(correct, error_rate=0.25)
        ortho_only.append(with_ortho)
        
        # Generate sentence with both types of errors
        with_syntax = introduce_syntax_error(correct)
        with_both = add_ortho_errors_to_sentence(with_syntax, error_rate=0.25)
        ortho_syntax_both.append(with_both)
    
    return ground_truth, ortho_only, ortho_syntax_both


def main():
    """Generate and save French corpus files."""
    import os
    
    print("Generating French corpus with 500 sentences...")
    
    # Ensure corpus directory exists
    corpus_dir = os.path.join(os.path.dirname(__file__), 'corpus')
    os.makedirs(corpus_dir, exist_ok=True)
    
    ground_truth, ortho_only, ortho_syntax_both = generate_corpus(500)
    
    # Save ground truth
    filepath = os.path.join(corpus_dir, 'corpus_ortho_syntax_ground_truth_fr.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        for sentence in ground_truth:
            f.write(sentence + '\n')
    print(f"✓ Saved {filepath} ({len(ground_truth)} sentences)")
    
    # Save orthographic errors only
    filepath = os.path.join(corpus_dir, 'corpus_ortho_errors_only_fr.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        for sentence in ortho_only:
            f.write(sentence + '\n')
    print(f"✓ Saved {filepath} ({len(ortho_only)} sentences)")
    
    # Save both types of errors
    filepath = os.path.join(corpus_dir, 'corpus_ortho_syntax_errors_both_fr.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        for sentence in ortho_syntax_both:
            f.write(sentence + '\n')
    print(f"✓ Saved {filepath} ({len(ortho_syntax_both)} sentences)")
    
    print("\nFrench corpus generation complete!")
    print("\nExample sentences:")
    print(f"\nGround truth: {ground_truth[0]}")
    print(f"Ortho only:   {ortho_only[0]}")
    print(f"Both errors:  {ortho_syntax_both[0]}")


if __name__ == "__main__":
    main()
