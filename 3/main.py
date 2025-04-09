import re

inverted_index = {}

def intersection(list1, list2):
    return [value for value in list1 if value in set(list2)]

def disintersection(list_to_exclude):
    full_list = list(range(1, 101))  
    return [value for value in full_list if value not in set(list_to_exclude)]

for i in range(1, 101):
    file_path = f'/Users/laptoptt/Documents/2025_ITIS_IS_11-107_LeTNL/2/tokens/doc_{i}.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        words = re.split(r'[\s\n]', file.read())
        words = [word for word in words if word.strip()]  
        
        for word in set(words):  
            if word in inverted_index:
                inverted_index[word].append(i)
            else:
                inverted_index[word] = [i]

with open('3/dictionary.txt', 'w', encoding='utf-8') as f:
    for word in sorted(inverted_index.keys()):
        doc_ids = ', '.join(str(doc_id) for doc_id in sorted(inverted_index[word]))
        f.write(f"{word}: {doc_ids}\n")

def evaluate_boolean_query(query: str):
    tokens = query.split()

    for i, token in enumerate(tokens):
        if token not in ['&', '|', '!']:
            tokens[i] = inverted_index.get(token, [])

    while '!' in tokens:
        idx = tokens.index('!')
        term_docs = tokens[idx + 1]
        tokens[idx + 1] = disintersection(term_docs)
        tokens.pop(idx)

    while '&' in tokens:
        idx = tokens.index('&')
        left = tokens[idx - 1]
        right = tokens[idx + 1]
        tokens[idx + 1] = intersection(left, right)
        tokens.pop(idx)      
        tokens.pop(idx - 1)  

    while '|' in tokens:
        idx = tokens.index('|')
        left = tokens[idx - 1]
        right = tokens[idx + 1]
        tokens[idx + 1] = list(set(left + right))
        tokens.pop(idx)
        tokens.pop(idx - 1)

    return sorted(tokens[0]) if tokens else []

# 🧪 Test các biểu thức mẫu
if __name__ == '__main__':
    queries = [
        'свободный & модель | материал',
        'глава | центр | материал',
        'кухня & центр & материал',
        'кухня & ! центр | ! глава',
        'глава | ! центр | ! модель'
    ]

    with open('3/results.txt', 'w', encoding='utf-8') as result_file:
        for query in queries:
            result = evaluate_boolean_query(query)
            output_text = f"Query: {query}\n→ Matching documents: {result}\n\n"
            print(output_text, end='')            
            result_file.write(output_text)        
