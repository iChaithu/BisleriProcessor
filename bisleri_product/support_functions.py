from datetime import datetime
import random ,pytz



class supporter:
    #get_indian time as time and date 
    get_india_datetime = lambda: (datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M:%S'), datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y'))
    
    #transaction_id_generator
    transaction_id_generator = lambda: f"{int(datetime.now().timestamp())}-{random.randint(1, 100000)}"