// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'
import { routes } from './router/routes'
import store from './store/store'

Vue.use(VueRouter)

Vue.config.productionTip = false

const router = new VueRouter({
	routes
})

/* eslint-disable no-new */
new Vue({
	el: '#app',
	router,
	store,
	render: h => h(App)
})
