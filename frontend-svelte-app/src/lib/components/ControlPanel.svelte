<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Summary } from '$lib/types';

	export let summary: Summary | null;
	export let columnOptions: any;
	export let dateFeatures: any;
	export let isLoading: boolean;
	export let selectedFile: File | undefined;

	const dispatch = createEventDispatcher();
</script>

<aside class="control-panel">
	<div class="card">
		<h3>1. Unggah Data</h3>
		<p>Mulai dengan memilih file CSV.</p>
		<input
			type="file"
			id="file-upload"
			on:change={(e) => dispatch('fileSelect', e)}
			accept=".csv"
		/>
		<label for="file-upload" class="file-label">
			{#if selectedFile}{selectedFile.name}{:else}Pilih File{/if}
		</label>
	</div>

	{#if summary}
		<div class="card">
			<h3>Workflow</h3>
			<div class="workflow-actions">
				<button class="secondary" on:click={() => dispatch('saveRecipe')}>💾 Simpan Resep</button>
				<label class="button secondary">
					📤 Muat Resep
					<input
						type="file"
						on:change={(e) => dispatch('loadRecipe', e)}
						accept=".json"
						style="display: none;"
					/>
				</label>
			</div>
		</div>
		<div class="card">
			<h3>2. Opsi Preprocessing</h3>

			{#if summary.date_columns.length > 0}
				<h4 class="option-header">Kolom Tanggal</h4>
				{#each summary.date_columns as col}
					<div class="option-row-vertical">
						<strong>{col}</strong>
						<div class="checkbox-group" on:change={() => dispatch('change')}>
							<label><input type="checkbox" bind:group={dateFeatures[col]} value="year" />Tahun</label>
							<label><input type="checkbox" bind:group={dateFeatures[col]} value="month" />Bulan</label>
							<label><input type="checkbox" bind:group={dateFeatures[col]} value="day" />Hari</label>
							<label><input type="checkbox" bind:group={dateFeatures[col]} value="dayofweek" />Hari/Minggu</label>
							<label><input type="checkbox" bind:group={dateFeatures[col]} value="is_weekend" />Akhir Pekan</label>
						</div>
					</div>
				{/each}
			{/if}

			<h4 class="option-header">Kolom Numerik</h4>
			{#each summary.numeric_columns as col}
				<div class="option-row-vertical">
					<div class="col-header">
						<strong>{col}</strong>
						<span>(Missing: {summary.missing_values[col] || 0})</span>
						{#if summary.outlier_info[col] > 0}
							<span class="outlier-warning">(Outliers: {summary.outlier_info[col]})</span>
						{/if}
					</div>
					<div class="controls">
						<select
							bind:value={columnOptions[col].impute}
							on:change={() => dispatch('change')}
							title="Metode Imputasi"
						>
							<option value="mean">Isi Rata-rata</option>
							<option value="median">Isi Median</option>
						</select>
						<select
							bind:value={columnOptions[col].scale}
							on:change={() => dispatch('change')}
							title="Metode Penskalaan"
						>
							<option value="standard">Standard</option>
							<option value="minmax">Min-Max</option>
						</select>
						<select
							bind:value={columnOptions[col].outlier_method}
							on:change={() => dispatch('change')}
							class:active={columnOptions[col].outlier_method !== 'ignore'}
							title="Penanganan Outlier"
						>
							<option value="ignore">Biarkan</option>
							<option value="remove">Hapus</option>
							<option value="cap">Batasi</option>
						</select>
						<button
							class="icon-button"
							on:click={() => dispatch('visualize', col)}
							title="Lihat Visualisasi">📊</button
						>
					</div>
				</div>
			{/each}

			<button class="process-button" on:click={() => dispatch('process')} disabled={isLoading}>
				{#if isLoading}<div class="spinner"></div>Memperbarui...{:else}🔄 Perbarui Pratinjau{/if}
			</button>
		</div>
	{/if}
</aside>

<style>
	.card {
		background-color: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius);
		padding: 1.5rem;
		box-shadow: var(--shadow);
	}
	.card h3 {
		margin-top: 0;
	}
	.control-panel {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}
	input[type='file'] {
		display: none;
	}
	.file-label {
		display: block;
		text-align: center;
		padding: 0.75rem;
		background-color: var(--bg-main);
		border: 2px dashed var(--border-color);
		border-radius: var(--radius);
		cursor: pointer;
		transition: all 0.2s;
	}
	.file-label:hover {
		background-color: #eef2ff;
		border-color: var(--primary-color);
	}
	.workflow-actions {
		display: flex;
		gap: 1rem;
	}
	.button,
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
		justify-content: center;
		gap: 0.5rem;
	}
	.button.secondary,
	button.secondary {
		background-color: var(--secondary-color);
		color: white;
	}
	.button.secondary:hover {
		background-color: var(--secondary-hover);
	}
	.option-header {
		margin-top: 1.5rem;
		margin-bottom: 0.5rem;
		border-bottom: 1px solid var(--border-color);
		padding-bottom: 0.5rem;
	}
	.option-row-vertical {
		display: flex;
		flex-direction: column;
		padding: 0.75rem 0;
		border-bottom: 1px solid var(--border-color);
	}
	.col-header {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-bottom: 0.75rem;
		flex-wrap: wrap;
	}
	.col-info span {
		font-size: 0.8rem;
		color: var(--text-light);
	}
	.outlier-warning {
		background-color: #fef2f2;
		color: #ef4444;
		font-size: 0.75rem;
		font-weight: 500;
		padding: 0.1rem 0.4rem;
		border-radius: 99px;
	}
	.controls {
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}
	select {
		font-size: 0.8rem;
		padding: 0.4rem 0.6rem;
		border-radius: var(--radius);
		border: 1px solid var(--border-color);
		background-color: var(--bg-card);
		flex-grow: 1;
	}
	select.active {
		border-color: var(--primary-color);
		box-shadow: 0 0 0 1px var(--primary-color);
	}
	.checkbox-group {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem 1rem;
		margin-top: 0.5rem;
		font-size: 0.9rem;
	}
	.process-button {
		background-color: var(--primary-color);
		color: white;
		width: 100%;
		margin-top: 1.5rem;
		font-size: 1rem;
	}
	.process-button:hover {
		background-color: var(--primary-hover);
	}
	.process-button:disabled {
		background-color: #d1d5db;
		cursor: not-allowed;
	}
	.icon-button {
		background: none;
		border: none;
		font-size: 1.5rem;
		color: var(--text-light);
		padding: 0;
		cursor: pointer;
		transition: color 0.2s;
	}
	.icon-button:hover {
		color: var(--primary-color);
	}
	.spinner {
		border: 4px solid rgba(0, 0, 0, 0.1);
		width: 20px;
		height: 20px;
		border-radius: 50%;
		border-left-color: #fff;
		animation: spin 1s ease infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>