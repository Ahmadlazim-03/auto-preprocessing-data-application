<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';

	export let isLoading: boolean = false;
	export let imageUrl: string | null = null;

	const dispatch = createEventDispatcher();
	let modalElement: HTMLDivElement;

	function closeModal() {
		dispatch('close');
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			closeModal();
		}
	}

	onMount(() => {
		modalElement.focus();
	});
</script>

<svelte:window on:keydown={handleKeydown} />

<div
	bind:this={modalElement}
	class="modal-backdrop"
	on:click={closeModal}
	role="dialog"
	aria-modal="true"
	tabindex="-1"
>
	<div class="modal-content" on:click|stopPropagation role="document">
		{#if isLoading}
			<div class="spinner large"></div>
			<p>Membuat plot...</p>
		{:else if imageUrl}
			<img src={imageUrl} alt="Visualisasi Transformasi Data" />
		{/if}
		<button class="close-button" on:click={closeModal} aria-label="Tutup modal">×</button>
	</div>
</div>

<style>
	.modal-backdrop {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.6);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 100;
	}
	.modal-content {
		background-color: white;
		padding: 2rem;
		border-radius: var(--radius);
		position: relative;
		max-width: 90%;
		max-height: 90%;
		text-align: center;
		box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
	}
	.modal-content img {
		max-width: 100%;
		max-height: 80vh;
	}
	.close-button {
		position: absolute;
		top: 10px;
		right: 15px;
		background: none;
		border: none;
		font-size: 2rem;
		cursor: pointer;
		color: #333;
		line-height: 1;
	}
	.spinner {
		border: 4px solid rgba(0, 0, 0, 0.1);
		width: 20px;
		height: 20px;
		border-radius: 50%;
		border-left-color: #fff;
		animation: spin 1s ease infinite;
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
</style>