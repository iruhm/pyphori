#!/usr/bin/python
import argparse
import hashlib
import os
import pyexiv2

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
    
    
    args = parser.parse_args()


    num_files = 0
    if args.data_dir is not None:
        
        print("\nopening data_dir : {}\n".format(args.data_dir))
        
        for root, dirs, files in os.walk(args.data_dir):
            for file in files:
                print("  process file: {}".format(file))
                print("      number: {}".format(num_files))
                print("      root:   {}".format(root))
                print("      md5:    {}".format(md5(root+'/'+file)))
                
                try:
                    metadata = pyexiv2.ImageMetadata(root+'/'+file)
                    metadata.read()
                    exif_out = metadata['Exif.Photo.DateTimeOriginal'].value
                    creation_date_time = str(exif_out)
                    print("      date:   {}".format(creation_date_time))
                except:
                    pass
                
                print("\n")
                num_files = num_files + 1;
                
    print("\nnumber of files processed: {}".format(num_files))
    

#=============
# main program
#=============
if __name__ == "__main__":
    main()