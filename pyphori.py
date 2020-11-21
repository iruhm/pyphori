#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import hashlib
import os
import pyexiv2
import sqlite3
import pandas as pd
import io
import re
import time

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
#        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def main():
    print("\nPython Photo Rename and Indexing Script\n")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d",
                        "--data_dir",
                        type = str,
                        help = "data directory that contains the photos")
    
    parser.add_argument("-t",
                        "--transfer_dir",
                        type = str,
                        help = "directory where new photos are uploaded for renaming and indexing")
    
    parser.add_argument("-e",
                        "--export",
                        type = str,
                        help = "export database as text")
    
    parser.add_argument("--database",
                        type = str,
                        help = "database file",
                        required = True)
    
    
    args = parser.parse_args()

    if args.database is not None:
        
        print("\nopening database : {}\n".format(args.database))
        
        # if the database exists then just open it
        if os.path.exists(args.database):
            database = sqlite3.connect(args.database)
            cursor = database.cursor()
            
        # if the database does not exists then create it
        else:
            database = sqlite3.connect(args.database)
            cursor = database.cursor()
            sql = "CREATE TABLE media(" \
                    "file_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                    "filename TEXT, " \
                    "full_filename TEXT, " \
                    "md5 TEXT, " \
                    "year INTEGER, " \
                    "month INTEGER, " \
                    "day INTEGER, "\
                    "time TEXT, "\
                    "filetype TEXT, "\
                    "scanned INTEGER)"
            cursor.execute(sql)

        database = sqlite3.connect(args.database)
        cursor = database.cursor()
        
    else:
        
        sys.exit("\nPlease specify a database")
            
    if args.export is not None:
        
        print("\nexporting database to file : {}\n".format(args.export))
        with io.open(args.export, mode="w", encoding="UTF8") as fd:
       
            cursor.execute("SELECT * FROM media")
            for row in cursor:
                print(row)
                print(row[1])
                fd.write(u"{:8} {:32} {:4}{:3}{:3} {:8} {:8} {:3} {:40}\t{}\n".format(row[0],row[3],row[4],row[5],row[6],row[7],row[9],row[8],row[1],row[2]))
        
        fd.close() 

    # get current time stamp for updating files in the database that were found    
    scan_ts = int(time.time())
    
    num_files = 0
    if args.data_dir is not None:
        
        print("\nopening data_dir : {}\n".format(args.data_dir))
        
        for root, dirs, files in os.walk(args.data_dir):
            for file in files:
                filename = root+'/'+file
                md5_str = md5(filename)
                print("  process file: {}".format(file))
                print("      number:   {}".format(num_files))
                print("      root:     {}".format(root))
                print("      md5:      {}".format(md5_str))
                
                if args.transfer_dir is not None and root.startswith(args.transfer_dir):
                    print("      type:  new file")
                    
                filetype = None
                try:
                    filename_extract = re.match (r"(.*)\.(.*)$",file)
                    filetype = filename_extract.group(2).lower()
                except:
                    pass
                print("      filetype: {}".format(filetype))
                
                creation_date_time = None
                cyear  = -1
                cmonth = -1
                cday   = -1
                ctime  = None
                try:
                    metadata = pyexiv2.ImageMetadata(root+'/'+file)
                    metadata.read()
                    exif_out = metadata['Exif.Photo.DateTimeOriginal'].value
                    creation_date_time = str(exif_out)
                    print("      date:     {}".format(creation_date_time))
                    
                    date_time_extract = re.match (r"(.*)-(.*)-(.*)\s(.*)",creation_date_time)
                    cyear  = int(date_time_extract.group(1))
                    cmonth = int(date_time_extract.group(2))
                    cday   = int(date_time_extract.group(3))
                    ctime  = date_time_extract.group(4)
                    print("      year:     {}".format(cyear))
                    print("      month:    {}".format(cmonth))
                    print("      day:      {}".format(cday))
                    print("      time:     {}".format(ctime))
                    
                except:
                    pass
                
                db_md5 = pd.read_sql_query(
                             "SELECT md5 FROM media WHERE(full_filename='{}')".format(filename),
                             database)
                
                try:
                    if db_md5.at[0,'md5'] == md5_str:
                        print("      status:   found in database")
                        sql = "UPDATE media SET scanned = {} WHERE (full_filename='{}')".format(scan_ts,filename)
                        print(sql)
                        cursor.execute(sql)
                        database.commit()
                    else:
                        print("      status:   file changed since last indexing")
                        # ToDo: check if file was renamed; if not store old md5 as deleted file
                except:
                    print("      status:   adding to database")
                    sql = "INSERT INTO media( filename, "\
                                             "full_filename, "\
                                             "md5, "\
                                             "year, "\
                                             "month, "\
                                             "day, "\
                                             "time, "\
                                             "filetype, "\
                                             "scanned ) "\
                                             " VALUES( '{}','{}','{}','{}',"\
                                                      "'{}','{}','{}','{}','{}')".format(
                                                                                 file,
                                                                                 filename,
                                                                                 md5_str,
                                                                                 cyear,
                                                                                 cmonth,
                                                                                 cday,
                                                                                 ctime,
                                                                                 filetype,
                                                                                 scan_ts)
                    print(sql)
                    cursor.execute(sql)
                    database.commit()

                print("\n")
                num_files = num_files + 1;
                
                
    print("\nnumber of files processed: {}".format(num_files))
    
    database.close()
    

#=============
# main program
#=============
if __name__ == "__main__":
    main()