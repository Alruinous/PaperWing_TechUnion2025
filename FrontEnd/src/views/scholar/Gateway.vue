<template>
  <PageHeader></PageHeader>
  <div class="container">
    <!-- 顶部基本信息区域 -->
    <section class="top-section">
      <div class="top-content">
        <div class="avatar">
          <img :src="user.avatar_url || 'https://ts1.tc.mm.bing.net/th/id/OIP-C.o3HTtaf_jy2WjeomIC5y1QAAAA?w=204&h=211&c=8&rs=1&qlt=70&o=7&cb=iavawebp1&dpr=1.5&pid=3.1&rm=3'" alt="头像" />
        </div>
        <div class="basic-info">
          <div class="info-header">
            <h1>{{ user.name }}</h1>
            <div class="button-container">
              <button
                  class="project-btn follow-btn"
                  :class="{ unfollow: isFollowing }"
                  @click="toggleFollow"
              >
                {{ isFollowing ? 'Unfollow' : 'Follow' }}
              </button>
              <button class="project-btn" @click="openMessageDialog">Send a message</button>
              <button class="project-btn" @click="openMyProjects">Invite him/her to join the project</button>
            </div>
          </div>
          <div class="meta-info">
            <span v-if="user.title" class="meta-item">{{ user.title }}</span>
            <span v-if="user.education" class="meta-item">{{ user.education }}</span>
            <span v-if="user.institution" class="meta-item">{{ user.institution }}</span>
          </div>
          <p v-if="user.bio" class="bio">{{ user.bio }}</p>
          <p v-if="user.research_fields" class="research-fields">
            <strong>Research_Fields:</strong>{{ user.research_fields }}
          </p>
        </div>
      </div>
    </section>
    <!-- 弹窗输入区 -->
    <div v-if="showDialog" class="modal-overlay" @click.self="showDialog = false">
      <div class="modal-content">
        <h3 class="modal-title">Send a message</h3>
        <textarea
            v-model="messageContent"
            placeholder="Please enter the message content"
            class="modal-textarea"
        ></textarea>
        <div class="modal-actions">
          <button class="modal-btn send" @click="sendPrivateMessage">Send</button>
          <button class="modal-btn cancel" @click="showDialog = false">Cancel</button>
        </div>
      </div>
    </div>
    <!-- 邀请弹窗 -->
    <div v-if="showMyProjectModal" class="modal-overlay" @click.self="closeMyProjects">
      <div class="modal-content">
        <h3 class="modal-title">The project I initiated</h3>
        <ul class="project-list">
          <li v-for="project in myProjects" :key="project.projectId" class="project-item">
            <span>{{ project.title || 'Unnamed project' }}</span>
            <button
                v-if="projectStatusMap[project.projectId] === 'not_involved'"
                class="invite-btn"
                @click="inviteOthers(project)">
              Invite him/her
            </button>
            <button
                v-else-if="projectStatusMap[project.projectId] === 'invited'"
                class="invite-btn invited"
                disabled>
              Invited
            </button>
            <button
                v-else-if="projectStatusMap[project.projectId] === 'pending'"
                class="invite-btn pending"
                disabled>
              Pending
            </button>
            <button
                v-else-if="projectStatusMap[project.projectId] === 'approved' || projectStatusMap[project.projectId] === 'admin'"
                class="invite-btn joined"
                disabled>
              Joined
            </button>
          </li>
        </ul>
        <div class="modal-footer">
          <button class="close-btn" @click="closeMyProjects">Close</button>
        </div>
      </div>
    </div>
    <!-- 顶部下方导航栏 -->
    <nav class="top-nav">
      <ul>
        <li v-for="item in topNav"
            :key="item.id"
            :class="{ active: activeTab === item.id }"
            @click="activeTab = item.id">
          <a href="javascript:void(0)">{{ item.label }}</a>
        </li>
      </ul>
    </nav>

    <!-- 动态内容区域 -->
    <div class="content-area">
      <!-- 我的成果 -->
      <div v-if="activeTab === 'research'" class="tab-content">
        <ul v-if="publications.length > 0" class="publication-list">
          <li
              v-for="pub in publications"
              :key="pub.pub_id"
              class="publication-item"
              @click="goToPublication(pub.pub_id)"
              style="cursor: pointer;"
          >
            <div style="display: flex; justify-content: space-between;">
              <h4>{{ pub.title || '未命名成果' }}</h4>
              <el-button v-if="pub.local_file_path !== ''" plain @click.stop="gotoPDF(`http://10.251.254.221:8000${pub.local_file_path}`)">View PDF</el-button>
            </div>
            <p><strong>Author:</strong>{{ pub.authors }}</p>
            <p v-if="pub.journal"><strong>Journal:</strong>{{ pub.journal }}</p>
            <p v-if="pub.year"><strong>Year:</strong>{{ pub.year }}</p>
            <p v-if="pub.abstract"><strong>Abstract:</strong>{{ pub.abstract }}</p>
          </li>
        </ul>

        <p v-else class="empty-message">No scientific research achievements at present</p>
      </div>
      <!-- 关注者列表 -->
      <div v-if="activeTab === 'followers'" class="tab-content">
        <div v-if="followers.length === 0" class="empty-text">No followers at the moment.</div>
        <ul class="follower-list" v-else>
          <li v-for="follower in pagedFollowers" :key="follower.userId" class="follower-item">
            <img
                style="cursor: pointer;"
                :src="follower.avatar_url || defaultAvatar"
                alt="头像"
                class="follower-avatar"
                @click="goToGateway(follower.userId)"
            />
            <div class="follower-info">
              <p class="follower-name">{{ follower.name }}</p>
              <p class="follower-meta">
                <span v-if="follower.title">{{ follower.title }}</span>
                <span v-if="follower.institution"> - {{ follower.institution }}</span>
              </p>
            </div>
          </li>
        </ul>

        <!-- 分页控件 -->
        <div v-if="totalFollowerPages > 1" class="pagination">
          <button @click="prevFollowerPage" :disabled="followerPage === 1">Prev</button>
          <span class="page-info">Page {{ followerPage }} in {{ totalFollowerPages }} </span>
          <button @click="nextFollowerPage" :disabled="followerPage === totalFollowerPages">Next</button>
        </div>
      </div>

      <!-- 粉丝列表 -->
      <div v-if="activeTab === 'fans'" class="tab-content">
        <div v-if="fans.length === 0" class="empty-text">No fans at the moment.</div>
        <ul class="follower-list" v-else>
          <li v-for="fan in pagedFans" :key="fan.userId" class="follower-item">
            <img
                style="cursor: pointer;"
                :src="fan.avatar_url || defaultAvatar"
                alt="头像"
                class="follower-avatar"
                @click="goToGateway(fan.userId)"
            />
            <div class="follower-info">
              <p class="follower-name">{{ fan.name }}</p>
              <p class="follower-meta">
                <span v-if="fan.title">{{ fan.title }}</span>
                <span v-if="fan.institution"> - {{ fan.institution }}</span>
              </p>
            </div>
          </li>
        </ul>

        <!-- 分页控件 -->
        <div v-if="totalFanPages > 1" class="pagination">
          <button @click="prevFanPage" :disabled="fanPage === 1">Prev</button>
          <span class="page-info">Page {{ fanPage }} in {{ totalFanPages }} </span>
          <button @click="nextFanPage" :disabled="fanPage === totalFanPages">Next</button>
        </div>
      </div>


      <!-- 关系图谱 -->
      <div v-if="activeTab === 'graph'" class="tab-content">
        <!-- 添加关系图谱控制区域 -->
        <div class="graph-controls">
          <el-radio-group v-model="graphType" size="large">
            <el-radio-button label="follow">Follow Network</el-radio-button>
            <el-radio-button label="institution">Institutional Network</el-radio-button>
          </el-radio-group>
        </div>
        
        <!-- 关系图谱容器 -->
        <div v-if="graphType === 'follow'" ref="followGraph" style="width: 100%; height: 600px; margin-top: 20px;"></div>
        <div v-else ref="institutionGraph" style="width: 100%; height: 600px; margin-top: 20px;"></div>
      </div>

      <!-- 创建的项目 -->
      <div v-if="activeTab === 'created-projects'" class="tab-content">
        <el-row :gutter="20">
          <el-col
              v-for="(project, index) in createdProjects"
              :key="project.projectId"
              :span="8"
              style="margin-bottom: 20px;"
          >
            <el-card
                shadow="hover"
                class="project-card"
                @click="goToProjectDetail(project.projectId)"
                style="cursor: pointer;"
            >
              <h4 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                {{ project.title || '未命名主题' }}
              </h4>
              <p><strong>Type:</strong>{{ formatType(project.type) }}</p >
              <p><strong>Initiator's ID:</strong>{{ project.initiatorId ?? '无' }}</p >
            </el-card>
          </el-col>
        </el-row>
        <p v-if="createdProjects.length === 0" class="empty-message">This user has not created any projects yet.</p >
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; {{ new Date().getFullYear() }} {{ user.name }}.  All rights reserved. </p>
      <p>Registered in {{ formatDate(user.register_time) }}</p>
    </footer>
  </div>
</template>

<script setup>
import { FollowUser, UnfollowUser } from '@/api/home.js'
import {sendMessage} from "@/api/message.js";
import { ref, reactive, watch } from 'vue'
import {fetchFollowers, fetchUserInfo} from "@/api/user.js";
import { fetchCreatedProjects, fetchParticipantStatus } from '@/api/discussions.js';
import { sendInvitationMessage } from '@/api/message.js';
import { onMounted, computed } from 'vue';
import {useRoute, useRouter} from 'vue-router'
import {useCookies} from "vue3-cookies"
import {post, get} from "@/api/api.js"
import * as echarts from 'echarts'
const router = useRouter()
import {fetchUserPublications} from "@/api/production.js"
const { cookies } = useCookies();
const isFollowing = ref(false)
const user = reactive({})
const route = useRoute();
const projectStatusMap = ref({})
const publications = ref([]);
const showDialog = ref(false)
const messageContent = ref('')

const followerPage = ref(1)
const followerPageSize = 5

const pagedFollowers = computed(() => {
  if (!Array.isArray(followers.value)) return []
  const start = (followerPage.value - 1) * followerPageSize
  return followers.value.slice(start, start + followerPageSize)
})

const totalFollowerPages = computed(() => {
  if (!Array.isArray(followers.value)) return 1
  return Math.ceil(followers.value.length / followerPageSize)
})

function prevFollowerPage() {
  if (followerPage.value > 1) {
    followerPage.value--
  }
}

function nextFollowerPage() {
  if (followerPage.value < totalFollowerPages.value) {
    followerPage.value++
  }
}

const fanPage = ref(1);
const fanPerPage = 5; // 每页条数

const pagedFans = computed(() => {
  if (!Array.isArray(fans.value)) return [];
  const start = (fanPage.value - 1) * fanPerPage;
  return fans.value.slice(start, start + fanPerPage);
});

const totalFanPages = computed(() =>
    fans.value.length > 0 ? Math.ceil(fans.value.length / fanPerPage) : 1
);

const prevFanPage = () => {
  if (fanPage.value > 1) fanPage.value--;
};

const nextFanPage = () => {
  if (fanPage.value < totalFanPages.value) fanPage.value++;
};

function openMessageDialog() {
  showDialog.value = true
}
const currentUserId = cookies.get('userId');
const targetUserId = route.query.userId;
function goToGateway(userId) {
  router.push({ 
    path: '/gateway', 
    query: { userId: userId } 
  });
}
async function checkIsFollowing(currentUserId, targetUserId) {
  try {
    const followers = await fetchFollowers(currentUserId)
    return followers.some(follower => follower.userId === Number(targetUserId))
  } catch (error) {
    console.error('checkIsFollowing error:', error)
    return false
  }
}

async function loadFollowStatus() {
  if (!currentUserId || !targetUserId) {
    isFollowing.value = false
    return
  }
  isFollowing.value = await checkIsFollowing(currentUserId, targetUserId)
}

async function toggleFollow() {
  try {
    if (isFollowing.value) {
      await UnfollowUser(currentUserId, targetUserId)
      isFollowing.value = false
    } else {
      await FollowUser(currentUserId, targetUserId)
      isFollowing.value = true
    }
  } catch (error) {
    console.error('Follow/close failed', error)
    alert('Operation failed, please try again later')
  }
}

async function sendPrivateMessage() {
  const senderId = Number(cookies.get('userId'))
  const receiverId = Number(route.query.userId)
  if (!messageContent.value.trim()) {
    alert('Please enter the message content')
    return
  }

  // 构造时间戳
  const now = new Date()
  const timestamp = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}/${now.getHours()}/${now.getMinutes()}`

  const payload = {
    senderId,
    receiverId,
    type: 'user',         // 私信类型
    content: messageContent.value.trim(),
    projectId: 0,         // 没有关联项目
    resultId: 0,          // 没有关联成果
    timestamp
  }

  try {
    const res = await sendMessage(payload)
    if (res.success === true) {
      alert('Message sent successfully')
      messageContent.value = ''
      showDialog.value = false
    } else {
      alert('Operation failed, please try again later')
    }
  } catch (error) {
    console.error('Sending message exception:', error)
    alert('Sending exception, please try again later.')
  }
}

function goToPublication(pubId) {
  router.push({
    name: 'production',    // 这里是路由名字
    query: { pubId }
  })
}

function gotoPDF(url) {
  window.open(url, '_blank');
}

// 顶部导航项和当前激活的标签
const topNav = ref([
  { id: 'research', label: 'Publications'},
  { id: 'followers', label: 'Following' },
  { id: 'fans', label: 'Followers' },
  { id: 'graph', label: 'Relation Graph' },
  { id: 'created-projects', label: 'Created Projects' },
])

const activeTab = ref('research') // 默认显示第一个标签

// 关系图谱类型
const graphType = ref('follow') // follow 或 institution

// 关注关系图谱
const followGraph = ref(null)
let followChart = null

// 同机构关系图谱
const institutionGraph = ref(null)
let institutionChart = null

// 存储后端获取的数据
const followersData = ref([])
const fansData = ref([])
const institutionUsersData = ref([])

// 加载关注者数据（用于关系图谱）
const loadFollowersData = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/users/following/', {
      userId: userId 
    })
    if (res && res.data) {
      followersData.value = res.data
    }
  } catch (error) {
    console.error('Failed to obtain followers', error)
  }
}

// 加载粉丝数据（用于关系图谱）
const loadFansData = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/users/followers/', {
      userId: userId 
    })
    if (res && res.data) {
      fansData.value = res.data
    }
  } catch (error) {
    console.error('Failed to acquire fans', error)
  }
}

// 加载同机构用户数据
const loadInstitutionUsers = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/users/same-institution/', {
      userId
    })
    
    if (res && res.data) {
      institutionUsersData.value = res.data
    }
  } catch (error) {
    console.error('Failed to obtain users from the same institution', error)
  }
}

// 渲染关注关系图谱（使用 symbolClipPath 实现圆形头像）
const renderFollowGraph = () => {
  if (!followGraph.value) return
  
  // 销毁之前的图表
  if (followChart) {
    followChart.dispose()
  }
  
  // 初始化图表
  followChart = echarts.init(followGraph.value)
  
  // 当前用户（中心节点）
  const centerNode = {
    id: 'me',
    name: user.name || "current user",
    symbol: `image://${user.avatar_url || defaultAvatar}`,
    symbolSize: 70,
    symbolKeepAspect: true,
    label: { 
      show: true, 
      position: 'bottom',
      fontSize: 14,
      fontWeight: 'bold'
    },
    x: 0, 
    y: 0,
    fixed: true,
    itemStyle: {
      color: '#409EFF',
      borderColor: '#fff',
      borderWidth: 2,
    },
    // 圆形裁剪
    symbolClipPath: {
      type: 'circle',
      r: 35
    },
    userId: route.query.userId
  }
  
  // 构建节点数据
  const nodes = [centerNode]
  const links = []
  
  // 左侧半圆：关注的人（最多10人）
  const following = followersData.value.slice(0, 10)
  const angleStep = 180 / Math.max(following.length, 1)
  const radius = 200
  
  following.forEach((userData, index) => {
    const angle = (-90 + index * angleStep) * Math.PI / 180
    const id = `f${userData.userId}`
    
    nodes.push({
      id,
      name: userData.name,
      symbol: `image://${userData.avatar_url || defaultAvatar}`,
      symbolSize: 50,
      symbolKeepAspect: true,
      label: { 
        show: true, 
        position: 'bottom',
        fontSize: 12
      },
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      itemStyle: {
        color: '#67C23A',
        borderColor: '#fff',
        borderWidth: 2,
      },
      // 圆形裁剪
      symbolClipPath: {
        type: 'circle',
        r: 25
      },
      title: userData.title,
      institution: userData.institution,
      userId: userData.userId
    })
    
    links.push({ 
      source: 'me', 
      target: id,
      lineStyle: {
        color: '#67C23A',
        width: 2
      }
    })
  })
  
  // 右侧半圆：粉丝（最多10人）
  const followers = fansData.value.slice(0, 10)
  const followerAngleStep = 180 / Math.max(followers.length, 1)
  
  followers.forEach((userData, index) => {
    const angle = (90 + index * followerAngleStep) * Math.PI / 180
    const id = `r${userData.userId}`
    
    nodes.push({
      id,
      name: userData.name,
      symbol: `image://${userData.avatar_url || defaultAvatar}`,
      symbolSize: 50,
      symbolKeepAspect: true,
      label: { 
        show: true, 
        position: 'bottom',
        fontSize: 12
      },
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      itemStyle: {
        color: '#E6A23C',
        borderColor: '#fff',
        borderWidth: 2,
      },
      // 圆形裁剪
      symbolClipPath: {
        type: 'circle',
        r: 25
      },
      title: userData.title,
      institution: userData.institution,
      userId: userData.userId
    })
    
    links.push({ 
      source: id, 
      target: 'me',
      lineStyle: {
        color: '#E6A23C',
        width: 2
      }
    })
  })
  
  // 图表配置
  const option = {
    title: {
      text: '',
      left: 'center',
      textStyle: {
        fontSize: 18
      }
    },
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') {
          const data = params.data
          return `
            <div style="text-align:center;padding:5px;">
              <img
                src="${data.symbol.replace('image://', '')}"
                style="width:60px;height:60px;border-radius:50%;margin-bottom:5px;"
              />
              <div style="font-weight:bold;">${data.name}</div>
              ${data.title ? `<div>${data.title}</div>` : ''}
              ${data.institution ? `<div>${data.institution}</div>` : ''}
            </div>
          `
        }
        return ''
      }
    },
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'none',
      roam: false,
      label: {
        show: true
      },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      data: nodes,
      links: links,
      lineStyle: {
        opacity: 0.9,
        width: 2,
        curveness: 0.2
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 3
        }
      }
    }]
  }

  followChart.setOption(option)

  // 添加点击事件
  followChart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.userId != route.query.userId) {
      const userId = params.data.userId
      if (userId) {
        router.push({
          path: '/gateway',
          query: { userId }
        })
      }
    }
  })

  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    followChart.resize()
  })
}

// 渲染同机构关系图谱（使用 symbolClipPath 实现圆形头像）
const renderInstitutionGraph = () => {
  if (!institutionGraph.value) return

  // 销毁之前的图表
  if (institutionChart) {
    institutionChart.dispose()
  }

  // 初始化图表
  institutionChart = echarts.init(institutionGraph.value)

  // 当前用户（中心节点）
  const centerNode = {
    id: 'me',
    name: user.name || "current user",
    symbol: `image://${user.avatar_url || defaultAvatar}`,
    symbolSize: 70,
    symbolKeepAspect: true,
    label: {
      show: true,
      position: 'bottom',
      fontSize: 14,
      fontWeight: 'bold'
    },
    x: 0,
    y: 0,
    fixed: true,
    itemStyle: {
      color: '#409EFF',
      borderColor: '#fff',
      borderWidth: 2,
    },
    // 圆形裁剪
    symbolClipPath: {
      type: 'circle',
      r: 35
    },
    userId: route.query.userId
  }

  // 构建节点数据
  const nodes = [centerNode]
  const links = []

  // 周围节点：同机构用户（最多20人）
  const colleagues = institutionUsersData.value.slice(0, 20)
  const angleStep = 360 / Math.max(colleagues.length, 1)
  const radius = 250

  colleagues.forEach((userData, index) => {
    const angle = (index * angleStep) * Math.PI / 180
    const id = `c${userData.userId}`

    nodes.push({
      id,
      name: userData.name,
      symbol: `image://${userData.avatar_url || defaultAvatar}`,
      symbolSize: 50,
      symbolKeepAspect: true,
      label: {
        show: true,
        position: 'bottom',
        fontSize: 12
      },
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      itemStyle: {
        color: '#909399',
        borderColor: '#fff',
        borderWidth: 2,
      },
      // 圆形裁剪
      symbolClipPath: {
        type: 'circle',
        r: 25
      },
      title: userData.title,
      institution: userData.institution,
      userId: userData.userId
    })

    links.push({
      source: 'me',
      target: id,
      lineStyle: {
        color: '#909399',
        width: 1.5
      }
    })
  })

  // 图表配置
  const option = {
    title: {
      text: '',
      left: 'center',
      textStyle: {
        fontSize: 18
      }
    },
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'node') {
          const data = params.data
          return `
            <div style="text-align:center;padding:5px;">
              <img 
                src="${data.symbol.replace('image://', '')}" 
                style="width:60px;height:60px;border-radius:50%;margin-bottom:5px;"
              />
              <div style="font-weight:bold;">${data.name}</div>
              ${data.title ? `<div>${data.title}</div>` : ''}
              ${data.institution ? `<div>${data.institution}</div>` : ''}
            </div>
          `
        }
        return ''
      }
    },
    animationDurationUpdate: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'none',
      roam: false,
      label: {
        show: true
      },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      data: nodes,
      links: links,
      lineStyle: {
        opacity: 0.9,
        width: 2,
        curveness: 0
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 3
        }
      }
    }]
  }
  
  institutionChart.setOption(option)
  
  // 添加点击事件
  institutionChart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.userId != route.query.userId) {
      const userId = params.data.userId
      if (userId) {
        router.push({
          path: '/gateway',
          query: { userId }
        })
      }
    }
  })
  
  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    institutionChart.resize()
  })
}

// 当切换到图谱标签时渲染图表
watch(activeTab, (newTab) => {
  if (newTab === 'graph') {
    setTimeout(() => {
      // 确保数据加载后再渲染
      Promise.all([
        loadFollowersData(),
        loadFansData(),
        loadInstitutionUsers()
      ]).then(() => {
        renderFollowGraph()
        renderInstitutionGraph()
      })
    }, 100)
  }
})

// 当切换图谱类型时重新渲染
watch(graphType, () => {
  setTimeout(() => {
    if (graphType.value === 'follow') {
      renderFollowGraph()
    } else {
      renderInstitutionGraph()
    }
  }, 100)
})

// 在组件挂载时初始化图表（如果当前在关系图谱标签）
onMounted(() => {
  if(route.query.userId == cookies.get('userId')){
    router.push({
      path: '/mygateway',
    })
    return;
  }
  if (activeTab.value === 'graph') {
    setTimeout(() => {
      // 确保数据加载后再渲染
      Promise.all([
        loadFollowersData(),
        loadFansData(),
        loadInstitutionUsers()
      ]).then(() => {
        renderFollowGraph()
        renderInstitutionGraph()
      })
    }, 500)
  }
})

onMounted(async () => {
  try {
    const userId = parseInt(route.query.userId);
    // 加载用户信息
    const userData = await fetchUserInfo(userId);
    Object.assign(user, userData);
    await loadFollowStatus()
    // 加载数据
    await loadPublications(userId)
    await loadFollowers()
    await loadFans()
    await loadCreatedProjects()
    
    // 获取用户创建的项目（用于邀请弹窗）
    const myUserId = parseInt(cookies.get('userId'));
    const result = await fetchCreatedProjects(myUserId);
    myProjects.value = result.projects || []
    
    // 拉取每个项目的参与状态
    for (const project of myProjects.value) {
      try {
        const status = await fetchParticipantStatus(userId, project.projectId)
        projectStatusMap.value[project.projectId] = status || 'not_involved'
      } catch (err) {
        console.warn(`Failed to fetch participation status for project ${project.projectId}`, err)
        projectStatusMap.value[project.projectId] = 'not_involved'
      }
    }
  } catch (error) {
    console.error('Failed to obtain user information:', error)
  }
})

// 格式化日期
const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('zh-CN', options)
}

const defaultAvatar = 'https://ts1.tc.mm.bing.net/th/id/OIP-C.o3HTtaf_jy2WjeomIC5y1QAAAA?w=204&h=211&c=8&rs=1&qlt=70&o=7&cb=iavawebp1&dpr=1.5&pid=3.1&rm=3'

// 示例关注者数据
const followers = ref([])
// 示例粉丝数据
const fans = ref([])

const searchQuery = ref('')


function handleFocus(e) {
  e.target.style.borderColor = '#409EFF'
  e.target.style.boxShadow = '0 0 8px rgba(64,158,255,0.4)'
}

function handleBlur(e) {
  e.target.style.borderColor = '#ddd'
  e.target.style.boxShadow = 'inset 0 2px 5px rgba(0,0,0,0.05)'
}

function handleMouseOver(e) {
  e.currentTarget.style.boxShadow = '0 6px 18px rgba(64,158,255,0.3)'
  e.currentTarget.style.transform = 'translateY(-3px)'
}

function handleMouseLeave(e) {
  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)'
  e.currentTarget.style.transform = 'translateY(0)'
}

async function loadPublications() {
  const userId = parseInt(route.query.userId);
  try {
    const data = await fetchUserPublications(userId);
    publications.value = data.publications || [];
  } catch (error) {
    console.error('Failed to load user achievements:', error);
  }
}
const createdProjects = ref([])

function formatType(type) {
  if (type === 'forum') return 'forum'
  if (type === 'project') return 'project'
  return 'unknown'
}

const showMyProjectModal = ref(false)
const myProjects = ref([])

const openMyProjects = async () => {
  try {
    const userId = cookies.get('userId');
    const result = await fetchCreatedProjects(userId);
    myProjects.value = result.projects || []
    showMyProjectModal.value = true
  } catch (err) {
    console.error('Project loading failed:', err)
  }
}

function closeMyProjects() {
  showMyProjectModal.value = false
}

function inviteOthers(project) {
  const userId = parseInt(route.query.userId);
  const payload = {
    senderId: cookies.get('userId'),
    receiverId: userId,
    type: 'invitation',
    content: `You're invited to join the project "${project.title}"`,
    projectId: project.projectId,
    resultId: 0,
    timestamp: getCurrentTimestamp()
  }
  sendInvitationMessage(payload)
      .then(() => {
        projectStatusMap.value[project.projectId] = 'invited'
      })
      .catch((err) => {
        console.error('Invitation message failed to send:', err)
      })
}

function getCurrentTimestamp() {
  const now = new Date()
  const parts = [
    now.getFullYear(),
    now.getMonth() + 1,
    now.getDate(),
    now.getHours(),
    now.getMinutes()
  ]
  return parts.join('/')
}
//获取创建的项目
const loadCreatedProjects = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/discussions/getCreatedProjects/', {
      userId: userId 
    })
    createdProjects.value = res.data.projects || []
  } catch (error) {
    console.error('Failed to retrieve the created project', error)
  }
}

const goToProjectDetail = (projId) => {
  router.push({
    path: '/project',
    query: {projId}
  });
};
// 加载关注者列表
const loadFollowers = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/users/following/', {
      userId: userId 
    })
    followers.value = res.data
  } catch (error) {
    console.error('Failed to obtain followers', error)
  }
}

// 加载粉丝列表
const loadFans = async () => {
  const userId = parseInt(route.query.userId);
  try {
    const res = await post('/users/followers/', {
      userId: userId 
    })
    fans.value = res.data
  } catch (error) {
    console.error('Failed to acquire fans', error)
  }
}
</script>

<style scoped>
.container {
  background-color: #f0f0f0;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  position: relative;
  min-height: 52vw;
}
.top-section {
  margin-top: 0;
  background-color: #ffffff;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  padding: 40px 20px;
  box-sizing: border-box;
  border-bottom: 1px solid #d1d9e6;
}

/* 内容最大宽度且居中 */
.top-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

/* 头像样式 */
.avatar img {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border: 3px solid white;
}

/* 基本信息区域，弹性布局填满剩余空间 */
.basic-info {
  flex: 1;
  min-width: 250px; /* 避免过窄 */
}

/* 头部姓名 + 编辑按钮 */
.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.info-header h1 {
  margin: 0;
  font-size: 1.9em;
  font-weight: 700;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.button-container {
  position: absolute;
  right: 300px;
  top: 200px;
  display: flex;
  gap: 15px; /* 按钮间距 */
}

.project-btn {
  padding: 8px 14px;
  font-size: 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background-color: #3b82f6; /* 蓝色背景 */
  color: white;
  transition: background-color 0.2s ease;
}

.project-btn:hover {
  background-color: #2563eb; /* hover 更深蓝 */
}

.project-btn.follow-btn {
  background-color: #007bff; /* 关注按钮默认蓝色 */
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}
.project-btn.follow-btn.unfollow {
  background-color: #e74c3c; /* 取关按钮红色 */
}
.project-btn.follow-btn:hover {
  opacity: 0.9;
}

/* 头衔等元信息 */
.meta-info {
  margin: 8px 0 12px;
  color: #3b82f6;
  font-weight: 500;
  font-size: 1.1em;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* 个人简介 */
.bio {
  margin: 0 0 12px;
  font-size: 1em;
  line-height: 1.5;
  color: #4b5563;
  max-height: 3em; /* 限制高度 */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}

/* 研究方向 */
.research-fields {
  margin: 0;
  font-size: 1em;
  color: #000000;
}

.research-fields strong {
  color: #000000;
}

/* 导航栏样式 */
.top-nav {
  margin: auto;
  margin-top: 20px;
  max-width: 1150px;
  background-color: #ffffff;
  padding: 10px 0;
  border-radius: 8px;
}
.top-nav ul {
  list-style: none;
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 0;
  margin: 0;
}
.top-nav li {
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s;
}
.top-nav li.active {
  background-color: #e0f7fa;
  font-weight: bold;
}
.top-nav li:hover {
  background-color: #e0f7fa;
}
.top-nav a {
  text-decoration: none;
  color: #00acee;
  font-weight: 500;
}

/* 内容区域样式 */
.content-area {
  max-width: 1100px;
  margin: auto;
  margin-top: 20px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  min-height: 300px;
}


/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
.form-group textarea {
  resize: vertical;
  min-height: 80px;
}
.footer {
  text-align: center;
  margin-top: 50px;
  color: #888;
  font-size: 0.9em;
}

.follower-list {
  list-style: none;
  padding: 0;
  margin-top: 20px;
}

.follower-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px;
  background-color: #fff;
  border-radius: 6px;
  margin-bottom: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  transition: box-shadow 0.2s ease;
}

.follower-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.follower-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #eee;
}

.follower-info {
  flex: 1;
}

.follower-name {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 4px;
}

.follower-meta {
  font-size: 0.9em;
  color: #666;
}

.unfollow-btn {
  background-color: #f87171;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
}

.unfollow-btn:hover {
  background-color: #ef4444;
}
.empty-text {
  color: #999;
  font-style: italic;
  margin-top: 15px;
}

.follow-btn {
  background-color: #1976d2;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.follow-btn:hover {
  background-color: #1565c0;
}

.history-tab {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
}

.search-input {
  width: 100%;
  padding: 12px 20px;
  border: 1.5px solid #ddd;
  border-radius: 30px;
  font-size: 16px;
  outline: none;
  margin-bottom: 30px;
  box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: border-color 0.3s, box-shadow 0.3s;
}

.card-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card-item {
  background: #fff;
  padding: 18px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s, transform 0.2s;
  cursor: default;
}

.card-content {
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 1.2em;
  color: #1f2937;
  font-weight: 700;
}

.card-author {
  margin-top: 6px;
  font-size: 0.95em;
  color: #6b7280;
}

.project-card {
  transition: transform 0.2s ease;
  border-radius: 12px;
  overflow: hidden;
}

.project-card:hover {
  transform: translateY(-4px);
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-in-out;
}

.modal-content {
  background: #fff;
  padding: 30px 40px;
  border-radius: 12px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease-out;
  font-family: "Helvetica Neue", sans-serif;
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

.project-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  font-size: 16px;
}

.invite-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s ease;
}

.invite-btn:hover {
  background-color: #66b1ff;
}

.modal-footer {
  margin-top: 20px;
  text-align: center;
}

.close-btn {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ccc;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s ease;
}

.close-btn:hover {
  background-color: #e6e6e6;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    background-color: rgba(0, 0, 0, 0);
  }
  to {
    background-color: rgba(0, 0, 0, 0.4);
  }
}
/* 默认按钮颜色（邀请） */
.invite-btn:not([disabled]) {
  background-color: #409EFF;
}

/* 已邀请（灰色） */
.invite-btn.invited {
  background-color: #909399;
}

/* 申请中（橙色） */
.invite-btn.pending {
  background-color: #E6A23C;
}

/* 已加入或管理员（绿色） */
.invite-btn.joined {
  background-color: #67C23A;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1rem;
  padding-bottom: 0.3rem;
  color: #2c3e50;
}

.publication-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.publication-item {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 1rem 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 6px rgb(0 0 0 / 0.1);
  transition: box-shadow 0.3s ease;
}

.publication-item:hover {
  box-shadow: 0 4px 12px rgb(0 0 0 / 0.15);
}

.pub-title {
  font-size: 1.3rem;
  color: #34495e;
  margin-bottom: 0.5rem;
}

.pub-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.8rem;
}

.meta-item strong {
  color: #34495e;
}

.pub-abstract {
  font-size: 1rem;
  line-height: 1.5;
  color: #444;
}

.empty-message {
  color: #999;
  font-style: italic;
}

/* 背景遮罩 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

/* 弹窗内容 */
.modal-content {
  background-color: #fff;
  border-radius: 12px;
  padding: 24px;
  width: 500px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
  animation: fadeInUp 0.25s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-title {
  margin-bottom: 12px;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.modal-textarea {
  width: 95%;
  height: 100px;
  resize: none;
  padding: 10px;
  font-size: 14px;
  margin-bottom: 16px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s ease;
}

.modal-btn.send {
  background-color: #3b82f6;
  color: #fff;
}

.modal-btn.send:hover {
  background-color: #2563eb;
}

.modal-btn.cancel {
  background-color: #f3f4f6;
}

.modal-btn.cancel:hover {
  background-color: #e5e7eb;
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  font-size: 14px;
}

.pagination button {
  padding: 6px 12px;
  border: 1px solid #d0d0d0;
  background-color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination button:hover:not(:disabled) {
  background-color: #f0f0f0;
}

.pagination button:disabled {
  cursor: not-allowed;
  color: #aaa;
  background-color: #f9f9f9;
  border-color: #eee;
}

.pagination .page-info {
  margin: 0 10px;
  color: #555;
  font-weight: 500;
}

</style>