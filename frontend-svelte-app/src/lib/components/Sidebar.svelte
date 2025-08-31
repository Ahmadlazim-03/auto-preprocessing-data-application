<script lang="ts">
	import { page } from '$app/stores';
</script>

<nav class="sidebar">
	<div class="sidebar-header">
		<h2>🚀 AutoPrep</h2>
	</div>
	<ul class="nav-links">
		<li>
			<a href="/" class:active={$page.url.pathname === '/'}>🏠 Home</a>
		</li>
		<li>
			<a href="/dashboard" class:active={$page.url.pathname === '/dashboard'}>📊 Dashboard</a>
		</li>
		<li>
			<a href="/about" class:active={$page.url.pathname === '/about'}>ℹ️ About</a>
		</li>
	</ul>
</nav>

<style>
	.sidebar {
		background-color: #111827;
		color: #d1d5db;
		display: flex;
		flex-direction: column;
		width: 250px;
		height: 100vh;
		position: fixed;
		top: 0;
		left: 0;
		border-right: 1px solid var(--border-color);
	}
	.sidebar-header {
		padding: 1.5rem;
		border-bottom: 1px solid #374151;
	}
	.sidebar-header h2 {
		margin: 0;
		color: #fff;
		font-size: 1.5rem;
	}
	.nav-links {
		list-style: none;
		padding: 0;
		margin: 1rem 0;
	}
	.nav-links a {
		display: block;
		padding: 0.75rem 1.5rem;
		color: #d1d5db;
		text-decoration: none;
		border-left: 3px solid transparent;
		transition: all 0.2s ease-in-out;
		font-weight: 500;
	}
	.nav-links a:hover {
		background-color: #374151;
		color: #fff;
	}
	.nav-links a.active {
		border-left-color: var(--primary-color);
		background-color: #1f2937;
		color: #fff;
	}
</style>