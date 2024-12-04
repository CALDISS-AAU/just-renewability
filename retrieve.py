#!/usr/bin/env python
# coding: utf-8

import os
from os.path import join
import requests
from newscatcherapi import NewsCatcherApiClient
import json
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time

# PATHS AND DIRS
project_dir = join('/work', 'CALDISS-projects', 'Leverancer', 'dlvr_just-renewability_F24')
data_dir = join(project_dir, 'data')

if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

# PARAMETERS

### query english
kws_eng = [
    '"green hydrogen"',
    'solar',
    'wind',
    '"power to x"',
    '("pink hydrogen" OR nuclear)',
    '(reindustrialisation OR industrialisation) ',
    #'growth',
    #'participation',
    #'citizen',
    '"environmental impact"',
    #'water',
    '"public hearings"',
    #'future',
    #'conflict',
    'resistance',
    #'support',
    '(finance OR investment)',
    'renewable'
    ]

q_en = ' OR '.join(kws_eng)

## SPAIN
### spanish query
kws_sp = [
    '"hidrógeno verde"',
    'solar', 
    'eólica', 
    '"power to x"', 
    '("hidrógeno rosa" OR nuclear)', 
    '(reindustrialización OR industrialización)', 
    #'crecimiento', 
    #'participación', 
    #'ciudadano', 
    '"impacto medioambiental"',
    #'agua', 
    '"audiencias públicas"', 
    #'futuro', 
    #'conflicto', 
    'resistencia', 
    #'apoyo', 
    '(finanzas OR inversiones)', 
    'renovable'
    ]

q_sp = ' OR '.join(kws_sp)

### spanish sources
src_sp = [
    'elmundo.es',
    'elpais.com',
    'lavanguardia.com',
    'larazon.es'
    ]

### parameters dictionary
sp_params = {
    'kws': kws_sp,
    'q': q_sp,
    'src': src_sp
    }


## ARGENTINA
### argentinian sources
src_arg = [
    'clarin.com',
    'pagina12.com.ar',
    'lanacion.com.ar',
    'eldiarioar.com'
    ]

### parameters dictionary
arg_params = {
    'kws': kws_sp,
    'q': q_sp,
    'src': src_arg
    }


## DANISH

### query danish
kws_da = [
    '"grøn brint"',
    'solcelle',
    'vind',
    '"power to x"',
    '("pink brint" OR atomkraft)',
    '(reindustralisering OR industralisering)',
    #'vækst',
    #'(deltagelse OR inddragelse)',
    #'borger',
    'miljøvurdering',
    #'vand',
    '"offentlig høring"',
    #'fremtid',
    #'konflikt',
    'modstand',
    #'opbakning',
    '(finansiering OR investering)',
    'vedvarende'
    ]

q_da = ' OR '.join(kws_da)


### danish sources
src_da = [
    'politiken.dk',
    'jyllands-posten.dk',
    'information.dk',
    'berlingske.dk'
    ]

### parameters dictionary
da_params = {
    'kws': kws_da,
    'q': q_da,
    'src': src_da
    }


# GLOBAL PARAMS
gl_params = {
    'page_size': 100,
    'from': '2023/05/01',
    'to': '2024/05/31',
    'sort_by': 'date'
    }

# Init newscatcher
API_KEY = 'X6_i1lcTsOTW_kr4b6a_kXA_1fgCSr02bX4G5D8X2DU' # API key
newscatcher = NewsCatcherApiClient(x_api_key=API_KEY)

# DATERANGE INTERVAL SPLITTER FUNCTION
def daterange_monthly(start_date, end_date):

    start_date = datetime.strptime(start_date, '%Y/%m/%d')
    end_date = datetime.strptime(end_date, '%Y/%m/%d')

    intervals = []
    current_start = start_date

    while current_start < end_date:
        # Calculate the end of the current month
        current_end = current_start + relativedelta(months=1) - timedelta(days = 1)
        
        # Append the current interval
        start_str = current_start.strftime('%Y/%m/%d')
        end_str = current_end.strftime('%Y/%m/%d')
        intervals.append((start_str, end_str))
        
        # Move to the next month's start
        current_start = current_end + timedelta(days = 1)

    return intervals


# WRAPPER FUNCTION
def get_articles(q, src, from_, to_, newscatcher = newscatcher, page_size = 100, sort_by = 'date', seconds_pause = 1.0):

    intervals = daterange_monthly(from_, to_)

    for c, interval in enumerate(intervals, start = 1):
        
        from_ = interval[0]
        to_ = interval[1]

        if c == 1:
            
            news_articles = newscatcher.get_search_all_pages(
            q = q,
            sources = src,
            from_ = from_,
            to_ = to_,
            page_size = page_size,
            sort_by = sort_by,
            seconds_pause = seconds_pause)

        if c > 1:

            more_articles = newscatcher.get_search_all_pages(
            q = q,
            sources = src,
            from_ = from_,
            to_ = to_,
            page_size = page_size,
            sort_by = sort_by,
            seconds_pause = seconds_pause)
            
            news_articles['articles'] = news_articles.get('articles') + more_articles.get('articles')

    return(news_articles)

# GET ARTICLES

## hits per keyword
#for kw in kws_sp:
#    news_articles = newscatcher.get_search(
#        q = kw,
#        sources = sp_params.get('src'),
#        from_ = '2023/05/01',
#        to_ = '2023/05/31',
#        page_size = 1)
#
#    print(f'{kw} yields {news_articles.get("total_hits")}')
#
#    time.sleep(1)



## SPAIN
articles_sp = get_articles(
    q = sp_params.get('q'), 
    src = sp_params.get('src'),
    from_ = gl_params.get('from'),
    to_ = gl_params.get('to')
    )

## ARGENTINA
articles_arg = get_articles(
    q = arg_params.get('q'), 
    src = arg_params.get('src'),
    from_ = gl_params.get('from'),
    to_ = gl_params.get('to')
    )

## DENMARK
articles_da = get_articles(
    q = da_params.get('q'), 
    src = da_params.get('src'),
    from_ = gl_params.get('from'),
    to_ = gl_params.get('to')
    )

# STORE ARTICLES
sp_p = join(data_dir, 'articles_sp_raw.json')
arg_p = join(data_dir, 'articles_arg_raw.json')
da_p = join(data_dir, 'articles_da_raw.json')

## spain
with open(sp_p, 'w') as f:
    json.dump(articles_sp, f)

## argentina
with open(arg_p, 'w') as f:
    json.dump(articles_arg, f)

## denmark
with open(da_p, 'w') as f:
    json.dump(articles_da, f)