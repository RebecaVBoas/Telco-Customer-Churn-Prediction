import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.base import BaseEstimator, TransformerMixin
import sklearn

sklearn.set_config(transform_output="pandas")


class BasicDataCleaner(BaseEstimator, TransformerMixin):
    """
    Realiza a limpeza inicial e a criação de features que NÃO dependem 
    de estatísticas dos dados de treino (ex: não usa média, quantil, etc).
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy() 
        
        cols_to_drop = ['customerID', 'gender', 'TotalCharges']
        df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
        
        df = df.rename(columns={'tenure': 'Tenure'})
        
        
        retention_services = ['TechSupport', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection']
        existing_services = [col for col in retention_services if col in df.columns]
        
        if len(existing_services) == len(retention_services):
            df['Security_Svc_Count'] = (df[existing_services] == 'Yes').sum(axis=1)
            df = df.drop(columns=existing_services)
            
        
        binary_features = ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 
                           'MultipleLines', 'StreamingTV', 'StreamingMovies']
        mapping = {'Yes': 1, 'No': 0, 'No internet service': 0, 'No phone service': 0}
        
        for col in binary_features:
            if col in df.columns:
                df[col] = df[col].map(mapping).fillna(0).astype(int)
                
        return df


class PriceShockTransformer(BaseEstimator, TransformerMixin):
    """
    Cria a feature Is_Price_Shock. Como ela depende de um quantil, 
    PRECISAMOS calcular isso no fit (dados de treino) e aplicar no transform.
    """
    def __init__(self):
        self.limiar_faturamento = None

    def fit(self, X, y=None):
       
        self.limiar_faturamento = X['MonthlyCharges'].quantile(0.80)
        return self

    def transform(self, X):
        df = X.copy()
        
        df['Is_Price_Shock'] = (df['MonthlyCharges'] > self.limiar_faturamento).astype(int)
        return df


one_hot_cols = ['Contract', 'PaymentMethod', 'InternetService']
num_cols = ['Tenure', 'MonthlyCharges', 'Security_Svc_Count'] 


preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), one_hot_cols)
    ],
    remainder='passthrough' 
)


meu_pipeline = Pipeline(steps=[
    ('cleaner', BasicDataCleaner()),
    ('price_shock', PriceShockTransformer()),
    ('preprocessor', preprocessor)
])