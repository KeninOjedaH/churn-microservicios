import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def cargar_datos(ruta_excel):
    """Carga y preprocesa los datos desde un archivo Excel."""
    df = pd.read_excel(ruta_excel)
    if "msisdn" in df.columns:
        df = df.drop(columns=["msisdn"])
    return df

def preparar_datos(df):
    """Prepara X e y para el entrenamiento del modelo."""
    df["flag_churn"] = df["flag_churn"].map({"No": 0, "Sí": 1, "Si": 1})
    X = df.drop(columns=["flag_churn"])
    y = df["flag_churn"]
    return X, y

def construir_pipeline(X):
    """Crea un pipeline con preprocesamiento y modelo Naive Bayes."""
    columnas_numericas = X.select_dtypes(include=[np.number]).columns.tolist()
    columnas_categoricas = X.select_dtypes(include=["object"]).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, columnas_numericas),
            ("cat", categorical_transformer, columnas_categoricas)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", GaussianNB())
    ])

    return pipeline

def entrenar_evaluar_y_guardar_modelo(X, y, ruta_modelo):
    """Entrena, evalúa y guarda el modelo bayesiano."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    pipeline = construir_pipeline(X)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\n📋 Reporte de clasificación (Bayesiano):")
    print(classification_report(y_test, y_pred))
    print("🧮 Matriz de confusión:")
    print(confusion_matrix(y_test, y_pred))

    joblib.dump(pipeline, ruta_modelo)
    print(f"\n💾 Modelo bayesiano guardado en: {ruta_modelo}")

def main():
    ruta_excel = "modelo_churn_entrenamiento.xlsx"
    ruta_salida_modelo = "agente_bayesiano_churn.joblib"  # ahora sí es bayesiano de verdad

    if not os.path.exists(ruta_excel):
        print(f"Error: No se encontró el archivo {ruta_excel}")
        return

    df = cargar_datos(ruta_excel)
    X, y = preparar_datos(df)
    entrenar_evaluar_y_guardar_modelo(X, y, ruta_salida_modelo)

if __name__ == "__main__":
    main()
