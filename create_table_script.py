from db.db_helper import DBHelper
from util import *

dbHelper = DBHelper(db_name='global.db')
create_sensor_table(dbHelper)

dbHelper = DBHelper(db_name='fog.db')
create_sensor_table(dbHelper)
