// src/lib/types.ts
export interface Recommendation {
	column?: string;
	type: string;
	message: string;
}

export interface Summary {
	filename: string;
	rows: number;
	columns: number;
	numeric_columns: string[];
	missing_values: Record<string, number>;
	preview: Record<string, unknown>[];
	recommendations: Recommendation[];
	outlier_info: Record<string, number>;
	date_columns: string[];
}

export type ProcessedRow = Record<string, string | number>;

export interface ReadinessReport {
	total_missing_values: number;
	is_fully_numeric: boolean;
	final_shape: { rows: number; columns: number };
}