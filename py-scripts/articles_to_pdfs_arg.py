#!/usr/bin/env python
# coding: utf-8

import os
import sys
from os.path import join
import pandas as pd

#sys.path.append('/work/Leverancer/dlvr_just-renewability_F24/modules')
sys.path.append('/work/dlvr_just-renewability_F24/modules')
#sys.path.append('/work/CALDISS-projects/Leverancer/dlvr_just-renewability_F24/modules')

from pdf_generator import generate_pdfs_from_ids

## PROJECT DIR
project_dir = '/work/dlvr_just-renewability_F24'

## PATH TO FONT
font_dir = join(project_dir, 'res')

## OUTPUT DIR
output_dir = join(project_dir, 'data', 'pdfs', 'ar')

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

## ARTICLE DATA
arg_articles_p = join(project_dir, 'data', 'articles_arg_raw.json')

## SELECTED ARTICLES
articles_filter_p = join(project_dir, 'output', 'article-filtering', 'articles_arg_meta_2024-08-22_renewable-energy_green-hydrogen_revisadoLW_jun25.xlsx')

## READ DATA
art_filt_df = pd.read_excel(articles_filter_p)

## KEEP
art_keep = art_filt_df.loc[art_filt_df['keep'] == 1, ['id', 'newscatcher_id']].reset_index(drop = True)

# Generate pdfs

generate_pdfs_from_ids(
    article_ids_df=art_keep,
    ctr='AR',
    json_file=arg_articles_p,
    output_dir=output_dir,
    #excluded_keywords=['(finanzas OR inversiones)', 'resistencia'],
    dejavu_font_dir=font_dir,
    replace=False
)