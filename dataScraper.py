# Author: Peter W.
# Date: 6/14/2019
# changes: no longer passes long list.
# inserts directly to table as soon as data is found
# Date: 6/14/2019
# Purpose: un-Tar log folders and extract only the log files for parsing into list for DB.

# most of the Key functions (unzipping, parsing, etc) will have both a major and a minor function.

import tarfile
import os
import re
import backend_database
import time as t
import logging
from datetime import datetime
import shutil
import csv

class DataBaseInfo:

    def __init__(self,dbname):
        # logname = "Scraper-log_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".log"
        self.dbms = backend_database.MyDatabase(
            backend_database.POSTGRES, dbname=dbname)
        # logging.basicConfig(filename=logname,
                            # filemode='a',
                            # format='%(asctime)s: %(levelname)s %(message)s',
                            # datefmt='%H:%M:%S',
                            # level=logging.DEBUG)
    
    def csv_reader(self,csv_filepath="database_create_info.csv"):
        csvlist = {}
        # with open('database_create_info.csv') as csvfile:
        with open(csv_filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csvlist[row['TableName']]= {'BaseCommand':row['BaseCommand'],'Regex':row['Regex'],'ReferenceBuffer':row['ReferenceBuffer'],'Unit':row['Unit'],"RESULT":row["Result"]}
        return csvlist


    def tgz_unzip(self, main_folder,model,testtype,start_time,end_time):
        '''This is the main un-zipping function that will determine if the selected folder has subfolders or if it is the main.
         the pass the file path to the "real" unzipping function which will extract all of the required information.'''
        if not os.path.isdir(main_folder):
            logging.warning("User Inputed directory does not exist:"+main_folder)
            print("User Inputed directory does not exist:"+main_folder)
            return None
        try:
            folders = next(os.walk(main_folder))[1]
        except StopIteration:
            folders = None
        if folders:
            if "extracted" in folders:
                logging.warning("extracted folder already exists, skipping extraction")
                print("extracted folder already exists, skipping extraction")
                self.skipped_extract = True
                return None
        else:
            if "extracted" in next(os.walk(os.path.abspath(os.path.join(main_folder, os.pardir))))[1]:
                logging.warning("extracted folder already exists, skipping extraction")
                print("extracted folder already exists, skipping extraction")
                self.skipped_extract = True
                return None
        self.skipped_extract = False
        start_time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time,"%Y-%m-%d %H:%M:%S")
        time_delta_A = start_time - end_time
        variables = {'Model':model,'TestType':testtype,"difTime":abs(time_delta_A),"StartTime":start_time,"EndTime":end_time}
        if not folders:
            logging.info(f"extracting:{main_folder}")
            print("extracting:" + main_folder)
            self.tgz_unzip_real(main_folder,variables)
        else:
            for x in folders:
                logging.info(f"extracting:{main_folder}/{x}")
                print("extracting:" + x)
                self.tgz_unzip_real(main_folder,variables, x)
        
        # checks for unknown folder, if it exist, moves the files. then check again. will quit if still there
                # looks for extacted folder
                
        try:
            main_folder += "\\extracted"
            # print(file_path)
            folders = next(os.walk(main_folder))[1]
        except StopIteration:
            main_folder = os.path.abspath(os.path.join(
                main_folder[:-13], os.pardir))+"\\extracted"
            # print(file_path)
            folders = next(os.walk(main_folder))[1]
        for folder in folders:
            if "Unknown" in next(os.walk(main_folder+"\\"+folder))[1]:
                logging.info(f"Correcting 'Unknown' folder in {folder}")
                print(f"Correcting 'Unknown' folder in {folder}")
                self.special_case(main_folder+"\\"+folder)

    def tgz_unzip_real(self, working_directory,variables, sub_dir=''):
        '''This is the minor un-zipping function that will look for .tgz files to extract any file that is in [16]".log".
        It then moves the files from the tar file to the aproperate directory.'''
        try:
            os.mkdir(os.path.abspath(os.path.join(working_directory, os.pardir))+"\\extracted\\")
        except FileExistsError:
            pass
        if sub_dir:
            working_directory += "\\"+sub_dir
        file_name = os.listdir(working_directory)
        reT = re.compile(r'/[a-zA-Z0-9\-]{16}\.log')

        for tar_file in file_name:
            if tar_file[-4:].casefold() != ".tgz":
                continue
            try:
                split_name = tar_file.split("=")[0:4] # general name format is date=teststation=model=test
                if not split_name[2]:
                    split_name[2] = "Unknown"
                if split_name[2] not in ["Unknown",variables["Model"]]:
                    continue
                if split_name[3] in variables["TestType"]:
                    pass
                elif "SFC" in variables["TestType"] and "SFC" == split_name[3].split("-")[0]:
                    pass
                else:
                    continue
                    
                parsed_date = datetime.strptime(split_name[0],"%Y-%m-%d_%H-%M-%S")
                time_delta_B = abs(variables["StartTime"]-parsed_date) + abs(variables["EndTime"]-parsed_date)
                if variables["difTime"] >= time_delta_B:
                    with tarfile.open(working_directory+"\\"+tar_file) as tf:
                        new_path = split_name[2]+"\\" + \
                            split_name[3]+"\\"+split_name[0]
                        listings = [
                            m for m in tf.getmembers() if reT.search(m.name)]
                        for file in listings:
                            if file.isreg():
                                file.name = os.path.basename(file.name)
                                if sub_dir:
                                    tf.extract(path=os.path.abspath(os.path.join(working_directory, os.pardir))+"\\extracted\\"+sub_dir+"\\"+new_path, member=file)
                                else:
                                    tf.extract(path=os.path.abspath(os.path.join(working_directory, os.pardir))+"\\extracted\\"+os.path.basename(working_directory)+"\\"+new_path, member=file)
            except tarfile.ReadError as e:
               logging.error(f"{tar_file} failed to read:"+str(e))
        logging.info(f"{working_directory} is done unzipping.")
# WE STARTING OVER BOIS
#=== Functions to move/sort/remove unknown models ===
    def special_case(self,file_path):
        '''special function that will be called if an "unknown" folder was spawned during the un-zipping processs.'''
        for test_type in next(os.walk(file_path+"\\Unknown"))[1]:
            for test_date in next(os.walk(file_path+"\\Unknown\\"+test_type))[1]:
                for files in os.listdir(file_path+"\\Unknown\\"+ test_type+"\\"+test_date):
                    self.for_unknown(file_path,test_type,test_date,files)
        self.removeEmptyFolders(file_path+"\\Unknown")

    def removeEmptyFolders(self,file_path, removeRoot=True):
        '''using recusion, it will remove all empty sub folders within a given directory as well as the root folder.'''
        if not os.path.isdir(file_path):
            return
        # remove empty subfolders
        files = os.listdir(file_path)
        if len(files):
            for f in files:
                fullpath = os.path.join(file_path, f)
                if os.path.isdir(fullpath):
                    self.removeEmptyFolders(fullpath)

        # if folder empty, delete it
        files = os.listdir(file_path)
        if len(files) == 0 and removeRoot:
            logging.debug("Removing empty folder:"+file_path)
            os.rmdir(file_path)

    @staticmethod
    def for_unknown(file_path,test_type="",test_date="",file_name=""):
        '''function to move a given "unknown" folder item to the corrected folder path.'''
        old_filepath = "\\".join([file_path,"Unknown",test_type,test_date,file_name])
        new_filepath = "\\".join([file_path,file_name[:6],test_type,test_date,file_name])
        if not os.path.exists("\\".join(new_filepath.split("\\")[:-1])):
            os.makedirs("\\".join(new_filepath.split("\\")[:-1]))
        try:
            shutil.move(old_filepath,new_filepath)
        except (FileExistsError,PermissionError) as e:
            logging.error(f"{old_filepath} => {new_filepath} failed:"+str(e))
# === Parsing functions ===
    def folder_parser(self, file_path,model_ui,test_type_ui,start_time,end_time):
        '''Major parsing function, will go through all folders the "extracted" folder. 
        Will also rename the completed parsed folders with a "=done" tag at the end to avvoid re-parsing'''
        # looks for extacted folder
        
        if not os.path.isdir(file_path):
            logging.warning("User Inputed directory does not exist:"+file_path)
            print("User Inputed directory does not exist:"+file_path)
            return False
        try:
            file_path += "\\extracted"
            folders = next(os.walk(file_path))[1]
        except StopIteration:
            file_path = os.path.abspath(os.path.join(
                file_path[:-13], os.pardir))+"\\extracted"
            folders = next(os.walk(file_path))[1]
        # double checks to make sure there are no unknown folders in the set.
        for folder in folders:
            if "Unknown" in next(os.walk(file_path+"\\"+folder))[1]:
                logging.error("Unknown folder found, should not exist. please check.")
                return False
        if self.skipped_extract:
            start_time = datetime.strptime(start_time,"%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time,"%Y-%m-%d %H:%M:%S")
            time_delta_A = start_time - end_time
        
        reader_info = self.csv_reader()
        # insert table name with units into table based on csv
        # $$$==Actual Parsing==$$$
        # forloop chain to interate through all folders in the "extracted" folder.
        for folder in folders:
            for model in next(os.walk(file_path+"\\"+folder))[1]:
                if model[-4:] == "done":
                    continue
                if model != model_ui:
                    continue
                for test_type in next(os.walk(file_path+"\\"+folder+"\\"+model))[1]:
                    if test_type[-4:] == "done":
                        continue
                    if test_type.split("-")[0] not in test_type_ui:
                        continue
                    print("checking:", folder, model, test_type)
                    cpt = sum([len(files) for r, d, files in os.walk(file_path+"\\"+folder+"\\"+model+"\\"+test_type)])
                    logging.info(f"checking: {folder} {model} {test_type} // Total number of files:{cpt}")
                    for test_date in next(os.walk(file_path+"\\"+folder+"\\"+model+"\\"+test_type))[1]:
                        if test_date[-4:] == "done":
                            continue
                        if self.skipped_extract:
                            parsed_date = datetime.strptime(test_date,"%Y-%m-%d_%H-%M-%S")
                            time_delta_B = abs(start_time-parsed_date) + abs(end_time-parsed_date)
                            if time_delta_A >= time_delta_B:
                                continue
                        current_path = file_path+"\\"+folder+"\\" +model+"\\"+test_type+"\\"+test_date+"\\"
                        file_name_list = os.listdir(file_path+"\\"+folder+"\\"+model+"\\"+test_type+"\\"+test_date)
                        for file_name in file_name_list:
                            logging.debug(f"checking:{file_name}")
                            self.file_paser(model, test_date, test_type, file_name[:-4], current_path+file_name, reader_info)
                            cpt-= 1 
                            logging.debug(f"Finished:{file_name}// remaining:{cpt}")
                        self.rename_to_done(file_path,folder,model,test_type,test_date)
                    self.rename_to_done(file_path,folder,model,test_type)
                self.rename_to_done(file_path,folder,model)



    def manual_log_parser(self, file_path,model_ui,test_type_ui=["IQC"]):
        '''Major parsing function, will go through all folders the "extracted" folder. 
        Will also rename the completed parsed folders with a "=done" tag at the end to avvoid re-parsing'''
        # looks for extacted folder
        reader_info = self.csv_reader()
        # insert table name with units into table based on csv
        # $$$==Actual Parsing==$$$
        # forloop chain to interate through all folders in the "extracted" folder.
        cpt = sum([len(files) for r, d, files in os.walk(file_path)])
        logging.info(f"checking: {file_path} // Total number of files:{cpt}")
        for file_name in  os.listdir(file_path):
            if file_name[:6] != model_ui:
                continue
            logging.debug(f"checking:{file_name}")
            self.file_paser(file_name[:6], datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), test_type_ui[0], file_name[:-4], file_path+"\\"+file_name, reader_info)
            cpt-= 1 
            logging.debug(f"Finished:{file_name}")



    @staticmethod
    def rename_to_done(file_path,folder="",model="",test_type="",test_date=""):
        '''Function to rename folders from their original state to include the "=done" tag at the end.'''
        old_filepath = "\\".join(list(filter(None,[file_path,folder,model,test_type,test_date])))
        new_filepath = old_filepath+"=done"
        try:
            os.rename(old_filepath,new_filepath)
        except (FileExistsError,PermissionError) as e:
            logging.error(f"{old_filepath} => {new_filepath} failed:"+str(e))

    def db_inserter_sensor(self, table_name, serial_number, test_date, test_type, line_number='', alarm='', reading='', ref_line=""):
        '''function to insert variables to main DB per Andy Lo\'s functions.
        Has its own function since test time needs to be reformatted into DB format. '''
        s = [x.rjust(2, '0') for x in test_date.replace("_", "-").split("-")]
        standardtime = s[0]+"-"+s[1]+"-"+s[2]+" "+s[3]+":"+s[4]+":"+s[5]
        update_reading = str(reading).replace(",","")
        self.dbms.sensor_insert(table_name.replace(
            "\\", ""), serial_number, standardtime, test_type, line_number, alarm, update_reading, ref_line)

    def file_paser(self, model, test_date, test_type, serial_number, filepath, csv_info):
        '''Minor Function that will go through the files passed in by the major parser.'''
        content = {}
        with open(filepath, "r", errors="ignore") as f:
            for i, x in enumerate(f.readlines(), 1):
                content[i] = x
        command_start,command_return = self.check_for_command(csv_info, content,serial_number)
        if command_start:
            for table_name in command_return:
                if command_return[table_name] == "BLACKLIST":
                    self.dbms.create_blacklist_table(table_name)
                    self.dbms.main_blacklist_table_insert(table_name)
                    self.obtain_blacklist(table_name,csv_info[table_name]["Regex"],content,serial_number,test_date,test_type)
                    continue
                for startline in command_return[table_name]:
                    sensor_dict = self.obtain_sensor(csv_info[table_name]["BaseCommand"], 
                                                    content,csv_info[table_name]['Regex'], startline, 
                                                    csv_info[table_name]["ReferenceBuffer"])
                    if sensor_dict:
                        self.dbms.create_sensor_table(table_name)
                        self.dbms.sensor_unit_table_insert(table_name, csv_info[table_name]["Unit"])
                        for pair in sensor_dict:
                            self.db_inserter_sensor(table_name, serial_number, test_date, test_type,
                                                    pair["line_number"], pair["alarm"],
                                                    pair["reading"], startline)


    @staticmethod
    def check_for_command(csv_info, content,serial_number):
        '''Checks a log for the given command and returns the line number that it occured on.
        used to determine where to start parsing for sensor data.'''
        lines = []
        cmd_set = {}
        end = len(content)
        start = end - 5
        if start < 0:
            start = 0
        for table_name in csv_info:
            skip = False
            if csv_info[table_name]["RESULT"] == 'FAIL':
                for x in range(start,end):
                    if re.search(serial_number+"\\s*Passed",content[x]):
                        skip = True
                        break
            elif csv_info[table_name]["RESULT"] == 'PASS':
                for x in range(start,end):
                    if re.search(serial_number+"\\s*Passed",content[x]):
                        break
                    if x == end-1:
                        skip = True
            else:
                pass
            if skip:
                continue
            if csv_info[table_name]["BaseCommand"] == "$$$BLACKLIST$$$":
                cmd_set[table_name] = "BLACKLIST"
                continue
            for x in content:
                if csv_info[table_name]["BaseCommand"] in content[x]:
                    lines.append(x)
            if lines:
                cmd_set[table_name] = lines
                lines = []
        if cmd_set:
            return True, cmd_set
        else:
            return False, {}

    def obtain_sensor(self,start_command, content, model_regex, start, sensor_length):
        '''function to go through the log based on the a list of start values.
        using a regular expression to obtain the sensor reading/values/alarm/units when avliable. 
        will also clean the data before passing a dictonary back to the minor parser.'''
        answer = []
        pattern = re.compile(model_regex)
        for x in range(start, (start+5)+int(sensor_length)):
            try:
                
                if start_command in content[x] and x > start:
                    break
            except KeyError:
                continue
            y = pattern.search(content[x])
            if y:
                try:
                    hex_reading = y.group("reading")
                    strng = str(y.group("reading")).lower()
                    for letter in ["a","b","c","d","e","f","x"]:
                        if letter in strng:
                            hex_reading = int(y.group("reading"), 16)
                            break
                except:
                    hex_reading=""
                try:
                    hex_alarm = y.group("alarm")
                    if hex_alarm == "ESR" or hex_alarm == "E":
                        hex_alarm = 0
                    elif hex_alarm =="SR":
                        hex_alarm = 1
                    elif 'x' in str(y.group("alarm")):
                        hex_alarm = int(y.group("alarm"), 16)
                    if y.group("alarm") == "ok":
                        hex_alarm = 0
                except IndexError:
                    hex_alarm=0
                answer.append({"line_number": x, "alarm": hex_alarm, "reading": hex_reading})
        return answer


        

    def obtain_blacklist(self,table_name,blacklist, content, serial_number, test_date, test_type):
        '''function to go through passed in log file to check for given blacklist variable. will clean data before insertion'''
        s = [x.rjust(2, '0') for x in test_date.replace("_", "-").split("-")]
        standardtime = s[0]+"-"+s[1]+"-"+s[2]+" "+s[3]+":"+s[4]+":"+s[5]
        not_found = True
        for x in content:
            if blacklist in content[x]:
                not_found = False
                corrected_content = re.sub(r"[^a-zA-Z0-9\.\-\_\s]", "", content[x])
                self.dbms.blacklist_insert(
                    table_name, serial_number, standardtime, test_type, x, corrected_content, True)
        if not_found:
            self.dbms.blacklist_insert(
                table_name, serial_number, standardtime, test_type, '', '', False)
    
# main_folder = r"C:\Users\wlo\Desktop\multitest"
# model = "FG100F"
# start_time = "1999-1-1 00:00:00"
# end_time = "2019-12-30 00:00:00"
# testtype = ["HTS"]
#
# help = DataBaseInfo('SearchEngine')
# help.tgz_unzip(main_folder,model,testtype,start_time,end_time)
# # help.folder_parser(main_folder,model,testtype,start_time,end_time)
# help.manual_log_parser(main_folder,model)