<template>
    <PageHeader/>

    <div style="background-color: rgb(246, 246, 246);min-height: 91vh;" element-loading-background="white">
        <div class="basic-info-box">
            <div v-if="loading">
              <el-skeleton :rows="3" animated style="width: 35vw;"/>
              <br/>
              <el-skeleton style="--el-skeleton-circle-size: 30px" animated>
                <template #template>
                  <el-skeleton-item variant="circle" />
                </template>
              </el-skeleton>
            </div>
            <div v-if="type.length > 0" class="type-box">{{ type }}</div>
            <div class="title-box">{{ title }}</div>
            <div class="subinfo-box">
                <span v-if="year && year.length>0">{{ year }}·</span>
                <span v-if="journal && journal.length>0">{{ journal }}·</span>
                <span v-if="volume && volume.length>0">{{ volume }}:</span>
                <span v-if="issue && issue.length>0">{{ issue }}</span>
            </div>
            <div class="authors-box">
                <span v-for="(author,index) in authors" style="">
                    <el-avatar @click="gotoGateway(author.user_id)" :size="30" :src="author.avatar" style="margin-right: 1vh;" />
                    <div style="display: inline-block;">
                      <span v-if="author.user_id != -1" class="author-link" @click="gotoGateway(author.user_id)">{{ author.name }}</span>
                      <span v-else>{{ author.name }}</span>
                      <span v-if="index != authors.length-1">,&ensp;&ensp;</span>
                    </div>
                </span>
                <el-divider style="margin-top: 3vh;margin-bottom: 0;"/>
            </div>
            <div class="menu-row">
                <el-menu
                    default-active="Abstract"
                    mode="horizontal"
                    active-text-color="#333"
                    background-color="white"
                    text-color="#606266"
                    class="my-menu"
                >
                    <el-menu-item index="Abstract" @click="showFirst = true">Abstract</el-menu-item>
                    <el-menu-item index="Comments" @click="showFirst = false;getComments()">Comment</el-menu-item>
                </el-menu>
                <el-button v-if="!isAuthor" type="primary" round class="blue-button" @click="claimResult()">Claim the result</el-button>
                <el-button v-if="!isAuthor && (!download || download.length==0)" type="primary" round class="blue-button" @click="requestData()">Request for full text</el-button>
                <el-button v-if="isAuthor && (!download || download.length==0)" type="primary" round class="blue-button" @click="dialog=true">Upload full text</el-button>
                <button class="Btn" v-if="download && download.length>0" @click="downloadPDF()">
                  <svg
                    class="svgIcon"
                    viewBox="0 0 384 512"
                    height="1em"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      d="M169.4 470.6c12.5 12.5 32.8 12.5 45.3 0l160-160c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L224 370.8 224 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 306.7L54.6 265.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l160 160z"
                    ></path>
                  </svg>
                  <span class="icon2"></span>
                </button>
                <el-button v-if="doi && doi.length>0" @click="gotourl(doi)" circle link><Link/></el-button>
                <div class="heart-container" title="Like">
                <input type="checkbox" class="checkbox" id="Give-It-An-Id" v-model="isFavor" @click="favor()">
                <div class="svg-container">
                    <svg viewBox="0 0 24 24" class="svg-outline" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.5,1.917a6.4,6.4,0,0,0-5.5,3.3,6.4,6.4,0,0,0-5.5-3.3A6.8,6.8,0,0,0,0,8.967c0,4.547,4.786,9.513,8.8,12.88a4.974,4.974,0,0,0,6.4,0C19.214,18.48,24,13.514,24,8.967A6.8,6.8,0,0,0,17.5,1.917Zm-3.585,18.4a2.973,2.973,0,0,1-3.83,0C4.947,16.006,2,11.87,2,8.967a4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,11,8.967a1,1,0,0,0,2,0,4.8,4.8,0,0,1,4.5-5.05A4.8,4.8,0,0,1,22,8.967C22,11.87,19.053,16.006,13.915,20.313Z">
                        </path>
                    </svg>
                    <svg viewBox="0 0 24 24" class="svg-filled" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.5,1.917a6.4,6.4,0,0,0-5.5,3.3,6.4,6.4,0,0,0-5.5-3.3A6.8,6.8,0,0,0,0,8.967c0,4.547,4.786,9.513,8.8,12.88a4.974,4.974,0,0,0,6.4,0C19.214,18.48,24,13.514,24,8.967A6.8,6.8,0,0,0,17.5,1.917Z">
                        </path>
                    </svg>
                    <svg class="svg-celebrate" width="100" height="100" xmlns="http://www.w3.org/2000/svg">
                        <polygon points="10,10 20,20"></polygon>
                        <polygon points="10,50 20,50"></polygon>
                        <polygon points="20,80 30,70"></polygon>
                        <polygon points="90,10 80,20"></polygon>
                        <polygon points="90,50 80,50"></polygon>
                        <polygon points="80,80 70,70"></polygon>
                    </svg>
                </div>
                </div>
            </div>
        </div>
        <div class="container">
            <transition :name="slideDirection" mode="out-in">
            <div v-if="showFirst" key="first">
              <el-row>
                <el-col :span="12">
                  <div class="page-box">
                    <div class="abstract-title">Abstract</div>
                    <el-divider/>
                    <div v-if="loading">
                      <el-skeleton :rows="5" animated style="width: 35vw;"/>
                    </div>
                    <div v-if="abstract && abstract.length>0" class="abstract-content">{{ abstract }}</div>
                    <div v-else class="abstract-content">Abstract information is currently unavailable.</div>
                  </div>
                  <div class="more-box">
                    <div class="more-title">🤔 More Publication?</div>
                    <el-divider/>
                    <div class="rec-content">Visit the <span @click="router.push({path: '/home'})" class="link">homepage</span> for more personalized recommendations!</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <!-- <div class="card">
                    <span
                      class="star-icon"
                      :class="{ active: isStarActive, animate: isAnimating }"
                      @click="handleStarClick"
                    >
                      {{ isStarActive ? '★' : '☆' }}
                    </span>
                    <div class="img">
                      <el-avatar class="center-avatar" :size="70" :src="user_avatar" @click="gotoMyGateway()"/>
                    </div>
                    <div class="text">
                      <p class="h3">👋 Discover scholars you may like</p>
                    </div>
                  </div> -->
                </el-col>
              </el-row>
            </div>
            <div v-else key="second" class="page-box">
                <el-avatar :size="50" :src="user_avatar" style="margin-right: 1vh;" @click="gotoMyGateway()"/>
                <div class="comment-title">Comment</div>
                <el-input v-model="content" style="width: 25vw;height: 5vh;" placeholder="Comment on the results." />
                <div style="display: flex;justify-content: flex-end;margin-top: 2vh;">
                  <el-button @click="sendComment()" type="primary" class="blue-button" round>Send</el-button>
                </div>
                <div v-for="(comment,index) in comments" class="comment-block">
                    <el-divider/>
                    <div style="display: flex;align-items: center;">
                        <el-avatar :size="30" :src="comment.user_avatar" @click="gotoGateway(comment.user_id)"/>
                        <span class="comment-user" @click="gotoGateway(comment.user_id)">{{ comment.user_account }}</span>
                    </div>
                    <div class="comment-content">{{ comment.content }}</div>
                </div>
            </div>
            </transition>
        </div>
    </div>

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

</template>

<script setup>
import { onMounted, ref } from 'vue';
import PageHeader from '@/components/PageHeader.vue';
import { ElMessage } from 'element-plus';
import { useRoute,useRouter } from 'vue-router'
import { GetProduction, PostConcelFavor, PostRequest, PostFavor, GetComments, PostComment, CheckClaimOwnership, uploadDocument, uploadFullText } from '@/api/production';
import { fetchUserInfo } from '@/api/user';
import axios from 'axios';
import { UploadFilled, Document } from '@element-plus/icons-vue';
import { GetAuthors, GetMessages } from '@/api/home';
import { Link } from 'lucide-vue-next';

const user_id = ref(1)
const user_account = ref('')
const pub_id = ref(0)
const user_name = ref('')
const loading = ref(true)
const user_avatar = ref('https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image')
const route = useRoute()
const router = useRouter()

// 基本信息
const title = ref("")
const type = ref('')
const authors = ref([])
const journal = ref('')
const volume = ref("")
const issue = ref("")
const year = ref("")
const abstract = ref("")
const created_by = ref(1)
const download = ref("")
const doi = ref("")
const isAuthor = ref(false)
const isFavor = ref(false)
const comments = ref([{"user_account":"Olurotimi Adeleye","user_id":1,"user_avatar":"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image","content":"你好"},{"user_account":"Olurotimi Adeleye","user_id":1,"user_avatar":"https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image","content":"hello！I love eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed!!!I want to eat and sleep!!!oh,I love my bed"}])
const content = ref('')

// 初始化
onMounted(() => { 
  pub_id.value = parseInt(route.query.pubId) || 0
  user_account.value = window.$cookies?.get('account') || 'Selena Lenning'
  var promise0 = fetchUserInfo(user_id.value)
  promise0.then((result) => { 
    if(result.success){
      user_name.value = result.data.name
    }
  })
  .finally(()=>{
    
  })
  user_id.value = parseInt(window.$cookies?.get('userId')) || 1
  user_avatar.value = window.$cookies?.get('avatarUrl') || 'https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image'
  var promise = GetProduction(pub_id.value,user_id.value)
  promise.then((result) => { 
    if(result.success){
      title.value = result.data.title
      type.value = result.data.type
      authors.value = result.data.authors
      journal.value = result.data.journal
      volume.value = result.data.volume
      issue.value = result.data.issue
      year.value = result.data.year
      abstract.value = result.data.abstract
      created_by.value = result.data.created_by
      isFavor.value = result.data.isFavour
      download.value = result.data.download
      doi.value = result.data.external_url
      authors.value.forEach((author) => { 
        if(author.user_id == user_id.value){
          isAuthor.value = true
        }
      })
      loading.value = false
    }
    else{
      ElMessageBox.confirm(
          "This publication doesn't exist.",
          "Tip",
          {
          confirmButtonText: "Confirm",
          cancelButtonText: "Cancel",
          type: "warning"
          }
      )
      .then(() => {
          // 点击确定，跳转到指定链接
          window.history.back();
      })
      .catch(() => {
          // 点击取消，返回上一页
          window.history.back();
      });
    }
  })
  .finally(() => {
    loading.value = false
  })



})

// 获取评论
function getComments(){
  var promise = GetComments(pub_id.value)
  promise.then((result) => { 
    if(result.success){
        comments.value = result.data.comments
    }
    else{
        ElMessage.error(result.message)
    }
  })
}

// 跳转
function gotoGateway(id){
  router.push({
    path: '/gateway',
    query: { userId: id }
  })
}
function gotoMyGateway(){
  router.push({
    path: '/myGateway'
  })
}

// 左右滑动效果
const showFirst = ref(true)
const slideDirection = ref('slide-right')
function togglePage() {
  slideDirection.value = showFirst.value ? 'slide-right' : 'slide-left'
  showFirst.value = !showFirst.value
}

// 申请数据
function getCurrentTime() {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  const hh = String(now.getHours()).padStart(2, '0')
  const min = String(now.getMinutes()).padStart(2, '0')
  return `${yyyy}/${mm}/${dd}/${hh}/${min}`
}

function requestData(){
  var promise = PostRequest(user_id.value,created_by.value,'ask',"尊敬的作者，您好！我是对您的研究成果感兴趣的学者"+user_name.value+"。为了进一步学习和研究相关内容，特此申请获取本成果的全文。非常感谢！",0,pub_id.value,getCurrentTime())
  
  promise.then((result) => { 
    if(result.success){
      ElMessage({
          message: 'Data request sent to creator.',
          type: 'success',
          plain: true,
      });
    }
    else{
      ElMessage.error(result.message)
    }
  })
}

function downloadPDF(){
  window.open("http://10.251.254.221:8000"+download.value, '_blank')
}

function gotourl(url){
  window.open(doi.value, '_blank')
}

// 认领成果
function claimResult(){
  var promise = CheckClaimOwnership(pub_id.value,user_id.value);
  promise.then((result) => { 
    if(result.is_owner){
      sendClaim()
    }
    else{
      ElMessageBox.alert('Name not found in author list. Please verify your authorship.', '', {
        confirmButtonText: 'OK',
        callback: () => {
          sendClaim()
        },
      })
    }
  });

}

function sendClaim(){
  var promise = PostRequest(user_id.value,created_by.value,'claim',"尊敬的作者，您好！我是我是"+user_name.value+"，本人是该成果的实际作者之一。希望能够获得您的认可，非常感谢！",0,pub_id.value,getCurrentTime())
  promise.then((result) => { 
    if(result.success){
      ElMessage({
          message: 'We have submitted a claim request to the creator for the full text.😊',
          type: 'success',
          plain: true,
      });
    }
    else{
      ElMessage.error(result.message)
    }
  })
}

// 评论
function sendComment(){
  var promise = PostComment(pub_id.value,user_id.value,content.value)
  promise.then((result) => { 
    if(result.success){
      getComments()
    }
    else{
      ElMessage.error(result.message)
    }
    content.value = ''
  })
}

// 点赞
function favor(){ 
  if(!isFavor.value){
    // 点赞
    var promise = PostFavor(pub_id.value,user_id.value)
    promise.then((result) => { 
      if(!result.success){
        ElMessage.error(result.message)
        isFavor.value = false
      }
    })
  }
  else{
    // 取消点赞
    var promise = PostConcelFavor(pub_id.value,user_id.value)
    promise.then((result) => { 
      if(!result.success){
        ElMessage.error(result.message)
        isFavor.value = true
      }
    })
  }
}

// 上传全文

const dialog = ref(false);
const dragover = ref(false);
const uploadError = ref('');
const fileInput = ref(null);
const fileSize = ref('');
const filePath = ref('');
const fileObj = ref(null); // 新增：存储文件对象

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

const isStarActive = ref(false)
const isAnimating = ref(false)

function handleStarClick() {
  isStarActive.value = !isStarActive.value
  isAnimating.value = false
  // 触发重绘以重置动画
  void document.body.offsetWidth
  isAnimating.value = true
  setTimeout(() => {
    isAnimating.value = false
  }, 500)
}
</script>

<style scoped>

.basic-info-box{
    padding-top: 2vw;
    padding-left: 20vw;
    box-shadow: 0 4px 16px rgba(0,0,0,0.10);
    background: #fff;
    border-radius: 5px;
}

.type-box {
    background-color: rgb(208, 238, 237);
    color: rgb(1, 23, 50);
    padding: 4px 5px;
    font-size: 14px;
    font-weight: light;
    display: inline-block;
    margin-bottom: 2vh;
}

.title-box{
    font-family: Tahoma,fantasy;
    font-weight:bold;
    font-size: 25px;
    line-height: 40px;
    color: #353535;
    width: 40vw;
    margin-bottom: 2vh;
}

.subinfo-box{
    font-size: 14px;
    color: rgb(82, 82, 111);
    margin-bottom: 2vh;
}

.authors-box{
  font-size: 14px;
  color: #353535;
}

.el-avatar{
    cursor:pointer
}

.author-link { 
    cursor: pointer;
}

.author-link:hover {
    text-decoration: underline;
}

.menu-row {
  display: flex;
  align-items: center;
  margin-bottom: 2vh;
}

.my-menu {
    font-weight: 20px;
    font-family: Microsoft YaHei, sans-serif;
    width: 100%;
    flex: 1;
}

.my-menu .el-menu-item.is-active {
    background: white;
}

.my-menu .el-menu-item:hover{
    background: white;
}

.blue-button {
    font-size: 14px;
    background-color: rgb(0, 109, 217);
}

.blue-button:hover {
    background-color: rgb(0, 57, 113);
}

.container {
    margin-top: 5vh;
    margin-left: 20vw;
}

.page-box {
  width: 35vw;
  background: white;
  font-size: 22px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 15px 15px 30px #bebebe,
              -15px -15px 30px #ffffff;
  padding: 2vw;
  transition: 0.2s ease-in-out;
}

.more-box {
  width: 35vw;
  background: white;
  font-size: 22px;
  background: #fff;
  border-radius: 2px;
  padding: 2vw;
  margin-top: 7vh;
  border-radius: 10px;
  box-shadow: 15px 15px 30px #bebebe,
              -15px -15px 30px #ffffff;
  transition: 0.2s ease-in-out;
}

.page-box:hover {
  box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
  transform: scale(1.03);
}

.more-box:hover {
  box-shadow: 0px 10px 20px rgba(0,0,0,0.1);
  transform: scale(1.01);
}

.more-title {
  font-weight: bold;
}

.rec-content {
  font-size: 15px;
  font-family: 'Times New Roman', Times, serif;
}

.rec-content .link {
  cursor: pointer;
  color: rgb(51.2, 126.4, 204);
}

.rec-content .link:hover {
  text-decoration: underline;
}

.abstract-title {
    font-size: 18px;
    font-weight: 20px;
    font-family: Microsoft YaHei, sans-serif;
}

.abstract-content {
    font-size: 16px;
    font-family: 'Times New Roman', Times, serif;
    line-height: 1.5;
}

.comment-title{
    margin-top: 2vh;
    margin-bottom: 1vh;
    font-size: 15px;
    font-weight: bold;
    font-family: Microsoft YaHei, sans-serif;
}

.comment-block {
    margin-bottom: 2vh;
}

.comment-user {
    font-size: 14px;
    font-weight: bold;
    font-family: Microsoft YaHei, sans-serif;
    cursor: pointer;
    margin: 1vh;
}

.comment-user:hover {
    text-decoration: underline;
}

.comment-content {
    font-size: 14px;
    margin-top: 1vh;
    font-weight: light;
    line-height: 2;
    font-family: 'Times New Roman', Times, serif;
}

/* 过渡动画 */
/* 右滑进，左滑出 */
.slide-right-enter-active, .slide-right-leave-active,
.slide-left-enter-active, .slide-left-leave-active {
  transition: all 0.4s cubic-bezier(.55,0,.1,1);
}
.slide-right-enter-from {
  transform: translateX(40%);
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
  transform: translateX(-40%);
  opacity: 0;
}

/* 左滑进，右滑出 */
.slide-left-enter-from {
  transform: translateX(-40%);
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
  transform: translateX(40%);
  opacity: 0;
}


/* 点赞 */
  .heart-container {
    --heart-color: rgb(255, 91, 137);
    position: relative;
    width: 3vh;
    height: 3vh;
    margin: 2vh;
    margin-right: 25vw;
    transition: .3s;
  }

  .heart-container .checkbox {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    z-index: 20;
    cursor: pointer;
  }

  .heart-container .svg-container {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .heart-container .svg-outline,
          .heart-container .svg-filled {
    fill: var(--heart-color);
    position: absolute;
  }

  .heart-container .svg-filled {
    animation: keyframes-svg-filled 1s;
    display: none;
  }

  .heart-container .svg-celebrate {
    position: absolute;
    animation: keyframes-svg-celebrate .5s;
    animation-fill-mode: forwards;
    display: none;
    stroke: var(--heart-color);
    fill: var(--heart-color);
    stroke-width: 2px;
  }

  .heart-container .checkbox:checked~.svg-container .svg-filled {
    display: block
  }

  .heart-container .checkbox:checked~.svg-container .svg-celebrate {
    display: block
  }

  @keyframes keyframes-svg-filled {
    0% {
      transform: scale(0);
    }

    25% {
      transform: scale(1.2);
    }

    50% {
      transform: scale(1);
      filter: brightness(1.5);
    }
  }

  @keyframes keyframes-svg-celebrate {
    0% {
      transform: scale(0);
    }

    50% {
      opacity: 1;
      filter: brightness(1.5);
    }

    100% {
      transform: scale(1.4);
      opacity: 0;
      display: none;
    }
  }

/* 下载 */
  .Btn {
    padding: 10px;
    width: 50px;
    height: 50px;
    border: none;
    border-radius: 50%;
    background-color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: relative;
    transition-duration: 0.3s;
  }

  .svgIcon {
    fill: #303133;
  }

  .icon2 {
    width: 18px;
    height: 5px;
    border-bottom: 2px solid #303133;
    border-left: 2px solid #303133;
    border-right: 2px solid #303133;
  }

  .tooltip {
    position: absolute;
    top: -50px;
    opacity: 0;
    background-color: rgb(12, 12, 12);
    color: white;
    padding: 10px 10px;
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition-duration: 0.2s;
    pointer-events: none;
    letter-spacing: 0.5px;
  }

  .tooltip::before {
    position: absolute;
    content: "";
    width: 10px;
    height: 10px;
    background-color: rgb(12, 12, 12);
    background-size: 1000%;
    background-position: center;
    transform: rotate(45deg);
    bottom: -5%;
    transition-duration: 0.3s;
  }

  .Btn:hover .tooltip {
    opacity: 1;
    transition-duration: 0.3s;
  }

  .Btn:hover {
    background-color: transparent;
    transition-duration: 0.3s;
  }

  .Btn:hover .icon2 {
    border-bottom: 2px solid #303133;
    border-left: 2px solid #303133;
    border-right: 2px solid #303133;
  }

  .Btn:hover .svgIcon {
    fill: #303133;
    animation: slide-in-top 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
  }

  @keyframes slide-in-top {
    0% {
      transform: translateY(-10px);
      opacity: 0;
    }

    100% {
      transform: translateY(0px);
      opacity: 1;
    }
  }

.upload-area {
  border: 2px dashed #DCDFE6;
  border-radius: 6px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
  width: 100%;
}

.upload-area:hover {
  border-color: #409EFF;
}

.upload-area.dragover {
  border-color: #409EFF;
  background-color: #f0f7ff;
}

.upload-content, .upload-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* .card {
  position: relative;
  margin-left: 2vw;
  width: 252px;
  height: 265px;
  background: white;
  border-radius: 30px;
  box-shadow: 15px 15px 30px #bebebe,
             -15px -15px 30px #ffffff;
  transition: 0.2s ease-in-out;
}

.img {
  width: 100%;
  height: 50%;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
  background: linear-gradient(rgb(250, 236.4, 216), rgb(159.5, 206.5, 255));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  position: relative;
}

.text {
  margin-top: 5vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 15px;
  font-family: 'Times New Roman', Times, serif;
  color: #353535;
}

.star-icon {
  position: absolute;
  top: 24px;
  right: 24px;
  font-size: 48px;
  color: #ffc107;
  cursor: pointer;
  user-select: none;
  transition: color 0.3s;
  z-index: 3;
  display: inline-block;
  line-height: 1;
}

.star-icon.active {
  color: #ffc107;
}

.star-icon:not(.active) {
  color: #ffc107;
}

.star-icon.animate {
  animation: star-bounce 0.5s;
}

@keyframes star-bounce {
  0% { transform: scale(1) rotate(0deg);}
  30% { transform: scale(1.5) rotate(-20deg);}
  60% { transform: scale(1.2) rotate(10deg);}
  100% { transform: scale(1) rotate(0deg);}
}

.save {
  transition: 0.2s ease-in-out;
  border-radius: 10px;
  margin: 20px;
  width: 30px;
  height: 30px;
  background-color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.save:hover {
  transform: scale(1.1) rotate(10deg);
}

.save:hover .svg {
  fill: #ced8de;
}

.center-avatar {
  position: absolute;
  left: 50%;
  bottom: -3vh;
  transform: translateX(-50%);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 3px solid #fff;
  background: #fff;
  z-index: 2;
}

.h3 {
  font-family: 'Lucida Sans' sans-serif;
  font-size: 15px;
  font-weight: 600;
  color: black;
}

.p {
  font-family: 'Lucida Sans' sans-serif;
  color: #999999;
  font-size: 13px;
}

.icon-box {
  margin-top: 15px;
  width: 70%;
  padding: 10px;
  background-color: #e3fff9;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: left;
}

.icon-box svg {
  width: 17px;
}

.icon-box .span {
  margin-left: 10px;
  font-family: 'Lucida Sans' sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: #9198e5;
} */


</style>