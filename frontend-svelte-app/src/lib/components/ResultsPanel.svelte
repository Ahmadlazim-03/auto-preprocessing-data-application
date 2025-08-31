<script lang="ts">
	import RecommendationCard from './RecommendationCard.svelte';
	import type { Summary, ProcessedRow, ReadinessReport } from '$lib/types';

	export let summary: Summary | null;
	export let processedData: ProcessedRow[] | null;
	export let readinessReport: ReadinessReport | null;
	export let isLoading: boolean;
	export let errorMessage: string;
</script>

<section class="main-content">
	{#if errorMessage}
		<div class="card error-card">{errorMessage}</div>
	{/if}

	{#if !summary && !isLoading}
		<div class="card placeholder">
			<h3>Selamat Datang!</h3>
			<p>Silakan unggah file CSV di panel kiri untuk memulai analisis.</p>
		</div>
	{/if}

	{#if isLoading && !processedData}
		<div class="card placeholder">
			<div class="spinner large"></div>
			<p>Mohon tunggu...</p>
		</div>
	{/if}

	{#if summary && !processedData && !isLoading}
		<div class="card">
			<h4>💡 Rekomendasi Asisten</h4>
			{#if summary.recommendations.length > 0}
				<div class="recommendations-grid">
					{#each summary.recommendations as rec}
						<RecommendationCard recommendation={rec} />
					{/each}
				</div>
			{:else}
				<p>Tidak ada rekomendasi khusus untuk data ini. Semuanya terlihat bagus!</p>
			{/if}
		</div>
	{/if}

	{#if processedData && readinessReport}
		<div class="card">
			<h3>3. Hasil</h3>
			<slot name="actions" />

			<div class="report-card">
				<h4>📊 Rapor Kualitas Data</h4>
				<ul>
					<li>
						Sepenuhnya Numerik:
						<strong>{readinessReport.is_fully_numeric ? '✅ Ya' : '❌ Tidak'}</strong>
					</li>
					<li>
						Total Nilai Hilang:
						<strong
							>{readinessReport.total_missing_values === 0
								? '✅ 0'
								: `❌ ${readinessReport.total_missing_values}`}</strong
						>
					</li>
					<li>
						Dimensi Akhir:
						<strong
							>{readinessReport.final_shape.rows} baris x {readinessReport.final_shape.columns}
							kolom</strong
						>
					</li>
				</ul>
			</div>

			<h4>Pratinjau Data Olahan (50 Baris Pertama)</h4>
			<div class="table-container">
				<table>
					<thead>
						<tr>
							{#if processedData.length > 0}
								{#each Object.keys(processedData[0]) as header}
									<th>{header}</th>
								{/each}
							{/if}
						</tr>
					</thead>
					<tbody>
						{#each processedData.slice(0, 50) as row}
							<tr>
								{#each Object.values(row) as cell}
									<td>{typeof cell === 'number' ? cell.toFixed(3) : cell}</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</section>

<style>
	.main-content {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}
	.card {
		background-color: var(--bg-card);
		border: 1px solid var(--border-color);
		border-radius: var(--radius);
		padding: 1.5rem;
		box-shadow: var(--shadow);
	}
	.placeholder {
		text-align: center;
		padding: 3rem;
	}
	.error-card {
		background-color: #fee2e2;
		border-color: #fca5a5;
		color: #b91c1c;
	}
	.recommendations-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}
	.report-card {
		background-color: var(--bg-main);
		padding: 1rem;
		border-radius: var(--radius);
		margin-top: 1rem;
		margin-bottom: 1.5rem;
	}
	.report-card ul {
		list-style-type: none;
		padding-left: 0;
		margin: 0;
	}
	.table-container {
		max-height: 450px;
		overflow: auto;
		border: 1px solid var(--border-color);
		border-radius: var(--radius);
	}
	table {
		width: 100%;
		border-collapse: collapse;
	}
	th,
	td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid var(--border-color);
		font-size: 0.9rem;
	}
	th {
		background-color: var(--bg-light);
		position: sticky;
		top: 0;
	}
	tbody tr:nth-child(even) {
		background-color: var(--bg-light);
	}
	.spinner.large {
		width: 40px;
		height: 40px;
		border-left-color: var(--primary-color);
		margin: 1rem auto;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	@media (max-width: 900px) {
		.recommendations-grid {
			grid-template-columns: 1fr;
		}
	}
</style>