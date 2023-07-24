import csv

from datetime import date
today = date.today()
formatted_date = today.strftime("%d/%m/%Y")

def compare_and_merge_csv(file1, file2, output_file):
    """
Функция  compare_and_merge_csv
сравнивает два CSV файла на основе определенного столбца, добавляет новый столбец,
указывающий статус каждой строки, и объединяет файлы в новый CSV файл. 
 
:param file1: Путь к первому CSV файлу, содержащему данные для сравнения и объединения 
:param file2: Путь ко второму CSV файлу, который вы хотите сравнить и объединить с file1 
:param output_file: Параметр output_file представляет собой имя или путь к файлу,
в котором будут сохранены объединенные данные.
    """
    ids_file1 = set()
    with open(file1, 'r', newline='', encoding='utf-8-sig') as csvfile1:
        reader1 = csv.reader(csvfile1,delimiter=';')
        next(reader1) 
        for row in reader1:
            ids_file1.add(row[0])  

    with open(file2, 'r', newline='', encoding='utf-8') as csvfile2,
            open(output_file, 'w', newline='', encoding='utf-8-sig') as output_csv:
        reader2 = csv.reader(csvfile2,delimiter=';')
        writer = csv.writer(output_csv,delimiter=';')
        header = next(reader2)
        header.append('Status')  
        writer.writerow(header)

        for row in reader2:
            if row[0] not in ids_file1:  
                row.append(formatted_date)  
            else:
                row.append('') 
            writer.writerow(row)

    print(f'Сравнение и объединение завершены. Результат сохранен в {output_file}.')



file1 = 'file1.csv'
file2 = 'file2.csv'
output_file = 'merged.csv'

compare_and_merge_csv(file1, file2, output_file)