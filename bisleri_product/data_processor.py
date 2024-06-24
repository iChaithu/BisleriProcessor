import os, time, pytz, json, gspread, pandas as pd
from google.oauth2.service_account import Credentials
from bisleri_product import support_functions

class Database:
    scope = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    creds_json = json.loads(os.environ['g_creds'])
    creds = creds = Credentials.from_service_account_info(info=creds_json, scopes=scope)
    
    @staticmethod
    def date_validator(input_date):
        try:
            worksheet = gspread.authorize(Database.creds).open('Bisleri_sales').worksheet('Sheet1')
            data = worksheet.get_all_values()
            df  = pd.DataFrame(data[1:], columns=data[0])
            sale_dates = pd.to_datetime(df['sale_date'],format='%d-%m-%Y',errors='coerce')
            Input_date = pd.to_datetime(input_date.get('sale_date', {}),format='%d-%m-%Y',errors='coerce')
            if pd.Timestamp(Input_date) in sale_dates.values:return True
            else:return False
        except Exception as e:return None

    @staticmethod
    def sheets_data_updater(dictionary, sheet_name, sheet_number, task):
        try:
            worksheet = gspread.authorize(Database.creds).open(sheet_name).worksheet(sheet_number)
            if task == 'Updating_sales_data':
                dictionary['transaction_id'] = support_functions.supporter.transaction_id_generator()
                worksheet.append_row(list(dictionary.values()))
                return True   
            elif task == 'Update_Stock_Finance':
                data = worksheet.get_all_values()
                required_data = {data[0][i]: int(row[i]) for i in range(len(data[0])) for row in data[1:]}
                updated_data = {
                    'available_stock': required_data['available_stock'] - ( int(dictionary["total_cans"]) + int(dictionary["Damage"])),
                    'available_empties': (required_data['available_empties'] + int(dictionary['wholesale_Retail_jars_return']) + int(dictionary["total_cans"]) + int(dictionary['e_commerece_empty_return'])) - (int(dictionary["online_deposites"]) + int(dictionary["retail_deposites"])),
                    'available_amount': required_data['available_amount'] + int(dictionary["final_payment"]),
                    'On_hold_amount': required_data['On_hold_amount'] + int(dictionary["On_hold_amount"]) - int(dictionary["received_on_hold_amount"]),
                    'e_commerce': required_data['e_commerce'] + int(dictionary["E-commerce_amount"]),
                    'Total_Expensives': required_data['Total_Expensives'] + int(dictionary["expenses"]),
                    'Deposit': required_data['Deposit'],
                    'Damage' : required_data['Damage'] + int(dictionary["Damage"])}
                dictionary['reason']="sales_data_updated"
                log_creater = Database.create_update_json(required_data, updated_data, dictionary)
                if log_creater:
                    for i in updated_data.keys():
                        column_index = worksheet.find(i).col
                        worksheet.update_cell(2, column_index, updated_data[i])
                    return True 
                else:
                    print("Log creater declined to work further ") 
            elif task == 'Updating_transaction_record':
                worksheet.append_row(list(dictionary.values()))
                return True
            elif task == 'Stock_data_update':
                data = worksheet.get_all_values()
                required_data = {data[0][i]: int(row[i]) for i in range(len(data[0])) for row in data[1:]}
                updated_data = {
                'available_stock': required_data.get('available_stock', 0) + int(dictionary.get("STOCK", 0)),
                'available_empties': required_data.get('available_empties', 0) - int(dictionary.get("EMPTIES", 0)) + int(dictionary.get("DEPOSIT", 0)),
                'Deposit': required_data.get('Deposit',0) + int(dictionary.get("DEPOSIT", 0)),
                'Damage': required_data.get('Damage',0) - int(dictionary.get("DAMAGE RETURN", 0)),
                'e_commerce': required_data.get('e_commerce', 0) + (int(dictionary.get("DAMAGE RETURN", 0)) * 61)}
                dictionary['transaction_id'] = support_functions.supporter.transaction_id_generator()
                dictionary['reason'] = task
                for i in updated_data.keys():
                    column_index = worksheet.find(i).col
                    worksheet.update_cell(2, column_index, updated_data[i])  
                data = worksheet.get_all_values()
                updated_dataa = {data[0][i]: int(row[i]) for i in range(len(data[0])) for row in data[1:]}  
                log_creater = Database.create_update_json(required_data, updated_dataa, dictionary)
                if log_creater:return True
            elif task == "Finance_data_update":
                data = worksheet.get_all_values()
                required_data = {data[0][i]: int(row[i]) for i in range(len(data[0])) for row in data[1:]}
                new_dict = {dictionary['column']: required_data[dictionary['column']] - int(dictionary['variable'])}
                column_index = worksheet.find(dictionary['column']).col
                worksheet.update_cell(2, column_index,new_dict[dictionary['column']])
                dictionary['transaction_id'] = support_functions.supporter.transaction_id_generator()
                data = worksheet.get_all_values()
                updated_dataa = {data[0][i]: int(row[i]) for i in range(len(data[0])) for row in data[1:]}
                log_creater = Database.create_update_json(required_data, updated_dataa, dictionary)
                if log_creater:return True
            else:print("Request out of bound!");return False
        except Exception as e:print(f"An error occurred while updating data: {e}");return False

    @staticmethod
    def create_update_json(old_data, new_data, information):
        try:
            update_dict = {key: {'old_value': old_data.get(key), 'new_value': new_data.get(key, {})} for key in new_data}
            my_dict = {f"{k}_{change_type}_value": v.get(change_type+'_value', '') for k, v in update_dict.items() for change_type in ['old', 'new']}
            my_dict.update(transaction_id=information['transaction_id'], reason = information['reason'], time=support_functions.supporter.get_india_datetime()[0], date=support_functions.supporter.get_india_datetime()[1])
            if Database.sheets_data_updater(my_dict, 'Bisleri_sales', 'Sheet3', 'Updating_transaction_record'): return True
        except Exception as e:print(f"Error occurred while creating or updating JSON: {e}");return False

    def sales_viewer(date):
        try:
            worksheet = gspread.authorize(Database.creds).open('Bisleri_sales').worksheet('Sheet1')
            df = pd.DataFrame(worksheet.get_all_values()[1:], columns=worksheet.get_all_values()[0])
            df['sale_date'] = pd.to_datetime(df['sale_date'], format='%d-%m-%Y', errors='coerce')         
            start_date = pd.to_datetime(date['starting_date'], format='%d-%m-%Y', errors='coerce')
            end_date = pd.to_datetime(date['Ending_date'], format='%d-%m-%Y', errors='coerce')                
            filtered_df = df[(df['sale_date'] >= start_date) & (df['sale_date'] <= end_date)]
            quote = {"Recived Total sale": filtered_df['final_payment'].astype(int).sum(),
            "Calculated amount": filtered_df['calculated_received_amount'].astype(int).sum(),
            "Total Expensives": filtered_df['expenses'].astype(int).sum(),
            "Total E- Comm": filtered_df['E-commerce_amount'].astype(int).sum(),
            "Total cans": filtered_df['total_cans'].astype(int).sum(),
            "Total Deposit Cans": (filtered_df['online_deposites'].astype(int).sum() + filtered_df['retail_deposites'].astype(int).sum() + filtered_df['wholesale_deposite'].astype(int).sum()),
            "Total Deposit amount": ((filtered_df['online_deposites'].astype(int).sum() + filtered_df['retail_deposites'].astype(int).sum() + filtered_df['wholesale_deposite'].astype(int).sum()) * 150),
            "Total Jars Return": (filtered_df['e_commerece_empty_return'].astype(int).sum() + filtered_df['wholesale_Retail_jars_return'].astype(int).sum())}
            return quote
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
    