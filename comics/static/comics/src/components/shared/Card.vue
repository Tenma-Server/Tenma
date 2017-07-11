<template lang="html">
	<div class="card">
		<img :src="'/' + item.image">
		<router-link :to="{ name: 'Series', params: { id: item.id }}">More...</router-link>
		<p>{{ item.name }}</p>
		<p v-if="item.number">Issue #{{ item.number }}</p>
	</div>
</template>

<script>
	export default {
		props: ['item']
	}
</script>

<style lang="css" scoped>
	.card {
		display: inline-block;
		width: 200px;
		height: auto;
	}

	img {
		width: 90%;
	}
</style>
