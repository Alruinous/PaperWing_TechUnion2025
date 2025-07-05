<script setup>
import { ref, computed } from 'vue';
import PageHeader from '@/components/PageHeader.vue';
import { ElMessage } from 'element-plus';
import { useRoute,useRouter } from 'vue-router'
import { getCurrentInstance } from 'vue';
import dayjs from 'dayjs';

import { GetQuestionDetail, GetQuestionReplies } from '../../api/projectAndQuestion.js'
import { PostRequest } from '../../api/production.js'


const route = useRoute()
const router = useRouter()
const questionId = ref(route.query.questionId)

const internalInstance = getCurrentInstance();
const internalData = internalInstance.appContext.config.globalProperties;
const userId = ref(internalData.$cookies.get('userId')); // 后面的为之前设置的cookies的名字
const userAvatar = ref(internalData.$cookies.get('avatarUrl'))

// 问题详情数据结构
const questionDetail = ref({
  avatar: 'https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image',
  userId: 1,
  userName: '张三',
  institution: '北京航空航天大学',
  title: '问题标题示例',
  abstract: '这是一个问题简介示例，介绍问题的主要内容和目标。',
  tags: [
    '人工智能',
    '计算机',
    '攀岩',
  ],
  year: '2024',
})

// 静态回复数据
const replies = ref([
  {
    avatar: 'https://img2.baidu.com/it/u=123456789,123456789&fm=253&fmt=auto&app=138&f=JPEG?w=200&h=200',
    userId: 11,
    userName: '胡彦哲',
    institution: '北京航空航天大学',
    year: '2024-6-25 10:48',
    content: 'wtf bro?wtf bro?'
  },
  {
    avatar: 'https://img2.baidu.com/it/u=123456789,123456789&fm=253&fmt=auto&app=138&f=JPEG?w=200&h=200',
    userId: 11,
    userName: '胡彦哲',
    institution: '北京航空航天大学',
    year: '2024-6-25 10:48',
    content: 'aaaaaa\na'
  },
  {
    avatar: 'https://img2.baidu.com/it/u=987654321,987654321&fm=253&fmt=auto&app=138&f=JPEG?w=200&h=200',
    userId: 22,
    userName: '丁晨曦',
    institution: '北京航空航天大学',
    year: '2024-6-25 10:48',
    content: 'eat eat eat'
  }
])
const replyInput = ref('')

const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth' // 平滑滚动
  });
};

const handleAddReply = () => {
    if(replyInput.value === ''){
        ElMessage.error('Please enter a comment.');
        return;
    }
    const timestamp = dayjs().format('YYYY-MM-DD HH:mm:ss');
    var promise = PostRequest(userId.value, 0, "forum", replyInput.value, questionId.value, 0, timestamp);
    promise.then((result)=>{
      if(result.success === true){
        ElMessage.success("Comment posted.");
        initHome();
      }
      else{
        ElMessage.error(result.message)
      }
    });
    replyInput.value = ""
}


const gotoGateway = (userId) => {
  router.push({
    path: '/gateway',
    query: {
        userId: userId
    }
  });
}

const isOwner = computed(() => {
    return userId.value == questionDetail.value.userId;
});







const initHome = () => {
    questionDetail.value = [];
    replies.value = [];
    

    var promise = GetQuestionDetail(questionId.value);
    promise.then((result)=>{
      if(result.success === true){
        questionDetail.value = result.detail
      }
      else{
        ElMessage.error("Question doesn't exist")
      }
    });

    var promise = GetQuestionReplies(questionId.value);
    promise.then((result)=>{
      if(result.success === true){
        result.replies.forEach(element => {
            replies.value.push(element);
        });
      }
      else{
        ElMessage.error("Unable to get question replies")
      }
    });

}

initHome();

</script>

<template>
  <PageHeader/>
  <div class="home" style="background-color:#f2f4f9">
    <div class="question-detail-container">
        <!-- 问题详情卡片 -->
        <el-card shadow="hover" class="question-card">
            <div class="question-header">
                <el-avatar :src="questionDetail.avatar" size="large" class="question-creator-avatar" style="cursor: pointer;" @click="gotoGateway(questionDetail.userId)"/>
                <div class="question-info">
                    <div class="creator-userName" style="cursor: pointer;" @click="gotoGateway(questionDetail.userId)">{{ questionDetail.userName }}<el-tag type="info" size="small" class="question-tag" v-if="isOwner">Yourself</el-tag></div>
                    <div class="creator-institution">{{ questionDetail.institution }}</div>
                    <div class="question-title">{{ questionDetail.title }}</div>
                    <div class="question-abstract">{{ questionDetail.abstract }}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center">
                        <template v-for="(tag, idx) in questionDetail.tags" :key="idx">
                            <el-tag type="success" size="small" :class="{ 'question-tag': idx !== 0 }">{{ tag }}</el-tag>
                        </template>

                        <!-- 自定义的 tag -->
                        <el-tag type="info" size="small" class="question-tag">{{ questionDetail.year }}</el-tag>
                    </div>
                </div>
                <div class="question-btn-group">
                    <el-button type="primary" size="small" class="reply-btn" @click="scrollToBottom">Go to comment</el-button>
                </div>
            </div>
        </el-card>

        <!-- 回复区卡片 -->
        <el-card shadow="never">
        <div class="reply-title">All comments ({{ replies.length }})</div>
        <div v-for="(reply, idx) in replies" :key="idx" class="reply-item">
            <el-avatar :src="reply.avatar" size="default" class="reply-avatar" style="cursor: pointer;" @click="gotoGateway(reply.userId)"/>
            <div class="reply-content">
            <div class="reply-user" style="cursor: pointer;" @click="gotoGateway(reply.userId)">{{ reply.userName }} <span class="reply-institution">{{ reply.institution }}</span></div>
            <div class="reply-time">{{ reply.year }}</div>
            <div class="reply-text">{{ reply.content }}</div>
            </div>
        </div>
        <el-divider />
        <div class="reply-input-area">
            <el-avatar :src="userAvatar" size="default" class="reply-avatar" />
            <el-input
            v-model="replyInput"
            type="textarea"
            :rows="2"
            placeholder="enter your reply..."
            class="reply-input"
            />
            <el-button type="primary" @click="handleAddReply">Comment</el-button>
        </div>
        </el-card>
    </div>
  </div>
</template>

<style scoped>
.home {
  background-color: #fff;
  min-width: 100%;
  min-height: 90vh;
  display: flex;
  justify-content: center; /* 水平居中 */
}


.question-detail-container {
  width: 45%;
  margin-top: 40px;
  margin-bottom: 50px;
  /* margin: 32px auto 0 auto; */
}
.question-card {
  margin-bottom: 24px;
}
.question-header {
  display: flex;
  align-items: flex-start;
  position: relative;
}

.question-btn-group {
  position: absolute;
  top: 0px;
  right: 0px;
  display: flex;
  gap: 5px;
  z-index: 2;
}
.question-creator-avatar {
  margin-right: 16px;
}
.question-info {
  flex: 1;
}
.creator-userName {
  display: flex;
  align-items: center;
  font-weight: bold;
  font-size: 18px;
  margin-bottom: 3px;
}
.creator-institution {
  color: #888;
  font-size: 14px;
}
.question-title {
  margin: 12px 0 8px 0;
  font-size: 20px;
  font-weight: bold;
}
.question-abstract {
  color: #666;
  margin-bottom: 8px;
}
.question-tag {
  margin-left: 8px;
}
.reply-btn {
  /* margin-left: 24px; */
  margin-right: 10px;
  height: 30px;
}
.reply-title {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 16px;
}
.reply-item {
  display: flex;
  margin-bottom: 20px;
  margin-top: 30px;
}
.reply-avatar {
  margin-right: 12px;
}
.reply-content {
  flex: 1;
}
.reply-user {
  font-weight: 500;
}
.reply-institution {
  color: #888;
  font-size: 13px;
}
.reply-time {
  color: #888;
  font-size: 13px;
}
.reply-text {
  margin: 6px 0 0 0;
}
.reply-input-area {
  display: flex;
  align-items: flex-start;
}
.reply-input {
  flex: 1;
  margin-right: 12px;
}
</style>