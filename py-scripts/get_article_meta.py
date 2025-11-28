#!/usr/bin/env python
# coding: utf-8

import sys
import os
from os.path import join
import json
import pandas as pd
import re

project_dir = join('/work', 'dlvr_just-renewability_F24')
modules_dir = join(project_dir, 'modules')
sys.path.append(modules_dir)

from just_renew_funs import *

# PATHS AND DIRS
data_dir = join(project_dir, 'data')
output_dir = join(project_dir, 'output')

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

## In paths
arg_data_p = join(data_dir, 'articles_arg_raw.json')
da_data_p = join(data_dir, 'articles_da_raw.json')
sp_data_p = join(data_dir, 'articles_sp_raw.json')

## Out paths
#arg_data_out = join(output_dir, 'articles_arg_meta_2024-08-02.xlsx')
da_data_out = join(output_dir, 'articles_da_meta_2025-11-28.xlsx')
#sp_data_out = join(output_dir, 'articles_sp_meta_2024-08-02.xlsx')

#arg_kw_out = join(output_dir, 'keyword-count_arg_2024-08-02.xlsx')
da_kw_out = join(output_dir, 'keyword-count_da_2025-11-28.xlsx')
#sp_kw_out = join(output_dir, 'keyword-count_sp_2024-08-02.xlsx')

# CONVERT TO DFs
#articles_arg_df = articles_to_df(arg_data_p, 'AR', excluded_keywords=['(finanzas OR inversiones)', 'resistencia'])
articles_da_df = articles_to_df(da_data_p, 'DK', excluded_keywords=['(finansiering OR investering)', 'modstand'])
#articles_sp_df = articles_to_df(sp_data_p, 'ES', excluded_keywords=['(finanzas OR inversiones)', 'resistencia'])

# STORE
#articles_arg_df.to_excel(arg_data_out, index = False)
articles_da_df.to_excel(da_data_out, index = False)
#articles_sp_df.to_excel(sp_data_out, index = False)

# KEYWORD COUNT
## Function for keyword counts
def count_keywords(df):
    
    keyword_cols = [col for col in list(df.columns) if col.startswith('keyword_')]

    df['keyword'] = df[keyword_cols].idxmax(axis=1)

    df['keyword'] = df['keyword'].str.replace('keyword_', '')

    kw_counts = df['keyword'].value_counts().to_frame().reset_index()

    return(kw_counts)

## apply counter to dfs
#arg_kw_count = count_keywords(articles_arg_df)
da_kw_count = count_keywords(articles_da_df)
#sp_kw_count = count_keywords(articles_sp_df)

## save kw counts
#arg_kw_count.to_excel(arg_kw_out, index = False)
da_kw_count.to_excel(da_kw_out, index = False)
#sp_kw_count.to_excel(sp_kw_out, index = False)
