<template lang="html">
	<div class="series">
		<img :src="'http://127.0.0.1:8000/' + series.image">
		<h1>{{ series.name }}</h1>
		<div v-html="series.desc"></div>
	</div>
</template>

<script>
export default {
	computed: {
		series () {
			return this.$store.getters.getSeriesById(this.$route.params.id)
		}
	}
}
</script>

<style>
</style>
