import pandas as pd
from sklearn.model_selection import cross_validate, StratifiedKFold

def evaluate_models(X, y, models, n_splits=5, random_state=42):
    """
    Realiza Cross-Validation em uma lista de modelos e retorna um DataFrame comparativo.
    
    Parâmetros:
    - X, y: Features e Target (NumPy arrays ou DataFrames)
    - models: Dicionário { "Nome": instancia_do_modelo }
    - n_splits: Quantidade de dobras para o StratifiedKFold
    """
    
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    results = []
    
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']

    for name, model in models.items():
        print(f"Avaliando {name}...")
        
        cv_results = cross_validate(
            model, X, y, 
            cv=skf, 
            scoring=scoring, 
            n_jobs=-1 
        )
        
        results.append({
            "Model": name,
            "Recall": cv_results['test_recall'].mean(),
            "Precision": cv_results['test_precision'].mean(),
            "F1-Score": cv_results['test_f1'].mean(),
            "ROC-AUC": cv_results['test_roc_auc'].mean(),
            "Accuracy": cv_results['test_accuracy'].mean()
        })

    df_results = pd.DataFrame(results).sort_values(by="Recall", ascending=False)
    
    return df_results