import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
import re

def load_and_prepare_data(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = []

    for line in lines:
        match = re.match(r'\((\d+\.\d+)\)\s+vcan0\s+([0-9A-Fa-f]{3})##([0-9A-Fa-f]*)', line.strip())
        if match:
            timestamp = float(match.group(1))
            id_hex = int(match.group(2), 16)
            dlc_data = match.group(3)

            dlc_values = [dlc_data[i:i+2] if i<len(dlc_data) else np.nan for i in range(0, 16, 2)]
            data_len = sum(1 for value in dlc_values if pd.notna(value))
            data.append([timestamp, id_hex, data_len] + dlc_values)

    columns = ['Timestamp', 'ID', 'LEN'] + [f'DLC{i}' for i in range(8)]
    df = pd.DataFrame(data, columns=columns)
    #df = df.dropna()
    df = df.fillna('0')
    df['ID']=df['ID'].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    df = df.reset_index(drop=True)
    df['Timestamp']=(df['Timestamp'] - df['Timestamp'][0])
    #df[['DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']] = df[['DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']].apply(pd.to_numeric, errors='coerce').astype(float)
    for i in range(8):
        df[f'DLC{i}'] = df[f'DLC{i}'].apply(lambda x: float(int(x, 16)))
    
    print(df.head(10))  #資料都轉十進制
    return df

def prepare_data_for_model(df):
    feature_columns = ['Timestamp', 'ID', 'LEN', 'DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']
    features = df[feature_columns].values

    scaler = joblib.load('scaler.joblib')
    features_scaled = scaler.transform(features)

    features_scaled = np.nan_to_num(features_scaled)
    features_scaled[np.isinf(features_scaled)] = 0

    return features_scaled

file = 'test_value (2).csv'

df = load_and_prepare_data(file)
# print(df.head())

test_value = prepare_data_for_model(df)
test_value = np.reshape(test_value, (test_value.shape[0], 1, test_value.shape[1]))

model = tf.keras.models.load_model('lstm_model.keras')

predictions = model.predict(test_value)
predictions = (predictions > 0.5).astype(int)

submission = pd.DataFrame(data=predictions, columns=['target']) #target=1表有dos attack
submission.to_csv("target.csv", index=False)

ban_id = df.loc[submission['target'] == 1, 'ID'].apply(lambda x: f"{x:03X}")
ban_id.to_csv("banned_id.txt", index=False, header=False)