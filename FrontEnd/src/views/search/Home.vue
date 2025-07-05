<!-- 首页 -->
<script setup>
import { computed,ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentInstance } from 'vue';
import PageHeader from '../../components/PageHeader.vue';
import { addHistory   } from '@/api/record';
const router = useRouter();

import { GetAuthors, GetMessages, FollowUser, UnfollowUser, GetCollection, DoFavorite } from '../../api/home.js'
import { Star, StarFilled } from '@element-plus/icons-vue'

const bannerImages = [
  new URL('../../assets/images/bg4.jpg', import.meta.url).href,
  new URL('../../assets/images/bg5.jpg', import.meta.url).href,
  new URL('../../assets/images/bg6.jpg', import.meta.url).href,
]

// 当前选中的标签页
const activeTab = ref('personalized')

// import { GetFields } from '../../api/home.js'

// const fields = ref([
//   {
//     fieldName: "ABC",
//     fieldId: "111",
//     topmessageName: "message1",
//     topmessageId: "1",
//     works_number: 66,
//   }
// ])
const recommended_messages = ref([
    {
        type: 1,
        authors: [
        {
            userId: 111,
            userName: "Sergei Belousov",
            registed: true
        },
        {
            userId: 111,
            userName: "Sergei Belousov",
            registed: true
        },
        ],
        paperId: 123456,
        paperTitle: "科研成果1",
        year: "2024",
        abstract: "ref(value: { authors: { userId: string; userName: string; }[];",
    },
    {
        type: 2,
        questionId: 111,
        questionTitle: "科研问题1",
        questionAuthorId: 111,
        questionAuthor: "Hu Yanzhe",
        year: "2024-06-24",
        abstract: "ref(value: { authors: { userId: string; userName: string; }[];",
    },
    {
        type: 3,
        authors: [
        {
            userId: 111,
            userName: "Sergei Belousov",
            registed: true
        },
        {
            userId: 0,
            userName: "Sergei Belousov",
            registed: false
        },
        ],
        paperId: 123456,
        paperTitle: "科研成果2",
        year: "2024",
        abstract: "ref(value: { authors: { userId: string; userName: string; }[];",
        followerName: "Alruinous",
    },
    {
        type: 4,
        questionId: 111,
        questionTitle: "科研问题2",
        questionAuthorId: 111,
        questionAuthor: "Hu Yanzhe",
        year: "2024-06-24",
        followerName: "Alruinous",
        abstract: "ref(value: { authors: { userId: string; userName: string; }[];",
    },
])

const recommended_documents = ref([
      {
        doc_id: 205,
        title: "基于机器学习的图像识别技术研究",
        authors: "王五, 赵六",
        year: 2022,
        abstract: "本文综述了传统机器学习与深度学习方法在图像识别中的应用，重点分析了CNN、ResNet等模型在多类图像数据集上的表现。",
        conference: "中国图像图形学学会年会（CSIG 2022）",
        local_file_path: "this is local_file_path",
        type: 0,
        isFavorite: true,
      },
      {
        doc_id: 309,
        title: "社交网络中的关系挖掘方法综述",
        authors: "孙七, 周八",
        year: 2020,
        abstract: "本论文综述了社交网络中节点关系建模与社区发现的方法，包括基于图的挖掘算法与表示学习技术。",
        conference: "全国人工智能大会（CCAI 2020）",
        local_file_path: "this is local_file_path",
        type: 1,
        isFavorite: false,
      }
    ])

const recommended_authors = ref([
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 1,
        avatar: "",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "",
    },
    {
        userId: "111",
        userName: "Sergei Belousov",
        isFollowed: 0,
        avatar: "",
    },
])


const internalInstance = getCurrentInstance();
const internalData = internalInstance.appContext.config.globalProperties;
const userId = ref(internalData.$cookies.get('userId')); // 后面的为之前设置的cookies的名字
// const userId = this.$root.OnlineUser;


// const gotoScholar = (userId) => {
//     router.push({
//       path: '/gateway',
//       query: {
//           userId: userId
//       }
//     });
// }
const gotoPaper = (paperId) => {


  addHistory({

    publicationId: paperId,
    userId: parseInt(userId.value)
  })

  router.push({
    path: '/production',
    query: {
      pubId: paperId
    }
  });
}
const gotoScholar = (userId) => {
  router.push({
    path: '/gateway',
    query: {
      userId: userId
    }
  });
}
const gotoQuestion = (questionId) => {
  router.push({
    path: '/question',
    query: {
      questionId: questionId
    }
  });
}
const gotoPDF = (url) => {
  window.open(url, '_blank');
}

// 定义 truncate 函数，接收标题作为参数
function truncate(title) {
  let words = title.split(' ') // 将标题按空格分割成单词数组
  let truncated = '' // 存储截断后的标题
  let charCount = 0 // 当前字符数
  // 遍历每个单词，逐个添加，直到字符数超过限制
  for (let word of words) {
    // 当前字符数加上这个单词的长度（如果有空格，需要加1）
    if (charCount + word.length + (truncated ? 1 : 0) <= 85) {
      // 如果字符数不超过限制，则添加该单词
      truncated += (truncated ? ' ' : '') + word
      charCount += word.length + (truncated ? 1 : 0) // 更新字符数
    } else {
      break // 一旦超过字符限制就跳出循环
    }
  }
  // 如果标题总字符数超过90，添加省略号
  if (charCount < title.length) {
    truncated += '...'
  }
  return truncated
}

const FormatString = (value) => {
  if (!value) return "";
  if (value.length > 200) {
    return value.slice(0,200) + "...";
  }
  return value;
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

const toggleFavorite = (docId) => {
  var promise = DoFavorite(userId.value, docId);
  promise.then((result)=>{
    if(result.success === true){
      ElMessage.success("Add to favorites!");
    }
    else{
      ElMessage.error(result.message)
    }
  });
}


// const regetAuthors = () => {
//   var promise = GetAuthors(userId.value);
//   promise.then((result)=>{
//     if(result.success === true){
//       result.authors.forEach(element => {
//         recommended_authors.value.push(element);
//       });
//     }
//     else{
//       ElMessage.error(result.message)
//     }
//   });
// }
const isRotating = ref(false)
const groupSize = 5;
const currentGroupIndex = ref(0);
const groupedAuthors = computed(() => {
  const groups = [];
  for (let i = 0; i < recommended_authors.value.length; i += groupSize) {
    groups.push(recommended_authors.value.slice(i, i + groupSize));
  }
  return groups;
});
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











//recommended_messages去重
function deduplicateMessages(messages) {
  const seenPaperIds = new Set();
  const seenQuestionIds = new Set();
  const result = [];

  for (const msg of messages) {
    if ((msg.type === 1 || msg.type === 3) && msg.paperId !== undefined) {
      if (!seenPaperIds.has(msg.paperId)) {
        seenPaperIds.add(msg.paperId);
        result.push(msg);
      }
    } else if ((msg.type === 2 || msg.type === 4) && msg.questionId !== undefined) {
      if (!seenQuestionIds.has(msg.questionId)) {
        seenQuestionIds.add(msg.questionId);
        result.push(msg);
      }
    }
  }

  return result;
}




const temperature = ref('--')
const today = new Date().toLocaleDateString('en-US', {
  month: 'long',
  day: 'numeric'
})


const fetchWeather = async () => {
  try {
    const url = "https://api.openweathermap.org/data/2.5/weather?q=Beijing&appid=6179268aadb88b9145ea3918aebd6a3c&units=metric&lang=zh_cn"
    const res = await fetch(url)
    const data = await res.json()
    if (res.ok) {
      temperature.value = Math.round(data.main.temp)
    } else {
      console.error('天气查询失败：', data.message)
    }
  } catch (err) {
    console.error('网络错误：', err)
  }
}

function limitAuthors(authorsStr, maxCount = 5) {
  const authors = authorsStr.split(',').map(name => name.trim());
  if (authors.length <= maxCount) {
    return authors.join(', ');
  } else {
    return authors.slice(0, maxCount).join(', ') + ', et al.';
  }
}







const initHome = (userId) => {
    recommended_authors.value = [];
    recommended_messages.value = [];
    recommended_documents.value = [];

    var promise = GetAuthors(userId);
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

    var promise = GetMessages(userId);
    promise.then((result)=>{
      if(result.success === true){
        result.messages.forEach(element => {
          recommended_messages.value.push(element);
        });
        recommended_messages.value = recommended_messages.value.sort(() => Math.random() - 0.5);
        //去重
        recommended_messages.value = deduplicateMessages(recommended_messages.value)
      }
      else{
        ElMessage.error(result.message)
      }
    });

    var promise = GetCollection(userId);
    promise.then((result)=>{
      if(result.success === true){
        result.data.关注者上传.forEach(element => {
          recommended_documents.value.push(element);
        });
        result.data.系统推荐.forEach(element => {
          recommended_documents.value.push(element);
        });
        recommended_documents.value = recommended_documents.value.sort(() => Math.random() - 0.5);
      }
      else{
        ElMessage.error(result.message)
      }
    });

}

initHome(parseInt(userId.value));

onMounted(fetchWeather)

</script>

<template>
<PageHeader></PageHeader>
<div class="home" style="background-color:#EBEEF5"
    element-loading-background="rgba(244, 246, 247,0.8)">
    <div class="main">
        <div class="uphalf">
            <div class="hero-left">
                <h1 class="hero-title">
                    Enhance Impact<br>
                    Network with Experts<br>
                    Connect with Peers<br>
                    Advance Career
                </h1>
                
                <!-- <button class="hero-join-button">Join for free</button> -->
            </div>
            <div class="hero-right">
              <!-- <img src="../../assets/images/bg4.jpg" alt="science" class="hero-image"> -->
              <el-carousel height="350px" indicator-position="outside" style="width: 100%; margin-left: -50px;">
                <el-carousel-item v-for="(img, index) in bannerImages" :key="index">
                  <img :src="img" class="carousel-img" />
                </el-carousel-item>
              </el-carousel>
            </div>
        </div>

        
        
        <div class="recommend">
            <div class="recommend-container">
                <div class="recommend-left">
                    <div class="recommend-tab">
                      <el-tabs v-model="activeTab" style="margin-bottom: 0px; background-color: white;">
                        <el-tab-pane label="TopicRadar" name="personalized" />
                        <el-tab-pane label="ScholarPick" name="literature" />
                      </el-tabs>
                    </div>
                    <!-- 个性化推荐 -->
                    <template v-if="activeTab === 'personalized'">
                      <div v-for="(message, index) in recommended_messages" v-bind:key="index">
                          <div class="message-card" v-if="message.type == 1 || message.type == 3">
                              <div style="text-align: left">
                                  <div style="margin-bottom: 10px">
                                      <span class="title" @click="gotoPaper(message.paperId)">{{ truncate(message.paperTitle) }}</span>
                                  </div>
                                  <span v-for="(author, index1) in message.authors" :key="author" class="author-name">
                                      <span v-if="author.registed == true" @click="gotoScholar(author.userId)"><u>{{ author.userName }}</u></span>
                                      <span v-else style="color: black; cursor: text;">{{ author.userName }}</span>
                                      <span v-if="index1 < message.authors.length-1">&nbsp;&nbsp;</span>
                                  </span>
                                  <span v-if="message.year != 0" class="publish-year">&nbsp;&nbsp;·&nbsp;&nbsp;{{ message.year }}</span>
                              </div>
                              <div style="text-align:left;margin-top:10px;">
                                  <span class="abstract">{{ FormatString(message.abstract) }}</span>
                              </div>
                              <div class="label" v-if="message.type == 1">
                                  <span>Publication</span>
                              </div>
                              <div class="label" v-else>
                                  <span>Following</span>
                              </div>
                          </div>
                          <div class="message-card" v-else-if="message.type == 2 || message.type == 4">
                              <div style="text-align: left; margin-bottom: 10px;">
                                  <span class="title" @click="gotoQuestion(message.questionId)">{{ truncate(message.questionTitle) }}</span>
                              </div>
                              <div style="text-align: left;">
                                  <span>by&nbsp;&nbsp;</span>
                                  <span class="author-name" @click="gotoScholar(message.questionAuthorId)"><u>{{ message.questionAuthor }}</u></span>
                                  <span v-if="message.year != 0" class="publish-year">&nbsp;&nbsp;·&nbsp;&nbsp;{{ message.year }}</span>
                              </div>
                              <div style="text-align:left;margin-top:10px;">
                                  <span class="abstract">{{ FormatString(message.abstract) }}</span>
                              </div>
                              <div class="label" v-if="message.type == 2">
                                  <span>Question</span>
                              </div>
                              <div class="label" v-else>
                                  <span>Following</span>
                              </div>
                          </div>
                      </div>
                    </template>
                    <!-- 文献推荐 -->
                    <template v-else-if="activeTab === 'literature'">
                      <div v-for="(message, index) in recommended_documents" v-bind:key="index">
                          <div class="message-card">
                              <div style="text-align: left">
                                  <div style="margin-bottom: 10px; display: flex; justify-content: space-between;">
                                      <span class="title" @click="gotoPDF(message.local_file_path)">{{ truncate(message.title) }}</span>
                                      <div>
                                        <el-button v-if="!message.isFavorite" type="warning" @click="toggleFavorite(message.doc_id); message.isFavorite = true" :icon="Star" circle></el-button>
                                        <el-button v-else plain disabled circle :icon="StarFilled"></el-button>
                                      </div>
                                  </div>
                                  <span style="font-size: 17px;">{{ limitAuthors(message.authors) }}</span>
                                  <span v-if="message.year != 0" class="publish-year">&nbsp;&nbsp;·&nbsp;&nbsp;{{ message.year }}</span>
                              </div>
                              <div style="text-align:left;margin-top:10px;">
                                  <span class="abstract">{{ FormatString(message.abstract) }}</span>
                              </div>
                              <div class="label" v-if="message.type == 0">
                                  <span>Following</span>
                              </div>
                              <div class="label" v-else>
                                  <span>Interested</span>
                              </div>
                          </div>
                      </div>
                    </template>
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
                        <div v-for="(author, index) in recommended_authors.slice(0, 5)" v-bind:key="index">
                            <div class="author-card">
                                <div class="author-info">
                                  <el-avatar :src="author.avatar ||'12-modified.png'" :size="40" @click="gotoScholar(author.userId)" style="cursor: pointer;"/>
                                  <span class="author-name" @click="gotoScholar(author.userId)" style="cursor: pointer;">{{ author.userName }}</span>
                                </div>
                                <div>
                                  <button v-if="!author.isFollowed" class="follow-button" @click="followUser(author.userId); author.isFollowed = 1">Follow</button>
                                  <button v-else class="followed-button" @click="unfollowUser(author.userId); author.isFollowed = 0">✓Following</button>
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
                    </div>    -->
                    
                    
                    <!-- From Uiverse.io by zanina-yassine --> 
                    <div class="weather-card">
                      <div class="weather-container">
                        <div class="cloud front">
                          <span class="left-front"></span>
                          <span class="right-front"></span>
                        </div>
                        <span class="sun sunshine"></span>
                        <span class="sun"></span>
                        <div class="cloud back">
                          <span class="left-back"></span>
                          <span class="right-back"></span>
                        </div>
                      </div>

                      <div class="card-header">
                        <span>China<br>Beijing</span>
                        <span>{{ today }}</span>
                      </div>

                      <span class="temp">{{ temperature }}°</span>

                      <!-- <div class="temp-scale">
                        <span>Celcius</span>
                      </div> -->
                    </div>


                </div>
            </div>
        </div>
    </div>
</div>
</template>

<style scoped>
.recommend-tab {
  background: #fff;
  border-radius: 6px;
  padding: 0 30px;
  margin-bottom: -15px;
  padding-top: 10px;
}
::v-deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500; /* 可选：加粗 */
}








.uphalf {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  padding: 80px 100px;
  gap: 60px;
}

.hero-left {
  flex: 1;
  max-width: 600px;
  margin-left: 30px;
  margin-bottom: 50px;
}

.hero-title {
  font-size: 40px;
  font-weight: 700;
  color: #1b1b1b;
  line-height: 1.4;
  margin-bottom: 30px;
}

.hero-join-button {
  background-color: #2bb673;
  color: white;
  font-size: 18px;
  font-weight: 600;
  padding: 14px 28px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.hero-join-button:hover {
  background-color: #249c63;
}

.hero-right {
  flex: 1;
  display: flex;
  justify-content: center;
}

.carousel-img {
  height: 100%;              /* 设定固定高度 */
  width: 100%;   
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}






.recommend {
  padding: 30px 0px;
  margin-top: 10px;
  width: 80vw;
  margin: 0 auto;
}

.recommend-container {
  display: flex;
  gap: 20px;
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

.card {
  background-color: #ffffff;
  padding: 32px 28px;
  border-radius: 6px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
}

.card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.recommend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}




.home {
  background-color: #fff;
  width: 98vw;
  height: 100%;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.home .main{

    width: 90%;
}


.message-card {
  background-color: #ffffff;
  padding: 24px 28px;
  border-radius: 6px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
  margin-bottom: 15px;
}

.message-card:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.title {
    font-size: 23px;
    font-weight: 700;
    line-height: 1.4;
    cursor: pointer;
    color: #262625;
    /* font-family: Tahoma,fantasy; */
}

.recommend-left .author-name {
    color: #2d94d4;
    cursor: pointer;
    font-size: 17px;
}

.abstract {
    /* cursor: pointer; */
    /* font-family: Georgia, Lato-Regular,Lato,sans-serif; */
    font-size: 18px;
    line-height: 22px;
    color: #262625;
    font-family: 'Times New Roman', Times, serif;
}

.publish-year {
    color:grey;
    font-size: 14px;
}


.label {
  text-align: right;
  font-size: 15px;
  margin-top: 10px;
  margin-bottom: -5px;
  color: #409EFF;
}


.recommend-right .author-name {
  font-weight: bold;
  font-size: 16px;
  color: #333;
  cursor: pointer;
}

.recommend-right .author-name:hover {
  text-decoration: underline;
}

.author-card {
  display: flex;
  justify-content: space-between;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.follow-button {
  margin-top: 5px;
  background-color: #409EFF;  /* Element Plus 默认主色蓝 */
  color: white;
  font-size: 14px;
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.follow-button:hover {
  background-color: #66b1ff; /* Element Plus hover 蓝色 */
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







/* From Uiverse.io by zanina-yassine */ 
.weather-card {
  /* width: 350px; */
  height: 200px;
  position: relative;
  padding: 25px;
  background: radial-gradient(178.94% 106.41% at 26.42% 106.41%, #fcf7ca 0%, rgba(255, 255, 255, 0) 71.88%) /* warning: gradient uses a rotation that is not supported by CSS and may not behave as expected */, #FFFFFF;
  box-shadow: 0px 155px 62px rgba(0, 0, 0, 0.01), 0px 87px 52px rgba(0, 0, 0, 0.05), 0px 39px 39px rgba(0, 0, 0, 0.09), 0px 10px 21px rgba(0, 0, 0, 0.1), 0px 0px 0px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  transition: all 0.8s cubic-bezier(0.15, 0.83, 0.66, 1);
  cursor: pointer;
  margin-top: 20px;
}

.weather-card:hover {
  transform: scale(1.01);
}

.weather-container {
  width: 250px;
  height: 250px;
  position: absolute;
  right: -35px;
  top: -50px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scale(0.7);
}

.cloud {
  width: 250px;
}

.front {
  padding-top: 45px;
  margin-left: 25px;
  display: inline;
  position: absolute;
  z-index: 11;
  animation: clouds 8s infinite;
  animation-timing-function: ease-in-out;
}

.back {
  margin-top: -30px;
  margin-left: 150px;
  z-index: 12;
  animation: clouds 12s infinite;
  animation-timing-function: ease-in-out;
}

.right-front {
  width: 45px;
  height: 45px;
  border-radius: 50% 50% 50% 0%;
  background-color: #4c9beb;
  display: inline-block;
  margin-left: -25px;
  z-index: 5;
}

.left-front {
  width: 65px;
  height: 65px;
  border-radius: 50% 50% 0% 50%;
  background-color: #4c9beb;
  display: inline-block;
  z-index: 5;
}

.right-back {
  width: 50px;
  height: 50px;
  border-radius: 50% 50% 50% 0%;
  background-color: #4c9beb;
  display: inline-block;
  margin-left: -20px;
  z-index: 5;
}

.left-back {
  width: 30px;
  height: 30px;
  border-radius: 50% 50% 0% 50%;
  background-color: #4c9beb;
  display: inline-block;
  z-index: 5;
}

.sun {
  width: 120px;
  height: 120px;
  background: -webkit-linear-gradient(to right, #fcbb04, #fffc00);
  background: linear-gradient(to right, #fcbb04, #fffc00);
  border-radius: 60px;
  display: inline;
  position: absolute;
}

.sunshine {
  animation: sunshines 2s infinite;
}

@keyframes sunshines {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }

  100% {
    transform: scale(1.4);
    opacity: 0;
  }
}

@keyframes clouds {
  0% {
    transform: translateX(15px);
  }

  50% {
    transform: translateX(0px);
  }

  100% {
    transform: translateX(15px);
  }
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-header span:first-child {
  word-break: break-all;
  font-weight: 800;
  font-size: 15px;
  line-height: 135%;
  color: rgba(87, 77, 51, 0.66);
}

.card-header span:last-child {
  font-weight: 700;
  font-size: 15px;
  line-height: 135%;
  color: rgba(87, 77, 51, 0.33);
}

.temp {
  position: absolute;
  left: 25px;
  bottom: 12px;
  font-weight: 700;
  font-size: 64px;
  line-height: 77px;
  color: rgba(87, 77, 51, 1);
}

.temp-scale {
  width: 80px;
  height: 36px;
  position: absolute;
  right: 25px;
  bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 9px;
}

.temp-scale span {
  font-weight: 700;
  font-size: 13px;
  line-height: 134.49%;
  color: rgba(87, 77, 51, 0.66);
}


</style>