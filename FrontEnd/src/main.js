import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入 ElementPlus
import ElementPlus, { ElMessage } from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import VueCookies from 'vue-cookies'


const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }//图标

// for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
//     app.component(key, component)
// }

app.use(router).use(ElementPlus,{locale: zhCn}).use(VueCookies);

app.mount('#app')

app.config.globalProperties.$cookies = VueCookies
VueCookies.config("1d");

// 禁用F12、Ctrl+Shift+I、Ctrl+U、右键菜单
document.addEventListener('keydown', function (e) {
  // F12
  // if (e.key === 'F12') {
  //   e.preventDefault();
  //   ElMessage.warning("If you're checking our console, we'll teach you a lesson. 🤗")
  //   return false;
  // }
  // Ctrl+Shift+I
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'i') {
    e.preventDefault();
    ElMessage.warning("If you're checking our console, we'll teach you a lesson. 🤗")
    return false;
  }
  // Ctrl+Shift+C
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'c') {
    e.preventDefault();
    ElMessage.warning("If you're checking our console, we'll teach you a lesson. 🤗")
    return false;
  }
  // Ctrl+U
  if (e.ctrlKey && e.key.toLowerCase() === 'u') {
    e.preventDefault();
    ElMessage.warning("If you're checking our console, we'll teach you a lesson. 🤗")
    return false;
  }
});

// 禁用右键菜单
document.addEventListener('contextmenu', function (e) {
  e.preventDefault();
});