<template>
  <div class="card-container">
    <div class="circle1"></div>
    <div class="circle2"></div>
    <div class="watermark">PAPERWING</div>
    <div class="container">
      <div class="log-card">
        <p class="heading">Welcome Back</p>
        <p>We are happy to have you again</p>

        <el-form
          :model="loginForm"
          :rules="rules"
          ref="loginFormRef"
          label-width="0"
          class="input-group"
        >
          <p class="text">Email</p>
          <el-form-item prop="account">
            <el-input
              v-model="loginForm.account"
              placeholder="For Ex: example@email.com"
              autocomplete="off"
              class="input"
              clearable
            />
          </el-form-item>

          <p class="text">Password</p>
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              placeholder="Enter Password"
              type="password"
              autocomplete="off"
              show-password
              class="input"
              clearable
            />
          </el-form-item>
        </el-form>

<!--        <div class="password-group">-->
<!--          <div class="checkbox-group">-->
<!--            <input type="checkbox" id="remember" />-->
<!--            <label class="label" for="remember">Remember Me</label>-->
<!--          </div>-->
<!--        </div>-->

        <el-button type="primary" class="btn" @click="submitLoginForm">Sign In</el-button>

        <p class="no-account">
          Don't have an account?
          <a class="link" @click="$router.push('/register')">Sign Up</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { Login } from '@/api/user';
import { useRouter } from 'vue-router';
import { useCookies } from 'vue3-cookies';

const { cookies } = useCookies();
const router = useRouter();

const loginForm = ref({
  account: '',
  password: '',
});

const loginFormRef = ref(null);

const rules = {
  account: [
    { required: true, message: 'Please enter your email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: ['blur', 'change'] },
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 8, message: 'Password must be at least 8 characters', trigger: 'blur' },
  ],
};

const submitLoginForm = () => {
  (loginFormRef.value as any).validate((valid: boolean) => {
    if (!valid) return;

    const form = loginForm.value;
    Login(form.account, form.password)
      .then((result: any) => {
        if (result.status === 'success') {
          ElMessage.success('Login successful');
          cookies.set('userId', result.user_id);
          cookies.set('account', form.account);
          cookies.set('avatarUrl', result.avatar_url || '');
          router.push('/home');
        } else {
          ElMessage.error(result.message || 'Incorrect email or password');
        }
      })
      .catch(() => {
        ElMessage.error('Login failed, please try again');
      });
  });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Monoton&family=Press+Start+2P&family=Anton&display=swap');
/* UI Card Template from Uiverse.io */
.card-container {
  width: 100vw;
  height: 100vh;
  background: #f0f4fc;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.container {
  display: flex;
  height: 100%;
  width: 100%;
  align-items: center;
  justify-content: center;
}

.circle1,
.circle2 {
  height: 80px;
  width: 80px;
  border-radius: 50%;
  position: absolute;
  z-index: 0;
}

.circle1 {
  background-color: #2879f3;
  top: 60px;
  left: 60px;
}

.circle2 {
  background-color: #f37e10;
  bottom: 60px;
  right: 60px;
}

.log-card {
  font-family: 'Segoe UI', sans-serif;
  position: relative;
  width: 420px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(6px);
  padding: 32px;
  background-color: rgba(255, 255, 255, 0.7);
  z-index: 10;
}

.heading {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
}

.para {
  font-size: 14px;
  font-weight: 500;
}

.input-group {
  margin-top: 16px;
  margin-bottom: 6px;
}

.text {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
  color: lightslategray;
}

:deep(.input .el-input__wrapper) {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 6px 14px;
  height: 42px;
}

:deep(.el-input__inner) {
  font-weight: 600;
  font-size: 15px;
  color: #2879f3;
}

.password-group {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.checkbox-group {
  color: black;
  font-size: 14px;
  font-weight: 500;
}

.btn {
  margin-top: 24px;
  margin-bottom: 12px;
  padding: 12px 20px;
  font-size: 17px;
  border-radius: 10px;
}

.btn:hover {
  background-color: #0653c7;
}

.no-account {
  font-size: 14px;
  font-weight: 400;
  text-align: center;
}

.link {
  font-weight: 800;
  color: #2879f3;
  margin-left: 6px;
  cursor: pointer;
}
.link:hover {
  color: #f37e10;
  text-decoration: underline;
}
.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-20deg);
  font-size: 160px;
  font-weight: 700;
  font-family: 'Monoton', 'Orbiran', 'Anton', sans-serif;
  letter-spacing: 24px;
  color: rgba(183, 225, 243, 0.863); /* 主色非常浅，接近半透明白 */
  white-space: nowrap;
  z-index: 0;
  user-select: none;
  pointer-events: none;

  /* 浅浅立体阴影，凸显轮廓 */
  text-shadow:
    1px 1px 0 rgba(0, 0, 0, 0.05),
    2px 2px 0 rgba(0, 0, 0, 0.04),
    3px 3px 0 rgba(255, 255, 255, 0.12),
    4px 4px 6px rgba(0, 0, 0, 0.06),
    -1px -1px 1px rgba(255, 255, 255, 0.15);
}
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;  /* 防止横向滚动 */
  background-color: #f0f2f5; /* 页面背景色 */
}
</style>
