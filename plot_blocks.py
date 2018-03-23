#!/usr/bin/python3
import argparse
import sys
import os
import csv
import gzip
import re
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

# ######### Defaults  #########

def extract_time(line):
    t =  line.split(" ", 2)[0:2]
    struct_time = time.strptime(t[0]+t[1], "%Y-%m-%d%H:%M:%S")
    dt = datetime.datetime(*(struct_time)[0:6])
    return dt

def create_csv(log_file):
    time_vec = list()
    progress_vec = list()
    blocks_vec = list()
    #start_time = datetime.datetime(datetime.MINYEAR, 1, 1, 12, 0, 0)
    with open(log_file, 'r')as f:
        first_line = f.readline()
        start_time = extract_time(first_line)
        for line in f:
            progress_string = re.findall('progress=(\d+\.\d+)', line)
            if progress_string:
                progress = float(progress_string[0])
                current_time = extract_time(line)
                if int(progress) == 100:
                    break

                if progress == 0:
                    start_time = current_time
                blocks_string = re.findall('height=(\d+)', line)
                blocks = int(blocks_string[0])

                td = current_time - start_time

                time_vec.append(int(td.seconds/60))
                blocks_vec.append(blocks)
                progress_vec.append(progress)


                #print("Last stats")
                #print(time_vec[-1])
                #print(blocks_vec[-1])
                #print(progress_vec[-1])

    # Trim the vectors
    time_vec = time_vec[::10]
    blocks_vec = blocks_vec[::10]
    progress_vec = progress_vec[::10]

    # Create csv file
    csv_writeable_file = base = os.path.splitext(log_file)[0] + ".csv"
    file_exists = os.path.isfile(csv_writeable_file)
    with open(csv_writeable_file, 'a') as csvfile:

        fieldnames = ['Time', 'Block', 'Progress']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # file doesn't exist yet, write a header

        for i in range(len(time_vec)):
            d = {'Time': time_vec[i], 'Block': blocks_vec[i], 'Progress': progress_vec[i]}
            writer.writerow(d)


def main(argv):
    args = get_args()
    times = list()
    blocks_results = list()
    progresses = list()

    for log_file in args.log_files:

        time_vec = list()
        progress_vec = list()
        blocks_vec = list()

        csv_writeable_file = base = os.path.splitext(log_file)[0] + ".csv"
        file_exists = os.path.isfile(csv_writeable_file)

        if not file_exists:
            create_csv(log_file)


        with open(csv_writeable_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                time_vec.append(float(row['Time']))
                progress_vec.append(float(row['Progress']))
                blocks_vec.append(int(row['Block']))


        times.append(time_vec)
        blocks_results.append(blocks_vec)
        progresses.append(progress_vec)



    for i in range(len(times)):
        plt.plot(times[i],blocks_results[i],label = 'id %s'%i)


    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    plt.title('Blocks over time')
    plt.show()


# Get arguments
def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument( 'log_files', metavar='log_file', default=None, help="Log file to plot", nargs='*')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main(sys.argv)
