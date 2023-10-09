import glob
import json
import time
import zipfile
from datetime import datetime
import os
import re
import csv
import semsgpdf
import mycache

from local_conf import PAGES
from pdfminer.high_level import extract_text


def convert_pdf_txt(name_scan_file, PAGES):
    pass


def find_values(text_pdf):
    # 1 find invoice No
    # "^Invoice No\n+(\d+)"

    inv_p = re.compile(r"^Invoice No\n+(\d+)", re.M)
    invoice_no = inv_p.findall(text_pdf)

    # 2 find Due amount
    # "^Total Due\n+\$(\d+\.\d+)"

    due_amo_p = re.compile(r"^Total Due\n+\$(\d+\.\d+)", re.M)
    due_amount = due_amo_p.findall(text_pdf)

    # 3 find Entry No: AEPFC3EJN,
    # "^Entry No:\s+([A-Z0-9]+)"

    entry_no_p = re.compile(r"^Entry No:\s+([A-Z0-9]+)", re.M)
    entry_no = entry_no_p.findall(text_pdf)

    #4 "Reference:\s+(\d+)"
    reference_p = re.compile(r"^Reference:\s+(\d+)", re.M)
    reference = reference_p.findall(text_pdf)

    # 5 find HAWB: 1Z03831204995 48616
    # "HAWB:\s+([A-Z0-9]+)\n([A-Z0-9]+)"

    hawb_p = re.compile(r"HAWB:\s+([A-Z0-9]+)[\n\s]([A-Z0-9]+)", re.M)
    hawb_values = hawb_p.findall(text_pdf)
    # just in case convert to string to avoid math +
    # hawb_value = str(hawb_values[0][0]) + str(hawb_values[0][1])
    # another join tuple members
    if not hawb_values:
        hawb_p = re.compile(r"HAWB:\s+([A-Z0-9]+)", re.M)
        hawb_values = hawb_p.findall(text_pdf)

    str_err = 'error read'
    hawb_value = ''.join(hawb_values[0]) if hawb_values else str_err
    _invoice_no = invoice_no[0] if invoice_no else str_err
    _due_amount = due_amount[0] if due_amount else str_err
    _entry_no = entry_no[0] if entry_no else str_err
    _reference = reference[0] if reference else str_err

    print('inv_no=', _invoice_no)
    print('due_amount=', _due_amount)
    print('entry_no=', _entry_no)
    print('reference=', _reference)
    print('hawb=', hawb_value)

    return {'invoice_no': _invoice_no,
            'due_amount': _due_amount,
            'entry_no': _entry_no,
            'hawb': hawb_value,
            'reference': _reference,
            }


def save_csv(save_path_name, save_dict_csv):
    csv_columns = ['file', 'invoice_no', 'due_amount', 'entry_no', 'hawb', 'reference']
    try:
        with open(save_path_name, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for key, data in save_dict_csv.items():
                data['file'] = key
                writer.writerow(data)
    except IOError:
        print("I/O error")


def process_pdfs(thread_id):
    # --спускаемся в директорию--------------------------------------------------------------------^
    dir_path = os.path.join(os.getcwd(), 'pdf')  # сюда передаем название исх директории
    save_path = os.path.join(os.getcwd(), 'result')  # сюда передаем название результ директории

    # Getting the list of directories
    # process if .msg first!
    semsgpdf.process_msg(thread_id)
    #get cache connect
    mc = mycache.create_client()
    # Use the glob module to search for .pdf files in the folder
    pdf_dir = glob.glob(dir_path + "/*.pdf")
    # Checking if the list is empty or not
    if len(pdf_dir) == 0:
        print("Empty pdf directory dont process pdf folder")
        mycache.update_progress(mc, thread_id, 100)
        return
    else:
        print("Not empty pdf directory, process pdfs folder")

    initial_path = os.getcwd()
    os.chdir(dir_path)

    #print(f'Мы здесь {os.getcwd()}')

    my_dir_list = os.listdir()
    my_dir_list.sort()

    print(f'\n{datetime.now()} Начинаем обработку:\nАнализируем директорию < {dir_path} >')

    s_count = 0
    # get list of files (sorted)
    pdf_files = [f for f in os.listdir(dir_path) if f.endswith('.pdf')]
    pdf_files.sort()

    print(f'pdf файлов в директории: {len(pdf_files)}')
    save_dict_csv = {}
    #progrsse bar
    dx = float(50 / len(pdf_files))
    progress = 50

    # process files fill a dictionary
    for idx, item_file in enumerate(pdf_files):
        if not os.path.isdir(item_file):
            try:
                with open(item_file, 'rb') as f:
                    item_file_text = extract_text(f)
                    # update progress bar
                    progress_new = 50 + int(dx * idx)
                    if progress_new > progress:
                        mycache.update_progress(mc, thread_id, progress_new, f' pdf file: {idx+1}')
                        #time.sleep(0.5)
                        progress = progress_new

            except Exception as err:
                print(f'Ошибка открытия файла: {item_file}')
                print(f"Unexpected error:", repr(err))
                item_file_text = ''
            name_scan_file = f'{dir_path}/{item_file}'

            print(f'\nФайл: {name_scan_file} номер: {idx+1}, поиск значений:')

           # print(f'Файл: {name_scan_file} перевод в text: {idx}')
           # text_pdf = convert_pdf_txt(name_scan_file, PAGES)

            #print('text=', item_file_text)
            values = find_values(item_file_text)
            save_dict_csv[item_file] = values


    # store dictionary to csv file
    #print(save_dict_csv)
    timestr = time.strftime("%d%m%Y-%H%M%S")
    file_name_csv = f"{save_path}/result_{timestr}.csv"

    #file_name_csv = f"{save_path}/result.csv"
    save_csv(file_name_csv, save_dict_csv)
    print(f'\n{datetime.now()} Обработка завершена. Результат в файле {file_name_csv}')

    # zip folder
    folder_name = dir_path
    zip_name = f"{save_path}/pdf.zip"
    #remove old zip
    if os.path.exists(zip_name):
        os.remove(zip_name)

    # create a ZipFile object
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # iterate over all the files in the folder and add them to the zip file
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_name)
                zipf.write(file_path, arcname=arcname)

            #for file in files:
            #    zipf.write(os.path.join(root, file))

    print(f'\n{datetime.now()} Архив zip pdf в файле {zip_name}')

    for idx, item_file in enumerate(pdf_files):
        if not os.path.isdir(item_file):
            try:
                full_item_file = f'{dir_path}/{item_file}'
                os.remove(full_item_file)

            except Exception as err:
                print(f'Ошибка удаления файла: {item_file}')
                print(f"Unexpected error:", repr(err))

            print(f'\nУдален фaйл: {item_file} номер: {idx+1}')

    mycache.update_progress(mc, thread_id, 100)
    os.chdir(initial_path)


if __name__ == '__main__':
    process_pdfs()
