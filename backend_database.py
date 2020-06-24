#Data base code for SearchEngine Using SQL Alchemy and PostgreSQL


from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float, Sequence, sql, DateTime
import csv
from zipfile import ZipFile
import os
from time import gmtime, strftime
import logging
import statistics
# Global Variables
SQLITE = 'sqlite'
POSTGRES = 'postgres'

# Table Names
USERS = 'users'
ADDRESSES = 'addresses'
SENSORS = 'sensors'
MAIN = 'main'
BLACKLIST = "blacklist"




class MyDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
        POSTGRES: 'postgres://postgres:fortinet@localhost/{DB}'
        #POSTGRES: 'postgres://postgres:fortinet@10.6.108.72:5432/{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None
    def __init__(self, dbtype, dbname=''):
        dbtype = dbtype.lower()
       
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            logging.error("DBType is not found in DB_ENGINE")

    # Create different table base on the sensor
    def create_sensor_table(self,sensor_name):
        metadata = MetaData()
        Table(sensor_name, metadata,
            Column('id',Integer, primary_key=True),
            Column('serial_number', String),
            Column('test_date', DateTime),
            Column('test_type', String),
            Column('line_number',Integer),
            Column('alarm', Float),
            Column('reading', Float),
            Column('ref_line_number', Integer)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, sensor_name):
                metadata.create_all(self.db_engine)
                logging.info("Sensor: {} Table created".format(sensor_name))
            else:
                logging.info("Sensor: {} Table already exists".format(sensor_name))
        except Exception as e:
            logging.error("Error occurred during Sensor Table creation!")
            logging.error(str(e))


    #Create different table base on blacklist
    def create_blacklist_table(self,blacklist_name):
        metadata = MetaData()
        Table(blacklist_name, metadata,
            Column('id', Integer, primary_key=True),
            Column('serial_number', String),
            Column('test_date', DateTime),
            Column('test_type', String),
            Column('line_number',Integer),
            Column('reading', String),
            Column('in_log', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, blacklist_name):
                metadata.create_all(self.db_engine)
                logging.info("BlackList Keyword: {} Table created".format(blacklist_name))
            else:
                logging.warning("BlackList Keyword: {} Table already exists".format(blacklist_name))
        except Exception as e:
            logging.error("Error occurred during BlackList Keyword Table creation!")
            logging.error(str(e))

    #Create a table that the graph is going to  base off with
    def create_graph_table(self,sensor_name):
        metadata = MetaData()
        sensor_name = sensor_name+"_graph"
        Table(sensor_name, metadata,
            Column('id',Integer, primary_key=True),
            Column('interval', String),
            Column('count', Integer),
            Column('unit', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, sensor_name):
                metadata.create_all(self.db_engine)
                logging.info("Sensor Interval: {} Table created".format(sensor_name))
            else:
                logging.warning("Sensor Interval: {} Table already exists, table will be overwritten".format(sensor_name))
                query = "DROP TABLE \"{}\";".format(sensor_name)
                self.execute_query(query)
                query = "DELETE FROM \"main_sensor_graph\" WHERE table_name = \'{}\';".format(sensor_name)
                self.execute_query(query)
                metadata.create_all(self.db_engine)
        except Exception as e:
            logging.error("Error occurred during Sensor Interval Table creation!")
            logging.error(str(e))

    #The main table keep tracks of all the graph table
    def create_main_graph_table(self):
        metadata = MetaData()
        Table("main_sensor_graph", metadata,
            Column('id',Integer, primary_key=True),
            Column('table_name', String),
            Column('start_graph', Float),
            Column('end_graph', Float),
            Column('interval', Float)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, "main_sensor_graph"):
                metadata.create_all(self.db_engine)
                logging.info("Main Sensor Interval: {} Table created".format("main_sensor_graph"))
            else:
                logging.warning("Main Sensor Interval: {} Table already exists".format("main_sensor_graph"))

        except Exception as e:
            logging.error("Error occurred during Main Sensor Interval Table creation!")
            logging.error(str(e))

    def create_main_vs_graph_table(self):
        metadata = MetaData()
        Table("main_vs_graph", metadata,
            Column('id',Integer, primary_key=True),
            Column('table_name', String),
            Column('sensor_x', String),
            Column('sensor_y', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, "main_vs_graph"):
                metadata.create_all(self.db_engine)
                logging.info("Main VS Sensor: {} Table created".format("main_vs_graph"))
            else:
                logging.warning("Main VS Sensor: {} Table already exists".format("main_vs_graph"))

        except Exception as e:
            logging.error("Error occurred during Main Sensor Interval Table creation!")
            logging.error(str(e))


    #Insert SN info if the SN has the blacklist keyword
    def blacklist_insert(self, table_name, serial_number='', test_date='', test_type='', line_number='', reading='', in_log=''):
        # Insert Data
        blacklist_dict = {'serial_number':serial_number, 'test_date':test_date, 'test_type':test_type, 'line_number':line_number, 'reading':reading, 'in_log':in_log}
        t_c = [x for x in blacklist_dict.keys() if blacklist_dict[x] != '']
        t_d = ["'" + str(x) + "'" for x in blacklist_dict.values() if x != '']
        query = "INSERT INTO \"{}\"({}) VALUES ({});".format(table_name,",".join(t_c),",".join(t_d))
        self.execute_query(query)




    # Insert, Update, Delete
    def execute_query(self, query=''):
        if query == '': return
        logging.info(query)

        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                logging.error(str(e))


    def sensor_insert(self,table_name, serial_number='', test_date='', test_type='', line_number='', alarm='', reading='', ref_line_number=''):
        # Insert Data
        if reading == None:
            sensor_dict = {'serial_number':serial_number, 'test_date':test_date, 'test_type':test_type, 'line_number':line_number, 'alarm':alarm, 'ref_line_number':ref_line_number}
        else:
            sensor_dict = {'serial_number':serial_number, 'test_date':test_date, 'test_type':test_type, 'line_number':line_number, 'alarm':alarm, 'reading':reading, 'ref_line_number':ref_line_number}


        t_c = [x for x in sensor_dict.keys() if sensor_dict[x] != '']
        t_d = ["'"+str(x)+"'" for x in sensor_dict.values() if x != '']

        query = "INSERT INTO \"{}\"({}) VALUES ({});".format(table_name,",".join(t_c),",".join(t_d))
        self.execute_query(query)

    def sensor_interval_insert(self, table_name, interval='',count='',unit=''):
        # Insert Data

        query = "INSERT INTO \"{}\" (interval, count, unit) VALUES ('{}',{},'{}');".format(table_name, interval, count,unit)
        self.execute_query(query)

    def main_sensor_graph_insert(self, table_name,start_graph ='', end_graph = '', interval='' ):
        # Insert Data

        query = "INSERT INTO \"main_sensor_graph\" (table_name, start_graph, end_graph, interval) VALUES ('{}',{}, {}, {});".format(table_name, start_graph, end_graph, interval)
        self.execute_query(query)


    def main_sensor_graph_update(self, table_name,start_graph ='', end_graph = '', interval='' ):
        # Update Data
        query = "UPDATE \"main_sensor_graph\" set start_graph={}, end_graph={}, interval={} WHERE table_name = '{}';".format(start_graph, end_graph, interval, table_name)
        self.execute_query(query)


    def return_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM \"{}\";".format(table)
        logging.info(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:

               logging.info(str(e))
            else:
                processed_result = [row for row in result]
                result.close()
                return (processed_result)

    def query_return_all_data(self,query=''):


        logging.info(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
               logging.info(str(e))
            else:

                processed_result = [row for row in result]
                result.close()
                return (processed_result)


    def print_all_data(self,query=''):
        print(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()
                print("\n")

    def return_all_model(self):
        # Sample Query
        query = "SELECT datname FROM pg_database WHERE datname != 'template1' AND datname != 'template0' AND datname != 'postgres'"

        try:
            result = self.db_engine.execute(query)
        except Exception as e:
           logging.error(str(e))
        else:
            processed_result = [row for row in result]
            result.close()
            return(processed_result)

    def return_all_sensor(self,table):

        if self.db_engine.dialect.has_table(self.db_engine, table):
            query = "SELECT sensor_name FROM \"{}\" ".format(table)
            try:
                result = self.db_engine.execute(query)
            except Exception as e:
                logging.error(str(e))
                return["No Table Selected"]
            else:
                processed_result = [row for row in result]
                result.close()
                return(processed_result)
        return ["No Table Selected"]

    def return_all_blacklist(self):

        query = "SELECT name FROM \"main_blacklist\" "
        try:
            result = self.db_engine.execute(query)
        except Exception as e:
            logging.error(str(e))
            return["No Table Selected"]

        processed_result = [row[0] for row in result]
        result.close()

        return(processed_result)


    def return_all_sensor_all_model(self):
        # Sample Query
        query = "select sensor_name from \"sensor_to_unit\" ORDER BY sensor_name"

        try:
            result = self.db_engine.execute(query)
        except Exception as e:
            logging.error(str(e))
            return["No Table Selected"]
        else:
            processed_result = [row for row in result]
            result.close()
            return(processed_result)



    def blacklist_query(self,q_blacklist=''):
        # Sample Query
        if q_blacklist:
            query = "SELECT * FROM \"{}\" WHERE name=\'{}\'".format(BLACKLIST,q_blacklist)
        else:
            query = "SELECT name FROM \"{}\" ".format(BLACKLIST)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
               logging.error(str(e))
            else:
                processed_result = [row for row in result]
                result.close()
                return(processed_result)

    def return_column_names(self, q_table):
        return ["".join(x) for x in self.query_return_all_data("SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = '{}';".format(q_table))]

    def return_list_of_views(self):
        return ["".join(x) for x in self.query_return_all_data("SELECT table_name FROM INFORMATION_SCHEMA.views WHERE table_schema = ANY (current_schemas(false));")]

    def return_list_of_graph(self):
        return ["".join(x) for x in self.query_return_all_data("SELECT table_name FROM \"main_sensor_graph\"")]

    def return_error_count(self, table):
        for x in self.query_return_all_data("SELECT COUNT (*) FROM (SELECT DISTINCT serial_number, test_date, test_type FROM \"{}\" WHERE in_log = 'True') as \"Dummy\"".format(table)):
            return int(list(x)[0])

    def return_sensor_max(self, table):
        for x in self.query_return_all_data("SELECT MAX(reading) FROM \"{}\"".format(table)):
            return float(list(x)[0])

    def return_sensor_min(self, table):
        for x in self.query_return_all_data("SELECT MIN(reading) FROM \"{}\"".format(table)):
            return float(list(x)[0])




    def return_unit(self, sensor):

        query = "SELECT unit FROM \"{}\" WHERE sensor_name = '{}'".format("sensor_to_unit", sensor)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
               logging.error(str(e))
            else:
                processed_result = ["".join(row) for row in result]
                result.close()
                return (processed_result[0])

    def return_unit_from_graph(self, sensor):
        try:
            return ["".join(str(x[0])) for x in self.query_return_all_data("SELECT DISTINCT (unit) from \"{}\"".format(sensor))][0]
        except:
            return []

    def return_sensor_count(self, table, min, max):
        for x in self.query_return_all_data("select COUNT (*) FROM \"{}\" WHERE reading >= {} AND reading < {}".format(table,min,max)):
            return int(list(x)[0])

    def return_graph_column_info(self, column, table_name):
        for x in self.query_return_all_data("SELECT {} FROM \"main_sensor_graph\" WHERE table_name = '{}'".format(column, table_name)):
            return float(list(x)[0])

    def return_list_of_column(self, table, column):
        try:
            return ["".join(str(x[0])) for x in self.query_return_all_data("SELECT {} FROM \"{}\"".format(column, table))]
        except TypeError as e:
           logging.error(str(e))

    def return_total_count(self, table):
        for x in self.query_return_all_data("select SUM (count) FROM \"{}\" ".format(table)):
            return int(list(x)[0])

    def return_test_type(self):

        try:
            for x in self.query_return_all_data("select sensor_name from \"sensor_to_unit\" LIMIT 1 "):
                table = (str(list(x)[0]))
            return ["".join(str(x[0])) for x in self.query_return_all_data("SELECT DISTINCT (test_type) from \"{}\"".format(table))]
        except:
            return []

    def return_error_count_cond(self, table, count,model):

        if model == "All":
            for x in self.query_return_all_data(
                    "SELECT COUNT(*) FROM (select serial_number, COUNT(reading) as mycount from \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type HAVING COUNT(reading) = {}) as \"Dummy\"".format(
                            table, count)):
                return int(list(x)[0])

        else:
            for x in self.query_return_all_data(
                    "SELECT COUNT(*) FROM (select serial_number, COUNT(reading) as mycount from \"{}\" WHERE in_log = 'True' AND serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type HAVING COUNT(reading) = {}) as \"Dummy\"".format(
                            table, model, count)):
                return int(list(x)[0])




        for x in self.query_return_all_data("SELECT COUNT(*) FROM (select serial_number, COUNT(reading) as mycount from \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type HAVING COUNT(reading) = {}) as \"Dummy\"".format(table, count)):
            return int(list(x)[0])



    def return_sn_count_cond(self, table, model):
        if model == "All":
            query = "SELECT COUNT (*) FROM (select serial_number from \"{}\" GROUP BY serial_number, test_date, test_type) AS \"Dummy\"".format(
                table)

        else:
            query = "SELECT COUNT (*) FROM (select serial_number from \"{}\" WHERE serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type) AS \"Dummy\"".format(
                table, model)


        for x in self.query_return_all_data(query):
            return int(list(x)[0])

    @classmethod
    def to_csv(cls,tables):

        model_list = [x[:6] for x in tables]


        for idx, table in enumerate(tables):
            temp_dbms = MyDatabase(POSTGRES, dbname=model_list[idx])
            result = temp_dbms.return_all_data(table)
            with open('{}_Summary.csv'.format(table[:-6]),'w') as out:
                field_names = temp_dbms.return_column_names(table)
                csv_out = csv.DictWriter(out,fieldnames=field_names,lineterminator ="\n")
                csv_out.writeheader()
                for row in result:
                    test = dict(zip(field_names,row))
                    csv_out.writerow(test)

        for idx, table in enumerate(tables):
            temp_dbms = MyDatabase(POSTGRES, dbname=model_list[idx])
            result = temp_dbms.return_all_data(table[:-6])
            with open('{}_SerialNumber.csv'.format(table[:-6]),'w') as out:
                field_names = temp_dbms.return_column_names(table[:-6])
                csv_out = csv.DictWriter(out,fieldnames=field_names,lineterminator ="\n")
                csv_out.writeheader()
                for row in result:
                    test = dict(zip(field_names,row))
                    csv_out.writerow(test)


        with ZipFile(strftime("%Y-%m-%d-%H-%M-%S", gmtime())+"_Tables.zip",'w') as zippie:
            for table in tables:
                zippie.write(table[:-6]+"_Summary.csv")
                zippie.write(table[:-6] + "_SerialNumber.csv")
                os.remove(table[:-6] + "_SerialNumber.csv")
                os.remove(table[:-6]+"_Summary.csv")


    def vs_graph_to_csv(self,table):

        result = self.return_all_data(table)
        with open('{}.csv'.format(table),'w') as out:
            field_names = self.return_column_names(table)
            csv_out = csv.DictWriter(out,fieldnames=field_names,lineterminator ="\n")
            csv_out.writeheader()
            for row in result:
                test = dict(zip(field_names,row))
                csv_out.writerow(test)

        with ZipFile(strftime("%Y-%m-%d-%H-%M-%S", gmtime())+"_XY_Tables.zip",'w') as zippie:
            zippie.write(table+".csv")
            os.remove(table+".csv")




    def to_csv_err_filter(self,table, model, low_bound, high_bound):


        if model == "All":
            query = "SELECT serial_number,test_date,test_type, COUNT(reading) AS BLCount FROM \"{}\" WHERE in_log = 'True' GROUP BY serial_number, test_date, test_type HAVING COUNT(reading) >= {} AND COUNT(reading) <= {} ORDER BY serial_number".format(
                table, low_bound, high_bound)

        else:
            query = "SELECT serial_number,test_date,test_type, COUNT(reading) AS BLCount FROM \"{}\" WHERE in_log = 'True' AND serial_number LIKE '{}%%' GROUP BY serial_number, test_date, test_type HAVING COUNT(reading) >= {} AND COUNT(reading) <= {} ORDER BY serial_number".format(
                table, model, low_bound, high_bound)


        result = self.return_all_data(query=query)
        with open('{}.csv'.format(table),'w') as out:
            field_names = ['Serial Number', 'Test Date', 'Test Type', 'BlackListCount per Log']
            csv_out = csv.DictWriter(out,fieldnames=field_names,lineterminator ="\n")
            csv_out.writeheader()
            for row in result:
                test = dict(zip(field_names,row))
                csv_out.writerow(test)
        with ZipFile(strftime("%Y-%m-%d-%H-%M-%S", gmtime())+"_BlackList_Tables.zip",'w') as zippie:
            zippie.write(table+".csv")
            os.remove(table+".csv")



    #Relationship table for Sensor and Unit
    def create_sensor_unit_table(self):
        metadata = MetaData()
        Table("sensor_to_unit", metadata,
            Column('sensor_name',String, primary_key=True),
            Column('unit', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, "sensor_to_unit"):
                metadata.create_all(self.db_engine)
                logging.info("Sensor to Unit Relationship: {} Table created".format("sensor_to_unit"))
            else:
                logging.warning("Sensor to Unit Relationship: {} Table already exists".format("sensor_to_unit"))

        except Exception as e:
            logging.error("Error occurred during Sensor to Unit Relationship Table Creation!")
            logging.error(str(e))

    def sensor_unit_table_insert(self,sensor_name ='', unit = 'Unavailable'):
        # Insert Data

        result = self.query_return_all_data("SELECT sensor_name FROM \"sensor_to_unit\" where sensor_name='{}' ".format(sensor_name))
        if result:
            query = "UPDATE \"sensor_to_unit\" set unit='{}' WHERE sensor_name='{}';".format(unit, sensor_name)
        else:
            query = "INSERT INTO \"sensor_to_unit\" (sensor_name, unit) VALUES ('{}','{}');".format(sensor_name, unit)
        self.execute_query(query)




    def create_model_sensor_info_table(self):
        metadata = MetaData()
        Table("model_sensor_info", metadata,
            Column('model',String, primary_key=True),
            Column('number_of_sensor', Integer),
            Column('sensor_command', String),
            Column('regular_expression', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, "model_sensor_info"):
                metadata.create_all(self.db_engine)
                print("Model Sensor Info: {} Table created".format("model_sensor_info"))
                logging.info("Model Sensor Info: {} Table created".format("model_sensor_info"))
            else:
                print("Model Sensor Info: {} Table already exists".format("model_sensor_info"))
                logging.warning("Model Sensor Info: {} Table already exists".format("model_sensor_info"))

        except Exception as e:
            print("Error occurred during Model Sensor Info Table Creation!")
            print(e)
            logging.error("Error occurred during Model Sensor Info Table Creation!")
            logging.error(str(e))

    def model_sensor_info_insert(self,model='', number_of_sensor=0, sensor_command='Please Enter Data', regular_expression='Please Enter Data'):
        # Insert Data
        result = ""
        for x in self.query_return_all_data("SELECT model FROM \"model_sensor_info\" where model='{}' ".format(model)):
            result = list(x)[0]
        if result:
            #query = "UPDATE \"model_sensor_info\" set number_of_sensor='{}', sensor_command='{}', regular_expression='{}' WHERE model='{}';".format(number_of_sensor, sensor_command, regular_expression,model)
            pass
        else:
            query = "INSERT INTO \"model_sensor_info\" (model, number_of_sensor, sensor_command, regular_expression) VALUES ('{}','{}','{}','{}');".format(model, number_of_sensor, sensor_command, regular_expression)
            self.execute_query(query)


    def model_sensor_info_return(self,model=''):
        # Insert Data
        result = ""
        for x in self.query_return_all_data("SELECT number_of_sensor, sensor_command, regular_expression FROM \"model_sensor_info\" where model='{}' ".format(model)):
            result = list(x)
        return result


    def create_model_table(self,model_name):
        metadata = MetaData()
        Table(model_name, metadata,
            Column('id',Integer, primary_key=True),
            Column('sensor_name', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, model_name):
                metadata.create_all(self.db_engine)
                logging.info("Model: {} Table created".format(model_name))
            else:
                logging.warning("Model: {} Table already exists".format(model_name))
        except Exception as e:
            logging.error("Error occurred during Model Table creation!")
            logging.error(str(e))

    def model_sensor_insert(self,model_table='', sensor_name=''):
        # Insert Data
        result = ""
        try:
            for x in self.query_return_all_data("SELECT sensor_name FROM \"{}\" where sensor_name='{}' ".format(model_table,sensor_name)):
                result = list(x)[0]
            if result:
                #query = "UPDATE \"model_sensor_info\" set number_of_sensor='{}', sensor_command='{}', regular_expression='{}' WHERE model='{}';".format(number_of_sensor, sensor_command, regular_expression,model)
                #print("sensor already exist")
                pass
            else:
                query = "INSERT INTO \"{}\" (sensor_name) VALUES ('{}');".format(model_table,sensor_name)
                self.execute_query(query)
        except:
            print(" {} table not exist".format(model_table))

    def return_sensor_min_max(self, condition, table_name, model, testtype):
        try:
            if condition == "max":
                if testtype == "All":
                    for x in self.query_return_all_data("SELECT MAX(reading) FROM \"{}\" WHERE serial_number LIKE '{}%%' ".format(table_name,model)):
                        return str(list(x)[0])
                else:
                    for x in self.query_return_all_data("SELECT MAX(reading) FROM \"{}\" WHERE serial_number LIKE '{}%%' AND test_type = '{}'".format(table_name,model,testtype)):
                        return str(list(x)[0])

            elif condition == "min":
                if testtype == "All":
                    for x in self.query_return_all_data("SELECT MIN(reading) FROM \"{}\" WHERE serial_number LIKE '{}%%'".format(table_name,model)):
                        return str(list(x)[0])
                else:
                    for x in self.query_return_all_data("SELECT MIN(reading) FROM \"{}\" WHERE serial_number LIKE '{}%%' AND test_type = '{}'".format(table_name,model,testtype)):
                        return str(list(x)[0])
            else:
                return ""
        except:
            return ""

    def main_sensor_vs_graph_insert(self, table_name, sensor_x ='', sensor_y =''):
        # Insert Data
        result = ""
        try:
            for x in self.query_return_all_data(
                    "SELECT table_name FROM \"main_vs_graph\" where table_name='{}' ".format(table_name)):
                result = list(x)[0]
            if result:
                query = "UPDATE \"main_vs_graph\" set sensor_x='{}', sensor_y='{}' WHERE table_name = '{}';".format(sensor_x, sensor_y, table_name)
            else:
                query = "INSERT INTO \"main_vs_graph\" (table_name, sensor_x, sensor_y) VALUES ('{}','{}', '{}');".format(
                    table_name, sensor_x, sensor_y)
        except:
            print(" main_vs_graph table not exist")


        self.execute_query(query)

    def return_list_of_vs_graph(self):
        return ["".join(x) for x in self.query_return_all_data("SELECT table_name FROM \"main_vs_graph\"")]

    def return_list_of_column_view(self, table, column):

        try:
            return ["".join(str(x[0])) for x in self.query_return_all_data("SELECT \"{}\" FROM \"{}\"".format(column, table))]
        except TypeError as e:
           logging.error(str(e))

    def return_sensor_graph_data(self,table_list):
        print(table_list)
        table_c = len(table_list)
        #table_c = 2
        graph_interval = []
        sensor_count = {"first_sensor":[],"second_sensor":[],"third_sensor":[]}
        labels = []
        interval = ""

        if table_c == 1:
            query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t1}\".unit from  \"{t1}\" WHERE \"{t1}\".count != 0 ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(t1 = table_list[0])

        if table_c == 2:
            query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t2}\".count AS \"{t2}_count\",\"{t1}\".unit from  \"{t1}\" INNER JOIN \"{t2}\" ON \"{t1}\".interval = \"{t2}\".interval WHERE (\"{t1}\".count + \"{t2}\".count) >0 ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(t1 = table_list[0],t2 = table_list[1])

        if table_c == 3:
            query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t2}\".count AS \"{t2}_count\",\"{t3}\".count AS \"{t3}_count\",\"{t1}\".unit from  \"{t1}\" INNER JOIN \"{t2}\" ON \"{t1}\".interval = \"{t2}\".interval INNER JOIN \"{t3}\" ON \"{t1}\".interval = \"{t3}\".interval WHERE \"{t1}\".count + \"{t2}\".count + \"{t3}\".count >0 ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(t1 = table_list[0],t2 = table_list[1],t3 = table_list[2])

        data = self.query_return_all_data(query)
        for row in data:

            for count in range(table_c+1):
                if count == 0:
                    graph_interval.append(row[count])
                elif count == 1:
                    sensor_count["first_sensor"].append(row[count])
                elif count == 2:
                    sensor_count["second_sensor"].append(row[count])
                elif count == 3:
                    sensor_count["third_sensor"].append(row[count])
                else:
                    print("Wrong count")


        for x in graph_interval:
            temp = x.split('-')
            if not interval:
                interval = str(format((abs(float(temp[1]) - float(temp[0]))) / 2, ".3f"))
            if float(interval) < 1:
                labels.append(str(format(statistics.mean([float(x) for x in temp]), '.3f')))
            else:
                labels.append(str(int(statistics.mean([float(x) for x in temp]))))

        return labels,sensor_count,interval


    def create_main_blacklist_table(self):
        metadata = MetaData()
        Table("main_blacklist", metadata,
            Column('id',Integer, primary_key=True),
            Column('name', String)
        )
        try:
            if not self.db_engine.dialect.has_table(self.db_engine, "main_blacklist"):
                metadata.create_all(self.db_engine)
                logging.info("main_blacklist: {} Table created".format("main_blacklist"))
            else:
                logging.warning("main_blacklist: {} Table already exists".format("main_blacklist"))

        except Exception as e:
            logging.error("Error occurred during Main Sensor Interval Table creation!")
            logging.error(str(e))


    def main_blacklist_table_insert(self, name):
        # Insert Data
        result = ""
        try:
            for x in self.query_return_all_data(
                    "SELECT name FROM \"main_blacklist\" where name='{}' ".format(name)):
                result = list(x)[0]
            if result:
                pass
            else:
                query = "INSERT INTO \"main_blacklist\" (name) VALUES ('{}');".format(name)
                self.execute_query(query)
        except:
            print(" main_blacklist table not exist")

    @classmethod
    def return_sensor_graph_data_dif_model(cls, table_list):


        model_list = [x[:6] for x in table_list]

        table_c = len(table_list)
        graph_interval = []
        sensor_count = {"first_sensor":[],"second_sensor":[],"third_sensor":[]}
        labels = []
        interval = ""


        for i, table in enumerate(table_list):
            if i == 0:
                temp_dbms = MyDatabase(POSTGRES, dbname=model_list[i])
                query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t1}\".unit from  \"{t1}\" ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(
                    t1=table_list[i])
                data = temp_dbms.query_return_all_data(query)
                for row in data:
                    for count in range(table_c + 1):
                        if count == 0:
                            graph_interval.append(row[count])
                        elif count == 1:
                            sensor_count["first_sensor"].append(row[count])
                        else:
                            pass #unit can be ignroed
                for x in graph_interval:
                    temp = x.split('-')
                    if not interval:
                        interval = str(format((abs(float(temp[1]) - float(temp[0]))) / 2, ".3f"))
                    if float(interval) < 1:
                        labels.append(str(format(statistics.mean([float(x) for x in temp]), '.3f')))
                    else:
                        labels.append(str(int(statistics.mean([float(x) for x in temp]))))
            elif i == 1:
                temp_dbms = MyDatabase(POSTGRES, dbname=model_list[i])
                query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t1}\".unit from  \"{t1}\" ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(
                    t1=table_list[i])
                data = temp_dbms.query_return_all_data(query)
                for row in data:
                    for count in range(table_c + 1):
                        if count == 1:
                            sensor_count["second_sensor"].append(row[count])
                        else:
                            pass #0 count and unit can be ignroed
            elif i == 2:
                temp_dbms = MyDatabase(POSTGRES, dbname=model_list[i])
                query = "SELECT \"{t1}\".interval,\"{t1}\".count AS \"{t1}_count\",\"{t1}\".unit from  \"{t1}\" ORDER BY SPLIT_PART(\"{t1}\".interval,'-', 1) ::FLOAT".format(
                    t1=table_list[i])
                data = temp_dbms.query_return_all_data(query)
                for row in data:
                    for count in range(table_c + 1):
                        if count == 1:
                            sensor_count["third_sensor"].append(row[count])
                        else:
                            pass #0 count and unit can be ignroed


        noneZero_labels = []
        noneZero_sensor_count = {"first_sensor": [], "second_sensor": [], "third_sensor": []}

        if table_c == 1:
            for i in range(len(labels)):
                if (int(sensor_count["first_sensor"][i]) == 0):
                    pass
                else:
                    noneZero_labels.append(labels[i])
                    noneZero_sensor_count["first_sensor"].append(sensor_count["first_sensor"][i])
        elif table_c == 2:
            for i in range(len(labels)):
                if (int(sensor_count["first_sensor"][i]) == 0 and int(sensor_count["second_sensor"][i]) == 0):
                    pass
                else:
                    noneZero_labels.append(labels[i])
                    noneZero_sensor_count["first_sensor"].append(sensor_count["first_sensor"][i])
                    noneZero_sensor_count["second_sensor"].append(sensor_count["second_sensor"][i])
        elif table_c == 3:
            for i in range(len(labels)):
                if (int(sensor_count["first_sensor"][i]) == 0 and int(sensor_count["second_sensor"][i]) == 0 and int(sensor_count["third_sensor"][i]) == 0):
                    pass
                else:
                    noneZero_labels.append(labels[i])
                    noneZero_sensor_count["first_sensor"].append(sensor_count["first_sensor"][i])
                    noneZero_sensor_count["second_sensor"].append(sensor_count["second_sensor"][i])
                    noneZero_sensor_count["third_sensor"].append(sensor_count["third_sensor"][i])
        else:
            print("something is wrong")




        return noneZero_labels,noneZero_sensor_count,interval

    @classmethod
    def graph_interval_compare(cls, tables):

        model_list = [x[:6] for x in tables]
        table_c = len(tables)
        if table_c == 1:
            return True
        elif table_c == 2:
            for idx, table in enumerate(tables):
                temp_dbms = MyDatabase(POSTGRES, dbname=model_list[idx])
                if idx == 0:
                    table1_interval = temp_dbms.return_list_of_column(table,'interval')
                else:
                    table2_interval = temp_dbms.return_list_of_column(table, 'interval')
            if table2_interval == table1_interval:
                return True
            return False
        elif table_c == 3:
            for idx, table in enumerate(tables):
                temp_dbms = MyDatabase(POSTGRES, dbname=model_list[idx])
                if idx == 0:
                    table1_interval = temp_dbms.return_list_of_column(table,'interval')
                elif idx == 1:
                    table2_interval = temp_dbms.return_list_of_column(table, 'interval')
                else:
                    table3_interval = temp_dbms.return_list_of_column(table, 'interval')
            if (table2_interval == table1_interval and table3_interval == table1_interval):
                return True
            return False


    def return_distict_sensor_reading(self, table_name):
        return [float(x[0]) for x in self.query_return_all_data("SELECT DISTINCT reading FROM \"{}\" WHERE reading IS NOT NULL ORDER BY reading".format(table_name))]




    def return_sensor_avg(self, table_name):
        try:
            for x in self.query_return_all_data("SELECT AVG(reading) FROM \"{}\"".format(table_name)):
                return str(round(list(x)[0],2))
        except:
            return ""

if __name__ == '__main__':
    # if MyDatabase.graph_interval_compare(['FGT60F_PHY B50182 temp sensor_IQC_Customized_graph','FGT61F_CPU ON-DIE thermal sensor_IQC_Customized_graph','FGT61F_PHY B50210-#2 temp sensor_IQC_Customized_graph']):
    #     print("ok")
    # else:
    #     print("Not OK")
    mydb = MyDatabase(POSTGRES,dbname='FG101F')
    print(mydb.return_distict_sensor_reading("CPU ON-DIE thermal sensor"))
    # labels,sensor_count,interval = MyDatabase.return_sensor_graph_data_dif_model(['FGT60F_PHY B50182 temp sensor_IQC_Customized_graph'])
    # print("self.labels: {}".format(labels))
    # print("self.sensor_data: {}".format(sensor_count))
    # print("self.interval: {}".format(interval))
    #mydb.create_model_sensor_info_table()
    #mydb.create_sensor_unit_table()