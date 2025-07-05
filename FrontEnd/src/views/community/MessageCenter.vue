<template>
  
    <!-- 顶部导航栏 -->
    <PageHeader></PageHeader>

    <!-- 通知标题与切换 -->
    
      <div class="notice-header">
        <h1 class="notice-title">Notifications</h1>
        <div class="btn-container">
        <div class="btn-group">
    <el-button
      v-for="btn in buttons"
      :key="btn.value"
      type="text"
      :class="{ active: box === btn.value }"
      
      @click="switchBox(btn.value)"
    >
      {{ btn.label }}
    </el-button>
    
  </div>
  <el-button type="primary" round class="message-btn" size="medium" @click="dialogVisible = true">
      Send Message
    </el-button>

    <el-dialog v-model="dialogVisible" title="Send Message" width="500px">
    <el-form :model="newMessageForm" label-width="80px">
      <el-form-item label="Receiver">
        <el-autocomplete
          v-model="receiverName"
          :fetch-suggestions="querySearch"
          placeholder="Input Id or Name please"
          @select="handleReceiverSelect"
        />
      </el-form-item>

      <el-form-item label="Subject">
        <el-input v-model="newMessageForm.subject" />
      </el-form-item>

      <el-form-item label="Content">
        <el-input
          v-model="newMessageForm.content"
          type="textarea"
          :rows="4"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSendMessage">Send</el-button>
      </span>
    </template>
  </el-dialog>
  </div>
      </div>
    <el-main class="main-content">
      <!-- 消息内容区域 -->
      <div class="message-container">
        <el-card class="message-card">
          <template v-if="!selectedMessage">
  <div
    class="message-item"
    v-for="msg in paginatedMessages"
    :key="msg.id"
    @click="openMessage(msg)"
  >
    <div class="left">
      <el-avatar :size="40" :src="box === 'inbox' ? msg.senderAvatar : msg.receiverAvatar" icon="el-icon-user" />
      <div class="id-text">
        {{ box === 'inbox' 
      ? msg.senderName + '（' + msg.senderUsername + '）' 
      : msg.receiverName + '（' + msg.receiverUsername + '）' 
  }}

      </div>
    </div>
    <div class="right">
      <div class="type">{{ typeLabelMap[msg.type] || 'Unknown' }}</div>
      <div class="content">{{ msg.content }}</div>
    </div>
  </div>

  <el-empty
    v-if="paginatedMessages.length === 0"
    description="No Messages..."
  />

  <el-pagination
    v-if="filteredMessages.length > pageSize"
    layout="prev, pager, next"
    :total="filteredMessages.length"
    :page-size="pageSize"
    v-model:current-page="currentPage"
    background
    class="pagination"
  />
  </template>
  <template v-else>
    <!-- 消息详情模式 -->
    <el-button type="text" icon="el-icon-arrow-left" @click="selectedMessage = null">
      Back
    </el-button>
    <el-divider />

    <div class="message-detail">
      <div class="sender-info">
        <div class="avatar-and-name">
        <el-avatar :size="50"  :src="box === 'inbox' ? selectedMessage.senderAvatar : selectedMessage.receiverAvatar" icon="el-icon-user" />
        <span class="id-text">
          {{ box === 'inbox' 
      ? selectedMessage.senderName + '（' + selectedMessage.senderUsername + '）' 
      : selectedMessage.receiverName + '（' + selectedMessage.receiverUsername + '）' 
  }}
        </span>
        </div>
        <div class="message-type">
        <strong>{{ typeLabelMap[selectedMessage.type] || 'Unknown' }}</strong>
      </div>
      </div>
      
      <div class="message-content-full">
        {{ selectedMessage.content }}
      </div>
    </div>
    <el-card class="project-detail-card" shadow="hover" v-if="selectedMessage.type === 'invitation'">
    <div v-if="selectedMessage.type === 'invitation'" >
    <h3>Project Detail</h3>
    <p><strong>Project Name:</strong>{{ projectDetail.title || 'Not yet' }}</p>
    <p><strong>Project Description:</strong>{{ projectDetail.abstract || 'Not yet'  }}</p>
    <p><strong>Project Manager:</strong>{{ projectDetail.userName || 'Not yet'  }}（ID: {{ projectDetail.userId || 'Not yet' }}）</p>
    <p><strong>Institution:</strong>{{ projectDetail.institution || 'Not yet' }}</p>
    <p><strong>Time:</strong>{{ projectDetail.year || 'Not yet' }}</p>
    <p><strong>Tags:</strong>
      <el-tag
        v-for="tag in projectDetail.tags"
        :key="tag"
        type="success"
        class="tag"
      >
        {{ tag || 'Not yet' }}
      </el-tag>
    </p>

  </div>
  <div class="button-group" v-if="box === 'inbox'">
  <div v-if="joinStatus === 'pending'">
    <el-button type="success" size="large" @click="handleRespond('accept')">Accept</el-button>
    <el-button type="danger" size="large" @click="handleRespond('decline')">Decline</el-button>
  </div>

  <div v-else-if="joinStatus === 'accepted'">
    <el-tag type="success" size="large">Joined</el-tag>
  </div>

  <div v-else-if="joinStatus === 'declined'">
    <el-tag type="danger" size="large">Declined</el-tag>
  </div>
</div>

<!-- 不是 inbox 时显示“等待中” -->
<div class="button-group" v-else>
  <el-tag type="info" size="large">Sent</el-tag>
</div>
  </el-card>
  <el-card class="project-detail-card" shadow="hover" v-else-if="selectedMessage.type === 'claim'">
  <template #header>
    <div class="card-header">
      Claim Detail
    </div>
  </template>

  <p><strong>Title:</strong>{{ resultDetail?.title || 'Not yet...' }}</p>
  <p><strong>Abstract:</strong>{{ resultDetail?.abstract || 'Not yet...' }}</p>
  <p><strong>Authors:</strong>
  <template v-if="resultDetail?.authors && resultDetail.authors.length > 0">
    <span v-for="(author, idx) in resultDetail.authors" :key="author.user_id">
      {{ author.name }}<span v-if="idx < resultDetail.authors.length - 1">, </span>
    </span>
  </template>
  <span v-else>Not yet...</span>
</p>
  <p><strong>Platform:</strong>{{ resultDetail?.journal || 'Not yet...' }}</p>
  <p><strong>Keywords:</strong>{{ resultDetail?.keywords || 'Not yet...' }}</p>
  <p><strong>Tags:</strong>
      <el-tag
        v-for="tag in resultDetail.research_fields"
        :key="tag"
        type="success"
        class="tag"
      >
        {{ tag || 'Not yet...' }}
      </el-tag>
    </p>
  <div class="button-group" v-if="box === 'inbox'">

    <el-button type="success" size="large" @click="handleRespondToResult('accept')">Accept</el-button>
    <el-button type="danger" size="large" @click="handleRespondToResult('decline')">Decline</el-button>



</div>

<!-- 不是 inbox 时显示“等待中” -->
<div class="button-group" v-else>
  <el-tag type="info" size="large">Sent</el-tag>
</div>
</el-card>
<el-card class="project-detail-card" shadow="hover" v-else-if="selectedMessage.type === 'apply'">
    <div v-if="selectedMessage.type === 'apply'" >
    <h3>Project Detail</h3>
    <p><strong>Project Name:</strong>{{ projectDetail2.title || 'Not yet' }}</p>
    <p><strong>Project Description:</strong>{{ projectDetail2.abstract || 'Not yet'  }}</p>
    <p><strong>Project Manager:</strong>{{ projectDetail2.userName || 'Not yet'  }}（ID: {{ projectDetail2.userId || 'Not yet' }}）</p>
    <p><strong>Institution:</strong>{{ projectDetail2.institution || 'Not yet' }}</p>
    <p><strong>Time:</strong>{{ projectDetail2.year || 'Not yet' }}</p>
    <p><strong>tags:</strong>
      <el-tag
        v-for="tag in projectDetail2.tags"
        :key="tag"
        type="success"
        class="tag"
      >
        {{ tag || 'Not yet' }}
      </el-tag>
    </p>

  </div>
  <div class="button-group" v-if="box === 'inbox'">
  <div v-if="ApplicationStatus === 'pending'">
    <el-button type="success" size="large" @click="handleRespondApplication('accept')">Accept</el-button>
    <el-button type="danger" size="large" @click="handleRespondApplication('decline')">Decline</el-button>
  </div>

  <div v-else-if="ApplicationStatus === 'accepted'">
    <el-tag type="success" size="large">Accepted</el-tag>
  </div>

  <div v-else-if="ApplicationStatus === 'declined'">
    <el-tag type="danger" size="large">Declined</el-tag>
  </div>
</div>

<!-- 不是 inbox 时显示“等待中” -->
<div class="button-group" v-else>
  <el-tag type="info" size="large">Sent </el-tag>
</div>
  </el-card>
  <el-card class="project-detail-card" shadow="hover" v-else-if="selectedMessage.type === 'ask'">
    <template #header>
    <div class="card-header">
      Detail
    </div>
  </template>

  <p><strong>Title:</strong>{{ resultDetail2?.title || 'Not yet' }}</p>
  <p><strong>Abstract:</strong>{{ resultDetail2?.abstract || 'Not yet' }}</p>
  <p><strong>Author:</strong>
  <template v-if="resultDetail2?.authors && resultDetail2.authors.length > 0">
    <span v-for="(author, idx) in resultDetail2.authors" :key="author.user_id">
      {{ author.name }}<span v-if="idx < resultDetail2.authors.length - 1">, </span>
    </span>
  </template>
  <span v-else>Not yet...</span>
</p>
  <p><strong>Platform:</strong>{{ resultDetail2?.journal || 'Not yet' }}</p>
  <p><strong>Keywords:</strong>{{ resultDetail2?.keywords || 'Not yet' }}</p>

  <div class="button-group" v-if="box === 'inbox'">
    <!-- 触发按钮 -->
  <el-button type="success" size="large" @click="dialog=true">Accept</el-button>
  <el-button type="danger" size="large" @click="dialog=false">Decline</el-button>
  </div>
  <div class="button-group" v-else>
  <el-tag type="info" size="large">Sent</el-tag>
</div>

  <!-- 弹窗 -->
  <el-dialog
    v-model="dialog"
    title="Upload full text"
    width="40%"
    align-center
  >
    <el-form label-position="top">
      <el-form-item>
        <div 
          class="upload-area"
          @dragover.prevent="dragover = true"
          @dragleave="dragover = false"
          @drop="handleDrop"
          :class="{ 'dragover': dragover }"
        >
          <div v-if="!filePath" class="upload-content">
            <el-icon :size="50" color="#409EFC"><UploadFilled /></el-icon>
            <div style="margin-top: 16px; font-size: 16px; color: #606266;">
              Drag and drop PDF file here or
            </div>
            <el-button 
              type="primary" 
              size="small" 
              style="margin-top: 16px;"
              @click.stop="triggerFileInput"
            >
              Select File
            </el-button>
            <input 
              type="file" 
              ref="fileInput"
              style="display: none" 
              accept=".pdf"
              @change="handleFileChange"
            />
          </div>
          <div v-else class="upload-preview">
            <el-icon :size="50" color="rgb(159.5, 206.5, 255)"><Document /></el-icon>
            <div style="margin-top: 16px; font-size: 16px; color: #606266;">
              {{ filePath }}
            </div>
            <div style="margin-top: 8px; font-size: 12px; color: #909399;">
              {{ fileSize }}
            </div>
            <el-button 
              type="danger" 
              size="small" 
              style="margin-top: 16px;"
              @click.stop="removeFile"
              plain
            >
              Remove
            </el-button>
          </div>
        </div>
        <div v-if="uploadError" style="color: #F56C6C; margin-top: 8px;">
          {{ uploadError }}
        </div>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialog = false">Cancel</el-button>
        <el-button 
          type="primary" 
          @click="submitFullText"
          :disabled="!filePath"
        >
          Submit
        </el-button>
      </div>
    </template>
  </el-dialog>
  </el-card>
  </template>
    
</el-card>

<!-- 弹窗 -->

      </div>
    </el-main>


</template>

<script setup>
import { ref, computed, watch,onMounted} from 'vue'
import { sendMessage, fetchMessages, respondInvitation,respondClaimRequest} from '@/api/message'
import { GetStatus,GetProjectDetail } from '@/api/projectAndQuestion'
import { useCookies } from 'vue3-cookies'
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { GetProduction } from '@/api/production'
import { post, get } from "@/api/api";
const { cookies } = useCookies()
const box = ref('inbox') // 默认显示收件箱'
const newMessageForm = reactive({
  receiver: '',
  subject: '',
  content: ''
})
const senderIdStr = cookies.get('userId');  // 取出来是字符串
const senderId = parseInt(senderIdStr, 10); // 转成整数，10 表示十进制
const currentUserId = senderId;
const messages = ref([]);  // 消息列表
const inboxMessages = ref([]);
const sentMessages = ref([]);
const typeLabelMap = {
  user: 'User',
  invitation: 'Invitation',
  system: 'System',
  apply: 'Application',
  claim: 'Claim',
  ask: 'Ask'
};
const selectedMessage = ref(null);
const projectId = ref(null);
const resultId = ref(null);
const projectId2 = ref(null);
watch(selectedMessage, (msg) => {
  if (msg && (msg.type === 'invitation'||msg.type === 'apply')) {
    if(msg.type === 'invitation')
    projectId.value = msg.projectId;  // 或你函数返回的值
  else if(msg.type === 'apply')
    projectId2.value = msg.projectId;  // 或你函数返回的值

  } else{
    projectId.value = null;
  }
});
watch(selectedMessage, (msg) => {
   if (msg && (msg.type === 'claim'||msg.type === 'ask')) {
    if(msg.type === 'claim')
    resultId.value = msg.resultId;  // 或你函数返回的值
    else if(msg.type === 'ask')
    resultId2.value = msg.resultId;  // 或你函数返回的值
  } else{
    resultId.value = null;
  }
});
const projectDetail = ref(null);

watch(projectId, async (id) => {
  if (id) {
    try {
      const res = await GetProjectDetail(id);
      if (res.success === true) {
        projectDetail.value = res.detail;

      } else {
        console.error('获取项目失败：', res.message);
      }
    } catch (err) {
      console.error('项目详情获取失败:', err);
    }
  } else {
    projectDetail.value = null;
  }
});

const projectDetail2 = ref(null);

watch(projectId2, async (id) => {
  if (id) {
    try {
      const res = await GetProjectDetail(id);
      if (res.success === true) {
        projectDetail2.value = res.detail;
      } else {
        console.error('获取项目失败：', res.message);
      }
    } catch (err) {
      console.error('项目详情获取失败:', err);
    }
  } else {
    projectDetail2.value = null;
  }
});

const resultDetail2 = ref(null);
const resultId2 = ref(null);
watch(resultId2, async (id) => {
  if (id) {
    try {
      const res = await GetProduction(id, currentUserId);
      if (res.success === true) {
        resultDetail2.value = res.data;

      } else {
      }
    } catch (err) {
    }
  } else {
    resultDetail2.value = null;
  }
});

const resultDetail = ref(null);

watch(resultId, async (id) => {
  if (id) {
    try {
      const res = await GetProduction(id, currentUserId);
      if (res.success === true) {
        resultDetail.value = res.data;

      } else {
      }
    } catch (err) {
    }
  } else {
    resultDetail.value = null;
  }
});
const handleRespondToResult = async (action) => {
  try {
    const payload = {
      publicationId: selectedMessage.value.resultId, // 或 resultId，请确认字段名
      claimerId: selectedMessage.value.senderId,
      approverId: currentUserId,
      messageId: selectedMessage.value.messageId,
      response: action // 'accept' 或 'decline'
    };

    const res = await respondClaimRequest(payload); // 按你的后端路径替换

    if (res.success==true) {
      ElMessage.success(action === 'accept' ? '已同意认领' : '已拒绝认领');
      window.location.reload();

    } else {
      ElMessage.error(res.message || '操作失败');
    }
  } catch (error) {
    console.error('发送认领响应失败:', error);
    ElMessage.error('请求失败，请稍后再试');
  }
};

// 加入状态：'pending' | 'accepted' | 'declined'
const joinStatus = ref('pending');
const ApplicationStatus = ref('pending'); // 申请状态
// 拉取消息列表函数
async function loadMessages() {
  try {

    const res = await fetchMessages({ box: box.value, userId: currentUserId })
    if (res.success === true) {
      if (box.value === 'inbox') {
        inboxMessages.value = res.data.messages;
      } else {
        sentMessages.value = res.data.messages;
      }
    } else {
      ElMessage.error('获取消息失败');
    }
  } catch (error) {
    ElMessage.error('请求异常，请稍后重试');
  }
}

onMounted(loadMessages);
watch(box, loadMessages);




function handleSendMessage() {
  const receiverUser = allReceivers.value.find(user => user.userId === newMessageForm.receiver);

  const fullContent = newMessageForm.subject
    ? `【${newMessageForm.subject}】\n${newMessageForm.content}`
    : newMessageForm.content;
  const now = new Date();
  const timestamp = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}/${now.getHours()}/${now.getMinutes()}`;
  const payload = {
    senderId: senderId,//currentUserId,
    receiverId: newMessageForm.receiver,//newMessageForm.receiverId,
    type:'user',
    content: fullContent,
    projectId:0,
    resultId: 0,
    timestamp: timestamp,
  };

  sendMessage(payload).then((res) => {

    if (res.success === true) {
      ElMessage.success('发送成功');
      // 关闭弹窗，重置表单
      newMessageForm.subject = '';
      newMessageForm.content = '';
      newMessageForm.receiver = '';
      dialogVisible.value = false;
      loadMessages();  // 你的消息刷新函数
    } else {
      ElMessage.error('发送失败');
    }
  });

}
const handleRespond = async (action) => {
  const payload = {
    userId: currentUserId,
    respond:action,
    projectId: selectedMessage.value.projectId,

  };



  try {
    const res = await respondInvitation(payload);
    if (res.success === true) {
      ElMessage.success(action === 'accept' ? '已成功加入项目' : '已拒绝邀请');
    } else {
      ElMessage.error(res.message || '操作失败');
    }
  } catch (e) {
    ElMessage.error('请求失败，请稍后再试');
  }
  fetchJoinStatus();
};

const handleRespondApplication = async (action) => {
  const payload = {
    userId: selectedMessage.value.senderId,   // 申请人
    respond: action ,                             // 'accept' or 'decline'
    projectId: selectedMessage.value.projectId,

  };

  try {
    const res = await respondInvitation(payload);

    if (res.success === true) {
      ElMessage.success(action === 'accept' ? '已同意加入请求' : '已拒绝加入请求');
      ApplicationStatus.value = action === 'accept' ? 'accepted' : 'declined';
    } else {
      ElMessage.error(res.message || '操作失败');
    }
  } catch (e) {
    ElMessage.error('请求失败，请稍后再试');
    console.error('处理申请失败：', e);
    fetchApplicationStatus();
  }
};
// 假设这是你从消息中提取的逻辑


// 模拟调用接口获取状态（你之后替换成真实接口调用）
const fetchJoinStatus = async () => {
  try {
    const res = await GetStatus(
      currentUserId, 
      selectedMessage.value.projectId
    );

    const statusMap = {
      approved: 'accepted',
      not_involved: 'declined'
    };
    joinStatus.value = statusMap[res.data.status] || 'pending'; // 默认pending

  } catch (e) {
    console.error('获取加入状态失败', e);
  }
};
const fetchApplicationStatus = async () => {
  try {
    const res = await GetStatus(
      selectedMessage.value.senderId, 
      selectedMessage.value.projectId
    );

    const statusMap = {
      approved: 'accepted',
      not_involved: 'declined'
    };
    ApplicationStatus.value = statusMap[res.data.status] || 'pending'; // 默认pending

  } catch (e) {
    console.error('获取加入状态失败', e);
  }
};
// 加载状态
//onMounted(fetchJoinStatus);

function openMessage(msg) {
  selectedMessage.value = msg

  if (msg.type === 'invitation'||msg.type === 'apply') {
    fetchJoinStatus();
    fetchApplicationStatus();
  } else {
    joinStatus.value = 'not_applicable'; // 非邀请消息不显示按钮
  }
}

const buttons = [
  { label: 'Inbox', value: 'inbox' },
  { label: 'Sent', value: 'sent' },
]



watch(box, () => {
  currentPage.value = 1
})
const currentMessages = computed(() => {
  return box.value === 'inbox'
    ? inboxMessages.value
    : sentMessages.value
})
const currentPage = ref(1)
const pageSize = 5

const filteredMessages = computed(() => {
  return box.value === 'inbox' ? inboxMessages.value : sentMessages.value
})

const paginatedMessages = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredMessages.value.slice(start, start + pageSize)
})

const dialogVisible = ref(false)



// 模拟的关注用户（用于 autocomplete）
const followedUsers = [
  { value: '张教授（u123）' },
  { value: '李博士（u456）' },
  { value: '王研究员（u789）' }
]

// 自动补全回调函数
const querySearch = (queryString, cb) => {
  const results = allReceivers.value
    .filter(user =>
      user.name.toLowerCase().includes(queryString.toLowerCase())
    )
    .map(user => ({
      value: user.name,      // el-autocomplete 要求每一项有 `value` 字段
      userId: user.userId,
      title: user.title,
      institution: user.institution,
      avatar_url: user.avatar_url
    }));
  cb(results);
};

watch(
  () => selectedMessage.value,
  (newVal) => {
    if (!newVal) return;
    if (newVal.type !== 'invitation'|| newVal.type !== 'apply') {
      joinStatus.value = 'not_applicable';
      ApplicationStatus.value = 'not_applicable';
    } else {
      joinStatus.value = 'pending'; // 或去触发 fetchJoinStatus
    }
  },
  { immediate: true } // 初始执行一次
);

const followers = ref([]);
const fans = ref([]);
const allReceivers = computed(() => {
  // 合并关注者和粉丝并去重（按 userId）
  const combined = [...followers.value, ...fans.value];
  const map = new Map();
  combined.forEach(user => {
    if (!map.has(user.userId)) {
      map.set(user.userId, user);
    }
  });
  return Array.from(map.values());
});
watch(allReceivers, (newVal) => {

});
const loadAllReceivers = async () => {
  const userId = cookies.get('userId');
  try {
    const [followersRes, fansRes] = await Promise.all([
      post('/users/following/', { userId }),
      post('/users/followers/', { userId }),
    ]);
    followers.value = followersRes.data || [];
    fans.value = fansRes.data || [];

  } catch (err) {
    console.error('加载粉丝或关注者失败', err);
  }
};

// 页面加载时调用
onMounted(() => {
  loadAllReceivers();
});
function getNameById(id) {
  const user = allReceivers.value.find(u => u.userId === id);
  return user ? user.name : '';
}
const receiverName = ref('');
watch(() => newMessageForm.receiver, (id) => {
  receiverName.value = getNameById(id);
});
const handleReceiverSelect = (item) => {
  newMessageForm.receiver = item.userId;
};

const respondDialogVisible = ref(false);
const respondActionType = ref(''); // 'accept' 或 'decline'

// 计算弹窗标题
const dialogTitle = computed(() => {
  return respondActionType.value === 'accept' ? '确认同意' : '确认拒绝';
});

// 打开弹窗
function openRespondDialog(action) {
  respondActionType.value = action;
  showUploadMessage.value = false; // 每次打开都隐藏文字
  respondDialogVisible.value = true;
}
const showUploadMessage = ref(false);
// 提交响应
function handleRespondSubmit() {
  if (respondActionType.value === 'accept') {
    showUploadMessage.value = true; // 显示“请自行上传”
  } else {
    respondDialogVisible.value = false; // 拒绝时直接关闭弹窗
  }
}
function switchBox(val) {
  box.value = val;
  selectedMessage.value = null; // 关键：退出详情页
}

//上传成果弹窗
// 上传全文
import {uploadFullText} from '@/api/production'
import axios from 'axios';
const dialog = ref(false);
const dragover = ref(false);
const uploadError = ref('');
const fileInput = ref(null);
const fileSize = ref('');
const filePath = ref('');
const fileObj = ref(null); // 新增：存储文件对象
const pub_id = ref();
const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    validateAndSetFile(file);
  }
};

const handleDrop = (e) => {
  e.preventDefault();
  dragover.value = false;
  const file = e.dataTransfer.files[0];
  if (file) {
    validateAndSetFile(file);
  }
};

const validateAndSetFile = (file) => {
  uploadError.value = '';
  
  if (file.type !== 'application/pdf') {
    uploadError.value = 'Only PDF files are allowed';
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    uploadError.value = 'File size cannot exceed 10MB';
    return;
  }

  filePath.value = file.name;
  fileSize.value = formatFileSize(file.size);
  fileObj.value = file; // 存储文件对象
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i))).toFixed(2) + ' ' + sizes[i];
};

const removeFile = () => {
  filePath.value = '';
  fileSize.value = '';
  fileObj.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

async function submitFullText() {
  if (!fileObj.value) {
    ElMessage.error('Please select a file first.');
    return;
  }
  pub_id.value = selectedMessage.value.resultId || selectedMessage.value.projectId; // 确保 pub_id 正确设置
  const formData = new FormData();
  formData.append('file', fileObj.value);
  formData.append('pub_id', pub_id.value);

  try {
    const response = await axios.post(
      'http://10.251.254.221:8000/publications/upload/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );

    if (response.data && response.data.file_path) {
      var promise = uploadFullText(pub_id.value, response.data.file_path);
      promise.then((result) => {
        if(result.success){
          ElMessage.success('Full text upload successfully.');
          download.value = response.data.file_path;
          dialog.value = false;
          removeFile(); 
        }
        else{
          ElMessage.error('Full text upload failed.');
        }
      })
    } else {
      ElMessage.error('Upload failed: File path not returned.');
    }
  } catch (error) {
    ElMessage.error('Upload Error:', error);
  }
}
</script>

<style scoped>
.full-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-x: hidden;
}

.nav-bar {
  background-color:white;
  color: grey;
  padding: 16px;
  font-size: 18px;
  border-bottom: 1px solid #ccc;
}

.nav-title {
  font-weight: bold;

}

.main-content {
  flex: 1;
  width: 100%;
  background-color: #f5f5f5;
  margin: 0;                /* 防止外边距影响布局 */
              /* 防止内边距影响布局 */
  min-height: 75vh;
  margin-bottom: 0%;
}

.notice-header {
    display: flex;
    flex-direction: column;
    padding-top: 10px;
    background-color: white;  
    text-align: left;        /* 改成左对齐 */
    

}

.notice-title {
    padding-left: 350px;      /* 向左留一点内边距，让文字不紧贴左边 */
  font-size: 40px;
  margin-bottom: 16px;
  font-weight: bold;
}
.btn-group {
    margin-top: 10px;
    display: flex;
    padding-left: 21%;      /* 向左留一点内边距，让文字不紧贴左边 */
}

.btn-group .el-button {
  position: relative;
  color: #606266;
  font-weight: 500;
  font-size: medium;
  padding: 10px 24px;

  transition: color 0.3s;
  user-select: none;
}

/* 鼠标悬停变色，并显示灰色下划线 */
.btn-group .el-button:hover {
  color: #409eff;
}

.btn-group .el-button:hover::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #c0c4cc;
}

/* 选中态文字蓝色加粗 */
.el-button.active {
  color: #409eff;
  font-weight: 700;
}

/* 选中态下划线蓝色 */
.el-button.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409eff;
}
.message-btn{
  margin-left: auto;
  margin-right: 20.5%;
  color: white !important;  /* 强制字体为白色 */
  white-space: nowrap;
  margin-bottom: 5px;
}
.btn-container {

  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
}
.message-container {
  
  
  max-width: 1200px;     /* 设置最大宽度，保证在大屏上不太宽 */
  margin: 0 auto;         /* 水平居中 */
  padding: 0 20%;        /* 左右留白，防止贴边 */
}

.message-card {
  width: 100%;
}

.message-type-title {
  font-size: 20px;
  margin-bottom: 10px;
}

.footer-placeholder {
  background-color: transparent;
}
.message-item {
  display: flex;
  padding: 16px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.message-item:hover {
  background-color: #f9f9f9;
}

.left {
  width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.id-text {
  font-size: 12px;
  font-weight: bold;
  margin-top: 6px;
  text-align: center;
}

.right {
  flex: 1;
  padding-left: 20px;
}

.type {
  font-size: 14px;
  color: #999;
  font-weight: normal;
}

.content {
  font-size: 14px;
  color: #444;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 限两行 */
  -webkit-box-orient: vertical;
}

.pagination {
  margin-top: 24px;
  text-align: center;
}
.message-detail {
  padding: 5px 20px 20px; /* 上下左右的内边距，上方从 20 改为 10 */
}

.sender-info {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 左右分布 */
  margin-bottom: 15px;
  width: 100%;
}
.avatar-and-name {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sender-info .id-text {
  margin-left: 10px;
  font-weight: 500;
  text-align: center;
}

.message-type {
  font-size: 16px;       /* 字体较小 */
  font-weight: normal;   /* 不加粗 */
  text-align: right;     
  margin-left: auto;     
  color: #888;           /* 浅灰色，常用于辅助信息 */
}

.message-content-full {
  line-height: 1.8;
  white-space: pre-wrap;
  background: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.project-detail-card {
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  padding: 20px;
  margin-top: 10px;
  backdrop-filter: blur(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.project-field {
  margin-bottom: 12px;
  font-size: 15px;
}

.description-content {
  margin-top: 4px;
  white-space: pre-wrap;
  color: #444;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
</style>
