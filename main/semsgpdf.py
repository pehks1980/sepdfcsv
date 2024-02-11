import glob
import os
import extract_msg
import time
from datetime import datetime

import mycache1


def process_msg(thread_id, sess_id):
    # setup logging

    # get files from a path
    #exporting_threads[thread_id].progress = 50
    # save_path = os.getcwd()
    # --спускаемся в директорию--------------------------------------------------------------------^
    dir_path = os.path.join(os.getcwd(), 'msg',f"_{sess_id}")  # сюда передаем название исх директории
    save_path = os.path.join(os.getcwd(), 'pdf',f"_{sess_id}")  # сюда передаем название результ директории
    #connect to cache
    mc = mycache1.create_client()
    msg_dir = glob.glob(dir_path + "/*.msg")
    # Checking if the list is empty or not
    if len(msg_dir) == 0:
        print("Empty msg directory, dont process msg folder..")
        mycache1.update_progress(mc, thread_id, 50)
        return

    initial_path = os.getcwd()
    os.chdir(dir_path)

    # print(f'Мы здесь {os.getcwd()}')

    my_dir_list = os.listdir()
    my_dir_list.sort()

    print(f'\n{datetime.now()} Начинаем обработку:\nАнализируем директорию < {dir_path} >')

    s_count = 0
    # get list of files (sorted)
    msg_files = [f for f in os.listdir(dir_path) if f.endswith('.msg')]
    msg_files.sort()

    print(f'msg файлов в директории: {len(msg_files)}')
    save_dict_csv = {}
    # process files fill a dictionary
    dx = float(50/len(msg_files))
    progress = 0
    mc = mycache1.create_client()
    mode = ' unpacking pdf from msg file:'
    for idx, item_file in enumerate(msg_files):
        if not os.path.isdir(item_file):
            try:
                with open(item_file, 'rb') as f:
                    msg = extract_msg.Message(f)
                    msg_sender = msg.sender
                    msg_date = msg.date
                    msg_subj = msg.subject
                    msg_message = msg.body
                    msg_attachments = msg.attachments

                    print('Sender: {}'.format(msg_sender))
                    print('Sent On: {}'.format(msg_date))
                    print('Subject: {}'.format(msg_subj))
                    print('Body: {}'.format(msg_message))

                    for attachment in msg_attachments:
                        print('attachment: {}'.format(attachment.name))
                        # Extract and save each attachment
                        attachment.save(customPath=save_path)

                    print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                    #update progress bar
                    progress_new = int(dx*idx)
                    if progress_new > progress:
                        mycache1.update_progress(mc, thread_id, progress_new, f'{mode} {idx+1}')
                        #time.sleep(1)
                        progress = progress_new

            except Exception as err:
                print(f'Ошибка открытия файла: {item_file}')
                print(f"Unexpected error:", repr(err))
                item_file_text = ''
            name_scan_file = f'{dir_path}/{item_file}'

            print(f'\nФайл: {name_scan_file} номер: {idx + 1}, поиск значений:')

        # print(f'Файл: {name_scan_file} перевод в text: {idx}')
        # text_pdf = convert_pdf_txt(name_scan_file, PAGES)

        # print('text=', item_file_text)
        # values = find_values(item_file_text)

        # save_dict_csv[item_file] = values

    # store dictionary to csv file
    # print(save_dict_csv)
    timestr = time.strftime("%d%m%Y-%H%M%S")
    # file_name_csv = f"{save_path}/result_{timestr}.csv"

    # file_name_csv = f"{save_path}/result.csv"
    # save_csv(file_name_csv, save_dict_csv)
    # print(f'\n{datetime.now()} Обработка завершена. Результат в файле {file_name_csv}')

    for idx, item_file in enumerate(msg_files):
        if not os.path.isdir(item_file):
            try:
                full_item_file = f'{dir_path}/{item_file}'
                os.remove(full_item_file)

            except Exception as err:
                print(f'Ошибка удаления файла: {item_file}')
                print(f"Unexpected error:", repr(err))

            print(f'\nУдален фaйл: {item_file} номер: {idx + 1}')

    os.chdir(initial_path)


if __name__ == '__main__':
    process_msg()
