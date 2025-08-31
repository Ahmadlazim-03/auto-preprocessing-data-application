<script lang="ts">
	import type { Recommendation } from '$lib/types';
	export let recommendation: Recommendation;
</script>

<div class="recommendation-card">
	<strong>{recommendation.type === 'SKEWNESS' ? 'Analisis Distribusi' : 'Rekayasa Fitur'}</strong>
	<p>{recommendation.message}</p>
</div>

<style>
	.recommendation-card {
		background-color: #eef2ff;
		border: 1px solid #c7d2fe;
		padding: 1rem;
		border-radius: var(--radius);
	}
    .recommendation-card strong {
        font-size: 0.9rem;
    }
	.recommendation-card p {
		margin: 0.5rem 0 0 0;
		font-size: 0.9rem;
        color: var(--text-dark);
        line-height: 1.5;
	}
</style>