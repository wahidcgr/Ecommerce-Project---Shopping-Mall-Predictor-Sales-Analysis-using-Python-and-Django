import os
import glob
import shutil

import os
import pandas as pd


gender = {
    "Male":1,
    "Female":2
}
category = {
    'Clothing':1,
    'Sports':2,
    'Home & Garden':3,
    'Toys':4,
    'Electronics':5
}
payment_method = {
    'Debit Card':1,
    'Cash':2,
    'Credit Card':3
}
shopping_mall = {
    'Emaar Square Mall':1,
    'Zorlu Center':2,
    'Kanyon':3,
    'Istinye Park':4,
    'Mall of Istanbul':5,
    'Viaport Outlet':6, 
    'Metrocity':7, 
    'Metropol AVM':8,
    'Cevahir AVM':9, 
    'Forum Istanbul':10
}

def categ_to_numer(gender_cat,categ_cat,payment_cat):
    gender_num = gender[gender_cat] 
    category_num = category[categ_cat]
    payment_method_num = payment_method[payment_cat]
    return gender_num,category_num,payment_method_num





def preprocess(BASE_DIRI):
    path = str(BASE_DIRI)+'\\media\\uploads'
    file_path = get_latest_file_in_dir(path)
    df = pd.read_csv(file_path)
    # df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d-%m-%Y')
    return df

def get_latest_file_in_dir(directory):
    # Get a list of all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    
    if not files:
        return None  # Return None if there are no files
    
    # Get the file with the latest modification time
    latest_file = max(files, key=os.path.getmtime)
    
    return latest_file