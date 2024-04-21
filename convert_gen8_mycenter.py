

'''
CONVERT GEN8 TO MYCENTER
=> school

dashboard_class => class
dashboard_student => student
dashboard_studentclass => studentclass
dashboard_attendance => attendance
dashboard_financialtransaction => financialtransaction

dashboard_tuitionplan
dashboard_discount
'''


import pandas as pd


# This function will read all the tables from the Excel file and convert them to a dictionary
def import_excel(excel_file):
    # Read all sheets of the excel file and store them in a dictionary of dataframes
    xls = pd.ExcelFile(excel_file)
    df_dict = {}
    for sheet_name in xls.sheet_names:
        df_dict[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)
    return df_dict

# Gen8 db excel file
gen8_excel_file = 'excel_db/gen8db_2024_04_21.xlsx'
gen8_dict = import_excel(gen8_excel_file)

# Mycennter db excel file
mycenter_dict = {}


# CONVERT EACH TABLE

# SCHOOL
transformed_data = {
    'id': [1],
    'name': ['Gen8 Long Hải'],
    'description': [''],
    'image': ['images/default/default_school.webp'],
    'created_at': ['2024-02-26 15:17:03']
}

# Create DataFrame
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['school'] = df_transformed

#SCHOOL USER
transformed_data = {
    'id': [1, 2, 3, 4, 5, 6],
    'school_id': [1, 1, 1, 1, 1, 1],
    'user_id': [1, 2, 3, 4, 5, 6]
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['schooluser'] = df_transformed

# USER
df_gen8 = gen8_dict['auth_user']
transformed_data = {
    'id': df_gen8['id'],    
    'password': df_gen8['password'],
    'last_login': df_gen8['last_login'],
    'is_superuser': df_gen8['is_superuser'],
    'username': df_gen8['username'],
    'first_name': df_gen8['first_name'],
    'last_name': df_gen8['last_name'],
    'email': df_gen8['email'],
    'is_staff': df_gen8['is_staff'],
    'is_active': df_gen8['is_active'],
    'date_joined': df_gen8['date_joined'],
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['auth_user'] = df_transformed

# CLASS
# Transforming data from gen8 class to match the structure of mycenter class
df_gen8 = gen8_dict['dashboard_class']
transformed_data = {
    'id': df_gen8['id'],
    'secondary_id': df_gen8['id'],
    'name': df_gen8['name'],
    'image': df_gen8['image'],
    'note': df_gen8['note'],
    'price_per_hour': 46153,  # Assigning a fixed value
    'created_at': pd.to_datetime(df_gen8['create_date']),  # Converting to datetime
    'school_id': 1  # Assigning a fixed value
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['class'] = df_transformed

# STUDENT
df_gen8 = gen8_dict['dashboard_student']
transformed_data = {
    'id': df_gen8['id'],
    'secondary_id': df_gen8['id'],
    'name': df_gen8['name'],
    'gender': df_gen8['gender'],
    'date_of_birth': pd.to_datetime(df_gen8['date_of_birth']),
    'parents': df_gen8['parents'],
    'phones': df_gen8['phone'],
    'status': df_gen8['status'],  # Assuming the status directly maps to the new status field
    'reward_points': df_gen8['money'],  # Assuming a fixed value for all entries
    'balance': 0,  # Assuming a fixed value for all entries
    'image': df_gen8['image'],
    'created_at': pd.to_datetime(df_gen8['create_date']),
    'note': df_gen8['note'],
    'school_id': 1  # Assuming a fixed school_id for all entries
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['student'] = df_transformed


# STUDENT CLASS
df_gen8 = gen8_dict['dashboard_studentclass']
transformed_data = {
    'id': df_gen8['id'],
    'is_payment_required': df_gen8['is_paid_class'],
    '_class_id': df_gen8['_class_id'],
    'student_id': df_gen8['student_id'],
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['studentclass'] = df_transformed



# ATTENDANCE
df_gen8 = gen8_dict['dashboard_attendance']
transformed_data = {
    'id': df_gen8['id'],
    'check_date': pd.to_datetime(df_gen8['check_date']),
    'status': df_gen8['status'],
    'learning_hours': df_gen8['learning_hours'],
    'note': df_gen8['note'],
    'created_at': pd.to_datetime(df_gen8['create_date']),
    'check_class_id': df_gen8['check_class_id'],
    'student_id': df_gen8['student_id'],
    'is_payment_required': df_gen8['is_paid_class'],
    'price_per_hour': 46153,  # Assuming a fixed value
    'school_id': 1  # Assuming a fixed school_id for all entries
}
df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['attendance'] = df_transformed





# FINANCIAL TRANSACTION
df_gen8 = gen8_dict['dashboard_financialtransaction']
converted_balance_data = {
    "Miễn phí trọn đời": 100000000,
    "HP cũ - Tiểu học trở lên - quý (1 triệu 300 nghìn)": 1800000,
    "HP cũ - Mầm non - quý (1 triệu 400 nghìn)": 1800000,
    "HP cũ - Tiểu học trở lên - tháng - hỗ trợ (400 ngàn)": 600000,
    "HP cũ - Tiểu học trở lên - tháng (450 ngàn)": 600000,
    "HP cũ - Tiểu học trở lên - tháng - siêu hỗ trợ (100 ngàn)": 600000,
    "Tiểu học trở lên - năm (5 triệu 640 nghìn)": 7200000,
    "Mầm non - quý (1 triệu 950 nghìn)": 1800000,
    "Tiểu học trở lên - nửa năm (3 triệu 240 nghìn)": 3600000,
    "Bù 1 buổi": 69231,
    "Bù 2 buổi": 138462,
    "Bù 5 buổi": 346155,
    "Tiểu học trở lên - tháng (720 nghìn)": 600000,
    "Mầm non - năm (5 triệu 980 nghìn)": 7200000,
    "Tiểu học trở lên - quý (1 triệu 800 nghìn)": 1800000,
    "Tiểu học trở lên - năm (5 triệu 640 nghìn)": 7200000,
    "Bù 8 buổi": 553848,
    "Bù 6 buổi": 415386,
    "Bù 3 buổi": 207693
}

transformed_data = {
    'id': df_gen8['id'],
    'secondary_id': df_gen8['id'],
    'income_or_expense': df_gen8['income_or_expense'],
    'transaction_type': df_gen8['transaction_type'],
    'giver': df_gen8['giver'],
    'receiver': df_gen8['receiver'],
    'amount': df_gen8['amount'],
    'note': df_gen8['note'],
    'created_at': pd.to_datetime(df_gen8['create_date']),
    'student_id': df_gen8['student_id'],
    'school_id': 1  # Assuming a fixed school_id for all entries

}

# get the discount % from the discount table
df_discount = gen8_dict['dashboard_discount']
df_discount = df_discount.set_index('id')
discount_dict = df_discount.to_dict()
discount_dict = discount_dict['name']
transformed_data['legacy_discount'] = df_gen8['discount_id'].map(discount_dict)

# get the tuition plan price from the tuition plan table
df_plan = gen8_dict['dashboard_tuitionplan']
df_plan = df_plan.set_index('id')
plan_dict = df_plan.to_dict()
plan_dict = plan_dict['plan']
transformed_data['legacy_tuition_plan'] = df_gen8['tuition_plan_id'].map(plan_dict)

# get the student_balance_increase from the balance table, the keys are legacy_tuition_plan
# Map student_balance_increase using converted_balance_data
transformed_data['student_balance_increase'] = transformed_data['legacy_tuition_plan'].map(converted_balance_data)
transformed_data['bonus'] = 0

df_transformed = pd.DataFrame(transformed_data)
mycenter_dict['financialtransaction'] = df_transformed

# Save the transformed data to a new excel file
with pd.ExcelWriter(gen8_excel_file.replace('gen8db', 'mycenter_db')) as writer:
    for sheet_name, df in mycenter_dict.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)


print("all done")