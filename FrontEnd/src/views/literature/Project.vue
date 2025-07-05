<script setup>
import { ref, computed } from 'vue';
import PageHeader from '@/components/PageHeader.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useRoute,useRouter } from 'vue-router'
import { getCurrentInstance } from 'vue';
import dayjs from 'dayjs';

import { GetProjectDetail, GetStatus, GetProjectReplies, PostProjectReply, searchUsers, RemoveMember } from '../../api/projectAndQuestion.js'
import { PostRequest } from '../../api/production.js'


const route = useRoute()
const router = useRouter()
const projId = ref(route.query.projId)

const internalInstance = getCurrentInstance();
const internalData = internalInstance.appContext.config.globalProperties;
const userId = ref(internalData.$cookies.get('userId')); // 后面的为之前设置的cookies的名字
const userAvatar = ref(internalData.$cookies.get('avatarUrl'))

// 项目详情数据结构
const projectDetail = ref({
  avatar: 'https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image',
  userId: 1,
  userName: '张三',
  institution: '北京航空航天大学',
  title: '项目标题示例',
  abstract: '这是一个项目简介示例，介绍项目的主要内容和目标。',
  tags: [
    '人工智能',
    '计算机',
    '攀岩',
  ],
  year: '2024',
  members: [
    {
      userId: 1,
      userName: '张三',
      avatar: "1-modified.png"
    },
    {
      userId: 1,
      userName: '张三',
      avatar: "2-modified.png"
    },
    {
      userId: 1,
      userName: '张三',
      avatar: "3-modified.png"
    },
  ]
})

const status = ref('not_involved')

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
    if(status.value !== "approved" && status.value !== "admin"){
        ElMessage.error('No permission to comment.');
        replyInput.value = ""
        return;
    }
    var promise = PostProjectReply(userId.value, projId.value, replyInput.value);
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

const isOwner = computed(() => {
    return status.value == "admin"
});

const applyJoin = () => {
    const timestamp = dayjs().format('YYYY-MM-DD HH:mm:ss');
    var promise = PostRequest(userId.value, projectDetail.value.userId, "apply", "申请加入您的项目", projId.value, 0, timestamp);
    promise.then((result)=>{
        if(result.success === true){
            ElMessage.success("Apply posted.");
            initHome();
        }
        else{
            ElMessage.error(result.message)
        }
    });
}


const gotoGateway = (userId) => {
  router.push({
    path: '/gateway',
    query: {
        userId: userId
    }
  });
}



const hasMembers = computed(() => {
  return projectDetail.value.members && projectDetail.value.members.length > 0
})

const removeMember = (userId) => {
  ElMessageBox.confirm(
    'Are you sure you want to remove this member?',
    'Confirmation',
    {
      confirmButtonText: 'Remove',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }
  ).then(() => {
    // User confirmed removal
    RemoveMember(userId, projId.value).then((result) => {
      if (result.success === true) {
        ElMessage.success('Member removed successfully.')
        initHome()
      } else {
        ElMessage.error(result.message)
      }
    })
  }).catch(() => {
    // User cancelled the operation
    ElMessage.info('Member removal cancelled.')
  })
}




const dialogVisible = ref(false)
const searchName = ref('')
const searchResults = ref([
// {
//       "id": 12,
//       "name": "张三丰",
//       "email": "zhangsanfeng@wudang.com",
//       "bio": "武当派创始人",
//       "avatar_url": "1-modified.png",
//       "institution": "武当山",
//       "followed": 108,
//       "paperCount": 5,
//       "research_fields": [
//         "太极",
//         "养生"
//       ],
//       "status": "admin"
//     },
//     {
//       "id": 15,
//       "name": "李小三",
//       "email": "lixiaosan@example.com",
//       "bio": "计算机科学家",
//       "avatar_url": "5-modified.png",
//       "institution": "北京大学",
//       "followed": 25,
//       "paperCount": 12,
//       "research_fields": [
//         "人工智能",
//         "机器学习"
//       ],
//       "status": "not_involved"
//     },
//     {
//       "id": 20,
//       "name": "王三",
//       "email": "wangsan@example.com",
//       "bio": "数据分析师",
//       "avatar_url": "3-modified.png",
//       "institution": "清华大学",
//       "followed": 50,
//       "paperCount": 8,
//       "research_fields": [
//         "数据科学"
//       ],
//       "status": "invited"
//     },
])
const selectedUsers = ref([])


const initInvite = () => {
  searchName.value = ''
  searchResults.value = []
  selectedUsers.value = []
  dialogVisible.value = true;
}

// 搜索按钮点击：调用后端搜索接口
const handleSearch = () => {
  searchResults.value = []

  if (!searchName.value.trim()) {
    ElMessage.warning('Please enter name to search!')
    return
  }

  var promise = searchUsers(searchName.value, projId.value);
  promise.then((result)=>{
    if(result.success === true){
      result.data.forEach(element => {
        searchResults.value.push(element);
      });
    }
    else{
      ElMessage.error("user doesn't exist")
    }
  });
}


// 选中某个人
const selectUser = (user) => {
  const exists = selectedUsers.value.find(u => u.id === user.id)
  if (!exists) {
    selectedUsers.value.push(user)
  }
}

// 移除某个选中用户
const removeUser = (index) => {
  selectedUsers.value.splice(index, 1)
}

// 发送邀请请求
const sendInvitations = () => {
  selectedUsers.value.forEach(user => {
    const timestamp = dayjs().format('YYYY-MM-DD HH:mm:ss');
    var promise = PostRequest(userId.value, user.id, "invitation", "申请您加入我的项目", projId.value, 0, timestamp);
    promise.then((result)=>{
        if(result.success === true){
            ElMessage.success("Invitation posted.");
        }
        else{
            ElMessage.error(result.message)
        }
    });
  })
  dialogVisible.value = false
}









const initHome = () => {
    projectDetail.value = [];
    replies.value = [];
    

    var promise = GetProjectDetail(projId.value);
    promise.then((result)=>{
      if(result.success === true){
        projectDetail.value = result.detail
      }
      else{
        ElMessage.error("Project doesn't exist")
      }
    });

    var promise = GetStatus(userId.value, projId.value);
    promise.then((result)=>{
      if(result.success === true){
        status.value = result.data.status
      }
      else{
        ElMessage.error("Unable to get status")
      }
    });

    var promise = GetProjectReplies(projId.value);
    promise.then((result)=>{
      if(result.success === true){
        result.replies.forEach(element => {
            replies.value.push(element);
        });
      }
      else{
        ElMessage.error("Unable to get replies")
      }
    });

}

initHome();

</script>

<template>
  <PageHeader/>
  <div class="home" style="background-color:#f2f4f9">
    <div class="project-detail-container">
        <!-- 项目详情卡片 -->
        <el-card shadow="hover" class="project-card">
            <div class="project-header">
                <el-avatar :src="projectDetail.avatar" size="large" class="project-creator-avatar" style="cursor: pointer;" @click="gotoGateway(projectDetail.userId)"/>
                <div class="project-info">
                    <div class="creator-userName" style="cursor: pointer;" @click="gotoGateway(projectDetail.userId)">{{ projectDetail.userName }}<el-tag type="info" size="small" class="project-tag" v-if="isOwner">Yourself</el-tag></div>
                    <div class="creator-institution">{{ projectDetail.institution }}</div>
                    <div class="project-title">{{ projectDetail.title }}</div>
                    <div class="project-abstract">{{ projectDetail.abstract }}</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center">
                        <template v-for="(tag, idx) in projectDetail.tags" :key="idx">
                            <el-tag type="success" size="small" :class="{ 'project-tag': idx !== 0 }">{{ tag }}</el-tag>
                        </template>

                        <!-- 自定义的 tag -->
                        <el-tag type="info" size="small" class="project-tag">{{ projectDetail.year }}</el-tag>
                    </div>
                </div>
                <div class="project-btn-group">
                  <el-button type="primary" size="small" class="reply-btn" @click="scrollToBottom">Go to comment</el-button>
                  <el-button class="reply-btn" size="small" v-if="!isOwner && status === 'not_involved'" @click="applyJoin">Apply</el-button>
                  <el-button class="reply-btn" size="small" v-else-if="!isOwner && status === 'pending'">✓Applied</el-button>
                  <el-button class="reply-btn" size="small" v-else-if="!isOwner && status === 'invited'">Invited</el-button>
                  <el-button type="primary" class="reply-btn" size="small" v-else-if="status === 'admin'" @click="initInvite">Invite</el-button>
                </div>
            </div>
        </el-card>

        <el-card style="margin-bottom: 20px;">
          <div class="reply-title" v-if="hasMembers">Project Members</div>
          <div class="reply-title" v-else>No Members</div>
          <div v-for="(user, userIndex) in projectDetail.members" :key="userIndex">
            <div class="user-row">
              <div class="user-info">
                <el-avatar :src="user.avatar" :size="40" style="cursor: pointer;" @click="gotoGateway(user.userId)" />
                <div class="user-name">{{ user.userName }}</div>
              </div>
              <el-button type="danger" v-if="status === 'admin'" @click="removeMember(user.userId)">Remove</el-button>
            </div>
          </div>
        </el-card>

        <!-- 回复区卡片 -->
        <el-card shadow="never">
          <div v-if="status === 'approved' || status === 'admin'">
            <div class="reply-title">All comments ({{ replies.length }})</div>
            <div v-for="(reply, idx) in replies" :key="idx" class="reply-item">
                <el-avatar :src="reply.avatar" size="default" class="reply-avatar" style="cursor: pointer;" @click="gotoGateway(reply.userId)"/>
                <div class="reply-content">
                <div class="reply-user" style="cursor: pointer;" @click="gotoGateway(reply.userId)">{{ reply.userName }} <span class="reply-institution">{{ reply.institution }}</span></div>
                <div class="reply-time">{{ reply.year }}</div>
                <div class="reply-text">{{ reply.content }}</div>
                </div>
            </div>
          </div>
          <div v-else>
            <div class="reply-title" style="height: 100px;">No permission to see the comments. Please join the project first...</div>
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


    <!-- 弹窗 -->
    <el-dialog title="Invite Members" v-model="dialogVisible" width="500px">
      <!-- 输入 + 搜索按钮 -->
      <div style="display: flex; gap: 10px; margin-bottom: 10px;">
        <el-input v-model="searchName" placeholder="Please enter name" @keyup.enter="handleSearch" />
        <el-button type="primary" @click="handleSearch">Search</el-button>
      </div>

      <!-- 匹配结果 -->
      <el-table
        :data="searchResults"
        style="width: 100%; margin-top: 10px; cursor: pointer;"
        height="300"
        @row-click="selectUser"
      >
        <!-- 头像列 -->
        <el-table-column label="Avatar" width="70">
          <template #default="{ row }">
            <el-avatar
              :src="row.avatar_url ||'12-modified.png'"
              :size="40"
            />
          </template>
        </el-table-column>

        <!-- 姓名 + 邮箱 -->
        <el-table-column label="Name" min-width="180">
          <template #default="{ row }">
            <div style="font-weight: bold">{{ row.name }}</div>
          </template>
        </el-table-column>

        <!-- 研究方向 -->
        <el-table-column label="Institution" min-width="160">
          <template #default="{ row }">
            <div style="font-weight: bold">{{ row.institution }}</div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 已选中成员 -->
      <div style="margin: 10px 0;">
        <el-tag
          v-for="(user, index) in selectedUsers"
          :key="user.id"
          closable
          @close="removeUser(index)"
        >
          {{ user.name }}
        </el-tag>
      </div>

      <!-- 底部按钮 -->
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="sendInvitations">邀请</el-button>
      </template>
    </el-dialog>
</template>

<style scoped>

.user-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px; /* 控制头像和名字之间的间距 */
}

.user-name {
  font-weight: 500;
}

.el-list-item:hover {
  background-color: #f5f7fa;
}


.home {
  background-color: #fff;
  min-width: 100%;
  min-height: 90vh;
  display: flex;
  justify-content: center; /* 水平居中 */
}


.project-detail-container {
  width: 45%;
  margin-top: 40px;
  margin-bottom: 50px;
  /* margin: 32px auto 0 auto; */
}
.project-card {
  margin-bottom: 24px;
}
.project-header {
  display: flex;
  align-items: flex-start;
  position: relative; /* 关键 */
}

.project-btn-group {
  position: absolute;
  top: 0px;
  right: 0px;
  display: flex;
  gap: 5px;
  z-index: 2;
}

.project-creator-avatar {
  margin-right: 16px;
}
.project-info {
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
.project-title {
  margin: 12px 0 8px 0;
  font-size: 20px;
  font-weight: bold;
}
.project-abstract {
  color: #666;
  margin-bottom: 8px;
}
.project-tag {
  margin-left: 8px;
}
.reply-btn {
  /* margin-left: 24px; */
  /* margin-right: 10px; */
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