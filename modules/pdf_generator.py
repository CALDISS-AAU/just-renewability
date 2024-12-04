#!/usr/bin/env python
# coding: utf-8

import json
from os.path import join
from fpdf import FPDF
from tqdm import tqdm
import os

from just_renew_funs import parse_article_meta

def generate_pdfs_from_ids(article_ids_df, ctr, json_file, output_dir, excluded_keywords = [], dejavu_font_dir = join('..', 'res'), replace=True):

    article_ncids = article_ids_df['newscatcher_id'].tolist()
    article_ctr_ids = article_ids_df['id'].tolist()

    # Read JSON file
    with open(json_file, 'r') as f:
        articles_raw = json.load(f)
    
    # Select articles
    articles = articles_raw.get('articles')

    # Filter JSON records based on the provided article IDs
    filtered_articles = [article for article in articles if article['_id'] in article_ncids]
    
    # Generate PDFs for each filtered article
    for article, id in tqdm(zip(filtered_articles, article_ctr_ids)):

        article_keywords = parse_article_meta(article, ctr=ctr, excluded_keywords=excluded_keywords).get('keywords')
        article['keywords'] = article_keywords

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Add a Unicode-compatible font (DejaVuSans)
        pdf.add_font('DejaVu', '', join(dejavu_font_dir, 'DejaVuSans.ttf'), uni=True)
        pdf.add_font('DejaVu', 'B', join(dejavu_font_dir, 'DejaVuSans-Bold.ttf'), uni=True)
        pdf.set_font('DejaVu', '', size=12)
        
        # Add article details to PDF
        pdf.set_font("DejaVu", style='B', size=14)
        pdf.multi_cell(0, 10, article.get("title", "No Title"))
        pdf.ln(5)
        
        pdf.set_font("DejaVu", size=12)
        pdf.cell(0, 10, f"Date: {article.get('published_date', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Country: {ctr}", ln=True)
        pdf.cell(0, 10, f"Source: {article.get('clean_url', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Link: {article.get('link', 'N/A')}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("DejaVu", style='B', size=12)
        pdf.cell(0, 10, "Keywords:", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, ', '.join(article.get("keywords", [])))
        
        pdf.ln(5)
        pdf.set_font("DejaVu", style='B', size=12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, article.get("summary", "No Summary"))
        
        # Save PDF with the article ID as filename
        outname = f"{id}.pdf"
        outpath = join(output_dir, outname)

        if replace:
            pdf.output(outpath)
        else:
            if os.path.isfile(outpath):
                continue
            else:
                pdf.output(outpath)