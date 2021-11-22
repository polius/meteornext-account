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
    path: '/',
    name: 'account',
    component: () => import('../components/Account'),
    meta: { requiresAuth: true }
  },
  {
    path: '/verify_email/:code',
    name: 'verifyEmail',
    component: () => import('../components/mail/VerifyEmail'),
  },
  {
    path: '/reset_password',
    name: 'resetPassword',
    component: () => import('../components/mail/ResetPassword'),
  },
  {
    path: '/reset_password/:code',
    name: 'resetPasswordCode',
    component: () => import('../components/mail/ResetPassword'),
  },
  {
    path: '/license',
    name: 'changeLicense',
    component: () => import('../components/license/Change'),
    meta: { requiresAuth: true }
  },
  {
    path: '/license/:id',
    name: 'changeLicenseResponse',
    component: () => import('../components/license/Change'),
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
