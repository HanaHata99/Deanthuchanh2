from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib import messages
from appdean.analysis import AnalysisData, get_database_pass

import pandas as pd
import pgsql
import json
from datetime import datetime, timedelta


def convert_row(row):
    # Class không có __dict__ method mà chỉ có __slots__ nên phải tự convert
    return {
            "batch_id": row.batch_id,
            "Brew_Date": row.Brew_Date,
            "Beer_Style": row.Beer_Style,
            "SKU": row.SKU,
            "Location": row.Location,
            "Fermentation_Time": row.Fermentation_Time,
            "Temperature": row.Temperature,
            "pH_Level": row.pH_Level,
            "Gravity": row.Gravity,
            "Alcohol_Content": row.Alcohol_Content,
            "Bitterness": row.Bitterness,
            "Color": row.Color,
            "Ingredient_Ratio": row.Ingredient_Ratio,
            "Volume_Produced": row.Volume_Produced,
            "Total_Sales": row.Total_Sales,
            "Quality_Score": row.Quality_Score,
            "Brewhouse_Efficiency": row.Brewhouse_Efficiency,
            "Loss_During_Brewing": row.Loss_During_Brewing,
            "Loss_During_Fermentation": row.Loss_During_Fermentation,
            "Loss_During_Bottling_Kegging": row.Loss_During_Bottling_Kegging
        }

#Listview
def listview(request):
    # Xử lý GET request
    if 'GET' == request.method:
        template = loader.get_template('viewdata.html')
        datas = []
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:
            statement = db.prepare("SELECT * FROM dulieudean LIMIT 1000")
            datas = list(statement())
            
            statement.close()

        context = {
            'mymembers': datas,
        }
        return HttpResponse(template.render(context, request))
    
    # Xử lý POST request: Submit form truy vấn dữ liệu
    else:
        # Convert form data sang dictionary python để sử dụng
        formData = dict(request.POST.dict())
        sql = '''
            SELECT  *
            FROM    dulieudean
            WHERE 1 = 1
            {}
            LIMIT 1000
        '''

        # Tạo biến để chứa toàn bộ kết quả tìm kiếm
        datas = []
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:

            # Trường hợp tìm kiếm trên các column chữ (text)
            if ('SKU' == formData['column'] or 
                'Location' == formData['column'] or 
                'Beer_Style' == formData['column'] or 
                'Color' == formData['column'] or 
                'Ingredient_Ratio' == formData['column']):
                
                where_clause = '''
                    AND LOWER("{}") LIKE $1
                '''.format(formData["column"])

                sql = sql.format(where_clause)
                print(f'{sql} {where_clause}')
                statement = db.prepare(sql)
                rows = list(statement(f'%{formData["keyword"].lower()}%'))

            # Trường hợp tìm kiếm trên các column ngày tháng (datetime)
            elif 'Brew_Date' == formData['column']:
                min_time = datetime.strptime(formData['keyword'], '%Y-%m-%d')
                max_time = min_time + timedelta(seconds=59, minutes=59, hours=11)
                where_clause = '''
                    AND TO_TIMESTAMP($1, 'YYYY-MM-DD') <= "{}"
                    AND "{}" <= TO_TIMESTAMP($2, 'YYYY-MM-DD HH:MI:SS PM')
                '''.format(formData["column"], formData["column"])
                
                sql = sql.format(where_clause)
                print(f'{sql} {where_clause}')
                statement = db.prepare(sql)
                rows = list(statement(min_time.strftime('%Y/%m/%d'), max_time.strftime('%Y/%m/%d %H:%M:%S PM')))

            # Trường hợp tìm kiếm trên các column số (integer/real)
            else:

                where_clause = '''
                    AND "{}"::text LIKE $1
                '''.format(formData["column"])

                sql = sql.format(where_clause)
                print(f'{sql} {where_clause}')
                statement = db.prepare(sql)
                rows = list(statement(f'%{formData["keyword"]}%'))
            
            datas = [convert_row(row) for row in rows]
            statement.close()
            
        # Dữ liệu được trả về ở dạng json
        return JsonResponse({'datas':json.dumps(datas)})

def analysis(request):
    template = loader.get_template('analysis.html')
    analysis = AnalysisData()

    sales_by_month = analysis.sales_by_month()
    context = {
        'sale_infos': sales_by_month[0],
        'sale_months': sales_by_month[1],
    }

    batch_by_month = analysis.batch_by_month()
    context['batch_infos'] = batch_by_month[0]
    context['batch_months'] = batch_by_month[1]

    volumn_by_month = analysis.volumn_by_month()
    context['volumn_infos'] = volumn_by_month[0]
    context['volumn_months'] = volumn_by_month[1]

    return HttpResponse(template.render(context, request=request))

#Detailview
def detailview(request):
    template = loader.get_template('viewdetail.html')
    A = request.GET.get('q', 'default')
    with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls = False) as db:

        with db.prepare("SELECT * FROM dulieudean where batch_id = $1") as person:
            detail = person(A).row()
            print(detail)
        

    context = {
        'detail': detail,
    }
    return HttpResponse(template.render(context, request))

#Xóa bản ghi
def delete_record(request):
    if request.method == "POST":
        record_id = request.POST.get('id')
        try:
            with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
                statement = db.prepare("DELETE FROM dulieudean WHERE batch_id = $1")
                statement(record_id)
                statement.close()

            # Redirect lại trang danh sách để tải lại
            return redirect('/listview/')  # Chuyển hướng về trang danh sách sau khi xóa
        except Exception as e:
            return HttpResponse(f"Lỗi: {e}", status=500)

    return HttpResponse("Phương thức không hợp lệ", status=400)

#Xóa toàn bộ dữ liệu
def delete_all_records(request):
    if request.method == "POST":
        try:
            with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
                # Lệnh SQL xóa toàn bộ dữ liệu
                statement = db.prepare("DELETE FROM dulieudean")
                statement()
                statement.close()

            # Redirect lại trang danh sách để tải lại sau khi xóa toàn bộ dữ liệu
            return redirect('/listview/')
        except Exception as e:
            return HttpResponse(f"Lỗi: {e}", status=500)

    return HttpResponse("Phương thức không hợp lệ", status=400)


#Hiển thị tab "Thêm dữ liệu"
def add_data_view(request):
    return render(request, 'add_data.html')

#Điền form
def add_manual_data(request):
    if request.method == 'POST':
        try:
            with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
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
            with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
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
        with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
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
            with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
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
    
#Get API để kết nối Tableau  
def get_all_data(request):
    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 50000))  # Lô 10000 bản ghi
    with pgsql.Connection(("localhost", 5432), "postgres", get_database_pass(), "postgres", tls=False) as db:
        statement = db.prepare("SELECT * FROM dulieudean OFFSET $1 LIMIT $2")
        rows = statement(offset, limit)
        data = [convert_row(row) for row in rows]
    return JsonResponse(data, safe=False)

