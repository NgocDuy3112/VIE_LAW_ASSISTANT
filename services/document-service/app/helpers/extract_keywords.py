from pyvi import ViTokenizer, ViPosTagger



def extract_legal_keywords(text: str) -> list[str]:
    # Tokenize and POS-tag
    words = ViPosTagger.postagging(ViTokenizer.tokenize(text))
    tokens, pos_tags = words[0], words[1]

    # Keep only relevant POS (nouns, verbs, adjectives, proper nouns)
    desired_tags = ["N", "Np", "V", "A"]  # You can add 'M' for classifiers if needed
    keywords = [token.replace('_', ' ') for token, pos in zip(tokens, pos_tags) if pos in desired_tags]

    return keywords