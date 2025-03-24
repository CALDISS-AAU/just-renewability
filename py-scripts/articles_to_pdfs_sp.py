#!/usr/bin/env python
# coding: utf-8

import os
import sys
from os.path import join
import pandas as pd

sys.path.append('/work/Leverancer/dlvr_just-renewability_F24/modules')

from pdf_generator import generate_pdfs_from_ids

## PATH TO FONT
font_dir = '/work/Leverancer/dlvr_just-renewability_F24/res/'

## OUTPUT DIR
output_dir = '/work/Leverancer/dlvr_just-renewability_F24/data/pdfs/sp'

## ARTICLE DATA
sp_articles_p = '/work/Leverancer/dlvr_just-renewability_F24/data/articles_sp_raw.json'

## SELECTED ARTICLES
articles_filter_p = '/work/Leverancer/dlvr_just-renewability_F24/output/article-filtering/articles_sp_meta_2024-08-22_renewable-energy_green-hydrogen_selection-nov24.xlsx'

## READ DATA
art_filt_df = pd.read_excel(articles_filter_p)

## KEEP
art_keep = art_filt_df.loc[art_filt_df['keep'] == 1, ['id', 'newscatcher_id']].reset_index(drop = True)

# Example usage

generate_pdfs_from_ids(
    article_ids_df=art_keep,
    ctr='ES',
    json_file=sp_articles_p,
    output_dir=output_dir,
    excluded_keywords=['(finanzas OR inversiones)', 'resistencia'],
    dejavu_font_dir=font_dir,
    replace=False
)