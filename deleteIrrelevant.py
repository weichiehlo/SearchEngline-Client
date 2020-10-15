import backend_database



snToBeDelete = []
dbs = ["FG440F", "FG441F"]
refTable = "PS4 VIN"
tableToBeDelete = ["PS4 VOUT_12V", "PS4 IIN", "PS4 IOUT_12V", "PS4 POUT", "PS4 Temp 1", "PS4 Temp 2", "PS4 Fan 1"]

for db in dbs:

    dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)

    for row in dbms.query_return_all_data("SELECT * FROM \"{}\" WHERE reading = 0".format(refTable)):
        snToBeDelete.append([row[1], row[7]])

    for table in tableToBeDelete:

        for result in snToBeDelete:
            dbms.execute_query("DELETE FROM \"{}\" WHERE serial_number = \'{}\' AND ref_line_number={}".format(table,result[0],result[1]))




# Original
# import backend_database
#
#
#
# snToBeDelete = []
# dbs = ["FG2K2E", "FG3K3E", "FG22E1", "FG33E1"]
# refTable = "PS4 VIN"
# tableToBeDelete = ["PS4 Fan 1", "PS4 VOUT_12V", "PS4 Temp 1", "PS4 Temp 2", "PS4 VIN"]
#
# for db in dbs:
#
#     dbms = backend_database.MyDatabase(backend_database.POSTGRES, dbname=db)
#
#     for row in dbms.query_return_all_data("SELECT * FROM \"{}\" WHERE alarm = 1".format(refTable)):
#         snToBeDelete.append([row[1], row[7]])
#
#     for table in tableToBeDelete:
#
#         for result in snToBeDelete:
#             dbms.execute_query("DELETE FROM \"{}\" WHERE serial_number = \'{}\' AND ref_line_number={}".format(table,result[0],result[1]))
#
#
