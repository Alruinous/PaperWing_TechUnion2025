<template>
  <PageHeader></PageHeader>
  <div class="container">
    <!-- 顶部基本信息区域 -->
    <section class="top-section">
      <div class="top-content">
        <div class="avatar">
          <img :src="user.avatar_url || '12-modified.png'" alt="头像" />
        </div>
        <div class="basic-info">
          <div class="info-header">
            <h1>{{ user.name }}</h1>
            <button class="edit-btn" @click="openEditModal">Edit Profile</button>
          </div>
          <div class="meta-info">
            <span v-if="user.title" class="meta-item">{{ user.title }}</span>
            <span v-if="user.education" class="meta-item">{{ user.education }}</span>
            <span v-if="user.institution" class="meta-item">{{ user.institution }}</span>
          </div>
          <p v-if="user.bio" class="bio">{{ user.bio }}</p>
          <p v-if="user.research_fields" class="research-fields">
            <strong>Research Fields：</strong>{{ user.research_fields }}
          </p>
        </div>
      </div>
    </section>

    <!-- 编辑信息模态框 -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="showEditModal = false">&times;</span>
        <h2>Edir Profile</h2>
        <form @submit.prevent="saveUserInfo">
          <!--<div class="form-group">
            <label>Name</label>
            <input v-model="editUser.name" type="text">
          </div>-->
          <div class="form-group">
            <label>Academic Title</label>
            <input v-model="editUser.title" type="text">
          </div>
          <div class="form-group">
            <label>Educational Background</label>
            <input v-model="editUser.education" type="text">
          </div>
          <div class="form-group">
            <label>Institution</label>
            <input v-model="editUser.institution" type="text">
          </div>
          <div class="form-group">
            <label>Bio</label>
            <textarea v-model="editUser.bio" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Research Fields</label>
            <input v-model="editUser.research_fields" type="text">
          </div>
          <div class="form-group">
            <label>Avatar</label>
            <div class="avatar-selector">
              <div v-for="i in 12" :key="i" class="avatar-option"
                   :class="{ selected: selectedAvatar === i }"
                   @click="selectAvatar(i)">
                <img :src="`${i}-modified.png`" alt="头像">
              </div>
            </div>
            <input v-model="editUser.avatar_url" type="hidden">
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="showEditModal = false">cancel</button>
            <button type="submit" class="save-btn">save</button>
          </div>
        </form>
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
      <div v-if="activeTab === 'my-research'" class="tab-content">
        <ul v-if="publications.length > 0" class="publication-list">
          <li
              v-for="pub in publications"
              :key="pub.pub_id"
              class="publication-item"
              @click="goToPublication(pub.pub_id)"
              style="cursor: pointer;"
          >
            <div style="display: flex; justify-content: space-between;">
              <h3>{{ pub.title || 'has not named yet'}}</h3>
              <el-button v-if="pub.local_file_path !== ''" plain @click="gotoPDF(`http://10.251.254.221:8000${pub.local_file_path}`)">View PDF</el-button>
            </div>
            <p><strong>Authors：</strong>{{ pub.authors }}</p>
            <p v-if="pub.journal"><strong>Journal：</strong>{{ pub.journal }}</p>
            <p v-if="pub.year"><strong>Year：</strong>{{ pub.year }}</p>
            <p v-if="pub.abstract"><strong>Abstract:</strong>{{ pub.abstract }}</p>
          </li>
        </ul>

        <p v-else class="empty-message">No publications yet</p>
      </div>

      <!-- 关注者列表 -->
      <div v-if="activeTab === 'followers'" class="tab-content">
        <div v-if="followers.length === 0" class="empty-text">There are currently no followers.</div>
        <ul class="follower-list" v-else>
          <li v-for="follower in pagedFollowers" :key="follower.userId" class="follower-item">
            <img style="cursor: pointer;" :src="follower.avatar_url || defaultAvatar" alt="头像" class="follower-avatar" @click="goToGateway(follower.userId)" />
            <div class="follower-info">
              <p class="follower-name">{{ follower.name }}</p>
              <p class="follower-meta">
                <span v-if="follower.title">{{ follower.title }}</span>
                <span v-if="follower.institution"> - {{ follower.institution }}</span>
              </p>
            </div>
            <button class="unfollow-btn" @click="unfollow(follower.userId)">Unfollow</button>
          </li>
        </ul>

        <!-- 分页控件 -->
        <div v-if="totalFollowerPages > 1" class="pagination">
          <button @click="prevFollowerPage" :disabled="followerPage === 1">← Prev</button>
          <span class="page-info">Page {{ followerPage }} in {{ totalFollowerPages }} </span>
          <button @click="nextFollowerPage" :disabled="followerPage === totalFollowerPages">Next →</button>
        </div>
      </div>



      <!-- 粉丝列表 -->
      <div v-if="activeTab === 'fans'" class="tab-content">
        <div v-if="fans.length === 0" class="empty-text">There are currently no fans.</div>
        <ul class="follower-list" v-else>
          <li v-for="fan in pagedFans" :key="fan.userId" class="follower-item">
            <img style="cursor: pointer;" :src="fan.avatar_url || defaultAvatar" alt="头像" class="follower-avatar" @click="goToGateway(fan.userId)" />
            <div class="follower-info">
              <p class="follower-name">{{ fan.name }}</p>
              <p class="follower-meta">
                <span v-if="fan.title">{{ fan.title }}</span>
                <span v-if="fan.institution"> - {{ fan.institution }}</span>
              </p>
            </div>
            <button
                class="follow-btn"
                @click="followBack(fan.userId)"
                :disabled="isMutualFollow(fan.userId)"
            >
              {{ isMutualFollow(fan.userId) ? 'Mutual Follow' : 'Follow Back' }}
            </button>
          </li>
        </ul>

        <!-- 分页控件 -->
        <div v-if="totalFanPages > 1" class="pagination">
          <button @click="prevFanPage" :disabled="fanPage === 1">← Prev</button>
          <span class="page-info">Page {{ fanPage }} in {{ totalFanPages }} </span>
          <button @click="nextFanPage" :disabled="fanPage === totalFanPages">Next →</button>
        </div>

      </div>


      <!-- 关系图谱 -->
      <div v-if="activeTab === 'graph'" class="tab-content">
        <div class="graph-controls">
          <el-radio-group v-model="graphType" size="large">
            <el-radio-button label="follow">Follow Network</el-radio-button>
            <el-radio-button label="institution">Institutional Network</el-radio-button>
          </el-radio-group>
        </div>

        <div v-if="graphType === 'follow'" ref="followGraph" style="width: 100%; height: 600px; margin-top: 20px;"></div>
        <div v-else ref="institutionGraph" style="width: 100%; height: 600px; margin-top: 20px;"></div>
      </div>

      <!-- 阅读历史 -->
      <div v-if="activeTab === 'history'" class="tab-content history-tab">
        <!-- 搜索框 -->
        <input
            v-model="searchQuery"
            type="text"
            placeholder="Search for literature titles or authors"
            class="search-input"
            @focus="handleFocus"
            @blur="handleBlur"
        />

        <!-- 搜索结果卡片列表 -->
        <div class="card-list">
          <div
              v-for="(record, index) in displayList"
              :key="index"
              class="card-item"
              @mouseover="handleMouseOver"
              @mouseleave="handleMouseLeave"
          >
            <div class="card-content" @click="record.type === 'publication' ? goToPublication(record.item.pub_id) : goToDocument(record.item.local_file_path)" >
              <strong class="card-title">{{ record.item.title }}</strong>
              <div class="card-meta">
                <span>Author: {{ record.item.authors }}</span><br>
                <span>Journal: {{ record.item.journal }}（{{ record.item.year }}年第{{ record.item.issue }}期）</span><br>

              </div>
              <p class="abstract-text">{{ record.item.abstract }}</p>
            </div>
          </div>
        </div>

        <p v-if="displayList.length === 0" style="color: #9ca3af; margin-top: 30px; font-style: italic; text-align: center;">
          No matching reading history found.
        </p>
      </div>

      <!-- 加入的项目 -->
      <div v-if="activeTab === 'joined-projects'" class="tab-content">
        <el-row :gutter="20">
          <el-col
              v-for="(project, index) in joinedProjects"
              :key="project.id"
              :span="8"
              style="margin-bottom: 20px;"
          >
            <el-card
                shadow="hover"
                class="project-card"
                @click="goToProjectDetail(project.id)"
                style="cursor: pointer;"
                draggable="true"
                @dragstart="handleDragStart($event, 1,project.id)"
            >
              <h4 style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">
                {{ project.title || '未命名主题' }}
              </h4>
              <p><strong>Type:</strong>{{ formatType(project.type) }}</p >
              <p><strong>Initiator's ID:</strong>{{ project.initiatorId ?? '无' }}</p >
            </el-card>
          </el-col>
        </el-row>
        <p v-if="joinedProjects.length === 0">You have not joined any projects yet.</p >
      </div>

      <!-- 收藏文献 -->
      <div v-if="activeTab === 'favorites'" class="tab-content">
          <div class="favorites-container">
            <!-- 分类选择器 -->
            <div class="filter-header">
              <el-dropdown trigger="click">
              <el-button class="category-button">
              📁 classification：{{ selectedCategory }} <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="selectCategory('all')">all</el-dropdown-item>
                    <el-dropdown-item @click="selectCategory('self-upload')">self-upload</el-dropdown-item>
                    <el-dropdown-item
                        v-for="category in filteredCategories"
                        :key="category"
                        @click="selectCategory(category)"
                    >
                      {{ category }}
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="showAddCategoryDialog = true">➕ Add classification</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <!-- 文献列表 -->
            <div class="doc-list">
              <div
                  v-for="doc in filteredDocs"
                  :key="doc.doc_id"
                  class="doc-card"
                  draggable="true"
                  @dragstart="handleDragStart($event,0 ,doc.doc_id)"
              >
                <div class="doc-header">
                  <h5 class="doc-title">{{ doc.title }}</h5>

                  <div class="doc-categories">
                    <el-tag
                        v-for="category in doc.categories"
                        :key="category"
                        type="info"
                        size="small"
                        class="mr-1"
                        v-if="doc.categories && doc.categories.length > 0"
                    >
                      {{ category }}
                    </el-tag>
                    <el-tag
                        v-else
                        type="warning"
                        size="small"
                        class="mr-1"
                    >
                    Unclassified
                    </el-tag>

                    <el-button size="small" @click="openClassifyDialog(doc)">Classify</el-button>
                  </div>
                </div>

                <p class="doc-authors">
                  👤 {{ doc.authors }} <span class="doc-year">({{ doc.year }})</span>
                </p>
                <p v-if="doc.abstract" class="doc-abstract">
                  <strong>Abstract:</strong> {{ doc.abstract }}
                </p>

                <p class="doc-conference">📌 {{ doc.conference }}</p>
                <div class="doc-link">
                  <el-button @click="openDoc(doc.doc_url,doc.doc_id)">View Document</el-button>
                </div>
              </div>
            </div>


            <!-- 添加分类 Dialog -->
            <el-dialog title="Add classification" v-model="showAddCategoryDialog">
              <el-input v-model="newCategoryName" placeholder="Please enter the category name" />
              <template #footer>
                <el-button @click="showAddCategoryDialog = false">Cancel</el-button>
                <el-button type="primary" @click="addCategory">Add</el-button>
              </template>
            </el-dialog>

            <!-- 文献分类 Dialog -->
            <el-dialog title="Classify the literature into .." v-model="showClassifyDialog">
              <el-checkbox-group v-model="selectedClassifyTargets">
                <el-checkbox
                    v-for="category in userCategories"
                    :key="category"
                    :label="category"
                >
                  {{ category }}
                </el-checkbox>
              </el-checkbox-group>
              <template #footer>
                <el-button @click="showClassifyDialog = false">Cancel</el-button>
                <el-button type="primary" @click="confirmClassify">Confirm</el-button>
              </template>
            </el-dialog>

          </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <p>&copy; {{ new Date().getFullYear() }} {{ user.name }}.All rights reserved.</p>
      <p>Registered on: {{ formatDate(user.register_time) }}</p>
    </footer>
  </div>

  <!-- AI辅助阅读弹窗 -->
  <div
    class="pin-area"
    @dragover.prevent
    @dragenter.prevent
    @drop="handleDrop"
  >
    <div class="pin-icon">
      <el-tooltip
        class="box-item"
        effect="dark"
        placement="left"
      >
        <template #content>
          <el-scrollbar max-height="25vh">
            <div v-if="aiLoading">
              <div class="loader">
                  <span class="bar"></span>
                  <span class="bar"></span>
                  <span class="bar"></span>
              </div>
            </div>
            <div v-else class="typing-container">
              <span class="typed-text">{{ summary }}</span>
              <span class="cursor" :class="{ 'blinking': !typingComplete }">|</span>
            </div>
          </el-scrollbar>
        </template>
        <div class="loader">
          <div class="modelViewPort">
            <div class="eva">
              <div class="head">
                <div class="eyeChamber">
                  <div class="eye"></div>
                  <div class="eye"></div>
                </div>
              </div>
              <div class="body">
                <div class="hand"></div>
                <div class="hand"></div>
                <div class="scannerThing"></div>
                <div class="scannerOrigin"></div>
              </div>
            </div>
          </div>
        </div>
      </el-tooltip>
    </div>
  </div>

</template>

<script setup>
import 'element-plus/dist/index.css'
import { FollowUser, UnfollowUser } from '@/api/home.js'
import { useRouter } from 'vue-router'
import { ref, reactive, nextTick} from 'vue'
import {
  fetchUserInfo,
  updateUserInfo,
  fetchFavorites,
  aiSummaryDoc,
  updateDocCategory,
  fetchFollowers
} from "@/api/user.js";
import {fetchUserCategories, fetchUserPublications, addUserCategory} from "@/api/production.js";
import { onMounted, watch } from 'vue'
import cookies from 'vue-cookies'
import { post, get } from "@/api/api";
import { getUserHistory, addDocHistory } from '@/api/record.js';
import {ElMessage} from "element-plus";
import * as echarts from 'echarts';
const selectedCategory = ref('all')
const showAddCategoryDialog = ref(false)
const showClassifyDialog = ref(false)
const newCategoryName = ref('')
const selectedClassifyTargets = ref([])
const currentDoc = ref(null)
const userCategories = ref([])
const usersPerPage = 5  // 每页显示数量，代替原 pageSize
const filteredCategories = computed(() =>
    (userCategories.value || []).filter(
        c => c.trim().toLowerCase() !== 'all' && c.trim().toLowerCase() !== 'self-upload'
    )
);

const CurrentPaperId = ref(null); // 用于存储当前文献的 ID
const openDoc = (url,paperId) => {
  const userId = cookies.get('userId')
  const userIdNum = parseInt(userId)
  addDocHistory({
    userId: userIdNum,
    documentId: paperId
    
  })
  if (url && typeof globalThis.open === 'function') {
    globalThis.open(url, '_blank');
  } else {
    console.warn('The document link is empty or cannot open a new window');
  }
};
// ---------- 粉丝分页 ----------
const fanPage = ref(1)

const pagedFans = computed(() => {
  const start = (fanPage.value - 1) * usersPerPage
  return fans.value.slice(start, start + usersPerPage)
})

const totalFanPages = computed(() => Math.ceil(fans.value.length / usersPerPage))

const nextFanPage = () => {
  if (fanPage.value < totalFanPages.value) fanPage.value++
}
const prevFanPage = () => {
  if (fanPage.value > 1) fanPage.value--
}

// ---------- 关注者分页 ----------
const followerPage = ref(1)

const pagedFollowers = computed(() => {
  const start = (followerPage.value - 1) * usersPerPage
  return followers.value.slice(start, start + usersPerPage)
})

const totalFollowerPages = computed(() => Math.ceil(followers.value.length / usersPerPage))

const nextFollowerPage = () => {
  if (followerPage.value < totalFollowerPages.value) followerPage.value++
}
const prevFollowerPage = () => {
  if (followerPage.value > 1) followerPage.value--
}
async function loadCategories() {
  try {
    const userId = cookies.get('userId');
    userCategories.value = await fetchUserCategories(userId)
  } catch (error) {
    console.error('Failed to obtain classification:', error.message)
  }
}

// 切换分类
const selectCategory = (cat) => {
  selectedCategory.value = cat
}

// 添加分类
const addCategory = async () => {
  const name = newCategoryName.value.trim()
  if (!name || userCategories.value.includes(name)) {
    ElMessage.warning('Duplicate or empty category name')
    return
  }

  try {
    const userId = cookies.get('userId');
    await addUserCategory(userId, name);
    // userId 是你当前用户的 ID
    userCategories.value.push(name)
    ElMessage.success('Added successfully')
    newCategoryName.value = ''
    showAddCategoryDialog.value = false
  } catch (error) {
    ElMessage.error(error.message || 'Add failed')
  }
}

// 点击“分类”按钮
const openClassifyDialog = (doc) => {
  currentDoc.value = doc
  selectedClassifyTargets.value = doc.categories
  showClassifyDialog.value = true
}

// 确认分类
const confirmClassify = async () => {
  try {
    const userId = cookies.get('userId');
    const docId = currentDoc.value.doc_id;
    await updateDocCategory(userId, docId, selectedClassifyTargets.value);
    ElMessage.success('Classification update successful');
    showClassifyDialog.value = false;
    // 可选：重新加载文献列表以刷新分类显示
    await loadAllDocs();
  } catch (err) {
    ElMessage.error('Classification update failed');
  }
};

// 选中的分类过滤文献
const filteredDocs = computed(() => {
  if (selectedCategory.value === 'all') {
    return allDocs.value
  } else {
    return allDocs.value.filter(d => d.categories.includes(selectedCategory.value))
  }
})

const allDocs = ref([])
async function loadAllDocs() {
  try {
    const userId = cookies.get('userId')
    allDocs.value = await fetchFavorites(userId)
  } catch (error) {
    console.error('Failed to load collected literature', error)
  }
}
function gotoPDF(url) {
  const userId = cookies.get('userId')

  addDocHistory({

    documentId: CurrentPaperId.value,
    userId: parseInt(userId)
  })
  window.open(url, '_blank');
}


onMounted(async () => {
  try {
    const userId = cookies.get('userId');
    await loadFollowers();
    await loadFans();
    await loadJoinedProjects();
    await loadPublications();
    await loadCategories();
    await loadAllDocs()
    // favorites.value = await fetchFavorites(userId)
    const data = await fetchUserInfo(userId)
    Object.assign(user, data)
  } catch (error) {
    console.error('Failed to obtain user information:', error)
  }
})

// 顶部导航项和当前激活的标签
const topNav = ref([
  { id: 'my-research', label: 'My Publications' },
  { id: 'followers', label: 'Following' },
  { id: 'fans', label: 'Followers' },
  { id: 'graph', label: 'Relation Graph' },
  { id: 'history', label: 'Reading History' },
  { id: 'joined-projects', label: 'Joined Projects' },
  { id: 'favorites', label: 'Favorite Papers' },
])

// 确保 activeTab 在 watch 之前定义
const activeTab = ref('my-research') // 默认显示第一个标签
const user = reactive({});
const joinedProjects = ref([]);
const publications = ref([]);
const router = useRouter();
const favorites = ref([]);
const defaultAvatar = "12-modified.png"

function goToPublication(pubId) {
  router.push({
    name: 'production',
    query: { pubId }
  })
}
function goToGateway(userId) {
  router.push({
    path: '/gateway',
    query: { userId: userId }
  });
}

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

// 加载关注者数据
const loadFollowers = async () => {
  try {
    const userId = cookies.get('userId');
    if (!userId) {
      console.warn('No userId found in cookies');
      return;
    }
    const data = await fetchFollowers(userId);
    followersData.value = data;
    followers.value = data;
  } catch (error) {
    console.error('Failed to obtain followers', error);
  }
}

const isMutualFollow = (userId) => {
  return followers.value.some(follower => follower.userId === userId)
}
// 加载粉丝数据
const loadFans = async () => {
  try {
    const res = await post('/users/followers/', {
      userId: cookies.get('userId')
    })
    if (res && res.data) {
      fansData.value = res.data;
      fans.value = res.data;
    }
  } catch (error) {
    console.error('Failed to obtain fans', error)
  }
}

// 加载同机构用户数据
const loadInstitutionUsers = async () => {
  try {
    const userId = cookies.get('userId')

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
    userId: cookies.get('userId')
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
    if (params.dataType === 'node' && params.data.userId != cookies.get('userId')) {
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
    userId: cookies.get('userId')
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
    if (params.dataType === 'node' && params.data.userId != cookies.get('userId')) {
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
        loadFollowers(),
        loadFans(),
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
  if (activeTab.value === 'graph') {
    setTimeout(() => {
      // 确保数据加载后再渲染
      Promise.all([
        loadFollowers(),
        loadFans(),
        loadInstitutionUsers()
      ]).then(() => {
        renderFollowGraph()
        renderInstitutionGraph()
      })
    }, 500)
  }
})

// 用户信息相关代码
const selectedAvatar = ref(1);
const selectAvatar = (index) => {
  selectedAvatar.value = index;
  editUser.avatar_url = `${index}-modified.png`;
  cookies.set('avatarUrl', `${index}-modified.png`);
};

// 编辑状态
const showEditModal = ref(false)
const editUser = reactive({})

// 打开编辑模态框时复制用户数据
const openEditModal = () => {
  Object.assign(editUser, {
    userId: user.user_id,
    name: user.name,
    title: user.title,
    education: user.education,
    institution: user.institution,
    avatar_url: user.avatar_url,
    bio: user.bio,
    research_fields: user.research_fields
  });
  
  // 解析当前头像对应的索引
  const avatarUrl = user.avatar_url || '';
  const match = avatarUrl.match(/^(\d+)-/);
  if (match && match[1]) {
      const index = parseInt(match[1]);
      if (index >= 1 && index <= 12) {
          selectedAvatar.value = index;
      }
  }
  showEditModal.value = true;
}

//获取加入的项目
const loadJoinedProjects = async () => {
  try {
    const res = await post('/discussions/joined/', {
      userId: cookies.get('userId') // 从 cookie 中读取用户 ID
    })
    joinedProjects.value = res || []
  } catch (error) {
    console.error('Failed to retrieve the joined project', error)
  }
}

const goToProjectDetail = (projId) => {
  router.push({
    path: '/project',
    query: {projId}
  });
};


// 保存用户信息
const saveUserInfo = async () => {
  try {
    await updateUserInfo(editUser)
    // 成功后，把修改合并到 user.value
    Object.assign(user, editUser)
    // 关闭编辑弹窗
    showEditModal.value = false
    window.location.reload();
  } catch (error) {
    console.error('Failed to save user information:', error)
    alert('Save failed, please try again')
  }
}
// 格式化日期
const formatDate = (dateString) => {
  const options = {year: 'numeric', month: 'long', day: 'numeric'}
  return new Date(dateString).toLocaleDateString('en-US', options)
}

// 示例关注者数据
const followers = ref([])

// 示例粉丝数据
const fans = ref([])

//取关
const unfollow = async (followerId) => {
  var promise = UnfollowUser(cookies.get('userId'), followerId);
  promise.then((result) => {
    if (result.success === true) {
      ElMessage.success("Unsubscribed!");
      loadFollowers();
    } else {
      ElMessage.error(result.message)
    }
  });
}
// 回关逻辑（可接入后端 API）
const followBack = async (followerId) => {
  var promise = FollowUser(cookies.get('userId'), followerId);
  promise.then((result) => {
    if (result.success === true) {
      ElMessage.success("Followed!");
      loadFollowers();
    } else {
      ElMessage.error(result.message)
    }
  });
}


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

// 加载用户成果
async function loadPublications() {
  try {
    const userId = cookies.get('userId');
    const data = await fetchUserPublications(userId);
    publications.value = data.publications || [];
  } catch (error) {
    console.error('Failed to load user achievements:', error);
  }
}

function formatType(type) {
  if (type === 'forum') return 'forum'
  if (type === 'project') return 'project'
  return 'Unknown'
}


// AI辅助阅读
const summary = ref("Drag and drop the collected literature here to generate an AI abstract")
const aiLoading = ref(false)
// 打字机效果相关
const typingComplete = ref(false)
const typingSpeed = 20 // 打字速度(毫秒/字符)

// 添加draggedId的ref
const draggedId = ref(null);
const type = ref(0) //是0的话就是文献，1的话就是项目

// 处理拖拽开始事件
const handleDragStart = (event, type0 ,id) => {
  type.value = type0
  draggedId.value = id;
  event.dataTransfer.setData('text/plain', id);
  event.dataTransfer.effectAllowed = 'move';
  CurrentPaperId.value = id;
};

// 处理拖拽放置事件
const handleDrop = (event) => {
  event.preventDefault();
  const id = event.dataTransfer.getData('text/plain');
  if (id) {
    openAiDialog(id);
  }
};

function openAiDialog(id) {
  typingComplete.value = false
  aiLoading.value = true
  
  var promise
  if(type.value == 0){
    promise = aiSummaryDoc(id)
  }
  else{
    promise = projectSummary(id)
  }
  let text;
  promise.then((result) => {
    if(result.success) {
      text = result.data.summary
    } else {
      text = "Sorry, we can't generate a summary for this document."
    }
  })
  .finally(() => {
    aiLoading.value = false
    typeWriterEffect(text)
  })
}

function typeWriterEffect(text) {

  let i = 0
  summary.value = ""

  function type() {
    if (i < text.length) {
      summary.value += text.charAt(i)
      i++
      setTimeout(type, typingSpeed)
    } else {
      typingComplete.value = true
    }
  }

  nextTick(() => {
    type()
  })
}


const historyList = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
watch(() => activeTab.value, (newVal) => {
  if (newVal === 'history') {
    loadHistory()
  }
})
const loadHistory = async () => {

  try {
    const userId = cookies.get('userId')

    const res = await getUserHistory({
      userId: parseInt(userId), // 确保 userId 是整数
      page: page.value,
      pageSize: pageSize.value
    })
    const data = res.data || {}
    historyList.value = data.results || []
    total.value = data.total_items || 0
    page.value = data.current_page || 1
    pageSize.value = data.page_size || 10
  } catch (err) {
    console.warn('Failed to load reading history', err)
  }
}

const handlePageChange = (newPage) => {
  page.value = newPage
  loadHistory()
}

onMounted(() => {
  loadHistory()
})

const searchQuery = ref('')
import { computed } from 'vue'
import { projectSummary } from '@/api/discussions';
const filteredHistory = computed(() => {
  if (!searchQuery.value.trim()) return historyList.value

  const keyword = searchQuery.value.toLowerCase()
  return historyList.value.filter(item => {
    const title = item.item.title?.toLowerCase() || ''
    const authors = item.item.authors?.toLowerCase() || ''
    return title.includes(keyword) || authors.includes(keyword)
  })
})

const displayList = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()
  if (!keyword) return historyList.value // 没有关键词，显示全部

  return historyList.value.filter(item => {
    const title = item.item.title?.toLowerCase() || ''
    const authors = item.item.authors?.toLowerCase() || ''
    return title.includes(keyword) || authors.includes(keyword)
  })
})
const goToDocument = (localPath) => {
  const baseURL = 'http://10.251.254.221:8000'
  const fullURL = baseURL + localPath
  window.open(fullURL, '_blank')  // 新窗口打开
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

/* 编辑按钮 */
.edit-btn {
  padding: 6px 14px;
  font-size: 0.9em;
  background-color: #3b82f6;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.edit-btn:hover {
  background-color: #2563eb;
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

.tab-content {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
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

.close {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 24px;
  cursor: pointer;
  color: #aaa;
}

.close:hover {
  color: #333;
}

.form-group {
  margin-bottom: 15px;
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  background-color: #d32f2f;
}

.save-btn:hover {
  background-color: #388E3C;
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
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s ease;
}

.follower-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.avatar-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr); /* 4列布局 */
  gap: 10px;
  margin-top: 10px;
}

.avatar-option {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.avatar-option:hover {
  transform: scale(1.1);
}

.avatar-option.selected {
  border-color: #409EFF;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.6);
}

.avatar-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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

.category-button {
  background-color: transparent;
  border: none;
  box-shadow: none;
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
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

.filter-header {
  margin-bottom: 16px; /* 或你想要的任意数值 */
}

.empty-message {
  color: #999;
  font-style: italic;
}
.favorites-container {
  padding: 20px;
  background-color: #f9f9fc;
}

.section-title {
  font-size: 24px;
  margin-bottom: 16px;
  color: #2c3e50;
}

.empty-message {
  font-size: 16px;
  color: #888;
  text-align: center;
  margin-top: 40px;
}

.category-section {
  margin-bottom: 30px;
}

.category-title {
  font-size: 20px;
  font-weight: bold;
  color: #34495e;
  margin-bottom: 12px;
  border-bottom: 2px solid #dcdfe6;
  padding-bottom: 4px;
}

.doc-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.doc-card {
  background-color: #ffffff;
  border: 1px solid #e1e4e8;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: transform 0.2s ease;
}

.doc-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.doc-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 6px;
}

.doc-authors {
  font-size: 14px;
  color: #666;
  margin-bottom: 6px;
}

.doc-year {
  color: #999;
}

.doc-abstract {
  font-size: 14px;
  color: #444;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 6; /* 最多显示6行 */
  overflow: hidden;
  text-overflow: ellipsis;
}


.doc-conference {
  font-size: 13px;
  color: #888;
  font-style: italic;
}

/* 强制图表中所有 image 元素裁剪为圆形 */
:deep(.echarts) image {
  clip-path: circle(50% at 50% 50%);
  -webkit-clip-path: circle(50% at 50% 50%);
}

/* 如果存在 ECharts tooltip 中的 <img>，也一并圆角 */
:deep(.echarts-tooltip) img {
  border-radius: 50%;
}
.doc-path {
  font-size: 13px;
  color: #555;
  font-family: "Courier New", monospace;
  word-break: break-all;
  margin-top: 4px;
}



/* 弹窗 */
.dialog-box {
  background-color: #F2F6FC;
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
  border-radius: 5px;
  line-height: 1.5;
  padding: 1vw;
  font-size: 15px;
}

/* 添加固钉区域的样式 */
.pin-area {
  position: fixed;
  bottom: 20vh;
  right: 3vw;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.3s ease;
}

.pin-area:hover {
  transform: scale(1.1);
}

.pin-icon {
  font-size: 24px;
  position: relative;
}

/* 修改卡片样式，添加拖拽效果 */
.doc-card {
  user-select: none;
}

.doc-card:active {
  cursor: grabbing;
}

/* 拖拽时的样式 */
.doc-card[draggable="true"]:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 打字机 */
.typed-text {
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 15vw;
  display: inline-block;
}

.cursor {
  display: inline-block;
  margin-left: 2px;
  color: #409EFF;
  font-weight: bold;
}

.blinking {
  animation: blink 0.7s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 机器人 */
.modelViewPort {
  /* The black circle background around the model*/
  perspective: 1000px;
  width: 6rem;
  aspect-ratio: 1;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: Transparent;
  overflow: hidden;
}

.eva {
  --EVA-ROTATION-DURATION: 4s;
  transform-style: preserve-3d;
  animation: rotateRight var(--EVA-ROTATION-DURATION) linear infinite alternate;
}

.head {
  position: relative;
  width: 1.8rem;
  height: 1.2rem;
  border-radius: 48% 53% 45% 55% / 79% 79% 20% 22%;
  background: linear-gradient(to right, white 45%, gray);
}

.eyeChamber {
  width: 1.35rem;
  height: 0.825rem;
  position: relative;
  left: 50%;
  top: 55%;
  border-radius: 45% 53% 45% 48% / 62% 59% 35% 34%;
  background-color: #0c203c;
  box-shadow: 0px 0px 2px 2px white, inset 0px 0px 0px 2px black;
  transform: translate(-50%, -50%);
  animation: moveRight var(--EVA-ROTATION-DURATION) linear infinite alternate;
}

.eye {
  width: 0.36rem;
  height: 0.45rem;
  position: absolute;
  border-radius: 50%;
}

.eye:first-child {
  left: 12px;
  top: 50%;
  background: repeating-linear-gradient(
    65deg,
    #9bdaeb 0px,
    #9bdaeb 1px,
    white 2px
  );
  box-shadow: inset 0px 0px 5px #04b8d5, 0px 0px 15px 1px #0bdaeb;
  transform: translate(0, -50%) rotate(-65deg);
}

.eye:nth-child(2) {
  right: 12px;
  top: 50%;
  background: repeating-linear-gradient(
    -65deg,
    #9bdaeb 0px,
    #9bdaeb 1px,
    white 2px
  );
  box-shadow: inset 0px 0px 5px #04b8d5, 0px 0px 15px 1px #0bdaeb;
  transform: translate(0, -50%) rotate(65deg);
}

.body {
  width: 1.8rem;
  height: 2.4rem;
  position: relative;
  margin-block-start: 0.25rem;
  border-radius: 47% 53% 45% 55% / 12% 9% 90% 88%;
  background: linear-gradient(to right, white 35%, gray);
}

.hand {
  position: absolute;
  left: -0.45rem;
  top: 0.225rem;
  width: 0.6rem;
  height: 1.65rem;
  border-radius: 40%;
  background: linear-gradient(to left, white 15%, gray);
  box-shadow: 5px 0px 5px rgba(0, 0, 0, 0.25);
  transform: rotateY(55deg) rotateZ(10deg);
}

.hand:first-child {
  animation: compensateRotation var(--EVA-ROTATION-DURATION) linear infinite
    alternate;
}

.hand:nth-child(2) {
  left: 92%;
  background: linear-gradient(to right, white 15%, gray);
  transform: rotateY(55deg) rotateZ(-10deg);
  animation: compensateRotationRight var(--EVA-ROTATION-DURATION) linear
    infinite alternate;
}

.scannerThing {
  width: 0;
  height: 0;
  position: absolute;
  left: 60%;
  top: 10%;
  border-top: 54px solid #9bdaeb;
  border-left: 75px solid transparent;
  border-right: 75px solid transparent;
  transform-origin: top left;
  mask: linear-gradient(to right, white, transparent 35%);
  animation: glow 2s cubic-bezier(0.86, 0, 0.07, 1) infinite;
}
.card-meta {
  font-size: 14px;
  color: #555;
  margin: 8px 0;
}
.abstract-text {
  white-space: nowrap;            /* 不换行 */
  overflow: hidden;               /* 超出隐藏 */
  text-overflow: ellipsis;        /* 显示省略号 */
  max-width: 100%;                /* 限定最大宽度，避免撑破容器 */
  display: block;                 /* 保证生效 */
  color: #4b5563;                 /* 可选：灰色字体更柔和 */
}

.scannerOrigin {
  position: absolute;
  width: 2.4px;
  aspect-ratio: 1;
  border-radius: 50%;
  left: 60%;
  top: 10%;
  background: #9bdaeb;
  box-shadow: inset 0px 0px 5px rgba(0, 0, 0, 0.5);
  animation: moveRight var(--EVA-ROTATION-DURATION) linear infinite;
}
@keyframes rotateRight {
  from {
    transform: rotateY(0deg);
  }
  to {
    transform: rotateY(25deg);
  }
}
@keyframes moveRight {
  from {
    transform: translate(-50%, -50%);
  }
  to {
    transform: translate(-40%, -50%);
  }
}
@keyframes compensateRotation {
  from {
    transform: rotateY(55deg) rotateZ(10deg);
  }
  to {
    transform: rotatey(30deg) rotateZ(10deg);
  }
}
@keyframes compensateRotationRight {
  from {
    transform: rotateY(55deg) rotateZ(-10deg);
  }
  to {
    transform: rotateY(70deg) rotateZ(-10deg);
  }
}
@keyframes glow {
  from {
    opacity: 0;
  }
  20% {
    opacity: 1;
  }
  45% {
    transform: rotate(-25deg);
  }
  75% {
    transform: rotate(5deg);
  }
  100% {
    opacity: 0;
  }
}

/* loading条 */
.loader {
  display: flex;
  align-items: center;
}

.bar {
  display: inline-block;
  width: 3px;
  height: 20px;
  background-color: rgba(255, 255, 255, .5);
  border-radius: 10px;
  animation: scale-up4 1s linear infinite;
}

.bar:nth-child(2) {
  height: 35px;
  margin: 0 5px;
  animation-delay: .25s;
}

.bar:nth-child(3) {
  animation-delay: .5s;
}

@keyframes scale-up4 {
  20% {
    background-color: #ffff;
    transform: scaleY(1.5);
  }

  40% {
    transform: scaleY(1);
  }
}

.doc-categories {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}
.mr-1 {
  margin-right: 4px;
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

.doc-link {
  margin-top: 0.75rem;
  text-align: right;
}

.doc-abstract {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3; /* 最多显示3行 */
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5em;
  max-height: 4.5em; /* line-height × 行数 */
  white-space: normal;
}
</style>