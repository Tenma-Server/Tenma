<template>
	<div>
		<app-header></app-header>
		<div>
			<router-view></router-view>
		</div>
	</div>
</template>

<script>
	import Header from './components/layout/Header'

	export default {
		components: {
			appHeader: Header
		}
	}
</script>

<style>
#app {
	font-family: 'Avenir', Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #2c3e50;
}
</style>
