from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from shop.utility import preprocess
from django.http import HttpResponse
from pathlib import Path
from datetime import datetime
import pandas as pd
from shop.utility import categ_to_numer,shopping_mall
import pickle


BASE_DIRI = Path(__file__).resolve().parent.parent
file_name = ''
# Create your views here.

def index(request):
    return render(request,'info.html')


def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        FILE_NAME = request.FILES['file'].name
        if form.is_valid():
            file_instance = form.save()
            return redirect("analyse")
    else:
        form = FileUploadForm()
    return render(request, 'upload_file.html', {'form': form})


def analyse(request):
    action = request.GET.get('action')

    if action == 'pie_chart':
        return render(request,'charts/pie_chart_filter.html')
    elif action == 'graph':
        return render(request,'charts/graph.html',{
        })
    elif action == 'bar':
        return render(request,'charts/bar_chart.html')
    elif action == 'predict':
        return render(request,'predict.html')
    return render(request,'analyses.html')

def graph(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI)
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], dayfirst=True)
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        if from_date and to_date:
            month_diff = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
            category = request.POST.get('category')
            if category == 'Gender':
                category = 'gender'
            elif category == 'Payment Method':
                category = 'payment_method'
            elif category == 'Shopping Mall':
                category = 'shopping_mall'
            elif category == 'Quantity':
                category = 'quantity'
            elif category == 'Category':
                category = 'category'
            date = list()

            # Process data by months
            data_lst = list()
            for i in range(month_diff):
                tf = df[(df['invoice_date'].dt.year == from_date.year) & 
                        (df['invoice_date'].dt.month == from_date.month + i)]
                temp = tf[category].value_counts().to_dict()
                data_lst.append(temp)
                date.append(tf['invoice_date'].head(1).dt.month.tolist()[0])

            unique_category = df[category].unique()
            data_dict = dict()
            for i in unique_category:
                temp = []
                for j in range(len(data_lst)):
                    temp.append(data_lst[j].get(i, 0))  # Use get(i, 0) to handle missing keys
                data_dict[i] = temp

            df = pd.DataFrame(data_dict)
            lst = ['r', 'g', 'b', 'c', 'm', 'y', 'k', '#FF5733', '#33FF57', '#3357FF']
            generated = True
            size = len(df)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False)

            # Render the template with the graph and data table
            return render(request, 'charts/graph.html', {
                'table': table,
                'size': size,
                'generated': generated,
                'date':date,
                'unique_category':unique_category,
                'keys':list(data_dict.keys()),
                'values':list(data_dict.values()),
                'iter':len(unique_category)
            })
    return render(request, 'charts/graph.html',{
        'min_date':min_date,
        'max_date':max_date
    })


def pie_chart_filter(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI)  # Assuming preprocess function loads your data
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'],dayfirst=True)

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                return HttpResponse("Invalid date format. Please use YYYY-MM-DD.")

            category = request.POST.get('category')

            # Filter data based on date range
            df = df[(df['invoice_date'] >= from_date) & (df['invoice_date'] <= to_date)]
            size = len(df)

            if size == 0:
                return HttpResponse(f"No data available for the selected date range.Please Select the date Range between {min_date} to {max_date}")

            # Create a dictionary based on the selected category
            dict1 = {}
            if category == 'Gender':
                dict1 = df['gender'].value_counts().to_dict()
            elif category == 'Payment Method':
                dict1 = df['payment_method'].value_counts().to_dict()
            elif category == 'Shopping Mall':
                dict1 = df['shopping_mall'].value_counts().to_dict()
            elif category == 'Quantity':
                dict1 = df['quantity'].value_counts().to_dict()
            elif category == 'Category':
                dict1 = df['category'].value_counts().to_dict()
            elif category == 'Age':
                dict1 = df['age'].value_counts().to_dict()
                # Create ranges for age groups
                dict2 = {'1-20': 0, '20-40': 0, '40-60': 0, '60-80': 0, '80-100': 0}
                for age, count in dict1.items():
                    if 1 <= age <= 20:
                        dict2['1-20'] += count
                    elif 21 <= age <= 40:
                        dict2['20-40'] += count
                    elif 41 <= age <= 60:
                        dict2['40-60'] += count
                    elif 61 <= age <= 80:
                        dict2['60-80'] += count
                    elif 81 <= age <= 100:
                        dict2['80-100'] += count
                dict1 = dict2

            labels = list(dict1.keys())
            sizes = list(dict1.values())

            generated = True

            # Display a sample of the filtered data (if large)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False)

            # Render template with the pie chart and filtered table
            return render(request, 'charts/pie_chart_filter.html', {
                'table': table,
                'size': size,
                'generated': generated,
                'from_date': from_date.strftime('%Y-%m-%d'),
                'to_date': to_date.strftime('%Y-%m-%d'),
                'labels':labels,
                'sizes':sizes
            })

    # Initial GET request
    return render(request, 'charts/pie_chart_filter.html',{
        'min_date':min_date,
        'max_date':max_date
    })

def bar_chart(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI) 
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], dayfirst=True)
    

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        if from_date and to_date:
            month_diff = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
            category = request.POST.get('category')
            if category == 'Gender':
                category = 'gender'
            elif category == 'Payment Method':
                category = 'payment_method'
            elif category == 'Shopping Mall':
                category = 'shopping_mall'
            elif category == 'Quantity':
                category = 'quantity'
            elif category == 'Category':
                category = 'category'
            date = list()
            data_lst = list()
            for i in range(month_diff):
                tf = df[(df['invoice_date'].dt.year == from_date.year) & 
                        (df['invoice_date'].dt.month == from_date.month + i)]
                temp = tf[category].value_counts().to_dict()
                data_lst.append(temp)
                date.append(tf['invoice_date'].head(1).dt.month.tolist()[0])

            unique_category = df[category].unique()
            data_dict = dict()
            for i in unique_category:
                temp = []
                for j in range(len(data_lst)):
                    temp.append(data_lst[j].get(i, 0))  
                data_dict[i] = temp
            df = pd.DataFrame(data_dict)
            generated = True
            size = len(df)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False,justify="center")

            return render(request, 'charts/bar_chart.html', {
                'table': table,
                'size': size,
                'generated': generated,
                'date':date,
                'unique_category':unique_category,
                'keys':list(data_dict.keys()),
                'values':list(data_dict.values()),
                'iter':len(unique_category)
            })

    return render(request, 'charts/bar_chart.html',{
        'min_date':min_date,
        'max_date':max_date
    })

def predict(request):
    model = str(BASE_DIRI)+'\\media\\uploads\\cnn.pkl'
    ans_cat = ''
    with open(model, 'rb') as file:
        loaded_model = pickle.load(file)
    if request.method == 'POST':
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        category = request.POST.get('category')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        payment_method = request.POST.get('payment_method')
        print(gender,age,category,quantity,price,payment_method)
        gender_num,category_num,payment_method_num = categ_to_numer(gender,category,payment_method)
        lst = [gender_num,age,category_num,quantity,price,payment_method_num]
        ans = loaded_model.predict([lst])
        for key, val in shopping_mall.items():
            if val == ans:
                ans_cat = key
        print(ans_cat)

    return render(request,'predict.html',{'ans_cat':ans_cat})