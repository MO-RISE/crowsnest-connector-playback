
import csv

def getNTproFileMetadata(filePath):

    metaObj = {}

    with open(
        filePath,
        newline="",
    ) as csvfile:
        row_reader = csv.reader(csvfile, delimiter=",")
        count = 0

        for row in row_reader:
            if row[0].find('Exercise date') >= 0:
                metaObj['scenario_recorded_date'] = row[0].split(' ')[2]
            elif row[0].find('Step (sec):') >= 0:
                metaObj['scenario_recorded_freqency'] = row[0].split(' ')[2]
            elif row[0].find('OS:') >= 0:
                metaObj['scenario_wartsila_OS_name'] = row[0].split(': ')[1]
            
            count += 1

            # Stopping after looped over header rows
            if count >= 8:
                break
    
    return metaObj