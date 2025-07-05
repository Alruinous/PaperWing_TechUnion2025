<script setup>

import { useRouter } from 'vue-router';
const router = useRouter();

const gotoLogin = () => {
    router.push({
      path: '/login'
    });
}

</script>

<template>
  <div class="hero-wrapper">
    <div class="circle1"></div>
    <div class="circle2"></div>
    <div class="watermark">PAPERWING</div>
    <div class="hero-container">
      <!-- 左侧文字部分 -->
      <div class="hero-text">
        <h1 class="main-title">
          PaperWing Tech-Union<br />
          纸翼科联，链接你我<br />
        </h1>
        <p class="sub-title">
          A platform to share knowledge, grow your network, and collaborate globally.
        </p>
        <button class="cta-button" @click="gotoLogin">Get Started</button>
      </div>

      <!-- 右侧图片部分 -->
      <div class="hero-image">
        <img src="../../assets/images/bg.jpg" alt="main" />
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Monoton&family=Press+Start+2P&family=Anton&display=swap');

.hero-wrapper {
  width: 100%;
  height: 100vh;
  /* background: linear-gradient(to right, #f0f4ff, #e9f3ff); */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.hero-container {
  display: flex;
  max-width: 1200px;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  
}

.hero-text {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.main-title {
  font-size: 32px;
  font-weight: 800;
  line-height: 1.4;
  color: #2b2b2b;
  margin-bottom: 20px;
}

.main-title::first-line {
  font-size: 45px; /* 第一行字体大小 */
}

.sub-title {
  font-size: 18px;
  color: #555;
  margin-bottom: 30px;
}

.cta-button {
  background-color: #409EFF;
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  width: fit-content;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.cta-button:hover {
  background-color: #66b1ff;
}

.hero-image {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.7);
}

.hero-image img {
  max-width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 0;
  margin-right: 80px;
}

* {
  box-sizing: border-box;
}

.circle1,
.circle2 {
  height: 80px;
  width: 80px;
  border-radius: 50%;
  position: absolute;
  z-index: -1;
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
  z-index: -1;
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

.simple-hero-card {
  display: flex;
  background: rgba(255,255,255,0.18);
  border-radius: 24px;
  box-shadow: 0 4px 32px 0 rgba(80,120,255,0.08);
  padding: 48px 56px;
  align-items: center;
  max-width: 900px;
  margin: 0 auto 48px auto;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}
</style>