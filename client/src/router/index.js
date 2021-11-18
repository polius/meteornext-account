import Vue from 'vue'
import VueRouter from 'vue-router'
import store from './../store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/register',
    name: 'register',
    props: true,
    component: () => import('../components/Register')
  },
  {
    path: '/login',
    name: 'login',
    props: true,
    component: () => import('../components/Login')
  },
  {
    path: '/verify_email/:code',
    name: 'verifyEmail',
    component: () => import('../components/mail/VerifyEmail'),
  },
  {
    path: '/',
    name: 'account',
    component: () => import('../components/Account'),
    meta: { requiresAuth: true }
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  if (to.path == '/logout') store.dispatch('app/logout').then(() => next({ path: '/login' }))
  else if (['/login','/register'].includes(to.path) && store.getters['app/isLoggedIn']) next('/')
  else if (to.matched.some(record => record.meta.requiresAuth)) {
    if (store.getters['app/isLoggedIn']) next()
    else next({ path: '/login' })
  }
  else next()
})

export default router
