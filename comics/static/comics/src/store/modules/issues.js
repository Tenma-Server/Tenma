import { http } from '@/http/http'

const state = {
	issues: []
}

const mutations = {
	'SET_ISSUES' (state, { list }) {
		state.issues = list
	}
}

const actions = {
	LOAD_ISSUES: ({commit}) => {
		http.get('issues?format=json')
		.then(response => {
			commit('SET_ISSUES', { list: response.data })
		})
		.catch(e => {
			console.log(e)
		})
	}
}

const getters = {
	issues: state => {
		return state.issues
	}
}

export default {
	state,
	mutations,
	actions,
	getters
}
