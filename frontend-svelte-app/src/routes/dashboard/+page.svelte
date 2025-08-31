<script lang="ts">
	import ControlPanel from '$lib/components/ControlPanel.svelte';
	import ResultsPanel from '$lib/components/ResultsPanel.svelte';
	import Modal from '$lib/components/Modal.svelte';
	import type { Summary, ProcessedRow, ReadinessReport } from '$lib/types';
	import { debounce } from 'lodash-es';

	let selectedFile: File | undefined;
	let summary: Summary | null = null;
	let columnOptions: any = {};
	let dateFeatures: Record<string, string[]> = {};
	let processedData: ProcessedRow[] | null = null;
	let readinessReport: ReadinessReport | null = null;
	let isLoading = false;
	let isPreviewLoading = false;
	let errorMessage = '';
	let modalImageUrl: string | null = null;
	let isVisualizing = false;

	const updatePreview = debounce(async () => {
		if (!selectedFile) return;

		isPreviewLoading = true;
		errorMessage = '';

		const optionsPayload = {
			column_options: columnOptions,
			date_features: dateFeatures
		};

		const formData = new FormData();
		formData.append('dataset', selectedFile);
		formData.append('options', JSON.stringify(optionsPayload));
		try {
			const res = await fetch('http://localhost:3000/api/preprocess', {
				method: 'POST',
				body: formData
			});
			if (!res.ok) {
				const err = await res.json();
				throw new Error(err.error || 'Gagal memuat pratinjau.');
			}
			const result = await res.json();
			processedData = result.processed_data;
			readinessReport = result.readiness_report;
		} catch (error: any) {
			errorMessage = error.message;
		} finally {
			isPreviewLoading = false;
		}
	}, 800);

	function initializeOptions(summaryData: Summary) {
		let newColOpts: any = {};
		summaryData.numeric_columns.forEach((col) => {
			newColOpts[col] = { impute: 'median', scale: 'standard', outlier_method: 'ignore' };
		});
		columnOptions = newColOpts;

		let newDateFeats: Record<string, string[]> = {};
		summaryData.date_columns.forEach((col) => {
			newDateFeats[col] = ['year', 'month', 'day', 'dayofweek', 'is_weekend'];
		});
		dateFeatures = newDateFeats;
	}

	async function handleFileSelect(event: CustomEvent) {
		const originalEvent = event.detail;
		const target = originalEvent.target as HTMLInputElement;
		selectedFile = target.files?.[0];
		if (!selectedFile) return;

		summary = null;
		processedData = null;
		readinessReport = null;
		errorMessage = '';
		isLoading = true;

		const formData = new FormData();
		formData.append('dataset', selectedFile);
		try {
			const res = await fetch('http://localhost:3000/api/summarize', {
				method: 'POST',
				body: formData
			});
			if (!res.ok) {
				const err = await res.json();
				throw new Error(err.error || 'Gagal memuat ringkasan.');
			}
			summary = await res.json();
			if (summary) {
				initializeOptions(summary);
				updatePreview();
			}
		} catch (error: any) {
			errorMessage = error.message;
		} finally {
			isLoading = false;
		}
	}

	function saveRecipe() {
		if (!summary) {
			errorMessage = 'Unggah dan analisis file terlebih dahulu sebelum menyimpan resep.';
			return;
		}
		const recipe = {
			column_options: columnOptions,
			date_features: dateFeatures
		};
		const blob = new Blob([JSON.stringify(recipe, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.setAttribute('href', url);
		a.setAttribute('download', 'autoprep_recipe.json');
		a.click();
		URL.revokeObjectURL(url);
	}

	function handleRecipeUpload(event: CustomEvent) {
		const originalEvent = event.detail;
		const target = originalEvent.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;

		const reader = new FileReader();
		reader.onload = (e) => {
			try {
				const recipe = JSON.parse(e.target?.result as string);
				if (recipe.column_options) columnOptions = recipe.column_options;
				if (recipe.date_features) dateFeatures = recipe.date_features;
				alert('Resep berhasil dimuat! Pratinjau akan diperbarui.');
				updatePreview();
			} catch (err) {
				errorMessage = 'File resep tidak valid.';
			}
		};
		reader.readAsText(file);
		target.value = '';
	}

	function downloadCSV() {
		if (!processedData || processedData.length === 0) return;
		const headers = Object.keys(processedData[0]);
		const csvRows = [headers.join(',')];
		for (const row of processedData) {
			const values = headers.map((header) => {
				const escaped = ('' + row[header]).replace(/"/g, '\\"');
				return `"${escaped}"`;
			});
			csvRows.push(values.join(','));
		}
		const csvString = csvRows.join('\n');
		const blob = new Blob([csvString], { type: 'text/csv' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.setAttribute('href', url);
		a.setAttribute('download', 'processed_data.csv');
		a.click();
	}

	async function handleExportCode() {
		if (!selectedFile) {
			errorMessage = 'Pilih file terlebih dahulu.';
			return;
		}
		const optionsPayload = {
			column_options: columnOptions,
			date_features: dateFeatures
		};
		const formData = new FormData();
		formData.append('dataset', selectedFile);
		formData.append('options', JSON.stringify(optionsPayload));
		try {
			const response = await fetch('http://localhost:3000/api/export-code', {
				method: 'POST',
				body: formData
			});
			if (!response.ok) {
				throw new Error('Gagal membuat skrip kode.');
			}
			const codeScript = await response.text();
			const blob = new Blob([codeScript], { type: 'text/plain' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.setAttribute('href', url);
			a.setAttribute('download', 'preprocessing_pipeline.py');
			a.click();
		} catch (error: any) {
			errorMessage = error.message;
		}
	}

	async function showVisualization(columnName: string) {
		if (!selectedFile) return;
		isVisualizing = true;
		modalImageUrl = null;
		errorMessage = '';
		const transformType = columnOptions[columnName]?.scale || 'standard';
		const formData = new FormData();
		formData.append('dataset', selectedFile);
		formData.append('column_name', columnName);
		formData.append('transform_type', transformType);
		try {
			const res = await fetch('http://localhost:3000/api/visualize-transform', {
				method: 'POST',
				body: formData
			});
			if (!res.ok) {
				throw new Error('Gagal membuat visualisasi.');
			}
			const imageBlob = await res.blob();
			modalImageUrl = URL.createObjectURL(imageBlob);
		} catch (error: any) {
			errorMessage = error.message;
		} finally {
			isVisualizing = false;
		}
	}

	function closeModal() {
		if (modalImageUrl) {
			URL.revokeObjectURL(modalImageUrl);
			modalImageUrl = null;
		}
	}
</script>

<div class="dashboard-container">
	<main class="dashboard-grid">
		<ControlPanel
			{summary}
			bind:columnOptions
			bind:dateFeatures
			isLoading={isLoading || isPreviewLoading}
			{selectedFile}
			on:fileSelect={handleFileSelect}
			on:process={updatePreview}
			on:change={updatePreview}
			on:visualize={(e) => showVisualization(e.detail)}
			on:saveRecipe={saveRecipe}
			on:loadRecipe={handleRecipeUpload}
		/>

		<ResultsPanel
			{summary}
			{processedData}
			{readinessReport}
			isLoading={isLoading || isPreviewLoading}
			{errorMessage}
		>
			<div slot="actions" class="button-area">
				<button on:click={downloadCSV} disabled={!processedData}>📥 Unduh CSV</button>
				<button class="secondary" on:click={handleExportCode} disabled={!processedData}>
					📜 Ekspor Kode
				</button>
			</div>
		</ResultsPanel>
	</main>
</div>

{#if modalImageUrl || isVisualizing}
	<Modal isLoading={isVisualizing} imageUrl={modalImageUrl} on:close={closeModal} />
{/if}

<style>
	.dashboard-container {
		padding: 2rem;
	}
	.dashboard-grid {
		display: grid;
		grid-template-columns: 400px 1fr;
		gap: 2rem;
	}
	.button-area {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
	}
	button {
		font-size: 0.9rem;
		padding: 0.6rem 1.2rem;
		border-radius: var(--radius);
		border: none;
		font-weight: 500;
		cursor: pointer;
		transition: background-color 0.2s;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		background-color: var(--primary-color);
		color: white;
	}
	button.secondary {
		background-color: var(--secondary-color);
	}
	button:disabled {
		background-color: #d1d5db;
		cursor: not-allowed;
	}
	@media (max-width: 1200px) {
		.dashboard-grid {
			grid-template-columns: 350px 1fr;
		}
	}
	@media (max-width: 900px) {
		.dashboard-grid {
			grid-template-columns: 1fr;
		}
	}
</style>