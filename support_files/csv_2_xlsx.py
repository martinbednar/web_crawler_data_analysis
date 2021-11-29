import os
import csv
from glob import glob
from xlsxwriter.workbook import Workbook

def convert():
    workbook = Workbook('./results/results.xlsx')
    number_format = workbook.add_format({'num_format': '# ### ##0'})
    percentage_format = workbook.add_format({'num_format': '0.00%'})
    
    for csvfile in glob(os.path.join('./results', '*.csv')):
        worksheet_name = csvfile[10:-4]
        worksheet_name = worksheet_name[:31]
        worksheet = workbook.add_worksheet(worksheet_name)
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    if (col.isnumeric()) or (col[0] == '-' and col[1:].isnumeric()):
                        worksheet.write_number(r, c, int(col), number_format)
                    elif (col.replace('.', '', 1).isnumeric()) or (col[0] == '-' and col[1:].replace('.', '', 1).isnumeric()):
                        worksheet.write_number(r, c, float(col), percentage_format)
                    else:
                        worksheet.write_string(r, c, col)
    
    workbook.close()


if __name__ == "__main__":
    convert()
