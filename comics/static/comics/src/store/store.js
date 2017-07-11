import Vue from 'vue'
import Vuex from 'vuex'

// import arcs from './modules/arcs'
// import characters from './modules/characters'
import issues from './modules/issues'
// import publishers from './modules/publishers'
import series from './modules/series'
// import teams from './modules/teams'

Vue.use(Vuex)

export default new Vuex.Store({
	modules: {
		issues,
		series
	}
})
