import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

UPLOAD_FOLDER = "uploads"

def read_csv_files():
    all_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.csv'):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            df = pd.read_csv(file_path)
            all_data.append(df)
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame(columns=["id", "local", "uv", "data", "hora"])

def preprocess_data(data):
    data['datetime'] = pd.to_datetime(data['data'] + ' ' + data['hora'], dayfirst=True, format='%d/%m/%Y %H:%M:%S')
    data['date'] = pd.to_datetime(data['data'], dayfirst=True, format='%d/%m/%Y')
    data['dayofyear'] = data['date'].dt.dayofyear
    return data

def generate_predictions():
    data = read_csv_files()
    if data.empty:
        return "<p>No data to process</p>"
    
    data = preprocess_data(data)
    
    html_table = "<table><tr><th>Local</th><th>Previsão UV para amanhã (W/M²)</th></tr>"
    tomorrow = (datetime.now() + timedelta(days=1)).timetuple().tm_yday

    for local in data['local'].unique():
        local_data = data[data['local'] == local]
        if len(local_data) < 2:
            continue
        
        X = local_data['dayofyear'].values.reshape(-1, 1)
        y = local_data['uv'].values

        model = LinearRegression()
        model.fit(X, y)
        
        predicted_uv = model.predict([[tomorrow]])[0]
        
        html_table += f"<tr><td>{local}</td><td>{predicted_uv:.2f}</td></tr>"

    html_table += "</table>"
    return html_table

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    html_result = generate_predictions()
    print(html_result)
