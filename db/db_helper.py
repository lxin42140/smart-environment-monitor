import sqlite3


class SensorData:

    def __init__(self, data) -> None:
        self.id = data[0]
        self.devicename = data[1]
        self.abright = data[2]
        self.atemp = data[3]
        self.ahum = data[4]
        self.timestamp = data[5]
        self.is_relayed = data[6]

    def to_dict(self):
        return {
            'id': self.id,
            'devicename': self.devicename,
            'abright': self.abright,
            'atemp': self.atemp,
            'ahum': self.ahum,
            'timestamp': str(self.timestamp),
            "is_relayed": self.is_relayed
        }


class DBHelper:

    def __init__(self, db_name) -> None:
        self.db_name = db_name

    def __connect__(self):
        try:
            self.con = sqlite3.connect(self.db_name)
            self.cur = self.con.cursor()
        except Exception as e:
            print("Exception occurred:{}".format(e))

    def __disconnect__(self):
        self.con.close()
        self.cur = None

    def execute(self, sql) -> None:
        try:
            self.__connect__()
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            print("Exception occurred:{}".format(e))
        finally:
            self.__disconnect__()

    def fetch(self, sql) -> list:
        try:
            self.__connect__()
            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print("Exception occurred:{}".format(e))
        finally:
            self.__disconnect__()

    ############################ READ SENSOR DATA ############################
    def select_all_sensor_readings(self):
        all_sensor_data = self.fetch('select * from sensor order by id desc;')

        return [SensorData(x)
                for x in all_sensor_data] if all_sensor_data else []

    ############################ DATA RELAY ############################
    def select_unrelayed_sensor_data(self) -> list[SensorData]:
        unrelayed_data = self.fetch(
            'select * from sensor where is_relayed = 0 order by id desc;')

        return [SensorData(x)
                for x in unrelayed_data] if unrelayed_data else []

    def update_relayed_sensor_data(self, ids: list[int]) -> None:
        sql = "update sensor set is_relayed = 1 where id in ({});".format(
            ','.join([str(id) for id in ids]))

        self.execute(sql)

    ############################ INSERT DATA ############################
    def insert_sensor_readings(self, data: dict) -> None:
        print("********INSERT SENSOR READINGS...********")

        for key, value in data.items():
            sql = '''
            insert into sensor
            ('devicename', 'abright', 'atemp', 'ahum', 'timestamp')
            values ('{}', {}, {}, {}, datetime('now', 'localtime'))
            '''.format(
                key,
                value[0],  # abright
                value[1],  # atemp
                value[2]  # ahum
            )

            print(sql)
            self.execute(sql)

    def insert_cloud_sensor_readings(self, data: list[dict]):
        print("********INSERT SENSOR READINGS...********")

        for sensor_data in data:
            sql = '''
            insert into sensor
            ('devicename', 'abright', 'atemp', 'ahum', 'timestamp')
            values ('{}', {}, {}, {}, datetime('{}'))
            '''.format(sensor_data['devicename'], sensor_data["abright"],
                       sensor_data["atemp"], sensor_data["ahum"],
                       sensor_data["timestamp"])

            print(sql)
            self.execute(sql)