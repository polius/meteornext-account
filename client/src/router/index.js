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
    component: () => import('../components/Login'),
  },
  {
    path: '/',
    name: 'accountPath',
    component: () => import('../components/Account'),
    alias: ["/license", "/billing", "/profile"],
    meta: { requiresAuth: true }
  },
  {
    path: '/license/change/:id?',
    name: 'changeLicense',
    component: () => import('../components/license/Change'),
    meta: { requiresAuth: true }
  },
  {
    path: '/verify/:code',
    name: 'verifyEmail',
    component: () => import('../components/mail/VerifyEmail'),
  },
  {
    path: '/reset/:code?',
    name: 'resetPassword',
    component: () => import('../components/mail/ResetPassword'),
  },
  {
    path: '/update/:code?',
    name: 'updatePayment',
    component: () => import('../components/mail/UpdatePayment'),
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
    else if (['license','billing','profile'].includes(to.fullPath.substring(1))) {
      next({ path: '/login', query: { url: to.fullPath.substring(1) } })
    }
    else next({ path: '/login' })
  }
  else next()
})

export default router
