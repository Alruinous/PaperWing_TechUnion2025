import { ElMessage } from 'element-plus'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'default',
      redirect: '/first'
    },
    {
      path: '/message',
      name: 'message',
      component: () => import('../views/community/MessageCenter.vue')
    },
    {
      path: '/forum',
      name: 'forum',
      component: () => import('../views/community/Forum.vue')
    },
    {
      path:'/production',
      name:'production',
      component: () => import('../views/literature/Production.vue')
    },
    {
      path:'/project',
      name:'project',
      component: () => import('../views/literature/Project.vue')
    },
    {
      path:'/question',
      name:'question',
      component: () => import('../views/literature/Question.vue')
    },
    {
      path:'/gateway',
      name:'gateway',
      component: () => import('../views/scholar/Gateway.vue')
    },
    {
      path:'/first',
      name:'first',
      component: () => import('../views/search/FirstPage.vue'),
    },
    {
      path:'/home',
      name:'home',
      component: () => import('../views/search/Home.vue')
    },
    {
      path:'/scholarRes',
      name:'scholarRes',
      component: () => import('../views/search/ScholarRes.vue')
    },
    {
      path:'/publicationRes',
      name:'publicationRes',
      component: () => import('../views/search/PublicationRes.vue')
    },
    {
      path:'/login',
      name:'login',
      component: () => import('../views/user/Login.vue'),
    },
    {
      path:'/register',
      name:'register',
      component: () => import('../views/user/Register.vue'),
    },
    {
      path:'/myGateway',
      name:'myGateway',
      component: () => import('../views/scholar/MyGateway.vue')
    },
    {
      path:'/trendAnalysis',
      name:'trendAnalysis',
      component: () => import('../views/scholar/TrendAnalysis.vue')
    },
  ]
})

// 添加全局前置守卫
router.beforeEach((to, from, next) => {
  const userInfo = window.$cookies?.get('userId')
  // 定义不需要登录的白名单路径
  const whiteList = ['/', '/first', '/login', '/register']
  
  if (!userInfo && !whiteList.includes(to.path)) {
    next('/')
  } else {
    next() 
  }
})


export default router;
