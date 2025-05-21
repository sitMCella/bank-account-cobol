import { createRouter, createWebHistory } from 'vue-router'
import AccountView from '../views/AccountView.vue'
import AdminView from '../views/AdminView.vue'
import TransactionView from '../views/TransactionView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/account'
    },
    {
      path: '/account',
      name: 'account',
      component: AccountView
    },
    {
      path: '/transaction',
      name: 'transaction',
      component: TransactionView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView
    }
  ]
})

export default router