#!/usr/bin/python3
import argparse

def main():
    print("\nPython Photo Rename and Indexing Script\n")

    parser = argparse.ArgumentParser()
    
    parser.add_argument("-d",
                        "--data_dir",
                        type = str,
                        help = "data directory that contains the photos",
                        required = True)
    
    
    args = parser.parse_args()


#=============
# main program
#=============
if __name__ == "__main__":
    main()