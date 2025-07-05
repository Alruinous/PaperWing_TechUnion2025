<template>
  <PageHeader/>
  <div class="scholar-page-root">
    <!-- 上栏标题 -->
    <div class="header-bar">
      <h1>Scholar Search Results</h1>
    </div>
    <!-- 下栏内容区 -->
    <div class="content-bg">
      <div class="content-main">
        <!-- 左侧：搜索结果列表 -->
        <div class="left-panel">
          <div class="sort-controls sort-controls-left">
            <div class="sort-btns">
              <el-radio-group v-model="sortBy" fill="#b5d1f0">
                <el-radio-button :value="1">Relevance</el-radio-button>
                <el-radio-button :value="2">Publications</el-radio-button>
              </el-radio-group>
              <p class="sort-icon-btn">
                <el-icon v-if="sortDown===1" @click="sortDown=-1" size="20" color="#385b9d"><SortDown /></el-icon>
                <el-icon v-if="sortDown===-1" @click="sortDown=1" size="20" color="#385b9d"><SortUp /></el-icon>
              </p>
            </div>
          </div>
          <div class="results-list">
            <div 
              v-for="(scholar, index) in showRes" 
              :key="index" 
              class="result-item"
              @click="viewScholar(scholar)"
            >
              <div class="item-avatar-col" style="margin-top: 5px; margin-left:15px;margin-right:10px;">
                <img class="item-avatar" :src="scholar.avatar_url || 'https://cdn.jsdelivr.net/gh/edent/SuperTinyIcons/images/svg/user.svg'" alt="avatar" />
                <button
                  v-if="scholar.id != userId && !scholar.isFollowed"
                  class="follow-btn"
                  :class="{ isFollowed: scholar.isFollowed }"
                  @click.stop="followScholar(scholar)"
                >
                  <span v-if="!scholar.isFollowed">+Follow</span>
                </button>
                <button
                  v-if="scholar.id != userId && scholar.isFollowed"
                  class="unfollow-btn"
                  :class="{ isFollowed: scholar.isFollowed }"
                  @click.stop="unFollowScholar(scholar)"
                >
                  <span>Followed</span>
                </button>
              </div>
              <div class="item-content-col">
                <div class="item-row1">
                  <span class="scholar-name">{{ scholar.name }}</span>
                  <span class="scholar-organization">{{ scholar.institution }}</span>
                  <span class="scholar-email">{{ scholar.email || 'No Email Available' }}</span>
                </div>
                <div class="item-divider"></div>
                <div class="item-row2">
                  <span class="scholar-bio">{{ scholar.bio || 'No Biography Available' }}</span>
                </div>
                <div class="item-row3">
                  <div class="item-fields-row">
                    <div class="item-fields">
                      <span
                        v-for="(field, idx) in scholar.research_fields"
                        :key="idx"
                        class="research-field"
                      >
                        <i class="field-icon"></i> {{ field }}
                      </span>
                    </div>
                    <div class="scholar-papers">
                      <span class="scholar-papers-text">Publications: {{ scholar.paperCount }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="!loading && showRes.length === 0" style="text-align:center; color:#868ea8; font-size:18px; padding:40px 0;">
              No relevant scholars found
            </div>
          </div>
          <div v-if="totalPages > 1" class="pagination">
            <button @click="goToPage(1)" :disabled="currentPage === 1">First Page</button>
            <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">Previous Page</button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Next Page</button>
            <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Last Page</button>
          </div>
        </div>
        <!-- 右侧：AI总结和推荐学者 -->
        <div class="right-panel" v-if="showRightPanel">
          <div class="ai-summary-card">
            <div class="ai-summary-content">
              <div style="color:#868ea8; text-align: center;">
                <div style="font-size:18px; color:#393942; font-weight: 600;">Can't find a scholar you know?</div>
                <div style="font-size:18px; color:#393942; font-weight: 600;">Invite them to join our platform!</div>
                <view style="margin: 10px 0;"> <img src="/img.png" style="height:200px;vertical-align:top;margin-right:8px;" /></view>
                <div style="font-size:12px; line-height:1.7; font-style: italic;">
                  PaperWings, a dedicated web development team: Empowering digital innovation. Code. Create. Inspire.
                </div>
              </div>
            </div>
          </div>
          <div class="recommend-card" v-if="displayed_authors.length > 0">
            <div class="recommend-header" style="margin-top:-10px; margin-bottom:10px; margin-left:-2px; display: flex; justify-content: space-between; align-items: flex-start;">
              <h3 style="margin: 0;">Recommended Scholars</h3>
              <el-icon v-if="recommended_authors.length > 5" :class="{ rotating: isRotating }" style="font-size: 20px; cursor: pointer; margin-right: 0px; margin-top: 6px;" @click="handleRefreshClick">
                <Refresh />
              </el-icon>
            </div>
            <div v-for="(author, index) in displayed_authors" :key="index">
              <div class="author-card">
                <div class="author-info">
                  <el-avatar :src="author.avatar" :size="40" />
                  <span class="author-name" @click="gotoScholar(author.userId)">{{ author.userName }}</span>
                </div>
                <div>
                  <button v-if="!author.isFollowed" class="follow-button" @click="followUser(author.userId, author)">Follow</button>
                  <button v-else class="followed-button" @click="unfollowUser(author.userId, author)">✓Followed</button>
                </div>
              </div>
              <el-divider v-if="index < displayed_authors.length - 1" class="el-divider"></el-divider>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchScholars } from '@/api/user';
import { FollowUser, UnfollowUser, GetAuthors } from '@/api/home';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import PageHeader from '../../components/PageHeader.vue';
import { ref, computed, getCurrentInstance } from 'vue';

export default {
  data() {
    return {
      allResults: [], // 保存所有结果
      showRes: [],    // 当前页显示的结果
      loading: false,
      currentPage: 1,
      totalPages: 1,
      sortBy: 1,
      sortDown: 1,
      pageSize: 10, // 每页条数
      userId: this.$cookies.get('userId'),
      router:useRouter(),
      showRightPanel: true, // 控制右侧AI总结和推荐卡片显示
      // 推荐学者相关
      recommended_authors: [], // 所有推荐学者
      displayed_authors: [],   // 当前展示的推荐学者
      displayCount: 5,
      isRotating: false,
    };
  },
  computed: {
    searchConditions() {
      const conditionsQuery = this.$route.query.conditions;
      if (!conditionsQuery) {
        return [];
      }
      try {
        const decodedConditions = decodeURIComponent(conditionsQuery);
        const conditions = JSON.parse(decodedConditions);
        return Array.isArray(conditions) ? conditions : [conditions].filter(Boolean);
      } catch (error) {
        console.error("Failed to parse search conditions:", error);
        return [];
      }
    },
    sortedResults() {
      if (this.sortBy === 1) {
        // 按相关度排序
        return this.sortDown === 1 ? this.allResults : this.allResults.slice().reverse();
      } else if (this.sortBy === 2) {
        // 按论文数排序
        let sorted = [...this.allResults];
        sorted.sort((a, b) => (b.paperCount - a.paperCount) * this.sortDown);
        return sorted;
      }
      return this.allResults;
    },
    pagedResults() {
      // 分页逻辑
      const start = (this.currentPage - 1) * this.pageSize;
      return this.sortedResults.slice(start, start + this.pageSize);
    },
    totalPagesComputed() {
      return Math.max(1, Math.ceil(this.allResults.length / this.pageSize));
    },
  },
  methods: {
    goToFieldPage(field) {
      this.$router.push({
        path: '/field',
        query: { id: field.fieldId }
      });
    },

    async fetchResults() {
      this.loading = true;
      try {
        const condition = this.$route.query.condition;
        const type = this.$route.query.type;
        const data = await fetchScholars(this.userId, condition, type);
        if (!data.success) {
          this.loading = false;
          this.allResults = [
            {
              id: '11',
              name: '测试学者A111111',
              email: 'a@buaa.edu.cn',
              institution: '北京航空航天大学',
              avatar_url: '',
              research_fields: ['人工智能', '深度学习'],
              isFollowed: false,
              bio: '这是一个很长的简介，用于测试多行省略效果。'.repeat(2),
              paperCount: 4,
              followed: 0
            },
            {
              id: '12',
              name: '测试学者B',
              email: 'b@tsinghua.edu.cn',
              institution: '清华大学',
              avatar_url: '',
              research_fields: ['机器学习', '数据挖掘'],
              isFollowed: false,
              bio: '专注于机器学习与数据挖掘。',
              paperCount: 12,
              followed: 0
            },
            {
              id: '13',
              name: '测试学者C',
              email: 'c@fudan.edu.cn',
              institution: '复旦大学',
              avatar_url: '',
              research_fields: ['自然语言处理', '知识图谱'],
              isFollowed: false,
              bio: '复旦大学教授，研究方向为自然语言处理、知识图谱、智能问答系统。'.repeat(2),
              paperCount: 30,
              followed: 0
            },
            {
              id: '14',
              name: '测试学者D',
              email: 'd@zju.edu.cn',
              institution: '浙江大学',
              avatar_url: '',
              research_fields: ['计算机视觉'],
              isFollowed: false,
              bio: '浙江大学副教授，主要研究方向为计算机视觉。',
              paperCount: 7,
              followed: 0
            },
            {
              id: '15',
              name: '测试学者E',
              email: 'e@nju.edu.cn',
              institution: '南京大学',
              avatar_url: '',
              research_fields: ['大数据', '智能系统'],
              isFollowed: false,
              bio: '南京大学博士生导师，研究兴趣包括大数据分析与智能系统。',
              paperCount: 22,
              followed: 0
            }
          ];
        } else {
          this.allResults = data.data.scholars;
          this.loading = false;
        }
        this.totalPages = this.totalPagesComputed;
        this.currentPage = 1;
        this.updateShowRes();
      } catch (error) {
        console.error("Error occurred while fetching results", error);
        this.loading = false;
      } finally {
        this.loading = false;
      }
    },
    updateShowRes() {
      this.showRes = this.pagedResults;
      this.totalPages = this.totalPagesComputed;
    },
    goToPage(page) {
      this.currentPage = page;
      this.updateShowRes();
    },
    viewScholar(scholar) {
      this.router.push({
        path: '/gateway',
        query: {
          userId: scholar.id
        }
      });
    },
    async followScholar(scholar) {
      if (!scholar.isFollowed) {
        try {
          scholar.isFollowed = true;
          const res = await FollowUser(this.userId, scholar.id);
        } catch (e) {
        }
      }
    },
    async unFollowScholar(scholar) {
      if (scholar.isFollowed) {
        try {
          scholar.isFollowed = false;
          const res = await UnfollowUser(this.userId, scholar.id);
        } catch (e) {
        }
      }
    },
    async fetchRecommendedAuthors() {
      this.recommended_authors = [];
      try {
        const res = await GetAuthors(this.userId);
        if (res.success) {
          this.recommended_authors = res.authors || [];
          this.displayed_authors = this.getRandomAuthors();
        }
      } catch (e) {
        console.error(e);
      }
    },
    handleRefreshClick() {
      if (this.isRotating) return;
      this.isRotating = true;
      this.displayed_authors = this.getRandomAuthors();
      setTimeout(() => {
        this.isRotating = false;
      }, 500);
    },
    gotoScholar(userId) {
      this.router.push({
        path: '/gateway',
        query: { userId }
      });
    },
    async followUser(followeeId, author) {
      try {
        const res = await FollowUser(this.userId, followeeId);
        if (res && res.success) {
          author.isFollowed = 1;
        }
      } catch (e) {
      }
    },
    async unfollowUser(followeeId, author) {
      try {
        const res = await UnfollowUser(this.userId, followeeId);
        if (res && res.success) {
          author.isFollowed = 0;
        }
      } catch (e) {
      }
    },
    getRandomAuthors() {
      // 过滤掉已关注的学者
      const unFollowed = this.recommended_authors.filter(a => !a.isFollowed);
      if (unFollowed.length <= this.displayCount) {
        return [...unFollowed];
      }
      const shuffled = unFollowed.slice();
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return shuffled.slice(0, this.displayCount);
    },
  },
  watch: {
    sortBy() {
      this.currentPage = 1;
      this.updateShowRes();
    },
    sortDown() {
      this.currentPage = 1;
      this.updateShowRes();
    },
    currentPage() {
      this.updateShowRes();
    },
    '$route.query': {
      handler() {
        this.fetchResults();
      },
      deep: true
    }
  },
  mounted() {
    this.fetchResults();
    this.fetchRecommendedAuthors();
  }
};
</script>
  
<style scoped>
:root {
  --theme-color: #385b9d;
  --mid-color:#5f96c7;
  --light-color: #e5f1fe;
  --button-color:#b5d1f0;
  --back-color: #fafbff;
  --shadow-color:rgba(85, 68, 183, 0.185);
  --deep-shadow:rgba(85, 65, 156, 0.311);
  --gray-color:#c7d6db;
  --dark-color: #868ea8;
  --secondary-color: #ecfbff;
  --second-text:#09255e;
  --text-color: #393942;
  --light-text-color: #4f4454;
}

.scholar-page-root {
  width: 100%;
  background: #f5f6fa;
  overflow-x: hidden;
}

.header-bar {
  width: 100%;
  height: 10vh;
  background: #fff;
  display: flex;
  box-shadow: 0 2px 8px rgba(85, 68, 183, 0.05);
  padding-left: 3vw;
  box-sizing: border-box;
}
.header-bar h1 {
  padding-top:3vh;
  font-size: 1.8rem;
  color: #393942;
  margin: 0;
}

.content-bg {
  width: 100%;
  min-height: 82vh;
  background: #f5f6fa;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 2vh;
  box-sizing: border-box;
}

.content-main {
  width: 70vw;
  display: flex;
  flex-direction: row;
  gap: 1vw;
  justify-content: center;
  box-sizing: border-box;
  padding-bottom: 12px;
}

.left-panel {
  width: 60vw;
  min-height: 600px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 10px var(--shadow-color);
  padding: 2vw 2vw 1vw 2vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.right-panel {
  width: 28vw;
  height: 76vh;
  display: flex;
  flex-direction: column;
  gap: 2vh;
  box-sizing: border-box;
}

.ai-summary-card, .recommend-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 10px var(--shadow-color);
  padding: 18px 24px 18px 24px;
  min-height: unset;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.ai-summary-card h3, .recommend-card h3 {
  margin: 0 0 1vh 0;
  color: #385b9d;
  font-size: 1.2rem;
}

.ai-summary-content, .recommend-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sort-controls.sort-controls-left {
  justify-content: flex-start;
  padding-left: 0;
  margin-bottom: 18px;
  box-sizing: border-box;
}
.sort-btns {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sort-icon-btn {
  width: 25px;
  height: 25px;
  border: 1px solid #c7d6db;
  border-radius: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 0 0 10px;
}

.results-list {
  overflow-y: visible;
  padding-top: 0;
  padding-left: 6px;
  box-sizing: border-box;
}

.result-item {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  padding: 18px 20px 18px 6px;
  border: 1px solid #e5f1fe;
  margin-bottom: 18px;
  border-radius: 4px;
  background-color: #fafbff;
  width: 100%;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 5px rgba(85, 68, 183, 0.13);
  transform-origin: 30% 50%;
  box-sizing: border-box;
}

.result-item:hover {
  transform: scale(1.015, 1.03);
  box-shadow: 0 2px 10px rgba(85, 65, 156, 0.211);
}

.item-avatar-col {
  flex: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  margin-right: 22px;
  min-width: 80px;
}
.item-avatar {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  object-fit: cover;
  background: #e5f1fe;
  border: 1px solid #c7d6db;
  margin-bottom: 8px;
}
.follow-btn {
  min-width: 48px;
  height: 24px;
  padding: 0 10px;
  border-radius: 6px;
  border: none;
  background: #385b9d;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 8px;
  transition: background 0.2s;
}
.unfollow-btn {
  min-width: 48px;
  height: 24px;
  padding: 0 10px;
  border-radius: 6px;
  border: 1px solid #385b9d;
  background: #eff2f8;
  color: #385b9d;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-bottom: 8px;
  transition: background 0.2s;
}

.item-content-col {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}
.item-row1 {
  display: flex;
  align-items: flex-end;
  gap: 0;
  margin-bottom: 0;
  min-width: 0;
  flex-wrap: nowrap;
}
.item-divider {
  width: 100%;
  height: 1px;
  background: #e5f1fe;
  margin: 2px 0 10px 0;
}
.scholar-name {
  font-size: 22px;
  font-weight: 600;
  color: #393942;
  margin: 0;
  position: relative;
  top: 2px;
  flex-shrink: 1;
  flex-grow: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}
.scholar-organization {
  font-size: 14px;
  color: #868ea8;
  font-weight: 400;
  margin-left: 8px;
  flex-shrink: 1;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: block;
}
.scholar-email {
  font-size: 14px;
  color: #868ea8;
  margin-left: auto;
  font-weight: 400;
}
.item-row2 {
  margin-bottom: 2px;
}
.scholar-bio {
  font-size: 15px;
  color: #868ea8;
  font-style: normal;
  font-weight: 400;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}
.item-row3 {
  margin-top: 8px;
}
.item-fields-row {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  justify-content: space-between;
  width: 100%;
}
.item-fields {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  width: 70%;
}
.item-fields .research-field {
  margin: 3px 8px 3px 0;
  padding: 4px 10px;
  border: 1px solid #c7d6db;
  border-radius: 15px;
  background-color: #ecfbff;
  font-size: 14px;
  color: #09255e;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}
.scholar-papers {
  font-size: 15px;
  color: #868ea8;
  align-self: flex-end;
  margin-left: auto;
  padding-right: 0;
  font-weight: 500;
}

.field-icon {
  margin-right: 5px;
  color: #385b9d;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  color: #393942;
}

.pagination button {
  padding: 5px 10px;
  margin: 0 5px;
  cursor: pointer;
  border: 1px solid #c7d6db;
  background-color: #fafbff;
  border-radius: 5px;
  color: #393942;
}

.pagination button:disabled {
  cursor: not-allowed;
  background-color: #e0e0e0;
}

.pagination span {
  align-self: center;
}

.scholar-papers-text {
  color: #868ea8;
}

/* 推荐学者卡片内部样式 */
.recommend-header {
  display: flex;
  align-items: center;
  margin-top: -10px;
  margin-bottom: 10px;
  margin-left: -2px;
}
.recommend-header h3 {
  font-size: 1.1rem;
  color: #393942;
  margin: 0 8px 0 0;
  font-weight: 600;
}
.author-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}
.author-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.author-name {
  font-size: 15px;
  color: #393942;
  font-weight: 500;
  cursor: pointer;
}
.follow-button, .followed-button {
  min-width: 48px;
  height: 24px;
  padding: 0 10px;
  border-radius: 6px;
  border: none;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-left: 8px;
  transition: background 0.2s;
}
.follow-button {
  background: #385b9d;
  color: #fff;
}
.followed-button {
  background: #c7d6db;
  color: #fff;
  cursor: not-allowed;
}

/* 推荐学者卡片分隔线间距优化 */
.recommend-card .el-divider {
  margin: 4px 0;
}
</style>
  
