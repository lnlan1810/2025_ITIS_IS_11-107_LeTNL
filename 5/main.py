import math
import os
from collections import Counter
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from four.main import compute_tf, compute_idf, compute_tf_idf
from pymystem3 import Mystem
from sklearn.metrics.pairwise import cosine_similarity 

mystem = Mystem() 


def query_to_vector(query: str, idf: dict[str, float], total_docs_count: int):
    
    words = mystem.lemmatize(query.lower()) 
    words = [word for word in words if word.strip() and word not in [' ', '\n']] 
    query_length = len(words) 
    words_counter = Counter(words) 
    query_vector: dict[str, float] = {} 

    for word, count in words_counter.items():
        tf = count / query_length 
        word_idf = idf.get(word, math.log10(total_docs_count)) 
        query_vector[word] = tf * word_idf

    return query_vector


def compute_cosine_similarity(doc_vector: dict[str, float], query_vector:  dict[str, float]) -> float:

    all_words = list(set(doc_vector.keys()).union(set(query_vector.keys())))
    doc_vector = [doc_vector.get(word, 0) for word in all_words]
    query_vector = [query_vector.get(word, 0) for word in all_words]
    return cosine_similarity([doc_vector], [query_vector])[0][0]

def vector_search_multi(queries: [str], tf_idf: dict[str, dict[str, float]], idf: dict[str, float],
                      total_docs_count: int, output_csv_file: str):
    sorted_results = {}
    
    for query in queries:
        query_vector = query_to_vector(query, idf, total_docs_count)
        scores = {}
        
        for doc, doc_vector in tf_idf.items():
            score = compute_cosine_similarity(doc_vector, query_vector)
            if score > 0:
                scores[doc] = score
        
        sorted_results[query] = [
            f"{doc} {score:.6f}" 
            for doc, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ]
    
    max_len = max(len(results) for results in sorted_results.values())
    
    data = {}
    for query in queries:
        data[query] = sorted_results[query] + [""] * (max_len - len(sorted_results[query]))
    
    pd.DataFrame(data).to_csv(output_csv_file, index=False)
    print(f"Результаты поиска сохранены в {output_csv_file}")


if __name__ == '__main__':
    path = '/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/2/tokens/'
    corpus = {}
    for file in os.listdir(path):
        with open(os.path.join(path, file), 'r') as f:
            corpus[file] = f.read().split()

    tf = {doc: compute_tf(text) for doc, text in corpus.items()}
    idf = compute_idf(corpus)
    tf_idf = compute_tf_idf(tf, idf)

    queries = ['элемент', 'элемент битный', 'элемент битный алгоритм']
    output_csv = '5/vector_search.csv'
    vector_search_multi(queries, tf_idf, idf, len(corpus), output_csv)
    
