import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer

def handle_outliers(df: pd.DataFrame, options: dict) -> pd.DataFrame:
    df_out = df.copy()
    column_options = options.get('column_options', {})

    for col in df_out.select_dtypes(include=np.number).columns:
        if col not in column_options:
            continue
            
        col_opts = column_options.get(col, {})
        method = col_opts.get('outlier_method', 'ignore')

        if method == 'ignore':
            continue

        Q1 = df_out[col].quantile(0.25)
        Q3 = df_out[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        if method == 'remove':
            df_out = df_out[(df_out[col] >= lower_bound) & (df_out[col] <= upper_bound)]
        elif method == 'cap':
            df_out[col] = np.clip(df_out[col], lower_bound, upper_bound)
            
    return df_out.reset_index(drop=True)

def engineer_date_features(df: pd.DataFrame, options: dict) -> pd.DataFrame:
    df_out = df.copy()
    date_options = options.get('date_features', {})

    for col, features_to_extract in date_options.items():
        if not features_to_extract or col not in df_out.columns:
            continue
        
        datetime_col = pd.to_datetime(df_out[col], errors='coerce')

        if 'year' in features_to_extract: df_out[f'{col}_year'] = datetime_col.dt.year
        if 'month' in features_to_extract: df_out[f'{col}_month'] = datetime_col.dt.month
        if 'day' in features_to_extract: df_out[f'{col}_day'] = datetime_col.dt.day
        if 'dayofweek' in features_to_extract: df_out[f'{col}_dayofweek'] = datetime_col.dt.dayofweek
        if 'is_weekend' in features_to_extract: df_out[f'{col}_is_weekend'] = (datetime_col.dt.dayofweek >= 5).astype(int)

        df_out.drop(columns=[col], inplace=True)
    return df_out

def auto_preprocess_data(df: pd.DataFrame, options: dict) -> pd.DataFrame:
    processed_df = df.copy()
    column_options = options.get('column_options', {})
    
    processed_df = handle_outliers(processed_df, options)
    processed_df = engineer_date_features(processed_df, options)

    numeric_cols = processed_df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = processed_df.select_dtypes(include=['object', 'category']).columns.tolist()

    for col in numeric_cols:
        col_opts = column_options.get(col, {})
        impute_strategy = col_opts.get('impute', 'median')
        if processed_df[col].isnull().sum() > 0:
            imputer = SimpleImputer(strategy=impute_strategy)
            processed_df[[col]] = imputer.fit_transform(processed_df[[col]])

        scale_strategy = col_opts.get('scale', 'standard')
        if scale_strategy != 'none' and col in column_options:
             if scale_strategy == 'minmax': scaler = MinMaxScaler()
             else: scaler = StandardScaler()
             processed_df[[col]] = scaler.fit_transform(processed_df[[col]])

    if categorical_cols:
        imputer_cat = SimpleImputer(strategy='most_frequent')
        processed_df[categorical_cols] = imputer_cat.fit_transform(processed_df[categorical_cols])
        
        cols_to_encode = [col for col in categorical_cols if processed_df[col].nunique() < 20]
        cols_to_drop = [col for col in categorical_cols if col not in cols_to_encode]
        processed_df.drop(columns=cols_to_drop, inplace=True)
        if cols_to_encode:
            processed_df = pd.get_dummies(processed_df, columns=cols_to_encode, drop_first=True)

    return processed_df