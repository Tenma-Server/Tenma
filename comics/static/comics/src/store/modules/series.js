import { http } from '@/http/http'

const state = {
	series: []
}

const mutations = {
	'SET_SERIES' (state, { list }) {
		state.series = list
	}
}

const actions = {
	LOAD_SERIES: ({commit}) => {
		http.get('series?format=json')
		.then(response => {
			commit('SET_SERIES', { list: response.data })
		})
		.catch(e => {
			console.log(e)
		})
	}
}

const getters = {
	series: state => {
		return state.series
	},
	getSeriesById: (state, getters) => (id) => {
		return state.series.find(s => s.id === id)
	}
}

export default {
	state,
	mutations,
	actions,
	getters
}
