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
            if pd.Timestamp(Input_date) in sale_dates.values:
                return True
            else:
                return False
        except Exception as e:
            return None

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
                    'available_stock': required_data['available_stock'] - int(dictionary["total_cans"]),
                    'available_empties': (required_data['available_empties'] + int(dictionary['wholesale_Retail_jars_return']) + int(dictionary['e_commerece_empty_return'])) - (int(dictionary["online_deposites"]) + int(dictionary["retail_deposites"])),
                    'available_amount': required_data['available_amount'] + int(dictionary["final_payment"]),
                    'On_hold_amount': required_data['On_hold_amount'] + int(dictionary["On_hold_amount"]) - int(dictionary["received_on_hold_amount"]),
                    'e_commerce': required_data['e_commerce'] + int(dictionary["E-commerce_amount"]),
                    'Total_Expensives': required_data['Total_Expensives'] + int(dictionary["expenses"])}
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
            else:
                print("Request out of bound!")
        except Exception as e:
            print(f"An error occurred while updating data: {e}")
            return False

    @staticmethod
    def create_update_json(old_data, new_data, information):
        try:
            update_dict = {key: {'old_value': old_data.get(key), 'new_value': new_data.get(key, {})} for key in new_data}
            my_dict = {f"{k}_{change_type}_value": v.get(change_type+'_value', '') for k, v in update_dict.items() for change_type in ['old', 'new']}
            my_dict.update(transaction_id=information['transaction_id'], reason = information['reason'], time=support_functions.supporter.get_india_datetime()[0], date=support_functions.supporter.get_india_datetime()[1])
            log_updater = Database.sheets_data_updater(my_dict, 'Bisleri_sales', 'Sheet3', 'Updating_transaction_record')
            if log_updater:
                return True
        except Exception as e:
            print(f"Error occurred while creating or updating JSON: {e}")
            return False

