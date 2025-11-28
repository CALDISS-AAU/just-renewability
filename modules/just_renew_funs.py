#!/usr/bin/env python
# coding: utf-8

import os
from os.path import join
import json
import pandas as pd
import re

# PATHS AND DIRS
project_dir = join('/work', 'dlvr_just-renewability_F24')
data_dir = join(project_dir, 'data')

## Keyword extraction

keywords = {
    'eng': [
        'green hydrogen',
        'solar',
        'wind',
        'power to x',
        '(pink hydrogen OR nuclear)',
        '(reindustrialisation OR industrialisation) ',
        'growth',
        'participation',
        'citizen',
        'environmental impact',
        'water',
        'public hearings',
        'future',
        'conflict',
        'resistance',
        'support',
        '(finance OR investment)',
        'renewable'
        ],
    'sp': [
        'hidrógeno verde',
        'solar', 
        'eólica', 
        'power to x', 
        '(hidrógeno rosa OR nuclear)', 
        '(reindustrialización OR industrialización)', 
        'crecimiento', 
        'participación', 
        'ciudadano', 
        'impacto medioambiental',
        'agua', 
        'audiencias públicas', 
        'futuro', 
        'conflicto', 
        'resistencia', 
        'apoyo', 
        '(finanzas OR inversiones)', 
        #'renovable',
        'energía renovable'
        ],
    'da': [
        'grøn brint',
        'solcelle',
        'vind',
        'power to x',
        'power-to-x', 
        'ptx',
        '(pink brint OR atomkraft)',
        '(reindustralisering OR industralisering)',
        'vækst',
        '(deltagelse OR inddragelse)',
        'borger',
        'miljøvurdering',
        'vand',
        'offentlig høring',
        'fremtid',
        'konflikt',
        'modstand',
        'opbakning',
        '(finansiering OR investering)',
        #'vedvarende',
        'vedvarende energi'
        ]
}

## Keyword finder
def keyword_finder(text, lang, keywords = keywords, excluded_keywords = None):

    keywords_use = keywords.get(lang).copy()

    if excluded_keywords:
        for keyword_exclude in excluded_keywords:
            keywords_use.remove(keyword_exclude)

    matched_keywords = []
    
    ## iterate over keywords

    for keyword in keywords_use: 
        if 'OR' in keyword: # keywords with OR converted to proper regex syntax
            keyword_regex = keyword.replace(' OR ', '|')
        else:
            keyword_regex = keyword

        ### compile word pattern
        keyword_pattern = re.compile(fr'\b{keyword_regex}', re.IGNORECASE)
        
        ### check for pattern
        if bool(keyword_pattern.search(text)):
            matched_keywords.append(keyword)
    
    return(matched_keywords)


## Parse article metadata
def parse_article_meta(article, ctr, excluded_keywords = None):

    title = article.get('title', '')
    if title is None:
        title = ''
    
    summary = article.get('summary', '')
    if summary is None:
        summary = ''

    text = title + '\n' + summary

    if ctr == 'DK':
        lang = 'da'
    elif ctr == 'ES':
        lang = 'sp'
    elif ctr == 'AR':
        lang = 'sp'
    else:
        raise ValueError(f"Countrycode {ctr} not valid. Acceptable inputs are DK, ES or ARG.")

    if text:
        keywords = keyword_finder(text, lang, excluded_keywords = excluded_keywords)
    else:
        keywords = []
    
    if keywords:
        n_keywords = len(keywords)
    else:
        n_keywords = 0

    article_parsed = {
        'title': article.get('title'),
        'date': article.get('published_date'),
        'article_link': article.get('link'),
        'source': article.get('clean_url'),
        'ctr': ctr,
        'newscatcher_id': article.get('_id'),
        'keywords': keywords,
        'keyword count': n_keywords
    }

    return(article_parsed)

## Articles to data frame
def articles_to_df(articles_p, ctr, excluded_keywords = None):

    ## Read
    with open(articles_p, 'r') as f:
        data = json.load(f)

    ## Get articles
    articles = data.get('articles')

    ## List for parsed articles
    articles_meta = []

    ## Parse articles
    for c, article in enumerate(articles, start = 1):
        
        parsed_article = parse_article_meta(article, ctr, excluded_keywords = excluded_keywords)
        parsed_article['id'] = c # add id

        ## add to list
        articles_meta.append(parsed_article)

    ## Convert to df
    meta_df = pd.DataFrame.from_records(articles_meta)

    ## Filter articles with no keywords
    meta_df = meta_df.loc[meta_df['keyword count'] > 0, :]

    ## Explode
    meta_df = meta_df.explode('keywords')

    ## Keywords to dummies
    meta_df = pd.get_dummies(meta_df, columns = ['keywords'], prefix = 'keyword')
    meta_df = meta_df.groupby('id').max().reset_index()

    return(meta_df)
