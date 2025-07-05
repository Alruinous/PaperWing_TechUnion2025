<template>
  <div class="publication-page-root">
    <PageHeader />
    <!-- 上栏白色卡片：标题+Tab -->
    <div class="header-bar card-bar">
      <h1>Academic Publication Search Results</h1>
      <el-tabs v-model="activeTab" class="pub-tabs" stretch>
        <el-tab-pane label="Journal Articles" name="journal"></el-tab-pane>
        <el-tab-pane label="Conference Papers" name="conference"></el-tab-pane>
        <el-tab-pane label="Technical Reports" name="techreport"></el-tab-pane>
        <!-- <el-tab-pane label="Posters" name="poster"></el-tab-pane> -->
        <el-tab-pane label="Books" name="book"></el-tab-pane>
        <!-- <el-tab-pane label="Datasets" name="data"></el-tab-pane> -->
        <el-tab-pane label="Patents" name="patent"></el-tab-pane>
      </el-tabs>
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
                <el-radio-button :value="2">Year</el-radio-button>
                <el-radio-button :value="3">Likes</el-radio-button>
              </el-radio-group>
              <p class="sort-icon-btn">
                <el-icon v-if="sortDown===1" @click="sortDown=-1" size="20" color="#385b9d"><SortDown /></el-icon>
                <el-icon v-if="sortDown===-1" @click="sortDown=1" size="20" color="#385b9d"><SortUp /></el-icon>
              </p>
              <div style="flex:1"></div>
              <el-checkbox v-model="onlyDownloadable" style="margin-left:auto;" @change="updateShowRes">Only show downloadable</el-checkbox>
            </div>
          </div>
          <div class="results-list">
            <template v-if="!loading">
            <div 
              v-for="(pub, index) in showRes" 
              :key="index" 
              class="result-item"
              @click="viewPublication(pub)"
            >
              <div class="item-content-col">
                <div class="item-row1">
                  <span class="publication-title">{{ pub.title }}</span>
                  <span class="publication-year">{{ pub.year }}</span>
                    <div class="pub-action-btns">
                      <el-tooltip v-if="pub.external_url" content="External Link" placement="top">
                        <el-icon class="pub-action-icon pub-action-icon-neutral" @click.stop="openExternal(pub.external_url)"><Link /></el-icon>
                      </el-tooltip>
                      <el-tooltip v-if="pub.local_file_path" content="Download" placement="top">
                        <el-icon class="pub-action-icon pub-action-icon-neutral" @click.stop="downloadFile(pub.local_file_path)"><Download /></el-icon>
                      </el-tooltip>
                      <el-tooltip :content="pub.is_favor ? 'Unlike' : 'Like'" placement="top">
                        <span class="favor-btn" :class="{ active: pub.is_favor }" @click.stop="toggleFavor(pub)">
                          <span class="pub-action-icon" :style="pub.is_favor ? 'color:#e74c3c;' : ''"><LucideHeart size="24" /></span>
                          <span class="favor-count">{{ pub.favor_count }}</span>
                        </span>
                      </el-tooltip>
                    </div>
                </div>
                <div class="item-divider"></div>
                <div class="item-row2">
                  <span class="publication-authors">
                      <span
                        v-for="(author, idx) in pub.authors"
                        :key="idx"
                        class="author-item"
                        :class="{ clickable: author.id }"
                        @click.stop="author.id && gotoScholar(author.id)"
                        :style="author.id ? 'cursor:pointer;' : ''"
                      >{{ author.name }}</span>
                  </span>
                </div>
                <div class="item-row3">
                  <span class="publication-abstract">{{ pub.abstract }}</span>
                </div>
                <div class="item-row4">
                  <span class="publication-keywords">
                    <span v-for="(kw, idx) in pub.keywords" :key="idx" class="keyword-item">{{ kw }}</span>
                  </span>
                </div>
              </div>
            </div>
              <div v-if="!loading && showRes.length === 0" style="text-align:center; color:#868ea8; font-size:18px; padding:40px 0;">
                No relevant publications found
              </div>
            </template>
          </div>
          <div v-if="totalPages > 1" class="pagination">
            <button @click="goToPage(1)" :disabled="currentPage === 1">First Page</button>
            <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">Previous Page</button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Next Page</button>
            <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Last Page</button>
          </div>
        </div>
        <!-- 右侧：AI总结和推荐成果 -->
        <div class="right-panel">
          <div class="ai-summary-card">
            <h3>AI Statistics</h3>
            <div class="ai-summary-content" :class="{ 'collapsed': !aiSummaryExpanded, 'expanded': aiSummaryExpanded }" ref="aiSummaryContent">
              <template v-if="aiLoading">
                <div class="ai-summary-loading-wrap">
                  <el-icon class="ai-summary-loading is-loading"><Loading /></el-icon>
                  <div class="ai-summary-wait-text">waiting for AI statistics...</div>
                </div>
              </template>
              <template v-else>
                <div v-html="formattedAiConclusion"></div>
                <div v-if="showAiSummaryToggle && !aiSummaryExpanded" class="ai-summary-fade"></div>
              </template>
            </div>
            <div v-if="showAiSummaryToggle" class="ai-summary-toggle">
              <el-button type="text" @click="aiSummaryExpanded = !aiSummaryExpanded" style="padding:0; font-size:14px; color:#385b9d;">
                {{ aiSummaryExpanded ? 'Collapse' : 'View More' }}
              </el-button>
            </div>
          </div>
          <div class="recommend-card" v-if="displayedRecommendedPubs.length > 0">
            <div class="recommend-header" style="margin-bottom:10px; display: flex; justify-content: space-between; align-items: flex-start;">
              <h3 style="margin: 0;">Recommended Publications</h3>
              <el-icon v-if="recommendedPubs.length > 5" :class="{ recRotating: isRecRotating }" style="font-size: 20px; cursor: pointer; margin-right: 0px; margin-top: 6px;" @click="handleRecRefreshClick">
                <Refresh />
              </el-icon>
            </div>
            <div v-if="displayedRecommendedPubs.length === 0" style="color:#868ea8;text-align:center;">No recommended publications</div>
            <div v-for="(item, idx) in displayedRecommendedPubs" :key="item.pub_id">
              <div class="rec-pub-item" @click="viewPublication(item)">
                <div class="rec-pub-title">{{ item.title }}</div>
                <div class="rec-pub-meta">{{ item.year }} <span v-if="item.authors">{{ item.authors }}</span></div>
              </div>
              <el-divider v-if="idx < displayedRecommendedPubs.length - 1" class="rec-pub-divider"></el-divider>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchPublications, fetchPublicationsRecommend, fetchPublicationsAI } from '@/api/user';
import PageHeader from '../../components/PageHeader.vue';
import { PostFavor, PostConcelFavor } from '@/api/production';
import { ElMessage } from 'element-plus';
import { Link, Download, Loading } from '@element-plus/icons-vue';
import { Heart as LucideHeart } from 'lucide-vue-next';
import MarkdownIt from 'markdown-it';

const tabTypeMap = {
  journal: 'Journal',
  conference: 'Conference Paper',
  techreport: 'Technical Report',
  book: 'Book',
  patent: 'Patent'
};

export default {
  components: { PageHeader, LucideHeart, Loading },
  data() {
    return {
      activeTab: 'journal',
      allResults: [],
      totalCount: 0,
      showRes: [],
      loading: false,
      currentPage: 1,
      totalPages: 1,
      sortBy: 1,
      sortDown: 1,
      pageSize: 10,
      userId: this.$cookies.get('userId'),
      aiConclusion: '*waiting for AI statistics...*',
      recommendedPubs: [],
      displayedRecommendedPubs: [],
      isRecRotating: false,
      onlyDownloadable: false,
      aiSummaryExpanded: false,
      showAiSummaryToggle: false,
      md: new MarkdownIt({ breaks: true }),
      resultsCache: {},
    };
  },
  computed: {
    filteredResults() {
      let filtered = [...this.allResults];
      if (this.onlyDownloadable) {
        filtered = filtered.filter(item => item.local_file_path && item.local_file_path !== '');
      }
      return filtered;
    },
    pagedResults() {
      // 排序
      let sorted = [...this.filteredResults];
      if (this.sortBy === 1) {
        if (this.sortDown === -1) sorted.reverse();
      } else if (this.sortBy === 2) {
        sorted.sort((a, b) => (b.year - a.year) * this.sortDown);
      } else if (this.sortBy === 3) {
        sorted.sort((a, b) => (b.favor_count - a.favor_count) * this.sortDown);
      }
      const start = (this.currentPage - 1) * this.pageSize;
      return sorted.slice(start, start + this.pageSize);
    },
    totalPagesComputed() {
      return Math.max(1, Math.ceil(this.filteredResults.length / this.pageSize));
    },
    aiCache() {
      const type = tabTypeMap[this.activeTab];
      return this.resultsCache[type] || {};
    },
    formattedAiConclusion() {
      return this.aiCache.aiConclusion ? this.md.render(this.aiCache.aiConclusion) : '';
    },
    aiLoading() {
      return this.aiCache.aiLoading !== undefined ? this.aiCache.aiLoading : true;
    }
  },
  methods: {
    async fetchResults() {
      const type = tabTypeMap[this.activeTab];
      const condition = this.$route.query.condition;
      // 初始化缓存对象（只初始化一次）
      if (!this.resultsCache[type]) {
        this.resultsCache[type] = {
          allResults: [],
          totalCount: 0,
          aiConclusion: '*waiting for AI statistics...*',
          aiLoading: true,
          pending: false,
          aiPending: false,
          condition: ''
        };
      }
      const cache = this.resultsCache[type];
      // 主结果请求防抖
      if (cache.pending) return;
      // 主结果缓存命中
      if (cache.condition === condition && cache.allResults.length > 0) {
        this.allResults = cache.allResults;
        this.totalCount = cache.totalCount;
        this.totalPages = this.totalPagesComputed;
        this.updateShowRes();
        return;
      }
      // 主结果未命中且未请求中
      cache.pending = true;
      this.loading = true;
      try {
        const res = await fetchPublications(this.userId, condition, type);
        if (res.success) {
          cache.allResults = res.data.publications;
          cache.totalCount = res.data.publications.length;
          cache.condition = condition;
        } else {
          cache.allResults = [];
          cache.totalCount = 0;
          cache.condition = condition;
        }
        this.allResults = cache.allResults;
        this.totalCount = cache.totalCount;
        this.totalPages = this.totalPagesComputed;
        this.updateShowRes();
      } catch (e) {
        cache.allResults = [];
        cache.totalCount = 0;
        cache.condition = condition;
        this.allResults = [];
        this.totalCount = 0;
        this.totalPages = 1;
        this.updateShowRes();
      } finally {
        cache.pending = false;
        this.loading = false;
      }
      // AI总结请求防抖
      if (cache.aiPending) return;
      // AI总结缓存命中
      if (cache.condition === condition && cache.aiConclusion && !cache.aiLoading) {
        // nothing to do, computed会自动渲染
        return;
      }
      // AI总结未命中且未请求中
      cache.aiPending = true;
      cache.aiLoading = true;
      try {
        const aiRes = await fetchPublicationsAI(this.userId, condition, type);
        if (aiRes && aiRes.success && aiRes.data && aiRes.data.conclusion) {
          cache.aiConclusion = aiRes.data.conclusion;
        } else {
          cache.aiConclusion = 'No AI statistics available.\nplease try again later.';
        }
      } catch (e) {
        cache.aiConclusion = 'No AI statistics available.';
      } finally {
        cache.aiPending = false;
        cache.aiLoading = false;
      }
    },
    async fetchRecommendedPubs() {
      try {
        const res = await fetchPublicationsRecommend(this.userId, tabTypeMap[this.activeTab]);
        if (res.success) {
          this.recommendedPubs = res.data || [];
        } else {
          this.recommendedPubs = [
            { pub_id: 1001, title: '模拟推荐成果A-这是一个非常非常长的成果标题用于测试超出省略效果', year: '2023', authors: '张三、李四、王五、赵六、孙七、周八、吴九' },
            { pub_id: 1002, title: '模拟推荐成果B-另一个超长标题测试', year: '2022', authors: '王五、李四、张三、赵六、孙七、周八、吴九' },
            { pub_id: 1003, title: '模拟推荐成果C-测试三', year: '2021', authors: '李四、王五、赵六、孙七、周八、吴九、张三' },
            { pub_id: 1004, title: '模拟推荐成果D-测试四', year: '2020', authors: '赵六、孙七、周八、吴九、张三、李四' },
            { pub_id: 1005, title: '模拟推荐成果E-测试五', year: '2019', authors: '孙七、周八、吴九、张三、李四、王五' },
            { pub_id: 1006, title: '模拟推荐成果F-测试六', year: '2018', authors: '周八、吴九、张三、李四、王五、赵六' }
          ];
        }
      } catch {
        this.recommendedPubs = [
          { pub_id: 1001, title: '模拟推荐成果A-这是一个非常非常长的成果标题用于测试超出省略效果', year: '2023', authors: '张三、李四、王五、赵六、孙七、周八、吴九' },
          ];
      }
      this.refreshRecommendedPubs();
    },
    refreshRecommendedPubs() {
      if (this.recommendedPubs.length <= 5) {
        this.displayedRecommendedPubs = [...this.recommendedPubs];
      } else {
        const arr = this.recommendedPubs.slice();
        for (let i = arr.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [arr[i], arr[j]] = [arr[j], arr[i]];
        }
        this.displayedRecommendedPubs = arr.slice(0, 5);
      }
    },
    handleRecRefreshClick() {
      if (this.isRecRotating) return;
      this.isRecRotating = true;
      this.refreshRecommendedPubs();
      setTimeout(() => {
        this.isRecRotating = false;
      }, 500);
    },
    updateShowRes() {
      this.showRes = this.pagedResults;
      this.totalPages = this.totalPagesComputed;
      if (this.currentPage > this.totalPages) {
        this.currentPage = 1;
        this.showRes = this.pagedResults;
      }
    },
    goToPage(page) {
      this.currentPage = page;
    },
    viewPublication(pub) {
      this.$router.push({
        path: '/production',
        query: { pubId: pub.pub_id }
      });
    },
    gotoScholar(userId) {
      this.$router.push({
        path: '/gateway',
        query: { userId }
      });
    },
    openExternal(url) {
      window.open(url, '_blank');
    },
    downloadFile(path) {
      window.open('http://10.151.254.221:8000' + path, '_blank');
    },
    async toggleFavor(pub) {
      if (!this.userId) {
        ElMessage.warning('Please log in to like publications.');
        return;
      }
      if (pub.is_favor) {
        // 取消点赞
        try {
          const res = await PostConcelFavor(pub.pub_id, this.userId);
          pub.is_favor = false;
          pub.favor_count = Math.max(0, (pub.favor_count || 1) - 1);
        } catch {}
      } else {
        // 点赞
        try {
          const res = await PostFavor(pub.pub_id, this.userId);
          pub.is_favor = true;
          pub.favor_count = (pub.favor_count || 0) + 1;
        } catch {}
      }
    },
    checkAiSummaryOverflow() {
      const el = this.$refs.aiSummaryContent;
      if (!el) return;
      const lineHeight = parseFloat(getComputedStyle(el).lineHeight) || 20;
      const maxHeight = lineHeight * 8 + 2;
      this.showAiSummaryToggle = el.scrollHeight - 2 > maxHeight;
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
      this.updateShowRes && this.updateShowRes();
    },
    activeTab() {
      this.currentPage = 1;
      this.allResults = [];
      this.showRes = [];
      this.totalPages = 0;
      this.fetchResults();
      this.fetchRecommendedPubs();
      this.showAiSummaryToggle = false;
    },
    aiConclusion: {
      handler() {
        this.$nextTick(this.checkAiSummaryOverflow);
      },
      immediate: true
    },
  },
  mounted() {
    this.fetchResults();
    this.fetchRecommendedPubs();
    this.$nextTick(() => {
      this.checkAiSummaryOverflow();
      // 监听AI总结内容变化
      const el = this.$refs.aiSummaryContent;
      if (el && window.MutationObserver) {
        this._aiSummaryObserver = new MutationObserver(() => {
          this.checkAiSummaryOverflow();
        });
        this._aiSummaryObserver.observe(el, { childList: true, subtree: true, characterData: true });
      }
    });
  },
  beforeUnmount() {
    if (this._aiSummaryObserver) {
      this._aiSummaryObserver.disconnect();
      this._aiSummaryObserver = null;
    }
  },
};
</script>

<style scoped>
.publication-page-root {
  width: 100%;
  background: #f5f6fa;
  overflow-x: hidden;
}
.card-bar {
  width: 100%;
  background: #fff;
  border-radius: 4px;
  padding: 0 3vw 0 3vw;
  margin-bottom: 18px;
  box-sizing: border-box;
}
.header-bar h1 {
  padding-top:3vh;
  font-size: 1.8rem;
  color: #393942;
  margin: 0 0 3vh 0;
  font-weight: 600;
}
.pub-tabs {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: -32px;
}
::v-deep .el-tabs__item {
  margin: 0 32px 0 0;
  font-size: 16px;
  padding: 0 0 16px 0;
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
  padding: 2vw 2vw 1vw 2vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
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
  padding: 18px 24px;
  border: 1px solid #e5f1fe;
  margin-bottom: 18px;
  border-radius: 8px;
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
  gap: 18px;
  margin-bottom: 0;
}
.item-divider {
  width: 100%;
  height: 1px;
  background: #e5f1fe;
  margin: 2px 0 10px 0;
}
.publication-title {
  font-size: 20px;
  font-weight: 600;
  color: #393942;
  margin: 0;
  position: relative;
  top: 2px;
}
.publication-year {
  font-size: 14px;
  color: #868ea8;
  font-weight: 400;
  margin-left: 0;
}
.publication-authors {
  font-size: 15px;
  color: #868ea8;
  font-style: normal;
  font-weight: 400;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}
.publication-venue {
  font-size: 15px;
  color: #868ea8;
  align-self: flex-end;
  margin-left: auto;
  padding-right: 0;
  font-weight: 500;
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
.author-item {
  margin-right: 8px;
}
.author-item.clickable {
  color: #385b9d;
  text-decoration: none;
  transition: color 0.2s;
}
.author-item.clickable:hover {
  color:rgb(36, 131, 255);
  text-decoration: underline;
}
.author-item:not(.clickable) {
  color: #868ea8;
}
.keyword-item {
  margin: 3px 8px 3px 0;
  padding: 4px 10px;
  border: 1px solid #c7d6db;
  border-radius: 15px;
  background-color: #ecfbff;
  font-size: 14px;
  color: #09255e;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.publication-abstract {
  display: -webkit-box;
  color: #868ea8;
  margin: 6px 0;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  word-break: break-all;
}
.right-panel {
  width: 28vw;
  display: flex;
  flex-direction: column;
  gap: 2vh;
  box-sizing: border-box;
}
.ai-summary-card, .recommend-card {
  background: #fff;
  border-radius: 4px;
  box-shadow: none;
  padding: 18px 24px 18px 24px;
  min-height: unset;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.ai-summary-card h3, .recommend-card h3 {
  margin: 0 0 -1vh 0;
  color: #393942;
  font-size: 1.2rem;
}
.ai-summary-content, .recommend-content {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  text-align: left;
  width: 100%;
  min-height: 40px;
  color:rgb(95, 104, 133);
}
.rec-pub-item {
  padding: 8px 0;
  cursor: pointer;
}
.rec-pub-item:hover {
  background: none;
}
.rec-pub-title {
  font-size: 16px;
  color: #385b9d;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
}
.rec-pub-meta {
  font-size: 13px;
  color: #868ea8;
  font-style: italic;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.rec-pub-divider {
  margin: 2px 0;
}
.recRotating {
  animation: rec-rotate 0.5s linear;
}
@keyframes rec-rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.pub-action-btns {
  display: flex;
  align-items: center;
  margin-left: auto;
  gap: 16px;
  position: relative;
  top: 4px;
}
.pub-action-icon {
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
  vertical-align: middle;
  color: inherit;
}
.pub-action-icon-neutral {
  color: #868ea8 !important;
}
.favor-btn {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  color: #868ea8;
  transition: color 0.2s;
  font-size: 18px;
}
.favor-btn.active .pub-action-icon {
  color: #e74c3c !important;
}
.favor-count {
  font-size: 15px;
  margin-left: 4px;
}
.ai-summary-content.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 8;
  max-height: 11.2em;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: max-height 0.2s;
  position: relative;
}
.ai-summary-content.expanded {
  display: block;
  -webkit-line-clamp: unset !important;
  max-height: none !important;
  overflow: visible !important;
  text-overflow: unset !important;
  transition: none;
}
.ai-summary-toggle {
  margin-top: 6px;
  text-align: right;
}
.ai-summary-fade {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -5px;
  height: 2.2em;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(245,246,250,0), #ffffff 90%);
  z-index: 2;
  border-radius: 0 0 4px 4px;
}
.ai-summary-loading {
  display: block;
  margin: 24px auto 8px auto;
  font-size: 32px;
}
.ai-summary-loading-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 60px;
}
.ai-summary-wait-text {
  color: #868ea8;
  font-size: 15px;
  text-align: center;
  margin-top: 4px;
  font-style: italic;
}
</style> 