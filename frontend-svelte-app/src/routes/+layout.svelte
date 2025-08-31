<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import '../app.css';
</script>

<div class="app-layout">
	<Sidebar />
	<div class="main-view">
		<slot />
	</div>
</div>

<style>
	.app-layout {
		display: flex;
	}
	.main-view {
		flex-grow: 1;
		margin-left: 250px; /* Lebar sidebar */
		padding: 0;
	}

	@media (max-width: 768px) {
		.main-view {
			margin-left: 0;
		}
		/* Di aplikasi nyata, Anda mungkin akan menyembunyikan sidebar di mobile */
	}
</style>