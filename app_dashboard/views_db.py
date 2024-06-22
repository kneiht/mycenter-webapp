from io import BytesIO
import pandas as pd
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from sqlalchemy import create_engine
from django.conf import settings

from django.http import JsonResponse
import time, datetime
def is_admin(user):
    if User.objects.count() == 0:
        return True
    else:
        return True
        #return user.is_active and user.is_staff and user.is_superuser


def delete_all_rows(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM {table_name};")


def insert_rows_using_to_sql(df, table_name):
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    host = settings.DATABASES['default']['HOST']
    port = settings.DATABASES['default']['PORT']

    if 'mysql' in db_engine:
        # MySQL database
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
    elif 'sqlite' in db_engine:
        # SQLite database
        engine = create_engine(f"sqlite:///{db_name}")
    else:
        # Add other database engines as needed
        raise NotImplementedError("Database engine not supported")

    # Write the DataFrame to the database table using df.to_sql
    columns_to_keep = [col for col in df.columns if "exclude" not in col]
    df_filtered = df[columns_to_keep]
    
    df_filtered.to_sql(table_name, con=engine, if_exists='append', index=False)


def reset_primary_key(table_name):
    # Check the database engine
    if 'postgresql' in connection.settings_dict['ENGINE']:
        sql = f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;"
    elif 'mysql' in connection.settings_dict['ENGINE']:
        sql = f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;"
    elif 'sqlite3' in connection.settings_dict['ENGINE']:
        # SQLite does not support altering the AUTOINCREMENT value.
        return
    else:
        raise ValueError("Unsupported database backend")

    with connection.cursor() as cursor:
        cursor.execute(sql)


def get_table_names():
    #print('\n\n', connection.vendor)
    # Get a list of all table names for the current database
    if connection.vendor == 'mysql':
        # For MySQL
        table_names = connection.introspection.table_names()
    elif connection.vendor == 'sqlite':
        # For SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]  # Exclude internal SQLite table
    else:
        # Handle other databases here
        table_names = []

    return table_names


def fetch_table_data(table_name):
    # Fetch data from the specified table
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    data = pd.DataFrame(rows, columns=columns)
    return data





@user_passes_test(is_admin)
def download_database_backup(request):
    # Get a list of all table names for the current database
    if connection.vendor == 'mysql':
        # Get list of all tables in the database
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            table_names = [row[0] for row in cursor.fetchall()]
    elif connection.vendor == 'sqlite':
        # Get list of all tables in the database for SQLite
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]  # Exclude internal SQLite table
    else:
        # Handle other databases here
        table_names = []

    # Create a Pandas Excel writer using XlsxWriter as the engine
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Loop through tables and write each to a separate sheet
        for table_name in table_names:
            data = fetch_table_data(table_name)
            # Shorten the table name for the Excel sheet
            shortened_table_name = table_name.replace('app_dashboard_', '')
            data.to_excel(writer, sheet_name=shortened_table_name, index=False)

    # Get the Excel file
    excel_data = output.getvalue()

    # Return the Excel file as an HTTP response
    response = HttpResponse(
        excel_data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # name the db based on time
    filename = f"gen8_db_{datetime.datetime.now().strftime('%Y_%m_%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response








@user_passes_test(is_admin)
def database_handle(request):
    if request.method == 'GET':
        return render(request, 'pages/db_backup_restore.html')

    if request.method == 'POST':
        excel_file = request.FILES.get('file')
        table_name_origin = request.POST.get('table_name')

        if excel_file and excel_file.name.endswith('.xlsx'):
            if table_name_origin=='all':
                table_list = [
                    #'auth_user',
                    'timeframe',
                    'thumbnail',
                    'school',
                    'schooluser',
                    'filtervalues',
                    'class',
                    'student',
                    'studentclass',
                    
                    'attendance',
                    'financialtransaction',
                ]
                table_list_reverse = list(table_list)
                table_list_reverse.reverse()

            else:
                table_list = [table_name_origin]
                table_list_reverse = list(table_list)
                table_list_reverse.reverse()


            for table_name in table_list_reverse:
                sql_table_name = 'app_dashboard_' + table_name if table_name != 'auth_user' else table_name
                try:
                    # Delete all current rows from the table
                    delete_all_rows(sql_table_name)
                    reset_primary_key(sql_table_name)
                except Exception as e:
                    return JsonResponse({'error': str(e), 'table': sql_table_name, 'delete':'delete'})


            for table_name in table_list:
                try:
                    # Read the Excel file into a DataFrame
                    df = pd.read_excel(excel_file, sheet_name=table_name)
                    sql_table_name = 'app_dashboard_' + table_name if table_name != 'auth_user' else table_name
                    # Insert new rows into the specified table using df.to_sql
                    insert_rows_using_to_sql(df, sql_table_name)

                except Exception as e:
                    return JsonResponse({'error': str(e), 'table': sql_table_name, 'update':'update'})
            return JsonResponse({'message': 'Data updated successfully'})
        else:
            return JsonResponse({'error': 'Please upload a valid Excel file (xlsx)'})

    return JsonResponse({'error': 'Invalid request'})










