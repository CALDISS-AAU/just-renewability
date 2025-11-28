#!/usr/bin/env python
# coding: utf-8

import os
import sys
from os.path import join
import pandas as pd

#sys.path.append('/work/Leverancer/dlvr_just-renewability_F24/modules')
sys.path.append('/work/dlvr_just-renewability_F24/modules')

from pdf_generator import generate_pdfs_from_ids

## PATH TO FONT
font_dir = '/work/dlvr_just-renewability_F24/res/'

## OUTPUT DIR
output_dir = '/work/dlvr_just-renewability_F24/data/pdfs/da'

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

## ARTICLE DATA
da_articles_p = '/work/dlvr_just-renewability_F24/data/articles_da_raw.json'

## SELECTED ARTICLES
articles_filter_p = '/work/dlvr_just-renewability_F24/output/article-filtering/articles_da_meta_2024-08-22_renewable-energy_green-hydrogen-b_selection-mar25.xlsx'
articles_new_p = '/work/dlvr_just-renewability_F24/output/articles_da_meta_2025-11-28.xlsx'

## READ DATA
art_filt_df = pd.read_excel(articles_filter_p)
art_new_df = pd.read_excel(articles_new_p)

## KEEP
art_keep = art_new_df.loc[~art_new_df['id'].isin(art_filt_df['id']), ['id', 'newscatcher_id']].reset_index(drop = True)

# Generate pdfs

generate_pdfs_from_ids(
    article_ids_df=art_keep,
    ctr='DK',
    json_file=da_articles_p,
    output_dir=output_dir,
    #excluded_keywords=['(finanzas OR inversiones)', 'resistencia'],
    dejavu_font_dir=font_dir,
    replace=False
)