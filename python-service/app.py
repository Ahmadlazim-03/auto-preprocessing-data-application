import pandas as pd
import numpy as np
import json
import io
from flask import Flask, request, jsonify, Response, send_file
from preprocessor import auto_preprocess_data
from scipy.stats import skew
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

def generate_readiness_report(df: pd.DataFrame) -> dict:
    report = {}
    report['total_missing_values'] = int(df.isnull().sum().sum())
    report['data_types'] = df.dtypes.apply(lambda x: x.name).to_dict()
    is_fully_numeric = all(np.issubdtype(dtype, np.number) for dtype in df.dtypes)
    report['is_fully_numeric'] = bool(is_fully_numeric)
    describe_stats = df.describe().round(3).to_dict()
    report['describe_stats'] = describe_stats
    report['final_shape'] = {'rows': df.shape[0], 'columns': df.shape[1]}
    report['final_columns'] = df.columns.tolist()
    return report

@app.route('/summarize', methods=['POST'])
def summarize_file():
    if 'dataset' not in request.files:
        return jsonify({"error": "File tidak ditemukan"}), 400
    
    file = request.files['dataset']
    try:
        df = pd.read_csv(file)
        
        recommendations = []
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        outlier_info = {}
        date_columns = []

        for col in numeric_cols:
            s = skew(df[col].dropna())
            if abs(s) > 1.0:
                recommendations.append({'column': col, 'type': 'SKEWNESS', 'message': f"Distribusi kolom '{col}' sangat miring (skewness: {s:.2f})."})
            
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outlier_count = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
            outlier_info[col] = int(outlier_count)

        if 'SibSp' in df.columns and 'Parch' in df.columns:
            recommendations.append({'type': 'FEATURE_ENGINEERING', 'message': "Gabungkan 'SibSp' dan 'Parch' untuk membuat 'FamilySize'."})
        
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() > 0:
                try:
                    if pd.to_datetime(df[col], errors='coerce').notna().sum() / len(df) > 0.7:
                        date_columns.append(col)
                except Exception:
                    continue

        df_preview = df.head().replace({np.nan: None})
        missing_values = {col: int(val) for col, val in df.isnull().sum().items()}

        summary = {
            "filename": file.filename, "rows": df.shape[0], "columns": df.shape[1],
            "numeric_columns": numeric_cols, "missing_values": missing_values,
            "preview": df_preview.to_dict(orient='records'), "recommendations": recommendations,
            "outlier_info": outlier_info, "date_columns": date_columns
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process', methods=['POST'])
def process_file():
    if 'dataset' not in request.files:
        return jsonify({"error": "File tidak ditemukan"}), 400
        
    file = request.files['dataset']
    options_str = request.form.get('options', '{}')
    
    try:
        options = json.loads(options_str)
        df_kotor = pd.read_csv(file)
        df_bersih = auto_preprocess_data(df_kotor, options)
        readiness_report = generate_readiness_report(df_bersih)
        final_response = {
            "processed_data": df_bersih.to_dict(orient='records'),
            "readiness_report": readiness_report
        }
        return jsonify(final_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/export-code', methods=['POST'])
def export_code():
    if 'dataset' not in request.files:
        return Response("File tidak ditemukan", status=400, mimetype='text/plain')

    file = request.files['dataset']
    options_str = request.form.get('options', '{}')
    
    try:
        options = json.loads(options_str)
        file.stream.seek(0)
        df = pd.read_csv(file)
        
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        cols_to_encode = [col for col in categorical_cols if df[col].nunique() < 20]
        
        column_options = options.get('column_options', {})
        impute_strategy_num = 'median'
        scale_strategy = 'standard'
        if numeric_cols and column_options.get(numeric_cols[0]):
            impute_strategy_num = column_options[numeric_cols[0]].get('impute', 'median')
            scale_strategy = column_options[numeric_cols[0]].get('scale', 'standard')

        scaler_class = "StandardScaler" if scale_strategy == 'standard' else "MinMaxScaler"

        python_code = f"""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder

try:
    df = pd.read_csv('{file.filename}')
except FileNotFoundError:
    print("File '{file.filename}' tidak ditemukan. Pastikan file berada di direktori yang benar.")
    exit()

TARGET_COLUMN = 'ganti_dengan_kolom_target_anda' 

if TARGET_COLUMN in df.columns:
    X = df.drop(TARGET_COLUMN, axis=1)
    y = df[TARGET_COLUMN]
else:
    X = df
    print(f"Peringatan: Kolom target '{{TARGET_COLUMN}}' tidak ditemukan. Seluruh data akan diproses.")

numeric_features = {numeric_cols}
categorical_features = {cols_to_encode}

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='{impute_strategy_num}')),
    ('scaler', {scaler_class}())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ],
    remainder='passthrough'
)

X_processed = preprocessor.fit_transform(X)

try:
    ohe_feature_names = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_features).tolist()
    remainder_features = [col for col in X.columns if col not in numeric_features and col not in categorical_features]
    processed_columns = numeric_features + ohe_feature_names + remainder_features
    X_processed_df = pd.DataFrame(X_processed, columns=processed_columns)
except ValueError:
    X_processed_df = pd.DataFrame(X_processed)


print("Preprocessing Selesai.")
print("Bentuk data setelah diproses:", X_processed_df.shape)
print("\\nData setelah diproses (5 baris pertama):")
print(X_processed_df.head())
"""
        return Response(
            python_code.strip(),
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment;filename=preprocessing_pipeline.py'}
        )
    except Exception as e:
        return Response(f"Gagal membuat kode: {e}", status=500, mimetype='text/plain')

@app.route('/visualize-transform', methods=['POST'])
def visualize_transform():
    if 'dataset' not in request.files:
        return Response("File tidak ditemukan", status=400)

    file = request.files['dataset']
    column_name = request.form.get('column_name')
    transform_type = request.form.get('transform_type')

    if not all([file, column_name, transform_type]):
        return Response("Parameter tidak lengkap", status=400)

    try:
        df = pd.read_csv(file)
        original_data = df[column_name].dropna()
        data_to_transform = original_data.values.reshape(-1, 1)

        if transform_type == 'standard':
            scaler = StandardScaler()
        elif transform_type == 'minmax':
            scaler = MinMaxScaler()
        else:
            return Response(f"Tipe transformasi tidak dikenal: {transform_type}", status=400)
            
        transformed_data = scaler.fit_transform(data_to_transform)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle(f'Distribusi Kolom "{column_name}"', fontsize=16)
        sns.histplot(original_data, kde=True, ax=axes[0])
        axes[0].set_title('Sebelum Transformasi')
        sns.histplot(transformed_data, kde=True, ax=axes[1])
        axes[1].set_title(f'Sesudah {scaler.__class__.__name__}')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)

        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return Response(f"Gagal membuat visualisasi: {e}", status=500)

if __name__ == '__main__':
    app.run(port=5001, debug=True)