import logging
import os
from datetime import datetime

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log" #file created with this naming convention
log_path = os.path.join(os.getcwd(),"logs",LOG_FILE) # directory called logs created in which log file is stord
os.makedirs(log_path,exist_ok=True)

LOG_FILE_PATH = os.path.join(log_path,LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format = '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    level = logging.INFO,
)
