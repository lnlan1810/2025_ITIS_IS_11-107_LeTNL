import math
import os
from collections import defaultdict
import pandas as pd

PRECISION = 6  

def compute_tf(text: list[str]) -> dict[str, float]:
    """
    Вычисляет TF (Term Frequency) - частоту термина в документе.
    TF = (Количество вхождений слова в документ) / (Общее количество слов в документе)
    """
    tf: defaultdict[str, int] = defaultdict(int)
    for word in text:
        tf[word] += 1
    total_words = sum(tf.values())
    return {word: round(count / total_words, PRECISION) for word, count in tf.items()}

def compute_idf(corpus: dict[str, list[str]]) -> dict[str, float]:
    """
    Вычисляет IDF (Inverse Document Frequency) - обратную частоту документа.
    IDF = log10(Общее количество документов / Количество документов, содержащих слово)
    """
    idf: defaultdict[str, int] = defaultdict(int)
    total_docs = len(corpus)
    for text in corpus.values():
        for word in set(text):  
            idf[word] += 1
    return {word: round(math.log10(total_docs / count), PRECISION) for word, count in idf.items()}


def compute_tf_idf(tf: dict[str, dict[str, float]], idf: dict[str, float]) -> dict[str, dict[str, float]]:
    """
    TF-IDF (комбини́рованную ме́трику ва́жности слов) для всех докуме́нтов.
    Вычисляет TF-IDF = TF * IDF для каждого слова в каждом документе
    """
    tf_idf: dict[str, dict[str, float]] = {}
    for file_name, tf_vals in tf.items():
        tf_idf[file_name] = {
            word: round(tf_val * idf.get(word, 0), PRECISION)
            for word, tf_val in tf_vals.items()
        }
    return tf_idf

def save_to_csv(data: pd.DataFrame, filename: str):
    """Сохраняет DataFrame в CSV файл с кодировкой UTF-8"""
    os.makedirs('4', exist_ok=True)
    data.to_csv(f'4/{filename}', encoding='utf-8')

if __name__ == '__main__':
    input_dir_path = '/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/2/tokens/' 

    corpus: dict[str, list[str]] = {}


    for input_file_name in sorted(os.listdir(input_dir_path)):
        if not input_file_name.endswith('.txt'): 
            continue
            
        input_file_path = os.path.join(input_dir_path, input_file_name)
        try:
            with open(input_file_path, encoding='utf-8') as file:
                text = file.read().split()
                if len(text) >= 1000:  
                    corpus[input_file_name] = text
        except Exception as e:
            print(f"LОшибка при чтении файла {input_file_name}: {str(e)}")

    if not corpus:
        print("Не найдено подходящих документов для обработки")
        exit()


    tf = {file_name: compute_tf(text) for file_name, text in corpus.items()}
    idf = compute_idf(corpus)
    tf_idf = compute_tf_idf(tf, idf)


    tf_df = pd.DataFrame(tf).fillna(0).round(PRECISION)
    save_to_csv(tf_df, 'tf.csv')

    idf_df = pd.DataFrame(idf.items(), columns=['Word', 'IDF']).set_index('Word')
    save_to_csv(idf_df, 'idf.csv')

    tf_idf_records: list[dict[str, str | float]] = []
    for file_name, word_vals in tf_idf.items():
        for word, value in word_vals.items():
            tf_idf_records.append({
                'Document': file_name,
                'Word': word,
                'TF-IDF': value
            })

    tf_idf_df = pd.DataFrame(tf_idf_records)
    tf_idf_pivot = tf_idf_df.pivot(index='Word', columns='Document', values='TF-IDF').fillna(0).round(PRECISION)
    save_to_csv(tf_idf_pivot, 'tf_idf.csv')

    print("Результаты успешно вычислены и сохранены в папку '4'")
