import pandas as pd 
#import numpy
import json
#import seaborn as sns
#import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches




####################TASK 1: 
#Step 1 - From json, get article and convert the raw dates. We will only be working with article

def get_raw_dates_and_convert(input_json):

    try:
        with open(input_json, 'r', encoding= "utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("Error finding the input file")

    #get the articles
    df = pd.DataFrame(data["articles"])

    #Convert date
    df["published_date"] = pd.to_datetime(df["published_date"])
    df = df.dropna(subset=["published_date"])

    #pandas.Series.dt.strftime to change date format
    df["Year-Month"] = df["published_date"].dt.strftime("%Y-%m")
    #get total articles per month
    result = df.groupby("Year-Month").size().reset_index(name="N_articles_total")
    
    return result 



#Step 2 - Change dates in Excel. OG dataset


def change_excel_dates(input_excel):
    #do the same as before with strf
    excel_df = pd.read_excel(input_excel)

    #Change the date column
    excel_df["date"] = pd.to_datetime(excel_df["date"])
    excel_df["Year-Month"] = excel_df["date"].dt.strftime("%Y-%m")

    return excel_df
    


#Step 3- What are the keyword filterings

def compute_filtered_counts(input_excel):
    key_columns = [column for column in input_excel.columns if column.startswith("keyword_")]
    
    #Check if any keyword is true

    any_keyword_TRUE = input_excel[key_columns].any(axis=1)

    ##Check if only keyword_conflic is TRUE
    other_keywords = [column for column in key_columns if column != "keyword_conflicto"]
    only_conflict = input_excel["keyword_conflicto"] & ~ input_excel[other_keywords].any(axis=1)

    #Exlude keywords where : 
    # A) only keyword_conflicto == TRUE 
    # B) all other keywords == FALSE
    filter_me_ready = input_excel[any_keyword_TRUE & ~only_conflict]

    #Count per month
    res = filter_me_ready.groupby("Year-Month").size().reset_index(name="N_articles_filtered")

    return res

# Step 4 : 4. Compute used counts

def compute_used_counts(input_dataframe):
    used_dataframe = input_dataframe[input_dataframe["keep"]==1]

    used_counts = (
        used_dataframe.groupby("Year-Month").size().reset_index(name="N_articles_used")
    )

    return used_counts

# Step 5:
#Merge results and join per country: 1) Raw monthly totals 2) Filtered counts 3)Used counts =>  Output final: Year-month | N_articles_total | N_articles_filtered | N_articles_used

def merge_dataset(input_json, input_excel, output_csv, output_xlsx):
    #Merge input_hsib + input_excel
    
    raw = get_raw_dates_and_convert(input_json)
    excel_df = change_excel_dates(input_excel)
    filtered_counts = compute_filtered_counts(excel_df)
    used_counts = compute_used_counts(excel_df)

    final_dataframe = raw.merge(filtered_counts, on = "Year-Month", how = "inner")
    final_dataframe = final_dataframe.merge(used_counts, on = "Year-Month", how = "inner")
    #NaN values fill with 0
    #Ensure that months with count = 0 contains 0 and not NULL, None or missing
    final_dataframe["N_articles_filtered"] = final_dataframe["N_articles_filtered"].fillna(0).astype(int)

    final_dataframe["N_articles_used"] = final_dataframe["N_articles_used"].fillna(0).astype(int)

    final_dataframe.to_csv(output_csv, index = False)
    final_dataframe.to_excel(output_xlsx, index = False)
    
    return final_dataframe

#Spain
spain_json_file = "./data/articles_sp_raw.json"
spain_excel_file = "./output/article-filtering/articles_sp_meta_2024-08-22_renewable-energy_green-hydrogen_selection-nov24.xlsx"
spain_output_csv_file = "./output/articles_sp_monthly_summary.csv"
spain_output_xlsx_file = "./output/tables/articles_sp_monthly_summary.xlsx"

argentina_json_file = "./data/articles_arg_raw.json"
argentina_excel_file = "./output/article-filtering/articles_arg_meta_2024-08-22_renewable-energy_green-hydrogen_revisadoLW_jun25.xlsx"
argentina_output_csv_file = "./output/articles_arg_monthly_summary.csv"
argentina_output_xlsx_file = "./output/tables/articles_arg_monthly_summary.xlsx"


SPAIN = merge_dataset(spain_json_file, spain_excel_file, spain_output_csv_file, spain_output_xlsx_file)
ARGENT = merge_dataset(argentina_json_file, argentina_excel_file, argentina_output_csv_file, argentina_output_xlsx_file)
print(SPAIN.head())
print(SPAIN.shape)

print(ARGENT.head())
print(ARGENT.shape)