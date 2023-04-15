def create_sensor_table(dbHelper):
    sql = '''
    CREATE TABLE sensor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    devicename CHAR(5) NOT NULL,
    abright INTEGER NOT NULL,
    atemp REAL NOT NULL,
    ahum REAL NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    is_relayed INTEGER DEFAULT 0 NOT NULL
    );
    '''
    dbHelper.execute(sql)
