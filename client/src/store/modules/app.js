import axios from 'axios'
import Cookies from 'js-cookie'

// initial state
const state = () => ({
  isLoggedIn: Cookies.get('csrf_access_token') !== undefined
})

// getters
const getters = {
  isLoggedIn: state => state.isLoggedIn
}

// actions
const actions = {
  init({ commit }, settings) {
    commit('init', settings)
  },
  login({ commit }, user) {
    return new Promise((resolve, reject) => {
      axios.post('/login', user)
        .then(response => {
          if (response.status == 200) {
            axios.defaults.headers.common['X-CSRF-TOKEN'] = Cookies.get('csrf_access_token')
            commit('auth')
          }
          resolve(response)
        })
        .catch(error => {
          commit('logout')
          Cookies.remove('csrf_access_token')
          reject(error)
        })
    })
  },
  logout({ commit }) {
    return new Promise((resolve) => {
      axios.post('/logout').finally(() => {
        commit('logout')
        Cookies.remove('csrf_access_token')
        delete axios.defaults.headers.common['X-CSRF-TOKEN']
        resolve()
      })
    })
  }
}

// mutations
const mutations = {
  auth(state) {
    state.isLoggedIn = true
  },
  logout(state) {
    state.isLoggedIn = false
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}