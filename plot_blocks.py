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

def create_csv(log_file, resolution):
    time_vec = list()
    progress_vec = list()
    blocks_vec = list()
    start_time = datetime.datetime(datetime.MINYEAR, 1, 1, 12, 0, 0)
    with open(log_file, 'r')as f:
        try:
            first_line = f.readline()
            start_time = extract_time(first_line)
        except:
            pass

        for line in f:
            progress_string = re.findall('progress=(\d+\.\d+)', line)
            if progress_string:
                progress = float(progress_string[0])
                current_time = extract_time(line)
                if int(progress) == 1:
                    break

                if progress == 0:
                    start_time = current_time
                blocks_string = re.findall('height=(\d+)', line)
                blocks = int(blocks_string[0])

                td = current_time - start_time

                time_vec.append((td.seconds/60))
                blocks_vec.append(blocks)
                progress_vec.append(progress)


                #print("Last stats")
                #print(time_vec[-1])
                #print(blocks_vec[-1])
                #print(progress_vec[-1])

    # Trim the vectors
    time_vec = time_vec[::resolution]
    blocks_vec = blocks_vec[::resolution]
    progress_vec = progress_vec[::resolution]

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
    lables = list()

    for log_file in args.log_files:


        time_vec = list()
        progress_vec = list()
        blocks_vec = list()
        
        base = os.path.splitext(log_file)[0]
        csv_writeable_file = base + ".csv"
        file_exists = os.path.isfile(csv_writeable_file)

        if args.csv_only:
            create_csv(log_file, int(args.tick))
            continue

        if not file_exists:
            create_csv(log_file, int(args.tick))


        with open(csv_writeable_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                time_vec.append(float(row['Time']))
                progress_vec.append(float(row['Progress']))
                blocks_vec.append(int(row['Block']))


        times.append(time_vec)
        blocks_results.append(blocks_vec)
        progresses.append(progress_vec)
        lables.append(base)


    if args.csv_only:
        return

    for i in range(len(times)):
        plt.plot(times[i],blocks_results[i],label = lables[i])

    plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    plt.title('Blocks over time')
    plt.xlabel('Minutes')
    plt.ylabel('Blocks')
    plt.show()


# Get arguments
def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument( 'log_files', metavar='log_file', default=None, help="Log file to plot", nargs='*')
    parser.add_argument('-c', '--csv-only', action='store_true',
        default=False, help="debug_3.7gh_1_core_hdd_dbcache4096.logOnly generate CSV files and exit")
    parser.add_argument('-t','--tick', help='how much to dilute the graph. Default: sample every 100 debug line.', type=int, default=100)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    main(sys.argv)
