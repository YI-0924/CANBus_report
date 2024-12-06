import re
import pandas as pd

#如果想要把有DOS的檔案全部target設為1就把process_can_data以及最後兩行註解掉
def process_can_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    processed_lines = []

    for line in lines:
        match = re.match(r'\((\d+\.\d+)\)\s+vcan0\s+([0-9A-Fa-f]{3})##([\dA-Fa-f]+)\s+(\d)', line.strip())
        if match:
            timestamp = match.group(1)
            can_id = match.group(2)
            data = match.group(3)
            flag = match.group(4)

            # 如果 CAN ID 是 000，將 flag 設為 1，否則設為 0
            if can_id == "000":
                flag = "1"
            else:
                flag = "0"

            # 重新組合處理後的行
            processed_line = f"({timestamp})  vcan0  {can_id}#{data} {flag}"
            processed_lines.append(processed_line)
        else:
            # 如果行不匹配格式，直接保留原行
            processed_lines.append(line.strip())
    
    # 將處理後的資料寫回原檔案
    with open(file_path, 'w') as f:
        f.write("\n".join(processed_lines))

# 呼叫處理函數

file = 'trainset.csv'
file2 = 'trainset_dos.csv'
df = pd.read_csv(file)
data = pd.read_csv(file2)
df['target'] = 0    # add target = 0 (no attack)
data['target'] = 1  # add target = 1 (DoS attack)
df.to_csv('trainset.csv', sep=' ',index = False, escapechar=' ', header=False)
data.to_csv('trainset_dos.csv', sep=' ',index = False, escapechar=' ', header=False)

file_path = 'trainset_dos.csv'  # 原始檔案名稱
process_can_data(file_path)