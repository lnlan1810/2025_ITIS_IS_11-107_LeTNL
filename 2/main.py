import os
import re
from multiprocessing import Pool
from pathlib import Path
from pymystem3 import Mystem

def load_stop_words(file_path: str) -> set[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

STOP_WORDS = load_stop_words('/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/2/stop_words.txt')
def is_valid_word(lemma: str) -> bool:
    return re.match(r'^[а-яА-ЯёЁa-zA-Z]+-?[а-яА-ЯёЁa-zA-Z]*$', lemma) is not None

def simple_tokenize(text: str) -> list[str]:
    return re.findall(r'[а-яА-ЯёЁa-zA-Z]+(?:-[а-яА-ЯёЁa-zA-Z]+)?', text.lower())

def process_file(directory: str, file_name: str) -> [str, list[str]]:
    file_path = os.path.join(directory, file_name)
    file_lemmas = []
    mystem = Mystem()

    print(f'Processing file: {file_path}')
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        tokens = simple_tokenize(text)  
        for word in tokens:
            lemma: str = mystem.lemmatize(word)[0]
            if lemma not in STOP_WORDS and is_valid_word(lemma):
                file_lemmas.append(lemma)

    return file_name, file_lemmas

def main(source_dir: str, output_dir: str):
    source_files = os.listdir(source_dir)
    Path(output_dir).mkdir(exist_ok=True)

    with Pool() as pool:
        file_lemmas_pairs = pool.starmap(
            process_file,
            [(source_dir, file_name) for file_name in source_files]
        )

    for file_name, lemmas in file_lemmas_pairs:
        output_file_path = os.path.join(output_dir, file_name)
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            for lemma in lemmas:
                output_file.write(f"{lemma}\n")
        print(f'Saved file {output_file_path}')

if __name__ == "__main__":
    main('/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/1/pages',
         '/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/2/tokens')
