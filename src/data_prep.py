import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def preprocess_basic(df):
    
    df = df.copy()
    
    cols_to_drop = ['customerID', 'gender', 'TotalCharges']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
    
    df = df.rename(columns={'tenure': 'Tenure'})
    
    retention_services = ['TechSupport', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection']
    if all(col in df.columns for col in retention_services):
        df['Security_Svc_Count'] = (df[retention_services] == 'Yes').sum(axis=1)
        df.drop(columns=retention_services, inplace=True)
        
    binary_features = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 
                       'MultipleLines', 'StreamingTV', 'StreamingMovies', 'SeniorCitizen', 'Churn']
    mapping = {'Yes': 1, 'No': 0, 'No internet service': 0, 'No phone service': 0}
    
    for col in binary_features:
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(0).astype(int)
            
    return df

class ChurnTransformer:
   
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
        self.limiar_faturamento = None
        self.one_hot_features = ['Contract', 'PaymentMethod', 'InternetService']
        self.numerical_features = ['Tenure', 'MonthlyCharges', 'Security_Svc_Count']

    def fit(self, df_train):
        self.limiar_faturamento = df_train['MonthlyCharges'].quantile(0.80)
        
        self.encoder.fit(df_train[self.one_hot_features])
        
        self.scaler.fit(df_train[self.numerical_features])

    def transform(self, df):
        df = df.copy()
        
        df['Is_Price_Shock'] = (df['MonthlyCharges'] > self.limiar_faturamento).astype(int)
        
        encoded_data = self.encoder.transform(df[self.one_hot_features])
        encoded_cols = self.encoder.get_feature_names_out(self.one_hot_features)
        df_encoded = pd.DataFrame(encoded_data, columns=encoded_cols, index=df.index)
        
        df = pd.concat([df.drop(self.one_hot_features, axis=1), df_encoded], axis=1)
        
        df[self.numerical_features] = self.scaler.transform(df[self.numerical_features])
        
        return df