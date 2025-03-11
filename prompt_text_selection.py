# -*- coding: utf-8 -*-

import json5
import pandas as pd
import json
import re

def load_config(config_file):
    with open(config_file, 'r') as f:
        config = json5.load(f)
    return config

def get_filter_condition(df, key, value, is_prompts=True):
    if is_prompts:
        if key == "prompts_type":
            return df['type'] == value
        elif key == "prompt_word_length_min":
            return df['word_length'] >= value
        elif key == "prompt_word_length_max":
            return df['word_length'] <= value
        elif key == "prompt_char_length_min":
            return df['char_length'] >= value
        elif key == "prompt_char_length_max":
            return df['char_length'] <= value
    else:
        if key == "oxford_category":
            return df['oxford_category'] == value
        elif key == "char_length_min":
            return df['char_length'] >= value
        elif key == "char_length_max":
            return df['char_length'] <= value
        elif key == "word_length_min":
            return df['word_length'] >= value
        elif key == "word_length_max":
            return df['word_length'] <= value
        elif key == "contains_rare":
            return df['rare'] == value
        elif key == "contains_gibberish":
            return df['gibberish'] == value
        elif key == "contains_spec_char":
            return df['spec_char'] == value
        elif key == "contains_number":
            return df['number'] == value
        elif key == "contains_sentences":
            return df['sentence'] == value
        elif key == "LAION_freq_min":
            return df['LAION_freq'] >= value
        elif key == "LAION_freq_max":
            return df['LAION_freq'] <= value
        elif key == "CoCo_freq_min":
            return df['CoCo_freq'] >= value
        elif key == "CoCo_freq_max":
            return df['CoCo_freq'] <= value
    return None

def combine_conditions(df, conditions, is_prompts=True):
    combined = None
    for key, condition in conditions.items():
        op = condition.get("operator", "and")
        value = condition.get("value")
        if value is None:
            continue

        filter_cond = get_filter_condition(df, key, value, is_prompts)
        if filter_cond is None:
            continue

        if combined is None:
            combined = filter_cond
        else:
            if op.lower() == "or":
                combined = combined | filter_cond
            else:
                combined = combined & filter_cond

    if combined is None:
        combined = pd.Series([True] * len(df), index=df.index)
    return combined

def filter_dataframes(config_file, prompts_csv, texts_csv):
    config = load_config(config_file)

    prompts_df = pd.read_csv(prompts_csv)
    texts_df = pd.read_csv(texts_csv)

    prompts_conditions = config.get("prompts", {})
    texts_conditions = config.get("texts", {})

    prompts_filter = combine_conditions(prompts_df, prompts_conditions, is_prompts=True)
    texts_filter = combine_conditions(texts_df, texts_conditions, is_prompts=False)

    filtered_prompts = prompts_df[prompts_filter]
    filtered_texts = texts_df[texts_filter]

    return filtered_prompts, filtered_texts

def generate_combined_json(filtered_prompts, filtered_texts, output_file):

    final_dict = {}
    for _, prompt_row in filtered_prompts.iterrows():
        prompt_template = prompt_row["prompts"]
        for _, text_row in filtered_texts.iterrows():
            substitution_word = text_row["words"]
            final_prompt = re.sub(r'".*?"', f'"{substitution_word}"', prompt_template, count=1)

            combined_data = text_row.to_dict()

            for col in prompt_row.index:
                if col != "prompts":
                    combined_data[f"prompt_{col}"] = prompt_row[col]

            final_dict[final_prompt] = combined_data

    with open(output_file, "w") as f:
        json.dump(final_dict, f, indent=4)

    print("Number of entries in final JSON:", len(final_dict))

if __name__ == "__main__":
    config_file = "./config.json"
    prompts_csv = "./all_prompts.csv"
    texts_csv = "./all_texts.csv"
    output_file = "./selected_prompts.json"

    filtered_prompts, filtered_texts = filter_dataframes(config_file, prompts_csv, texts_csv)
    generate_combined_json(filtered_prompts, filtered_texts, output_file)
    print(f"\nCombined JSON saved to {output_file}")