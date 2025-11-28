#!/usr/bin/env python
# coding: utf-8

import os
import sys
from os.path import join
import pandas as pd
from urllib.parse import urlparse

project_dir = join('/work', 'dlvr_just-renewability_F24')
modules_dir = join(project_dir, 'modules')
sys.path.append(modules_dir)

from just_renew_funs import *

# PATHS AND DIRS
data_dir = join(project_dir, 'data')
output_dir = join(project_dir, 'output')

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

## In paths raw
arg_data_p = join(data_dir, 'articles_arg_raw.json')
da_data_p = join(data_dir, 'articles_da_raw.json')
sp_data_p = join(data_dir, 'articles_sp_raw.json')

## In paths filtered
arg_data_filt_p = "/work/dlvr_just-renewability_F24/output/articles_arg_meta_2024-08-02.xlsx"
da_data_filt_p = "/work/dlvr_just-renewability_F24/output/articles_da_meta_2025-11-28.xlsx"
sp_data_filt_p = "/work/dlvr_just-renewability_F24/output/articles_sp_meta_2024-08-02.xlsx"


# Raw counts
def urlparser(url):
    main_url = urlparse(url).netloc
    if main_url.endswith('.ar'):
        keep_url = '.'.join(main_url.split('.')[-3:])
    else:
        keep_url = '.'.join(main_url.split('.')[-2:])
    return(keep_url)

raw_counts_df = pd.DataFrame()

for filepath in [arg_data_p, da_data_p, sp_data_p]:
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    articles_df = pd.DataFrame.from_records(data.get('articles'))
    articles_df['newssite'] = articles_df['link'].apply(lambda x: urlparser(x))
    
    ctr = articles_df['country'].value_counts().index[0] # assuming top count to be country
    articles_df['country'] = ctr
    
    ctr_counts_df = articles_df.groupby(['newssite', 'country']).size().reset_index().rename(columns = {0: 'articles raw'})
    raw_counts_df = pd.concat([raw_counts_df, ctr_counts_df])


# filtered counts
filtered_counts_df = pd.DataFrame()

for filepath in [arg_data_filt_p, da_data_filt_p, sp_data_filt_p]:
    df = pd.read_excel(filepath)
    
    df['newssite'] = df['article_link'].apply(lambda x: urlparser(x))
    df['country'] = df['ctr']

    ctr_counts_df = df.groupby(['newssite', 'country']).size().reset_index().rename(columns = {0: 'articles kw_filtered'})
    filtered_counts_df = pd.concat([filtered_counts_df, ctr_counts_df])


# Join
overview_df = pd.merge(raw_counts_df, filtered_counts_df, how='left', on=['newssite', 'country'])

# Export
file_out = join(output_dir, 'articles_overview_2025-11-28.xlsx')
overview_df.to_excel(file_out, index=False)