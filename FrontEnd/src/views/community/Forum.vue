<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentInstance } from 'vue';
import PageHeader from '../../components/PageHeader.vue';
const router = useRouter();

import { GetAuthors, FollowUser, UnfollowUser } from '../../api/home.js'
import { GetQuestions, PostCancelFollow, PostFollow } from '@/api/projectAndQuestion';

const internalInstance = getCurrentInstance();
const internalData = internalInstance.appContext.config.globalProperties;
const userId = ref(0); // 后面的为之前设置的cookies的名字
const dialogQuestionVisible = ref(false)
const loading = ref(true)

const recommended_questions = ref([
    {
        questionId: 111,
        title: "Why is the sky blue?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        initiatorId: "111",
        initiatorName: "Sergei Belousov",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        year: "2023-04-25 T18:00:00.000Z",
        isFollowed: true
    },
    {
        questionId: 111,
        title: "Why is the sky blue?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        initiatorId: "111",
        initiatorName: "Sergei Belousov",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        year: "2023-04-25 T18:00:00.000Z",
        isFollowed: false
    },
])

const followed_questions = ref([
    {
        questionId: 111,
        title: "Why is the sky red?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        initiatorId: "111",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        initiatorName: "Sergei Belousov",
        year: "2023-04-25 T18:00:00.000Z",
        isFollowed: true
    },
    {
        questionId: 111,
        title: "Why is the sky red?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        initiatorId: "111",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        initiatorName: "Sergei Belousov",
        year: "2023-04-25 T18:00:00.000Z",

        isFollowed: false
    },
])

const my_questions = ref([
    {
        questionId: 111,
        title: "Why is the sky yellow?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        year: "2023-04-25 T18:00:00.000Z",
        initiatorId: "111",
        initiatorName: "Sergei Belousov",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        isFollowed: true
    },
    {
        questionId: 111,
        title: "Why is the sky yellow?",
        abstract: "Ref<({ questionId: number; title: string; abstract: string; initiatorId: string; initiatorName:",
        year: "2023-04-25 T18:00:00.000Z",
        initiatorId: "111",
        initiatorName: "Sergei Belousov",
        initiatorAvatar:"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
        isFollowed: false
    },
])

const recommended_authors = ref([
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 1,
        avatar: "https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image",
    },
])



const activeTab = ref('think')
const prevTab = ref('think')
const slideDirection = ref('slide-right')
const handleTabSelect = (key) => {
  // 判断切换方向
  const tabOrder = ['think', 'follow', 'asked'];
  const prevIndex = tabOrder.indexOf(prevTab.value);
  const newIndex = tabOrder.indexOf(key);
  slideDirection.value = newIndex > prevIndex ? 'slide-left' : 'slide-right';
  prevTab.value = key;
  activeTab.value = key;
}

// 根据当前 tab 返回对应的问题列表
const currentQuestions = computed(() => {
  if (activeTab.value === 'think') return recommended_questions.value
  if (activeTab.value === 'follow') return followed_questions.value
  if (activeTab.value === 'asked') return my_questions.value
  return []
})






const isRotating = ref(false)
const handleRefreshClick = () => {
  if (isRotating.value) return // 防止重复点击
  
  isRotating.value = true

  
  // 打乱 recommended_authors 顺序
  recommended_authors.value = recommended_authors.value.sort(() => Math.random() - 0.5);


  // 动画时间后移除旋转类（与CSS动画时长一致）
  setTimeout(() => {
    isRotating.value = false
  }, 500) // 1秒旋转动画
}

function gotoScholar(id){
  router.push({
    path: '/gateway',
    query: { userId: id }
  })
}

function gotoGateway(id){
  if(activeTab === 'think' || activeTab === 'follow'){
    router.push({
      path: '/gateway',
      query: { userId: id }
    })
  }
  else{
    router.push({
      path: '/myGateway'
    })
  }
}

function gotoQuestion(questionId){
  router.push({
    path: '/question',
    query: { questionId: questionId }
  })
}

const followUser = (followerId) => {
  var promise = FollowUser(userId.value, followerId);
  promise.then((result)=>{
    if(result.success === true){
      ElMessage.success("Followed!");
    }
    else{
      ElMessage.error(result.message)
    }
  });
}

const unfollowUser = (followerId) => {
  var promise = UnfollowUser(userId.value, followerId);
  promise.then((result)=>{
    if(result.success === true){
      ElMessage.success("Unfollowed!");
    }
    else{
      ElMessage.error(result.message)
    }
  });
}

function follow(question){
  if(!question.isFollowed){
    // 关注
    var promise = PostFollow(question.questionId,userId.value)
    promise.then((result) => { 
      if(!result.success){
        ElMessage.error(result.message)
        question.isFollowed = false
      }
    })
  }
  else{
    // 取关
    var promise = PostCancelFollow(question.questionId,userId.value)
    promise.then((result) => { 
      if(!result.success){
        ElMessage.error(result.message)
        question.isFollowed = true
      }
    })
  }
}

onMounted(() => {
  userId.value = parseInt(window.$cookies?.get('userId')) || 1

  recommended_authors.value = [];
  recommended_questions.value = [];
  followed_questions.value = [];
  my_questions.value = [];

  var promise = GetAuthors(userId.value);
  promise.then((result)=>{
    if(result.success === true){
      result.authors.forEach(element => {
        recommended_authors.value.push(element);
      });
    }
    else{
      ElMessage.error(result.message)
    }
  });

  promise = GetQuestions(userId.value)
  promise.then((result)=>{ 
    if(result.success === true){
      recommended_questions.value = result.data.recommended_questions
      followed_questions.value = result.data.followed_questions
      my_questions.value = result.data.my_questions
      loading.value = false
    }
    else{
      ElMessage.error(result.message)
    }
  });
})

</script>

<template>
<PageHeader></PageHeader>
<div class="home" style="background-color:#EBEEF5"
    element-loading-background="rgba(244, 246, 247,0.8)">
    <div class="main">
        <div class="uphalf">
            <div class="qa-container">
                <div class="qa-title">
                    <h2>Q&amp;A</h2>
                </div>
                <span style="font-size: 18px;font-family: 华文隶书;color: #909399;padding-left: 2vw;">
                  Here, you may ask any academic questions of interest or initiate a discussion.
                </span>
                <div class="qa-menu-row">
                    <el-menu
                        :default-active="activeTab"
                        mode="horizontal"
                        background-color="#f5fafa"
                        text-color="#666"
                        active-text-color="#409EFF"
                        class="qa-menu"
                        @select="handleTabSelect"
                    >
                        <el-menu-item index="think" style="font-family: 'Times New Roman', Times, serif;">Recommend</el-menu-item>
                        <el-menu-item index="follow" style="font-family: 'Times New Roman', Times, serif;">Following</el-menu-item>
                        <el-menu-item index="asked" style="font-family: 'Times New Roman', Times, serif;">Yours</el-menu-item>
                    </el-menu>
                    <div class="qa-buttons">
                        <!-- <el-button type="primary" round class="qa-button" @click="dialogQuestionVisible = true">Create</el-button> -->
                    </div>
                </div>
            </div>
        </div>


        <div class="recommend">
            <div class="recommend-container">
                <div class="recommend-left">
                    <transition :name="slideDirection" mode="out-in">
                      <div :key="activeTab">
                        <div v-if="loading" class="question-card">
                          <el-skeleton style="--el-skeleton-circle-size: 30px;" animated >
                            <template #template>
                              <el-skeleton-item variant="circle" />
                            </template>
                          </el-skeleton>
                          <br/>
                          <el-skeleton :rows="2" animated style="width: 20vw;"/>
                        </div>
                        <div v-if="loading" class="question-card">
                          <el-skeleton style="--el-skeleton-circle-size: 30px;" animated >
                            <template #template>
                              <el-skeleton-item variant="circle" />
                            </template>
                          </el-skeleton>
                          <br/>
                          <el-skeleton :rows="2" animated style="width: 20vw;"/>
                        </div>
                        <div class="question-card" v-for="(q, index) in currentQuestions" :key="index">
                            <div class="card-header">
                                <img class="card-avatar" :src="q.initiatorAvatar ||'12-modified.png'" @click="gotoScholar(q.initiatorId)"/>
                                <div class="header-text">
                                    <div class="username"  @click="gotoScholar(q.initiatorId)">{{ q.initiatorName }}</div>
                                    <div class="time">in · {{ q.year.slice(0, 10) }}</div>
                                </div>
                            </div>

                            <div class="card-body">
                                <div style="display: flex; align-items: center;">
                                    <span class="question-title" @click="gotoQuestion(q.questionId)">{{ q.title }}</span>
                                </div>
                                <p class="summary">{{ q.abstract }}</p>
                                <hr>
                                <div class="card-footer">
                                    <el-button color="#66b1ff" @click="gotoQuestion(q.questionId)" plain round>Reply</el-button>
                                    <!-- From Uiverse.io by Omar-Molotov --> 
                                    <div class="footer-right" v-if="activeTab === 'think' || activeTab === 'follow'">
                                        <label class="container">
                                            <input type="checkbox" checked="checked" v-model="q.isFollowed"  @click="follow(q)"/>
                                            <svg
                                                class="save-regular"
                                                xmlns="http://www.w3.org/2000/svg"
                                                height="1em"
                                                viewBox="0 0 384 512"
                                            >
                                                <path
                                                d="M0 48C0 21.5 21.5 0 48 0l0 48V441.4l130.1-92.9c8.3-6 19.6-6 27.9 0L336 441.4V48H48V0H336c26.5 0 48 21.5 48 48V488c0 9-5 17.2-13 21.3s-17.6 3.4-24.9-1.8L192 397.5 37.9 507.5c-7.3 5.2-16.9 5.9-24.9 1.8S0 497 0 488V48z"
                                                ></path>
                                            </svg>
                                            <svg
                                                class="save-solid"
                                                xmlns="http://www.w3.org/2000/svg"
                                                height="1em"
                                                viewBox="0 0 384 512"
                                            >
                                                <path
                                                d="M0 48V487.7C0 501.1 10.9 512 24.3 512c5 0 9.9-1.5 14-4.4L192 400 345.7 507.6c4.1 2.9 9 4.4 14 4.4c13.4 0 24.3-10.9 24.3-24.3V48c0-26.5-21.5-48-48-48H48C21.5 0 0 21.5 0 48z"
                                                ></path>
                                            </svg>
                                        </label>
                                        <span class="follow">{{ q.isFollowed ? 'Following' : 'Follow' }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                      </div>
                    </transition>
                </div>
                <div class="recommend-right">
                  <div class="card">
                    <div style="margin-top: -30px; margin-bottom: 10px; margin-left: -5px;" class="recommend-header">
                            <h3 v-if="recommended_authors.length !== 0">People You May Like</h3>
                            <h3 v-else>No More People You Can Like...</h3>
                            <el-icon
                              :class="{ rotating: isRotating }"
                              style="margin-right: 10px; font-size: 20px; cursor: pointer;"
                              @click="handleRefreshClick"
                              v-if="recommended_authors.length !== 0"
                            >
                              <Refresh />
                            </el-icon>
                        </div>
                        <div class="author-card">
                          <div v-if="loading">
                            <el-skeleton style="--el-skeleton-circle-size: 30px;" animated >
                              <template #template>
                                <el-skeleton-item variant="circle" />
                              </template>
                            </el-skeleton>
                            <br/>
                            <el-skeleton :rows="1" animated style="width: 20vw;"/>
                            <br/>
                            <el-skeleton style="--el-skeleton-circle-size: 30px" animated>
                              <template #template>
                                <el-skeleton-item variant="circle" />
                              </template>
                            </el-skeleton>
                            <el-skeleton :rows="1" animated style="width: 20vw;"/>
                          </div>
                        </div>
                        <div v-for="(author, index) in recommended_authors.slice(0, 5)" v-bind:key="index">
                            <div class="author-card">
                                <div class="author-info">
                                  <el-avatar :src="author.avatar ||'12-modified.png'" :size="40" @click="gotoScholar(author.userId)" style="cursor: pointer;"/>
                                  <span class="author-name" @click="gotoScholar(author.userId)" style="cursor: pointer;">{{ author.userName }}</span>
                                </div>
                                <div>
                                  <button v-if="!author.isFollowed" class="follow-button" @click="followUser(author.userId); author.isFollowed = 1">关注</button>
                                  <button v-else class="followed-button" @click="unfollowUser(author.userId); author.isFollowed = 0">✓已关注</button>
                                </div>
                            </div>
                            <el-divider v-if="index < recommended_authors.length - 1"></el-divider>
                        </div>
                    </div>
                    <!-- From Uiverse.io by vinodjangid07 --> 
                    <!-- <div class="my-card">

                        <a href="https://www.bilibili.com/video/BV1GJ411x7h7" target="_blank" class="socialContainer containerOne">
                            <svg class="socialSvg instagramSvg" viewBox="0 0 16 16"> <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z"></path> </svg>
                        </a>
                        
                        <a href="https://www.bilibili.com/video/BV1GJ411x7h7" target="_blank" class="socialContainer containerTwo">
                            <svg class="socialSvg twitterSvg" viewBox="0 0 16 16"> <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"></path> </svg>              </a>
                            
                        <a href="https://www.bilibili.com/video/BV1GJ411x7h7" target="_blank" class="socialContainer containerThree">
                            <svg class="socialSvg linkdinSvg" viewBox="0 0 448 512"><path d="M100.28 448H7.4V148.9h92.88zM53.79 108.1C24.09 108.1 0 83.5 0 53.8a53.79 53.79 0 0 1 107.58 0c0 29.7-24.1 54.3-53.79 54.3zM447.9 448h-92.68V302.4c0-34.7-.7-79.2-48.29-79.2-48.29 0-55.69 37.7-55.69 76.7V448h-92.78V148.9h89.08v40.8h1.3c12.4-23.5 42.69-48.3 87.88-48.3 94 0 111.28 61.9 111.28 142.3V448z"></path></svg>
                        </a>
                        
                        <a href="https://www.bilibili.com/video/BV1GJ411x7h7" target="_blank" class="socialContainer containerFour">
                            <svg class="socialSvg whatsappSvg" viewBox="0 0 16 16"> <path d="M13.601 2.326A7.854 7.854 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.933 7.933 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.898 7.898 0 0 0 13.6 2.326zM7.994 14.521a6.573 6.573 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.557 6.557 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592zm3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.729.729 0 0 0-.529.247c-.182.198-.691.677-.691 1.654 0 .977.71 1.916.81 2.049.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232z"></path> </svg>
                        </a>
                    </div>              -->


                </div>
            </div>
        </div>
    </div>
</div>

  <!-- 新建问题弹窗 -->
<el-dialog
  v-model="dialogQuestionVisible"
  title="新建问题"
  width="40%"
  class="custom-dialog"
>
  <el-form label-position="top">
    <el-form-item label="问题标题" class="required-item">
      <el-input class="input" v-model="questionTitle" placeholder="请输入问题标题" />
    </el-form-item>
    <el-form-item label="问题简介" class="required-item">
      <el-input
        class="input"
        type="textarea"
        rows="4"
        v-model="questionDescription"
        placeholder="请输入问题简介"
      />
    </el-form-item>
    <el-form-item label="研究领域" class="required-item">
      <el-input class="input" v-model="questionField" placeholder="请输入研究领域" />
    </el-form-item>
  </el-form>
  <template #footer>
    <div class="dialog-footer">
      <el-button @click="dialogQuestionVisible = false">取消</el-button>
      <el-button type="primary" @click="submitQuestion">提交</el-button>
    </div>
  </template>
</el-dialog>

</template>

<style scoped>
.uphalf {
  display: flex;
  justify-content: center;
  background-color: #fff;
  /* padding: 80px 100px; */
  gap: 60px;
}

.qa-container {
  width: 70vw;
  display: flex;
  flex-direction: column;
  /* align-items: center; */
  gap: 16px;
  margin-top: 20px;
}

.qa-title {
  font-family: 华文宋体;
  /* text-align: center; */
}

.qa-title h2 {
  font-weight: bold;
  font-size: 30px;
}

.qa-title span {
  margin-left: 20px;
  /* margin-top: 6px; */
  font-size: 20px;
  color: #555;
}

.qa-menu-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}

.qa-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.qa-button {
  font-size: 16px;
  padding: 18px;
  background-color: rgb(0, 109, 217);
  font-family: 'Montserrat';
}

.qa-button:hover {
  background-color: rgb(0, 57, 113);
}

.qa-menu {
  /* justify-content: center; */
  border-bottom: none;
  /* font-size: 14px; */
  background-color: transparent;
  min-width: 50%;
}

.qa-menu .el-menu-item {
  font-weight: 500;
  font-size: 16px;
  padding: 0 20px;
  height: auto;
  line-height: 28px;
  border-bottom: 2px solid transparent;
  margin-right: 20px;
}

.qa-menu .el-menu-item.is-active {
  font-weight: 600;
  border-color: #409EFF;
  color: #409EFF !important;
  background-color: #fff;
}

.qa-menu .el-menu-item:hover {
  background-color: #fff;
  border-color: #bbbbbc;
}



.recommend {
  display: flex;
  justify-content: center;
  margin-top: 2vw;
}

.recommend-container {
  display: flex;
  width: 80vw;
  gap: 20px;
  margin: 0 auto; /* 水平居中 */
}

.recommend-left {
  flex: 2;
}

.recommend-right {
  flex: 1;
}

/* 可选：为卡片内容添加一些基本排版样式 */
.recommend-left h2,
.recommend-right h2 {
  font-size: 24px;
  margin-bottom: 12px;
  color: #333;
}

.recommend-left p,
.recommend-right p {
  font-size: 16px;
  line-height: 1.6;
  color: #555;
}




.question-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px 40px 30px 40px;
  margin-bottom: 20px;
  width: 45vw;
  box-shadow: 15px 15px 30px #bebebe,
              -15px -15px 30px #ffffff;
  transition: 0.2s ease-in-out;
}

.question-card:hover {
  box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
  transform: scale(1.01);
}

.card-avatar {
  width: 50px;
  height: auto;
  border-radius: 50%;
  margin-right: 10px;
  cursor: pointer;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.header-text .username {
  font-weight: bold;
  font-size: 17px;
  margin-bottom: 5px;
  cursor: pointer;
}

.header-text .username:hover {
  text-decoration: underline;
}

.header-text .time {
  font-size: 14px;
  color: #888;
}

.card-body {
    /* border: rgb(200, 200, 200) solid 1px; */
    /* padding: 20px 30px; */
    margin-top: 20px;
}

.question-title {
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
}

.question-title:hover {
  text-decoration: underline;
}

.tag {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  font-size: 14px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-left: 10px;
  margin-top: 3px;
}

.tag.new {
  background-color: #02675c;
  color: #fff;
  border: none;
}

.tag.discussion {
  background-color: #e0f3f1;
  color: #02675c;
}

.tag.reply-count {
  background-color: #e0f3f1;
  color: #02675c;
}

.summary {
  font-size: 14px;
  margin-bottom: 20px;
  color: #333;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 20px; /* 控制图标与文本之间的距离 */
}


.card {
  background-color: #ffffff;
  padding: 32px 28px;
  border-radius: 6px;
  box-shadow: 15px 15px 30px #bebebe,
              -15px -15px 30px #ffffff;
  transition: 0.2s ease-in-out;
}

.card:hover {
  box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
}

.recommend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}




.home {
  background-color: #f0f7ff;
  min-width: 100%;
  min-height: 90vh;
  display: flex;
  justify-content: center; /* 水平居中 */
}

.home .main{
  width: 90%;
}

.author-card {
  display: flex;
  justify-content: space-between;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.recommend-right .author-name {
  font-weight: bold;
  font-size: 16px;
  color: #333;
  cursor: pointer;
}

.recommend-right .author-name:hover {
  text-decoration: underline;
  transform: scale(1.02);
}

.follow-button {
  margin-top: 5px;
  background-color: #409EFF;
  color: white;
  font-size: 14px;
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.follow-button:hover {
  background-color: #66b1ff;
}

.followed-button {
  margin-top: 5px;
  background-color: #ccc; /* 灰色背景 */
  color: #666; /* 暗灰色文字 */
  font-size: 14px;
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.rotating {
  animation: rotate360 0.5s ease-in-out;
}

@keyframes rotate360 {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(-360deg);
  }
}




/* From Uiverse.io by vinodjangid07 */ 
.my-card {
  margin-top: 20px;
  /* width: fit-content; */
  height: 100px;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 25px 25px;
  gap: 20px;
  border-radius: 6px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
}

.my-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

/* for all social containers*/
.socialContainer {
  width: 52px;
  height: 52px;
  background-color: rgb(44, 44, 44);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition-duration: .3s;
}
/* instagram*/
.containerOne:hover {
  background-color: #d62976;
  transition-duration: .3s;
}
/* twitter*/
.containerTwo:hover {
  background-color: #00acee;
  transition-duration: .3s;
}
/* linkdin*/
.containerThree:hover {
  background-color: #0072b1;
  transition-duration: .3s;
}
/* Whatsapp*/
.containerFour:hover {
  background-color: #128C7E;
  transition-duration: .3s;
}

.socialContainer:active {
  transform: scale(0.9);
  transition-duration: .3s;
}

.socialSvg {
  width: 17px;
}

.socialSvg path {
  fill: rgb(255, 255, 255);
}

.socialContainer:hover .socialSvg {
  animation: slide-in-top 0.3s both;
}

@keyframes slide-in-top {
  0% {
    transform: translateY(-50px);
    opacity: 0;
  }

  100% {
    transform: translateY(0);
    opacity: 1;
  }
}





/* From Uiverse.io by Omar-Molotov */ 
/*------ Settings ------*/
.container {
  --color: #66b1ff;
  --size: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  cursor: pointer;
  font-size: var(--size);
  user-select: none;
  fill: var(--color);
}

.container .save-regular {
  position: absolute;
  animation: keyframes-fill 0.5s;
  transform-origin: top;
}

.container .save-solid {
  position: absolute;
  animation: keyframes-fill 0.5s;
  display: none;
  transform-origin: top;
}

/* ------ On check event ------ */
.container input:checked ~ .save-regular {
  display: none;
}

.container input:checked ~ .save-solid {
  display: block;
}

/* ------ Hide the default checkbox ------ */
.container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

/* ------ Animation ------ */
@keyframes keyframes-fill {
  0% {
    transform: scale(0);
    opacity: 0;
  }

  50% {
    transform: scaleY(1.2);
  }
}

/* 滑动动画 */
.slide-left-enter-active, .slide-left-leave-active,
.slide-right-enter-active, .slide-right-leave-active {
  transition: all 0.3s cubic-bezier(.55,0,.1,1);
  position: absolute;
  width: 45vw;
}
.slide-left-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.slide-left-enter-to {
  transform: translateX(0);
  opacity: 1;
}
.slide-left-leave-from {
  transform: translateX(0);
  opacity: 1;
}
.slide-left-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
.slide-right-enter-from {
  transform: translateX(-100%);
  opacity: 0;
}
.slide-right-enter-to {
  transform: translateX(0);
  opacity: 1;
}
.slide-right-leave-from {
  transform: translateX(0);
  opacity: 1;
}
.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

</style>
