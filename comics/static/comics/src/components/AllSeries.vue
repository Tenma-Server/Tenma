<template lang="html">
	<div class="all-series">
		<ul>
			<app-card v-for="item in allSeries" :item="item" :key="item.id">
			</app-card>
		</ul>
	</div>
</template>

<script>
	import Card from './shared/Card.vue'

	export default {
		computed: {
			allSeries () {
				return this.$store.getters.series
			}
		},
		components: {
			appCard: Card
		},
		mounted () {
			this.$store.dispatch('LOAD_SERIES')
		}
	}
</script>

<style lang="css">
</style>
