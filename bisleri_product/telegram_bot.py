import os, pytz, telebot
from bisleri_product import data_processor, support_functions
from datetime import datetime
from telebot import types


class BotGadu:
    print("Bisleri Bot on Force...!")
    def __init__(self):
        self.bot = telebot.TeleBot(os.environ['token'])
        
        @self.bot.message_handler(commands=['start'])
        def start(message):
            print(f"Bot working for user First name: {message.from_user.first_name} Last name: {message.from_user.last_name} and ID : {message.chat.id}")
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("Sales Entry Mode"),types.KeyboardButton("Authoriser Mode"),types.KeyboardButton("Menu"))
            user_input = self.bot.reply_to(message, "Hello Amigo! Choose the Option ",reply_markup=markup)
            self.bot.register_next_step_handler(user_input, self.login_processor)
    
    def login_processor(self, user_input):
        if user_input.text == "Sales Entry Mode" or user_input.text == "Authoriser Mode":
            self.bot.send_message(user_input.chat.id,"Enter the Passcode to Proceed")
            self.bot.register_next_step_handler(user_input, self.authorize_user)
        elif user_input.text == "Menu": 
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("Get sales By Date "))
            self.bot.send_message(user_input.chat.id,"Select the Option!",reply_markup=markup)
            self.bot.register_next_step_handler(user_input, self.sales_definer, "take_date_data")
        return
            
    def authorize_user(self, user_input):
        if int(user_input.text) == int(os.environ['sales_enter_password']): 
            self.bot.send_message(user_input.chat.id,"Entered into the sales data entry Mode")
            date = self.bot.send_message(user_input.chat.id,"Please Enter the Date of sales in this format: dd-mm-yyyy (e.g. 02-06-2004)")
            self.bot.register_next_step_handler(date, self.get_date)
            
        elif int(user_input.text) == int(os.environ['Authoriser']): 
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("Update stock"),types.KeyboardButton("Update Finance"))
            handler = self.bot.send_message(user_input.chat.id, "Entered into Authoriser Mode..\n Select an Option",reply_markup=markup)
            self.bot.register_next_step_handler(handler, self.sales_finance_Handler)
            return
        else:
            self.bot.send_message(user_input.chat.id, "Hey! You gone into Else block , Please contact Chaithu for further assistance.")

    def get_date(self, user_input):
        sale_checker = data_processor.Database.date_validator({'sale_date': datetime.strptime(user_input.text, "%d-%m-%Y").date()})
        if sale_checker == True:
            self.bot.send_message(user_input.chat.id, f"The data for the date {user_input.text} already exists.")
            self.bot.send_message(user_input.chat.id, "Click /start to restart and Try Again")
        elif sale_checker == False:
            sales_data = sales_data = {'sale_date': datetime.strptime(user_input.text, "%d-%m-%Y").date().strftime("%d-%m-%Y")}
            off_cans = self.bot.send_message(user_input.chat.id, f"Please enter the Retail sales can(s) count on {user_input.text}.")
            self.bot.register_next_step_handler(off_cans, self.get_retail_sales, sales_data)
        else:
            self.bot.send_message(user_input.chat.id, f"Hey, there seems to be an issue with the database. The error encountered is: {sale_checker}")
        return 
            
    def get_retail_sales(self, user_input, sales_data):
        try:
            retail_can_sales = int(user_input.text)
        except ValueError:
            self.bot.send_message(user_input.chat.id, "Invalid input, please enter a numerical value for Retail can(s) sales, Please /start again here.")
        sales_data['retail_can_sales'] = retail_can_sales
        try:
            online_cans = self.bot.send_message(user_input.chat.id, f" Enter Online Can(s) sales on {sales_data.get('sale_date', {})}")
            self.bot.register_next_step_handler(online_cans, self.get_online_sales, sales_data)
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error: {e} occurred while sending the message for online sales. Please /start again here.")
        return 
    
    def get_online_sales(self, user_input, sales_data):
        try:
            online_can_sales = int(user_input.text)
        except ValueError:
            self.bot.send_message(user_input.chat.id, "Invalid input, please enter a numerical value for Online can(s) sales, Please /start again here.")
        sales_data['online_can_sales'] = online_can_sales
        try:
            whole_sale_cans = self.bot.send_message(user_input.chat.id, f" Enter Wholesale Can(s) sales on {sales_data.get('sale_date', {})}")
            self.bot.register_next_step_handler(whole_sale_cans, self.get_whole_sales, sales_data)
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
    
    def get_whole_sales(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['wholesale_can_sales'] = user_input.text
                online_cans_deposite = self.bot.send_message(user_input.chat.id,f"Enter the Online Can(s) Deposite count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(online_cans_deposite, self.get_online_deposite, sales_data)   
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return   
                
    def get_online_deposite(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['online_deposites'] = user_input.text
                offline_can_deposite = self.bot.send_message(user_input.chat.id,f"Please Enter Retail can(s) deposite on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(offline_can_deposite, self.get_retail_deposite, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
        
    def get_retail_deposite(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['retail_deposites'] = user_input.text
                whole_sale_deposite = self.bot.send_message(user_input.chat.id,f"Enter the Whole sale can(s) deposite count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(whole_sale_deposite, self.get_wholesale_deposite, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return   
        
    def get_wholesale_deposite(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['wholesale_deposite'] = user_input.text
                e_commerece_empty_return = self.bot.send_message(user_input.chat.id, f"Enter E-commerece empty can(s) return count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(e_commerece_empty_return, self.get_online_cans_return, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
        
    def get_online_cans_return(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['e_commerece_empty_return'] = user_input.text
                wholesale_Retail_jars_return = self.bot.send_message(user_input.chat.id, f"Enter Total wholesale and Retail can(s) return count on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(wholesale_Retail_jars_return, self.get_wholesale_retail_cans_return, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
        
    def get_wholesale_retail_cans_return(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['wholesale_Retail_jars_return'] = user_input.text 
                complimentry_cans = self.bot.send_message(user_input.chat.id,f"Enter the Damage can(s) on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(complimentry_cans, self.get_leakage, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
        
    def get_leakage(self, user_input, sales_data):
        try:
            leakage = user_input.text
            if leakage.isnumeric():
                sales_data['Damage'] = leakage
                complimentry_cans = self.bot.send_message(user_input.chat.id,f"Enter the complementry can(s) on {sales_data.get('sale_date', {})}")
                self.bot.register_next_step_handler(complimentry_cans, self.sale_confirmation, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return        
                
        
    def sale_confirmation(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['complimentry_cans'] = user_input.text
                sales_data['total_cans'] = int(sales_data['retail_can_sales']) + int(sales_data['online_can_sales']) + int(sales_data['wholesale_can_sales']) + int(sales_data['complimentry_cans'])
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.add(types.KeyboardButton("Yes"),types.KeyboardButton("No"))
                confirm_total_cans = self.bot.send_message(user_input.chat.id, f"Please confirm that {sales_data['total_cans']} can(s) delivered on {sales_data.get('sale_date', {})} including complementry cans {sales_data.get('complimentry_cans', {})} by pressing Yes",reply_markup=markup)
                self.bot.register_next_step_handler(confirm_total_cans, self.confirm_calculator, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        return
        
    def confirm_calculator(self, user_input, sales_data):
        if user_input.text == 'Yes':
            try:
                sales_data['retail_can_sales_amount'] = (int(sales_data['retail_can_sales']) * 90)
                sales_data['retail_deposite_amount'] = (int(sales_data['retail_deposites']) * 150)
                sales_data['whole_sale_amount'] = (int(sales_data['wholesale_can_sales']) * 75)
                sales_data['whole_sale_deposite_amount'] = (int(sales_data['wholesale_deposite']) * 150)
                sales_data['E-commerce_amount'] = (int(sales_data['online_can_sales']) * 90 + int(sales_data['online_deposites']) * 150)
                sales_data['calculated_received_amount'] = sum([sales_data.get(key, 0) for key in ['retail_can_sales_amount', 'whole_sale_amount', 'retail_deposite_amount', 'whole_sale_deposite_amount',(int(sales_data['complimentry_cans']) * 61)]]) - (int(sales_data.get('wholesale_Retail_jars_return', 0)) * 150  + int(sales_data['e_commerece_empty_return']) * 150)
                amount_message = {'Whole sale Deposit can(s)': sales_data.get('retail_deposites'),
                                'Online deposit can(s)': sales_data['online_deposites'],
                                'E-commerce can(s) return count': sales_data['e_commerece_empty_return'],
                                'Retail and Whole sale Can(s) return count': sales_data['wholesale_Retail_jars_return']}
                self.bot.send_message(user_input.chat.id, '\n'.join([f'{key} : {value}' for key, value in amount_message.items()]))
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.add(types.KeyboardButton("Yes"),types.KeyboardButton("No"))
                amount = self.bot.send_message(user_input.chat.id, "Press Yes to Confirm and Continue",reply_markup=markup)
                self.bot.register_next_step_handler(amount, self.payments_on_hold, sales_data)
            except Exception as e:
                self.bot.send_message(user_input.chat.id, f"Error {e} Occured")
        else:
            self.bot.send_message(user_input.chat.id, 'Invalid input, Click /start to restart')
        return  

    def payments_on_hold(self, user_input, sales_data):
        try:
        	if user_input.text == "Yes":
        		payment_hold = self.bot.send_message(user_input.chat.id,f"Please enter the total payment on hold on {sales_data['sale_date']}")
        		self.bot.register_next_step_handler(payment_hold, self.on_hold_payments_recieved, sales_data)
        	else:
        		self.bot.send_message(user_input.chat.id,"Got into wrong step Click here to restart /start")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"Error {e} Occured")

    def on_hold_payments_recieved(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data["On_hold_amount"] = user_input.text
                on_hold_payment_received = self.bot.send_message(user_input.chat.id, "Please enter the amount of on-hold payments received from previous orders:")
                self.bot.register_next_step_handler(on_hold_payment_received, self.get_expenses, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occured")
            
    def get_expenses(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['received_on_hold_amount'] = user_input.text
                expenses = self.bot.send_message(user_input.chat.id, f"Enter the total Expensives on {sales_data['sale_date']}")
                self.bot.register_next_step_handler(expenses, self.get_received_on_hold_amount, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occured")
        return
    
    def get_received_on_hold_amount(self, user_input, sales_data):
        try:
            if user_input.text.isnumeric():
                sales_data['expenses'] = user_input.text
                sales_data['final_payment'] = (int(sales_data['calculated_received_amount']) + int(sales_data['received_on_hold_amount'])) - (int(sales_data['On_hold_amount']) + int(sales_data['expenses']))
                final_view = {'Expenses for today': sales_data['expenses'],'Amount received for on-hold payments': sales_data.get('received_on_hold_amount'),'Total amount received for sales': sales_data.get('final_payment')}
                self.bot.send_message(user_input.chat.id, '\n'.join([f'{key} : {value}' for key, value in final_view.items()]))
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.add(types.KeyboardButton("Yes"),types.KeyboardButton("No"))
                self.bot.send_message(user_input.chat.id, 'Press Yes to confirm and complete the sales update',reply_markup=markup)
                self.bot.register_next_step_handler(user_input, self.complete_print, sales_data)
            else:
                self.bot.send_message(user_input.chat.id, "Input should be a numeric value. Click /start to restart")
        except Exception as error:
            self.bot.send_message(user_input.chat.id, f"Error {error} Occurred")
 
    def complete_print(self, user_input, sales_data):
        try:
            if user_input.text == "Yes":
                final_text = '\n'.join([f'{key} : {value}' for key, value in sales_data.items()])
                self.bot.send_message(user_input.chat.id, final_text)
                profit = int(sales_data['retail_can_sales']) * 29 + int(sales_data['online_can_sales']) * 29 + int(sales_data['wholesale_can_sales']) * 14
                final_text += f'Profit : {profit}\n'
                self.bot.send_message(5579239229, final_text)
                self.bot.send_message(user_input.chat.id,"Data is updating in the back-end. Please wait for confirmation.")
                db_update_confirmation =  data_processor.Database.sheets_data_updater(sales_data,'Bisleri_sales', 'Sheet1', 'Updating_sales_data')
                if db_update_confirmation == True:
                    self.bot.send_message(user_input.chat.id, "Sales data updated successfully.\nNow stock and finance data is updating.")
                    sales_data['reason']="sales_data_updated"
                    checker = data_processor.Database.sheets_data_updater(sales_data, 'Bisleri_sales', 'Sheet2','Update_Stock_Finance')
                    if checker == True:
                        self.bot.send_message(user_input.chat.id, "Stock and Finance Data Updated Sucessfully\n /start ")
                    else:
                        self.bot.send_message(user_input.chat.id, "Error Ocured while Updating the stock and finance and the error")       
                    return 
                else:
                    self.bot.send_message(user_input.chat.id, f"Data Unable to Update Sucessfully due to this error {db_update_confirmation}.")      
            else:
                self.bot.send_message(user_input.chat.id, "Data updating failed. Please try again by pressing /start.")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error {e} occurred while processing your request.Please try again by pressing /start.")

    def sales_finance_Handler(self, user_input):
        if user_input.text == "Update stock":
            user_input = self.bot.send_message(user_input.chat.id, support_functions.Questions.stock_questions[1][0])
            self.bot.register_next_step_handler(user_input, self.stock_data, count = 1)
            return
        elif user_input.text == "Update Finance":
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("deduct available amount"),types.KeyboardButton("ecommerce amount received"),types.KeyboardButton("deduct on_hold amount"),types.KeyboardButton("deduct expenses"),types.KeyboardButton("deduct Deposit"))
            user_input = self.bot.send_message(user_input.chat.id, 'Choose an Option to update the data in the DataBase', reply_markup=markup)
            self.bot.register_next_step_handler(user_input, self.Finance_data)
            return 
        
    def stock_data(self, user_input, count=None, stock_data=None):
        if stock_data is None:
            stock_data = {}
            
        if count and count < len(support_functions.Questions.stock_questions) + 1:
            stock_data[support_functions.Questions.stock_questions[count][1]] = user_input.text
            count = count + 1
            if count < len(support_functions.Questions.stock_questions) + 1:
                user_input = self.bot.send_message(user_input.chat.id, support_functions.Questions.stock_questions[count][0])
                self.bot.register_next_step_handler(user_input, self.stock_data, count, stock_data)
            else:
                message_text = ""
                for item, key in stock_data.items():
                    message_text += f'{item} : {key}\n'
                message_text += "Press Yes to confirm the stock data and Update the Database"
                markup = types.ReplyKeyboardMarkup(row_width=2)
                markup.add(types.KeyboardButton("Yes"),types.KeyboardButton("No"))
                self.bot.send_message(user_input.chat.id, message_text, reply_markup=markup)
                self.bot.register_next_step_handler(user_input, self.db_data_updater, dict = {'data': stock_data, 'mode': 'Stock_data_update'})
        else:
            print('Request Out of bound')
        return
        
    def Finance_data(self, user_input, confirmer=False, variable=None, reason=False,my_dict= None ):
        if reason and variable:
            my_dict = {}
            my_dict['variable'] = user_input.text
            my_dict['column'] = variable
            user_input = self.bot.send_message(user_input.chat.id, "Please Enter the reason for this Transaction Update")
            self.bot.register_next_step_handler(user_input, self.Finance_data, True, variable, False, my_dict) 
        if confirmer:
            my_dict['reason'] = user_input.text 
            markup = types.ReplyKeyboardMarkup(row_width=2)
            markup.add(types.KeyboardButton("Yes"), types.KeyboardButton("No"))
            user_input = self.bot.send_message(user_input.chat.id, "Press Yes to Confirm the Transaction", reply_markup=markup)
            self.bot.register_next_step_handler(user_input, self.db_data_updater, dict ={'data': my_dict, 'mode': 'Finance_data_update'})
            return
        else:
            if user_input.text in support_functions.Questions.finance_questions:
                variable = support_functions.Questions.finance_questions[user_input.text][1]
                user_input = self.bot.send_message(user_input.chat.id, support_functions.Questions.finance_questions[user_input.text][0])
                self.bot.register_next_step_handler(user_input, self.Finance_data, False, variable, True)

    def db_data_updater(self, user_input, dict):
        if user_input.text == "Yes":
            if dict['mode'] == 'Stock_data_update':
                self.bot.send_message(user_input.chat.id, "Kindly hold on while the data is being updated.")
                confirmer = data_processor.Database.sheets_data_updater(dict['data'],'Bisleri_sales','Sheet2',dict['mode'])
                if confirmer:
                    self.bot.send_message(user_input.chat.id, "Data Updated!") 
                    return
            elif dict['mode'] == 'Finance_data_update':
                self.bot.send_message(user_input.chat.id, "Kindly hold on while the data is being updated.")
                confirmer = data_processor.Database.sheets_data_updater(dict['data'],'Bisleri_sales','Sheet2',dict['mode'])
                if confirmer:
                    self.bot.send_message(user_input.chat.id, "Data Updated!")  
                    return  

    def sales_definer(self, user_input, mode, date=None):
        try:
            if mode == "take_date_data":
                user_input = self.bot.send_message(user_input.chat.id, "Kindly provide the starting date for the sales data you need in the following format: dd-mm-yyyy (e.g., 02-06-2004).")
                self.bot.register_next_step_handler(user_input, self.sales_definer, "take_end_date_data")
            elif mode == "take_end_date_data":
                date = dict()
                date['starting_date'] = datetime.strptime(user_input.text, "%d-%m-%Y").date()
                user_input = self.bot.send_message(user_input.chat.id, "Kindly provide the Ending date for the sales data you need in the following format: dd-mm-yyyy (e.g., 02-06-2004).")
                self.bot.register_next_step_handler(user_input, self.sales_definer, "get_required_data", date)
            elif mode == "get_required_data":
                if date:
                    date['Ending_date'] = datetime.strptime(user_input.text, "%d-%m-%Y").date()
                    self.bot.send_message(user_input.chat.id, "Kindly wait while the bot is calculating the data.")
                    confirmer = data_processor.Database.sales_viewer(date)
                    if confirmer:
                        self.bot.send_message(user_input.chat.id, '\n'.join([f'{key} : {value}' for key, value in confirmer.items()]))
                        self.bot.send_message(user_input.chat.id, "Restart the Bot here > /start <")
                    else:
                        self.bot.send_message(user_input.chat.id, "There was an issue processing the data. Please try again or Contact ChaithU.")
        except Exception as e:
            self.bot.send_message(user_input.chat.id, f"An error occurred: {str(e)}")
        return

    def run(self):
        self.bot.infinity_polling()





