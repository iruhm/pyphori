#!/usr/bin/python
import argparse
import hashlib
import os
import pyexiv2
import sqlite3
import pandas as pd

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
                        help = "data directory that contains the photos",
                        required = True)
    
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
                    "filename TEXT PRIMARY KEY, " \
                    "md5 TEXT, " \
                    "date TEXT )"
            cursor.execute(sql)

        database = sqlite3.connect(args.database)
        cursor = database.cursor()
        
    else:
        
        sys.exit("\nPlease specify a database")
            

    num_files = 0
    if args.data_dir is not None:
        
        print("\nopening data_dir : {}\n".format(args.data_dir))
        
        for root, dirs, files in os.walk(args.data_dir):
            for file in files:
                filename = root+'/'+file
                md5_str = md5(filename)
                print("  process file: {}".format(file))
                print("      number: {}".format(num_files))
                print("      root:   {}".format(root))
                print("      md5:    {}".format(md5_str))
                
                creation_date_time = "unkown"
                try:
                    metadata = pyexiv2.ImageMetadata(root+'/'+file)
                    metadata.read()
                    exif_out = metadata['Exif.Photo.DateTimeOriginal'].value
                    creation_date_time = str(exif_out)
                    print("      date:   {}".format(creation_date_time))
                except:
                    pass
                
                db_md5 = pd.read_sql_query(
                             "SELECT md5 FROM media WHERE(filename='{}')".format(filename),
                             database)
                
                try:
                    if db_md5.at[0,'md5'] == md5_str:
                        print("   status:    found in database")
                    else:
                        print("   status:    file changed since last indexing")
                except:
                    print("   status:    adding to database")
                    sql = "INSERT INTO media VALUES('{}','{}','{}')".format(filename,md5_str,creation_date_time)
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