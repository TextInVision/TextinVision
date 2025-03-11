import pandas as pd
from collections import Counter


def find_longest_ordered_match(s1, s2):
    s1, s2 = s1.lower(), s2.lower()
    max_sub = ""
    s1_length, s2_length = len(s1), len(s2)
    for i in range(s1_length):
        for j in range(s2_length):
            l = 0
            while (i + l < s1_length and 
                   j + l < s2_length and 
                   s1[i + l] == s2[j + l]):
                l += 1
                if l > len(max_sub):
                    max_sub = s2[j:j + l]
    return max_sub

def find_lcs(s1, s2):
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    dp = [[""] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if s1[i] == s2[j]:
                dp[i + 1][j + 1] = dp[i][j] + s1[i]
            else:
                dp[i + 1][j + 1] = (dp[i + 1][j] 
                                     if len(dp[i + 1][j]) > len(dp[i][j + 1]) 
                                     else dp[i][j + 1])
    return dp[m][n]

def remove_common_words_once(s1, s2):

    s1 = s1.split()
    s2 = s2.split()
    
    counter1 = Counter(s1)
    counter2 = Counter(s2)
    
    common_words = counter1 & counter2
    
    for word in common_words:
        if counter1[word] > 0 and counter2[word] > 0:
            counter1[word] -= 1
            counter2[word] -= 1
    
    s1_new = []
    for word in s1:
        if counter1[word] > 0:
            s1_new.append(word)
            counter1[word] -= 1
    
    s2_new = []
    for word in s2:
        if counter2[word] > 0:
            s2_new.append(word)
            counter2[word] -= 1
    
    s1_new = ' '.join(s1_new)
    s2_new = ' '.join(s2_new)
    
    return s1_new, s2_new

def find_smart_levenshtein_distance(s1, s2):
    s1, s2 = s1.lower(), s2.lower()
    
    s1_new, s2_new = remove_common_words_once(s1, s2)
    
    if not s1_new and not s2_new:
        return 0 

    s1_new_no_space = s1_new.replace(' ', '')
    s2_new_no_space = s2_new.replace(' ', '')
    
    if len(s1_new_no_space) < len(s2_new_no_space):
        s1_new_no_space, s2_new_no_space = s2_new_no_space, s1_new_no_space
    previous_row = list(range(len(s2_new_no_space) + 1))
    for i, c1 in enumerate(s1_new_no_space):
        current_row = [i + 1]
        for j, c2 in enumerate(s2_new_no_space):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def algorithm1(ocr_text, exp_text):
    """
    Edit distance based score

    Algorithm:
      1. If exp_text is a substring of ocr_text, return 0.
      2. If exp_text is a single word:
           - Split ocr_text into words.
           - For each word, compute the LCS with exp_text.
           - Select the word with the longest LCS as the best match.
           - Return the smart edit distance between the best match and exp_text.
      3. Else (exp_text contains multiple words):
           - Compute the smart edit distance between ocr_text and exp_text.
    """
    if exp_text in ocr_text:
        return 0

    exp_words = exp_text.split()
    if len(exp_words) == 1:
        ocr_words = ocr_text.split()
        max_lcs_len = 0
        best_match = ""
        for w in ocr_words:
            lcs_str = find_lcs(w, exp_text)
            if len(lcs_str) > max_lcs_len:
                max_lcs_len = len(lcs_str)
                best_match = w
        return find_smart_levenshtein_distance(best_match, exp_text)

    return find_smart_levenshtein_distance(ocr_text, exp_text)

def process_csv(expected_csv, ocr_csv, output_csv):
    """
    Reads two input CSV files (expected text and OCR output), computes scores for each row,
    and writes the results to an output CSV file.

    Parameters:
        expected_csv (str): Path to CSV file containing expected texts.
        ocr_csv (str): Path to CSV file containing OCR outputs.
        output_csv (str): Path where the output CSV with scores will be saved.
    """

    df_expected = pd.read_csv(expected_csv)
    df_ocr = pd.read_csv(ocr_csv)

    if len(df_expected) != len(df_ocr):
        raise ValueError("Input CSV files have different number of rows")
    
    results = []
    
    for i in range(len(df_expected)):

            # Assumes the text is stored in the "content" column.

        expected_text = str(df_expected.loc[i, "content"])
        ocr_text = str(df_ocr.loc[i, "content"])
        
        longest_match_str = find_longest_ordered_match(expected_text, ocr_text)
        score_longest = len(longest_match_str)
        
        lcs_str = find_lcs(expected_text, ocr_text)
        score_lcs = len(lcs_str)
        
        score_lev = find_smart_levenshtein_distance(expected_text, ocr_text)
        
        score_additional = algorithm1(expected_text, ocr_text)
        
        results.append({
            'expected_text': expected_text,
            'ocr_text': ocr_text,
            'score_longest_match': score_longest,
            'score_lcs': score_lcs,
            'score_levenshtein': score_lev,
            'score_algorithm1': score_additional
        })
    
    df_results = pd.DataFrame(results)
    df_results.to_csv(output_csv, index=False)


if __name__ == "__main__":

    excepted_text = 'excepted_text.csv'
    ocr_output = 'ocr_output.csv'
    score = './score.csv'

    process_csv(excepted_text, ocr_output, score)
