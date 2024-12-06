import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import tensorflow as tf
import joblib
import re

def load_and_prepare_dataset(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    data = []

    for line in lines:
        match = re.match(r'\((\d+\.\d+)\)\s+vcan0\s+([0-9A-Fa-f]{3})#([0-9A-Fa-f]*\s+([0-9]))', line.strip())
        if match:
            timestamp = float(match.group(1))
            id_hex = int(match.group(2), 16)
            dlc_data = match.group(3)   #data field
            target_data = match.group(4)

            dlc_values = [dlc_data[i:i+2] if i<len(dlc_data) else np.nan for i in range(0, 16, 2)]
            data_len = sum(1 for value in dlc_values if pd.notna(value))
            data.append([timestamp, id_hex, data_len] + dlc_values + [target_data])

    columns = ['Timestamp', 'ID', 'LEN'] + [f'DLC{i}' for i in range(8)] + ['target']
    df = pd.DataFrame(data, columns=columns)
    #df = df.dropna()
    df = df.fillna('0')
    df['ID']=df['ID'].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    df = df.reset_index(drop=True)
    df['Timestamp']=df['Timestamp'] - df['Timestamp'][0]
    
    for i in range(8):
        df[f'DLC{i}'] = df[f'DLC{i}'].apply(lambda x: float(int(x, 16)))
    #df[['DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']] = df[['DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']].apply(pd.to_numeric, errors='coerce').astype(float)
    
    df['target'] = df['target'].apply(pd.to_numeric, errors='coerce')
    print(df.head(10))
    return df

# Preprocess the data
def preprocess_data(data):
    features = data[['Timestamp', 'ID', 'LEN', 'DLC0', 'DLC1', 'DLC2', 'DLC3', 'DLC4', 'DLC5', 'DLC6', 'DLC7']].values
    labels = data['target'].values
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    return features_scaled, labels, scaler

# Build the LSTM model
def build_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=input_shape),
        tf.keras.layers.LSTM(100, return_sequences=True, kernel_regularizer=tf.keras.regularizers.l2(0.01)),    #L2 正則化，用於防止過擬合，會對權重施加懲罰，值越大，正則化效果越強。
        tf.keras.layers.Dropout(0.2),   #隨機丟棄 20% 的神經元，減少過擬合
        tf.keras.layers.LSTM(50, kernel_regularizer=tf.keras.regularizers.l2(0.01)),    #第二個 LSTM 層，包含 50 個隱藏單元
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation='sigmoid')  #最後一層是全連接層，將 LSTM 的輸出映射到一個二元分類結果/輸出維度為 1，對應二元分類任務的最終輸出/論文中sigmoid表現最好
    ])
    optimizer = tf.keras.optimizers.Adam(clipvalue=1.0, learning_rate=0.001)    #論文中Adam/Nadam表現最好
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])    #loss用於二元分類問題，計算預測值與真實標籤之間的差異
    return model

normal_data_path = 'trainset.csv'
dos_data_path = 'trainset_dos.csv'

normal_data = load_and_prepare_dataset(normal_data_path)
dos_data = load_and_prepare_dataset(dos_data_path)
#print(normal_data.head(10))
# Combine the datasets
combined_data = pd.concat([normal_data, dos_data])

# Shuffle the combined dataset
combined_data = combined_data.sample(frac=1).reset_index(drop=True)

features_scaled, labels, scaler = preprocess_data(combined_data)

features_scaled = np.nan_to_num(features_scaled)    # 0代替NaN
features_scaled[np.isinf(features_scaled)] = 0  # 正負無窮

joblib.dump(scaler, 'scaler.joblib')

# Split data X_train=training data, y_train=trainig data's answer(target), X_test=testing data, y_test=testing data's answer
X_train, X_test, y_train, y_test = train_test_split(features_scaled, labels, test_size=0.2, random_state=42, stratify=labels)

#LSTM 層期望的輸入形狀為 (樣本數行數, timesteps表連續觀察幾個樣本, 特徵數)
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

#參數(timestamps, 特徵數)
model = build_model((X_train.shape[1], X_train.shape[2]))

# Add learning rate scheduler and early stopping
lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6)
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

history = model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.2, callbacks=[lr_scheduler, early_stopping])

loss, accuracy = model.evaluate(X_test, y_test)
print(f'Test Accuracy: {accuracy}')

y_pred = model.predict(X_test)
y_pred = (y_pred > 0.5).astype(int)

accuracy = accuracy_score(y_test, y_pred)
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
fpr = fp / (fp + tn)
fnr = fn / (fn + tp)

print(f'Accuracy: {accuracy}')
print(f'False Positive Rate: {fpr}')
print(f'False Negative Rate: {fnr}')

model.save('lstm_model.keras')
print("Model trained and saved as 'lstm_model.keras'")