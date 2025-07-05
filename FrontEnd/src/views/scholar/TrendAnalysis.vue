<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getCurrentInstance } from 'vue';
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import PageHeader from '../../components/PageHeader.vue';
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import dayjs from 'dayjs'
import MarkdownIt from 'markdown-it'
const md = new MarkdownIt()
const renderedHTML = ref("")

// === 引入你的 API 模块 ===
import { PostTrendAnalysis, GetTrendResultById, IsGenerated } from '../../api/trend.js'

const internalInstance = getCurrentInstance();
const internalData = internalInstance.appContext.config.globalProperties;
const userId = ref(internalData.$cookies.get('userId')); // 后面的为之前设置的cookies的名字


const showPDFDom = ref(false)


// 用户输入
const keyword = ref('')
const cycle = ref('weekly')
const isGenerated = ref(false)

const disable = ref(false)

// 状态控制
const loading = ref(false)
// const resultData = ref({
//   report: "人工智能（AI）已成为当前最活跃的研究领域之一。根据近一年（2024年6月–2025年6月） arXiv、IEEE、ACL、NeurIPS 等开放文献库统计，涉及“Artificial Intelligence”的论文数量超过 12 万篇，同比增长约 18.3%。研究焦点持续聚集在 大语言模型（LLM）、多模态学习、AI生成内容（AIGC）、强化学习 和 可解释性AI 等核心方向。",
//   wordCloudData: [
//     { name: "深度学习", value: 150 },
//     { name: "Transformer", value: 120 },
//     { name: "多模态", value: 100 },
//     { name: "知识图谱", value: 80 },
//     { name: "自动驾驶", value: 75 },
//     { name: "生物智能", value: 65 },
//     { name: "强化学习", value: 60 },
//     { name: "AIGC", value: 55 },
//     { name: "图神经网络", value: 45 },
//     { name: "联邦学习", value: 40 }
//   ],
//   years: ["2021", "2022", "2023", "2024"],
//   topics: ["计算机视觉", "自然语言处理", "机器人", "医疗AI", "推荐系统"],
//   heatmapData: [
//     [0, 0, 0.8], [1, 0, 0.9], [2, 0, 0.95], [3, 0, 0.92],
//     [0, 1, 0.6], [1, 1, 0.7], [2, 1, 0.75], [3, 1, 0.78],
//     [0, 2, 0.5], [1, 2, 0.65], [2, 2, 0.7], [3, 2, 0.85],
//     [0, 3, 0.4], [1, 3, 0.6], [2, 3, 0.65], [3, 3, 0.68],
//     [0, 4, 0.3], [1, 4, 0.45], [2, 4, 0.5], [3, 4, 0.6]
//   ],
//   mindMapData: {
//     name: "人工智能前沿",
//     children: [
//       {
//         name: "大模型",
//         children: [
//           { name: "GPT-4" },
//           { name: "Claude" },
//           { name: "Sora" }
//         ]
//       },
//       {
//         name: "多模态",
//         children: [
//           { name: "文本-图像融合" },
//           { name: "视频生成" }
//         ]
//       },
//       {
//         name: "AIGC",
//         children: [
//           { name: "图像生成" },
//           { name: "文案生成" },
//           { name: "代码生成" }
//         ]
//       },
//       {
//         name: "可解释性",
//         children: [
//           { name: "模型可视化" },
//           { name: "因果推理" }
//         ]
//       }
//     ]
//   }
// })
const resultData = ref({})



const renderAllPdfCharts = () => {
  // 词云图
  echarts.init(document.getElementById('wordcloud-pdf')).setOption({
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      gridSize: 8,
      sizeRange: [20, 80],
      rotationRange: [0, 0],
      data: resultData.value.wordCloudData,
      textStyle: {
        fontFamily: 'Impact',
        fontWeight: 'bold',
        color: () => '#' + Math.floor(Math.random() * 16777215).toString(16)
      }
    }]
  })

  // 热点图
  echarts.init(document.getElementById('heatmap-pdf')).setOption({
    grid: {
      left: 150  // ← 关键：增加左边距防止Y轴文字被截断
    },
    xAxis: { type: 'category', data: resultData.value.years },
    yAxis: { type: 'category', data: resultData.value.topics },
    visualMap: { min: 0, max: 1, show: false },
    series: [{
      type: 'heatmap',
      data: resultData.value.heatmapData,
      label: { show: false }
    }]
  })

  // 思维导图
  echarts.init(document.getElementById('mindmap-pdf')).setOption({
    series: [{
      type: 'tree',
      data: [resultData.value.mindMapData],
      top: '10%',
      left: '10%',
      bottom: '10%',
      right: '10%',
      symbolSize: 16,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 14
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left',
          fontSize: 14
        }
      },
      expandAndCollapse: true,
      animationDuration: 500
    }]
  })
}



const exportPDF = async () => {

  showPDFDom.value = true

  await nextTick()
  renderAllPdfCharts() // 你自己已有的图表渲染函数，确保能正确画在 #mindmap-pdf 等位置

  ElMessage.info('Generating PDF, please wait...')
  setTimeout(async () => {
    const pdf = new jsPDF('p', 'mm', 'a4')
    const pageWidth = 210  // mm
    const pageHeight = 297
    const margin = 10

    const pages = [
      document.getElementById('pdf-page-1'),  // 合并后的第一页和第二页
      document.getElementById('pdf-page-2'),
      document.getElementById('pdf-page-3'),
      document.getElementById('pdf-page-4')
    ]

    for (let i = 0; i < pages.length; i++) {
      const pageEl = pages[i]
      const canvas = await html2canvas(pageEl, { scale: 2, useCORS: true })
      const imgData = canvas.toDataURL('image/png')

      const imgProps = pdf.getImageProperties(imgData)
      const imgWidth = pageWidth - 2 * margin
      const imgHeight = (imgProps.height * imgWidth) / imgProps.width

      const yOffset = Math.max((pageHeight - imgHeight) / 2, margin)  // 垂直居中

      if (i > 0) pdf.addPage()
      pdf.addImage(imgData, 'PNG', margin, yOffset, imgWidth, imgHeight)

      // ✅ 设置页脚，不乱码
      pdf.setFont('helvetica', 'normal')
      pdf.setFontSize(10)
      pdf.setTextColor(150)
      pdf.text(`Page ${i + 1} · ${dayjs().format('YYYY-MM-DD HH:mm')}`, pageWidth - 60, pageHeight - 10)
    }

    pdf.save(`AI-Trend-Report-${dayjs().format('YYYYMMDD-HHmm')}.pdf`)
    
    
    showPDFDom.value = false


    ElMessage.success('PDF exported successfully!')
  }, 1000)
}









const activeChartTab = ref('wordcloud')  // 默认显示词云图

// 切换 tab 时重新渲染图表，避免空白
watch(activeChartTab, (tab) => {
  nextTick(() => {
    if (tab === 'wordcloud') {
      echarts.getInstanceByDom(document.getElementById('wordcloud'))?.resize()
    } else if (tab === 'heatmap') {
      echarts.getInstanceByDom(document.getElementById('heatmap'))?.resize()
    } else if (tab === 'mindmap') {
      echarts.getInstanceByDom(document.getElementById('mindmap'))?.resize()
    }
  })
})

window.addEventListener('resize', () => {
  ['wordcloud', 'heatmap', 'mindmap'].forEach(id => {
    echarts.getInstanceByDom(document.getElementById(id))?.resize()
  })
})

// 获取分析结果（也按你的风格封装）
const fetchResult = () => {
  loading.value = true

  var promise = GetTrendResultById(userId.value)
  promise.then((res) => {
    if (res.success === true) {
      isGenerated.value = true
      resultData.value = res.data
      renderCharts()
    } else {
      ElMessage.error("Result not generated")
    }
    loading.value = false
  })
}

// 提交分析请求（使用你的风格）
const submitAnalysis = () => {
  if (!keyword.value) {
    ElMessage.warning('Please enter keywords in the research field')
    return
  }

  loading.value = true

  // 使用封装好的 PostTrendAnalysis 方法
  var promise = PostTrendAnalysis(userId.value, keyword.value, cycle.value)
  promise.then((res) => {
    if (res.success === true) {
      ElMessage.success('The analysis task has been submitted, and the results will be displayed later')
    } else {
      ElMessage.error(res.message)
    }
    loading.value = false
  })
}

// 渲染词云图和热点图
const renderCharts = () => {

  renderedHTML.value = md.render(resultData.value.report)


  const wordCloudChart = echarts.init(document.getElementById('wordcloud'))
  wordCloudChart.setOption({
    series: [{
      type: 'wordCloud',
      shape: 'circle',
      data: resultData.value.wordCloudData,
      textStyle: { fontFamily: 'sans-serif' }
    }]
  })

  const heatmapChart = echarts.init(document.getElementById('heatmap'))
  heatmapChart.setOption({
    grid: {
      left: 150  // ← 关键：增加左边距防止Y轴文字被截断
    },
    xAxis: { type: 'category', data: resultData.value.years },
    yAxis: { type: 'category', data: resultData.value.topics },
    visualMap: { min: 0, max: 1, show: false },
    series: [{
      name: '热点',
      type: 'heatmap',
      data: resultData.value.heatmapData
    }]
  })

  const mindMapChart = echarts.init(document.getElementById('mindmap'))
  mindMapChart.setOption({
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [{
      type: 'tree',
      data: [resultData.value.mindMapData],
      top: '5%',
      left: '10%',
      bottom: '5%',
      right: '10%',
      symbolSize: 10,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 12
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left'
        }
      },
      expandAndCollapse: true,
      animationDuration: 750
    }]
  })

}

const initHome = () => {
  var promise = IsGenerated(userId.value)
  promise.then((res) => {
    if (res.success === true) {
      if(res.isGenerated === true) {
        isGenerated.value = true
        fetchResult()
      }
      else{
        ElMessage.info("Please define keywords and cycles first, and we will generate a report for you later")
      }
    } else {
      ElMessage.error(res.message)
    }
  })
}

initHome()
// onMounted(() => {
//   renderCharts()
// })

</script>

<template>
  <PageHeader></PageHeader>
  <div class="trend-container">
    <!-- 设置关键词和周期 -->
    <el-card>
      <div class="form-area">
        <el-input v-model="keyword" placeholder="Please enter keywords" style="width: 300px; margin-right: 20px" />
        <el-select v-model="cycle" placeholder="分析频率" style="width: 150px">
          <el-option label="weekly" value="weekly" />
          <el-option label="monthly" value="monthly" />
          <el-option label="quarterly" value="quarterly" />
        </el-select>
        <el-button v-if="!disable" type="primary" @click="submitAnalysis(); disable = true" :loading="loading" style="margin-left: 20px;">Submit</el-button>
        <el-button v-else type="primary" style="margin-left: 20px;" disabled>Submit</el-button>
        <el-button type="primary" @click="fetchResult" style="margin-left: 20px;">Fetch Result</el-button>

        <el-button type="success" @click="exportPDF" style="margin-left: 20px;" v-if="isGenerated">Download PDF</el-button>
      </div>
    </el-card>

    <!-- 分析结果展示 -->
    <el-card style="margin-top: 20px">
      <h2 v-if="isGenerated">Analysis results</h2>
      <h2 v-else>Report not generated...</h2>
      <div class="report" v-if="isGenerated">
        <h3>Trend report</h3>
        <!-- <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{ resultData.report }}</span> -->
        <div class="markdown-body" v-html="renderedHTML"></div>
      </div>
      <el-tabs v-model="activeChartTab" type="border-card" class="chart-tab" v-if="isGenerated">
        <el-tab-pane label="WordCloud" name="wordcloud">
          <div id="wordcloud" class="chart-box"></div>
        </el-tab-pane>
        <el-tab-pane label="HeatMap" name="heatmap">
          <div id="heatmap" class="chart-box"></div>
        </el-tab-pane>
        <el-tab-pane label="MindMap" name="mindmap">
          <div id="mindmap" class="chart-box"></div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>


  <!-- 合并后的第一页（包含趋势报告和词云图） -->
  <div v-if="showPDFDom" class="pdf-capture-container">
    <div class="pdf-page" id="pdf-page-1" style="width: 1000px; height: 1500px; padding: 40px 20px;">
      <!-- 趋势报告 -->
      <div style="height: 1500px;">
        <h2>AI Trend Analysis Report</h2>
        <!-- <p style="text-indent: 2em; font-size: 16px;">{{ resultData.report }}</p> -->
        <div class="markdown-body" v-html="renderedHTML"></div>
      </div>

      
    </div>
    
    <div class="pdf-page" id="pdf-page-2" style="width: 1000px; height: 700px; padding: 40px 20px;">
      <!-- 词云图 -->
      <div style="height: 700px;">
        <h3>Keyword Word Cloud</h3>
        <div id="wordcloud-pdf" style="width: 960px; height: 600px;"></div>
      </div>
    </div>

    <!-- 保留后面页 -->
    <div class="pdf-page" id="pdf-page-3" style="width: 1000px; height: 700px; padding: 20px;">
      <h3>Research Hotspot Map</h3>
      <div id="heatmap-pdf" style="width: 960px; height: 600px;"></div>
    </div>

    <div class="pdf-page" id="pdf-page-4" style="width: 1500px; height: 700px; padding: 20px;">
      <h3>Mind Map</h3>
      <div id="mindmap-pdf" style="width: 1460px; height: 600px;"></div>
    </div>
  </div>



</template>

<style scoped>
.trend-container {
  padding: 20px;
}
.form-area {
  display: flex;
  align-items: center;
}
.report {
  margin-top: 20px;
  margin-left: 20px;
  margin-bottom: 50px;
}
.chart-tab {
  margin-top: 20px;
  background: #fff;
}

.chart-box {
  width: 80%;
  height: 500px;
  margin: 0 auto; /* 水平居中 */
  display: flex;
  justify-content: center;
  align-items: center;
}

#mindmap {
  width: 80%;
  height: 500px;
  margin: 0 auto; /* 水平居中 */
}

.pdf-capture-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 2000px;
  height: auto;
  opacity: 0;        /* ✅ 不可见但可渲染 */
  z-index: -9999;     /* ✅ 不遮挡页面元素 */
  pointer-events: none; /* ✅ 避免事件穿透问题 */
}
</style>
