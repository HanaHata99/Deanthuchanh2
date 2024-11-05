from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages

import pandas as pd
import pgsql

#Listview
def listview(request):
    template = loader.get_template('viewdata.html')
    datas = []
    with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls = False) as db:
        statement = db.prepare("SELECT * FROM dulieudean LIMIT 1000")
        datas = list(statement())
        
        statement.close()

    context = {
        'mymembers': datas,
    }
    return HttpResponse(template.render(context, request))

#Detailview
def detailview(request):
    template = loader.get_template('viewdetail.html')
    A = request.GET.get('q', 'default')
    with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls = False) as db:

        with db.prepare("SELECT * FROM dulieudean where batch_id = $1") as person:
            detail = person(A).row()
            print(detail)
        

    context = {
        'detail': detail,
    }
    return HttpResponse(template.render(context, request))

#Hiển thị tab "Thêm dữ liệu"
def add_data_view(request):
    return render(request, 'add_data.html')

#Điền form
def add_manual_data(request):
    if request.method == 'POST':
        try:
            with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls=False) as db:
                batch_id = request.POST.get('batch_id')
                brew_date = request.POST.get('Brew_Date')
                beer_style = request.POST.get('Beer_Style')
                sku = request.POST.get('SKU')
                location = request.POST.get('Location')
                fermentation_time = request.POST.get('Fermentation_Time')
                temperature = request.POST.get('Temperature')
                ph_level = request.POST.get('pH_Level')
                gravity = request.POST.get('Gravity')
                alcohol_content = request.POST.get('Alcohol_Content')
                bitterness = request.POST.get('Bitterness')
                volume_produced = request.POST.get('Volume_Produced')
                color = request.POST.get('Color')
                ingredient_ratio = request.POST.get('Ingredient_Ratio')
                total_sales = request.POST.get('Total_Sales')
                quality_score = request.POST.get('Quality_Score')
                brewhouse_efficiency = request.POST.get('Brewhouse_Efficiency')
                loss_during_brewing = request.POST.get('Loss_During_Brewing')
                loss_during_fermentation = request.POST.get('Loss_During_Fermentation')
                loss_during_bottling_kegging = request.POST.get('Loss_During_Bottling_Kegging')

                # Chuyển đổi và validate dữ liệu
                try:
                    batch_id = int(batch_id)
                    fermentation_time = int(fermentation_time)
                    temperature = float(temperature)
                    ph_level = float(ph_level)
                    gravity = float(gravity)
                    alcohol_content = float(alcohol_content)
                    bitterness = int(bitterness)
                    volume_produced = int(volume_produced)
                    total_sales = float(total_sales) if total_sales else None
                    quality_score = float(quality_score) if quality_score else None
                    brewhouse_efficiency = float(brewhouse_efficiency) if brewhouse_efficiency else None
                    loss_during_brewing = float(loss_during_brewing) if loss_during_brewing else None
                    loss_during_fermentation = float(loss_during_fermentation) if loss_during_fermentation else None
                    loss_during_bottling_kegging = float(loss_during_bottling_kegging) if loss_during_bottling_kegging else None
                
                except ValueError as e:
                    messages.error(request, f'Lỗi định dạng dữ liệu: {str(e)}')
                    return redirect('add_data')

                # Insert dữ liệu
                insert_stmt = db.prepare("""
                    INSERT INTO dulieudean (
                        batch_id, "Brew_Date", "Beer_Style", "SKU", "Location", 
                        "Fermentation_Time", "Temperature", "pH_Level", "Gravity", 
                        "Alcohol_Content", "Bitterness", "Color", "Ingredient_Ratio", 
                        "Volume_Produced", "Total_Sales", "Quality_Score", 
                        "Brewhouse_Efficiency", "Loss_During_Brewing", 
                        "Loss_During_Fermentation", "Loss_During_Bottling_Kegging"
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 
                              $12, $13, $14, $15, $16, $17, $18, $19, $20)
                """)
                insert_stmt(
                    batch_id, brew_date, beer_style, sku, location,
                    fermentation_time, temperature, ph_level, gravity, 
                    alcohol_content, bitterness, color, ingredient_ratio,
                    volume_produced, total_sales, quality_score,
                    brewhouse_efficiency, loss_during_brewing,
                    loss_during_fermentation, loss_during_bottling_kegging
                )
                messages.success(request, 'Thêm dữ liệu thành công!')

        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
        
    return redirect('add_data')


#Upload file
def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']

        # Kiểm tra định dạng file
        try:
            if file.name.endswith('.csv'):
                data = pd.read_csv(file)
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                data = pd.read_excel(file)
            else:
                messages.error(request, "Chỉ hỗ trợ file CSV và Excel.")
                return redirect('upload_file')

            # Kết nối với database và tải dữ liệu
            with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls=False) as db:
                statement = db.prepare("""
                    INSERT INTO dulieudean (
                        batch_id, "Brew_Date", "Beer_Style", "SKU", "Location", 
                        "Fermentation_Time", "Temperature", "pH_Level", "Gravity", 
                        "Alcohol_Content", "Bitterness", "Color", "Ingredient_Ratio", 
                        "Volume_Produced", "Total_Sales", "Quality_Score", 
                        "Brewhouse_Efficiency", "Loss_During_Brewing", 
                        "Loss_During_Fermentation", "Loss_During_Bottling_Kegging"
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                """)

                for _, row in data.iterrows():
                    # Chạy statement với các tham số từ dòng dữ liệu
                    statement(
                        row['Batch_ID'], row['Brew_Date'], row['Beer_Style'], row['SKU'], row['Location'],
                        row['Fermentation_Time'], row['Temperature'], row['pH_Level'], row['Gravity'],
                        row['Alcohol_Content'], row['Bitterness'], row['Color'], row['Ingredient_Ratio'],
                        row['Volume_Produced'], row['Total_Sales'], row['Quality_Score'],
                        row['Brewhouse_Efficiency'], row['Loss_During_Brewing'],
                        row['Loss_During_Fermentation'], row['Loss_During_Bottling_Kegging']
                    )

                messages.success(request, "Tải dữ liệu thành công.")
        
        except Exception as e:
            messages.error(request, f"Lỗi khi tải file: {e}")
    return redirect('add_data')
    
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


#Điền Form API
@api_view(['POST'])
def add_manual_data_api(request):
    try:
        with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls=False) as db:
            # Lấy dữ liệu từ request JSON
            batch_id = request.data.get('batch_id')
            brew_date = request.data.get('Brew_Date')
            beer_style = request.data.get('Beer_Style')
            sku = request.data.get('SKU')
            location = request.data.get('Location')
            fermentation_time = request.data.get('Fermentation_Time')
            temperature = request.data.get('Temperature')
            ph_level = request.data.get('pH_Level')
            gravity = request.data.get('Gravity')
            alcohol_content = request.data.get('Alcohol_Content')
            bitterness = request.data.get('Bitterness')
            volume_produced = request.data.get('Volume_Produced')
            color = request.data.get('Color')
            ingredient_ratio = request.data.get('Ingredient_Ratio')
            total_sales = request.data.get('Total_Sales')
            quality_score = request.data.get('Quality_Score')
            brewhouse_efficiency = request.data.get('Brewhouse_Efficiency')
            loss_during_brewing = request.data.get('Loss_During_Brewing')
            loss_during_fermentation = request.data.get('Loss_During_Fermentation')
            loss_during_bottling_kegging = request.data.get('Loss_During_Bottling_Kegging')

            # Thực hiện câu lệnh chèn dữ liệu
            insert_stmt = db.prepare("""
                INSERT INTO dulieudean (
                    batch_id, "Brew_Date", "Beer_Style", "SKU", "Location", 
                    "Fermentation_Time", "Temperature", "pH_Level", "Gravity", 
                    "Alcohol_Content", "Bitterness", "Color", "Ingredient_Ratio", 
                    "Volume_Produced", "Total_Sales", "Quality_Score", 
                    "Brewhouse_Efficiency", "Loss_During_Brewing", 
                    "Loss_During_Fermentation", "Loss_During_Bottling_Kegging"
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 
                          $12, $13, $14, $15, $16, $17, $18, $19, $20)
            """)
            insert_stmt(
                batch_id, brew_date, beer_style, sku, location,
                fermentation_time, temperature, ph_level, gravity, 
                alcohol_content, bitterness, color, ingredient_ratio,
                volume_produced, total_sales, quality_score,
                brewhouse_efficiency, loss_during_brewing,
                loss_during_fermentation, loss_during_bottling_kegging
            )

        return Response({"message": "Thêm dữ liệu thành công!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": f"Lỗi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#Upload File Api
class UploadFileAPIView(APIView):
    def post(self, request):
        # Lấy file từ yêu cầu và địa chỉ IP của người dùng
        file = request.FILES.get('file')
        ip_address = request.META.get('REMOTE_ADDR')

        if not file:
            return Response({"error": "No file uploaded", "ip_address": ip_address}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Kiểm tra định dạng file và đọc dữ liệu
            if file.name.endswith('.csv'):
                data = pd.read_csv(file)
            elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                data = pd.read_excel(file)
            else:
                return Response({"error": "Only CSV and Excel files are supported", "ip_address": ip_address}, status=status.HTTP_400_BAD_REQUEST)

            # Kết nối tới PostgreSQL và tải dữ liệu vào database
            with pgsql.Connection(("localhost", 5432), "postgres", "24032003", "postgres", tls=False) as db:
                statement = db.prepare("""
                    INSERT INTO dulieudean (
                        batch_id, "Brew_Date", "Beer_Style", "SKU", "Location", 
                        "Fermentation_Time", "Temperature", "pH_Level", "Gravity", 
                        "Alcohol_Content", "Bitterness", "Color", "Ingredient_Ratio", 
                        "Volume_Produced", "Total_Sales", "Quality_Score", 
                        "Brewhouse_Efficiency", "Loss_During_Brewing", 
                        "Loss_During_Fermentation", "Loss_During_Bottling_Kegging"
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                        $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                """)

                for _, row in data.iterrows():
                    # Chạy statement với dữ liệu từ từng dòng
                    statement(
                        row['Batch_ID'], row['Brew_Date'], row['Beer_Style'], row['SKU'], row['Location'],
                        row['Fermentation_Time'], row['Temperature'], row['pH_Level'], row['Gravity'],
                        row['Alcohol_Content'], row['Bitterness'], row['Color'], row['Ingredient_Ratio'],
                        row['Volume_Produced'], row['Total_Sales'], row['Quality_Score'],
                        row['Brewhouse_Efficiency'], row['Loss_During_Brewing'],
                        row['Loss_During_Fermentation'], row['Loss_During_Bottling_Kegging']
                    )

            return Response({"message": "File uploaded successfully", "ip_address": ip_address}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"File upload error: {str(e)}", "ip_address": ip_address}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
