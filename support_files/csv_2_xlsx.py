import os
import csv
from glob import glob
from xlsxwriter.workbook import Workbook

def convert():
    workbook = Workbook('./results/results.xlsx')

    for csvfile in glob(os.path.join('./results', '*.csv')):
        worksheet_name = csvfile[10:-4]
        worksheet_name = worksheet_name[:31]
        worksheet = workbook.add_worksheet(worksheet_name)
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write_string(r, c, col)
    
    workbook.close()


if __name__ == "__main__":
    convert()
