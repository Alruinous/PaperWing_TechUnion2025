<template>
  <!-- Navigation Bar -->
  <el-affix :offset="0">
  <el-container class="navbar">
    <el-header>
      <div class="logo" @click="goToHome">
        TechUnion
      </div>

      <el-menu
        :default-active="activeTab"
        mode="horizontal"
        active-text-color="#333"
        background-color="white"
        text-color="#606266"
        class="my-menu"
      >
        <el-menu-item index="/home" @click="goTo('/home')">Home</el-menu-item>
        <el-menu-item index="/forum" @click="goTo('/forum')">Forum</el-menu-item>
        <el-menu-item index="/trendAnalysis" @click="goTo('/trendAnalysis')">Express</el-menu-item>
      </el-menu>

      <!-- Search Box -->
      <span class="search-box">
        <el-input
          v-model="searchQuery"
          @focus="showSelectBox = true"
          placeholder="Search for articles, people..."
        >
          <template #suffix>
            <el-button type="text">
              <Search :size="18" color="black"/>
            </el-button>
          </template>
        </el-input>
        <div class="select-box" v-if="searchQuery.length > 0 && showSelectBox" ref="selectBoxRef">
          <div style="padding: 1%;">Search for Articles</div>
          <el-divider style="margin: 1vh 0;"/>
          <div class="choice-box" @click="goToPubSearch()">
            <Search :size="18" color="black"/>
            <span style="color: #303133;font-weight: bold;margin-left: 1vh;">
              {{ searchQuery }}
            </span>
          </div>
          <el-divider style="margin: 1vh 0;"/>
          <div style="padding: 1%;">Search for People</div>
          <el-divider style="margin: 1vh 0;"/>
          <div class="choice-box" @click="goToSearch('name')">
            <Search :size="18" color="black"/>
            <span style="color: #303133;font-weight: bold;margin-left: 1vh;">
              {{ searchQuery }}
            </span>
            &ensp;in Name
          </div>
          <el-divider style="margin: 1vh 0;"/>
          <div class="choice-box"  @click="goToSearch('title')">
            <Search :size="18" color="black"/>
            <span style="color: #303133;font-weight: bold;margin-left: 1vh;">
              {{ searchQuery }}
            </span>
            &ensp;in Title
          </div>
          <el-divider style="margin: 1vh 0;"/>
          <div class="choice-box" @click="goToSearch('institution')">
            <Search :size="18" color="black"/>
            <span style="color: #303133;font-weight: bold;margin-left: 1vh;">
              {{ searchQuery }}
            </span>
            &ensp;in Institution
          </div>
          <el-divider style="margin: 1vh 0;"/>
          <div class="choice-box" @click="goToSearch('field')">
            <Search :size="18" color="black"/>
            <span style="color: #303133;font-weight: bold;margin-left: 1vh;">
              {{ searchQuery }}
            </span>
            &ensp;in Field
          </div>
        </div>
      </span>

      <!-- Right Buttons -->
      <span class="button-box">
        <el-button type="" link circle style="margin: 1vw;padding:1vh" @click="goTo('/message')">
          <Bell :size="20"/>
        </el-button>
          <el-dropdown @command="handleSelfBoxCommand">
            <el-avatar :size="40" :src="user_avator" style="margin-left: 1vw; margin-right: 1vw; cursor:pointer;" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">Your profile</el-dropdown-item>
                <el-dropdown-item command="logout">Log out</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>        
        <el-button type="primary" class="add-new-button" round @click="drawer = true">
          Add New
        </el-button>
      </span>
    </el-header>
  </el-container>
  </el-affix>
  <!-- Drawer Menu -->
  <el-drawer
    v-model="drawer"
    size="20%"
    :with-header="false"
    class="drawer-box"
  >
    <div class="drawer-title">Add New</div>
    <el-divider></el-divider>
    <el-menu default-active="2" class="menu-box">
      <el-sub-menu index="1">
        <template #title >
          <StickyNote />
          <span style="margin-left: 1vh;">Publication</span>
        </template>
        <el-menu-item index="1-1" @click="openPublicationDialog('Journal')">Journal Paper</el-menu-item>
        <el-menu-item index="1-2" @click="openPublicationDialog('Conference Paper')">Conference Paper</el-menu-item>
        <el-menu-item index="1-3" @click="openPublicationDialog('Technical Report')">Technical Report</el-menu-item>
        <el-menu-item index="1-5" @click="openPublicationDialog('Book')">Book</el-menu-item>
        <el-menu-item index="1-7" @click="openPublicationDialog('Patent')">Patent</el-menu-item>
      </el-sub-menu>
      
      <el-menu-item index="2" @click="openQuestionDialog">
        <BadgeQuestionMark />
        <span style="margin-left: 1vh;">Question</span>
      </el-menu-item>
      <el-menu-item index="3" @click="openProjectDialog">
        <Users />
        <span style="margin-left: 1vh;">Project</span>
      </el-menu-item>
      <!-- Literature -->
      <el-menu-item index="4" @click="openLiteratureDialog">
        <Album />
        <span style="margin-left: 1vh;">Literature</span>
      </el-menu-item>
    </el-menu>
  </el-drawer>

  <!-- New Project Dialog -->
  <el-dialog
    v-model="dialogProjectVisible"
    title="Create Project"
    width="40%"
    class="custom-dialog"
  >
    <div class="scroll-container">
      <el-form label-position="top">
        <el-form-item label="Project Title" class="required-item">
          <el-input class="input" v-model="projectTitle" placeholder="Enter project title" />
        </el-form-item>
        <el-form-item label="Project Description" class="required-item">
          <el-input
            class="input"
            type="textarea"
            rows="4"
            v-model="projectDescription"
            placeholder="Enter project description"
          />
        </el-form-item>
        <el-form-item label="Research Field (comma separated, e.g.: Biology, Genetics)" class="required-item">
          <el-input class="input" v-model="projectField" placeholder="Enter research field" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogProjectVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitProject">Submit</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- New Question Dialog -->
  <el-dialog
    v-model="dialogQuestionVisible"
    title="Create Question"
    width="40%"
    class="custom-dialog"
  >
    <div class="scroll-container">
      <el-form label-position="top">
        <el-form-item label="Question Title" class="required-item">
          <el-input class="input" v-model="questionTitle" placeholder="Enter question title" />
        </el-form-item>
        <el-form-item label="Question Description" class="required-item">
          <el-input
            class="input"
            type="textarea"
            rows="4"
            v-model="questionDescription"
            placeholder="Enter question description"
          />
        </el-form-item>
        <el-form-item label="Research Field (comma separated, e.g.: Biology, Genetics)" class="required-item">
          <el-input class="input" v-model="questionField" placeholder="Enter research field" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogQuestionVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitQuestion">Submit</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- New Publication Dialog -->
<el-dialog
  v-model="dialogPublicationVisible"
  title="Create Publication"
  width="60%"
  class="custom-dialog publication-dialog"
>
  <br />
  <!-- Tabs -->
  <el-tabs v-model="activeTabName" type="card" class="tabs-header">
    <el-tab-pane label="Single Entry" name="single">
      <!-- Single Entry Form -->
      <div class="scroll-container">
        <el-form label-position="top" ref="publicationFormRef">
          <el-form-item label="Type" prop="type" class="required-item">
            <el-select v-model="publicationForm.type" placeholder="Select type" style="width:100%">
              <el-option label="Journal" value="Journal" />
              <el-option label="Conference Paper" value="Conference Paper" />
              <el-option label="Technical Report" value="Technical Report" />
              <el-option label="Book" value="Book" />
              <el-option label="Patent" value="Patent" />
            </el-select>
          </el-form-item>

          <el-form-item prop="title" class="required-item">
            <template #label>
              <span class="required-star">*</span> Title
            </template>
            <el-input v-model="publicationForm.title" placeholder="Enter publication title" />
          </el-form-item>

          <el-form-item prop="authors" class="required-item">
            <template #label>
              <span class="required-star">*</span> Authors (comma separated)
            </template>
            <el-input v-model="publicationForm.authors" placeholder="Alice Zhang, Bob Li" />
          </el-form-item>

          <el-form-item prop="research_fields" class="required-item">
            <template #label>
              <span class="required-star">*</span> Research Fields (comma separated, e.g.: Biology, Genetics)
            </template>
            <el-input v-model="publicationForm.research_fields" placeholder="Enter research fields" />
          </el-form-item>

          <!-- 以下是非必填项，保持不变 -->
          <el-form-item label="Journal/Conference/Publisher" prop="journal">
            <el-input v-model="publicationForm.journal" />
          </el-form-item>

          <div class="form-row">
            <el-form-item label="Volume" prop="volume" style="flex:1; margin-right:10px;">
              <el-input v-model="publicationForm.volume" />
            </el-form-item>

            <el-form-item label="Issue" prop="issue" style="flex:1; margin-right:10px;">
              <el-input v-model="publicationForm.issue" />
            </el-form-item>

            <el-form-item label="Year" prop="year" style="flex:1;">
              <el-input v-model="publicationForm.year" type="number" />
            </el-form-item>
          </div>

          <el-form-item label="Abstract" prop="abstract">
            <el-input type="textarea" rows="3" v-model="publicationForm.abstract" />
          </el-form-item>

          <el-form-item label="Keywords (comma separated)" prop="keywords">
            <el-input v-model="publicationForm.keywords" />
          </el-form-item>

          <el-form-item label="External Link or File (optional)" prop="external_url">
            <div style="width: 100%;">
              <el-input
                v-model="publicationForm.external_url"
                placeholder="Enter external link (e.g. DOI)"
                style="margin-bottom: 10px;"
              />
              <div style="display: flex; align-items: center;">
                <el-upload
                  class="big-upload"
                  action="http://10.251.254.221:8000/publications/upload/"
                  :show-file-list="false"
                  :before-upload="beforeUpload"
                  @success="handleUploadSuccess"
                >
                  <el-button size="small" type="primary">Select File</el-button>
                </el-upload>
                <span v-if="publicationForm.local_file_path" style="margin-left: 8px;">
                  Uploaded: {{ publicationForm.local_file_path }}
                </span>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-tab-pane>
    
    <el-tab-pane label="Bulk Upload" name="batch">
        <!-- Bulk Upload Content -->
        <div class="bulk-upload">
          <div class="batch-upload-container">
          <!-- Download Template Button -->
          <div style="margin-bottom: 15px; text-align: right;">
            <el-button type="primary" @click="downloadTemplate" size="small">
              Download Template
            </el-button>
          </div>
          
          <!-- Upload Area -->
          <el-upload
            ref="batchUploadRef"
            :show-file-list="false"
            :before-upload="beforeBatchUpload"
            :on-change="handleFileChange"
            accept=".xls,.xlsx"
            drag
            style="margin-bottom: 20px;"
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">Drag Excel file here or <em>click to upload</em></div>
            <div class="el-upload__tip" slot="tip">Only .xls and .xlsx formats supported</div>
          </el-upload>

          <!-- Upload Progress -->
          <div v-if="uploading" style="margin-top: 10px;">
            Uploading {{ currentIndex + 1 }} / {{ totalCount }} records...
            <el-progress :percentage="uploadPercent" />
          </div>

          <!-- Upload Result -->
          <div v-if="uploadResult" style="margin-top: 10px;">
            <el-alert
              :title="`Upload completed: ${uploadResult.success} succeeded, ${uploadResult.failed} failed`"
              type="success"
              show-icon
            />
            <ul style="max-height: 150px; overflow-y: auto; margin-top: 10px;">
              <li v-for="(fail, idx) in uploadResult.failDetails" :key="idx" style="color: red;">
                {{ fail }}
              </li>
            </ul>
          </div>
        </div>
        </div>
      </el-tab-pane>
  </el-tabs>

  <template #footer>
    <div class="dialog-footer">
      <el-button @click="dialogPublicationVisible = false">Cancel</el-button>

      <el-button v-if="activeTabName === 'single'" type="primary" @click="validateAndSubmitPublication">
        Submit
      </el-button>

      <el-button
        v-if="activeTabName === 'batch'"
        type="primary"
        @click="startBatchUpload"
        :disabled="!excelData.length || uploading"
      >
        Start Upload
      </el-button>
    </div>
  </template>
</el-dialog>

<!-- New Literature Dialog -->
<el-dialog v-model="dialogLiteratureVisible" title="Upload Literature" width="40%" class="custom-dialog">
  <div class="scroll-container">
    <el-form label-position="top">
      <el-form-item class="required-item">
        <template #label>
          <span class="required-star">*</span> Literature Title
        </template>
        <el-input v-model="literatureForm.title" placeholder="Enter literature title" />
      </el-form-item>

      <el-form-item class="required-item">
        <template #label>
          <span class="required-star">*</span> Authors (comma separated)
        </template>
        <el-input v-model="literatureForm.authors" placeholder="Alice Zhang, Bob Li" />
      </el-form-item>

      <el-form-item class="required-item">
        <template #label>
          <span class="required-star">*</span> Research Fields (comma separated)
        </template>
        <el-input v-model="literatureForm.research_fields" placeholder="Enter research fields" />
      </el-form-item>

      <el-form-item label="Upload File (PDF format)" class="required-item">
        <div style="display: flex; align-items: center;">
          <el-upload
            class="big-upload"
            action="http://10.251.254.221:8000/publications/upload/"
            :show-file-list="false"
            :before-upload="beforeLiteratureUpload"
            @success="handleLiteratureUploadSuccess"
          >
            <el-button size="small" type="primary">Select File</el-button>
          </el-upload>
          <span v-if="literatureForm.localFilePath" style="margin-left: 8px;">
            Uploaded: {{ literatureForm.localFilePath }}
          </span>
        </div>
      </el-form-item>

      <el-form-item label="Journal/Conference">
        <el-input v-model="literatureForm.journal" placeholder="Enter journal or conference" />
      </el-form-item>

      <el-form-item label="Year">
        <el-input v-model="literatureForm.year" type="number" placeholder="Enter publication year" />
      </el-form-item>

      <el-form-item label="Abstract">
        <el-input type="textarea" rows="3" v-model="literatureForm.abstract" placeholder="Enter abstract" />
      </el-form-item>

      <el-form-item label="Keywords (comma separated)">
        <el-input v-model="literatureForm.keywords" placeholder="Enter keywords" />
      </el-form-item>
    </el-form>
  </div>

  <template #footer>
    <div class="dialog-footer">
      <el-button @click="dialogLiteratureVisible = false">Cancel</el-button>
      <el-button type="primary" @click="submitLiterature">Submit</el-button>
    </div>
  </template>
</el-dialog>

</template>

<script setup>
import { ref, getCurrentInstance, watch, onMounted, onBeforeUnmount } from 'vue'
import { Search, Bell, StickyNote, BadgeQuestionMark, Users, Album } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { useRouter, useRoute } from 'vue-router'
import { useCookies } from 'vue3-cookies'
import { PostNewProjectOrQuestion, PostProductionAfter, CheckAuthorOwnership, PostNewLiterature, CreateNewPublication } from '../api/components.js'
import {checkDuplicateTitle} from '../api/production.js'

const { cookies } = useCookies;
const router = useRouter()
const internalInstance = getCurrentInstance()
const internalData = internalInstance.appContext.config.globalProperties

// User Info
const userId = ref(parseInt(internalData.$cookies.get('userId')))
const user_avator = ref(internalData.$cookies.get('avatarUrl') || 'https://img-nos.yiyouliao.com/alph/b16a79fc8870f1f5b88d8f256b813e5f.jpeg?yiyouliao_channel=vivo_image')

// Navigation & Drawer
const drawer = ref(false)

// Navigation Methods
const goTo = (path) => { 
  router.push(path) 
  searchQuery.value = ''
}
const goToHome = () => { 
  router.push('/home') 
  searchQuery.value = ''
}

function goToSearch(type){
  router.push({
    path: '/scholarRes',
    query: { condition: searchQuery.value, type: type }
  })
  searchQuery.value = ''
}

function goToPubSearch(){
  router.push({
    path: '/publicationRes',
    query: { condition: searchQuery.value}
  })
  searchQuery.value = ''
}

// Search
const searchQuery = ref('')
const showSelectBox = ref(false)
const selectBoxRef = ref(null)

const handleClickOutside = (event) => {
  if (
    showSelectBox.value &&
    selectBoxRef.value &&
    !selectBoxRef.value.contains(event.target)
  ) {
    showSelectBox.value = false
  }
}
onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})

const handleSelfBoxCommand = (command) => {
  if (command === 'profile') {
    goTo('/mygateway')
  } else if (command === 'logout') {
    internalData.$cookies.remove('userId')
    internalData.$cookies.remove('avatarUrl')
    internalData.$cookies.remove('account')
    goTo('/first')
  }
}

// Project Dialog
const dialogProjectVisible = ref(false)
const projectTitle = ref('')
const projectDescription = ref('')
const projectField = ref('')
const submitProject = () => {
  var promise = PostNewProjectOrQuestion(userId.value, projectTitle.value, projectDescription.value, projectField.value, 0)
  promise.then((result) => {
    if(result.success === true){
      ElMessage.success('Project submitted')
    }
    else{
      ElMessage.error(result.message)
    }
  })
  dialogProjectVisible.value = false
  window.location.reload()
}

// Question Dialog
const dialogQuestionVisible = ref(false)
const questionTitle = ref('')
const questionDescription = ref('')
const questionField = ref('')
const submitQuestion = () => {
  var promise = PostNewProjectOrQuestion(userId.value, questionTitle.value, questionDescription.value, questionField.value, 1)
  promise.then((result) => {
    if(result.success === true){
      ElMessage.success('Question submitted')
    }
    else{
      ElMessage.error(result.message)
    }
  })
  dialogQuestionVisible.value = false
  window.location.reload()
}

// Publication Dialog
const dialogPublicationVisible = ref(false)
const activeTabName = ref('single')
const publicationForm = ref({
  title: '',
  type: '',
  authors: '',
  research_fields: '',
  journal: '',
  volume: '',
  issue: '',
  year: 0,
  abstract: '',
  keywords: '',
  external_url: '',
  local_file_path: '',
  created_by: ''
})
const publicationFormRef = ref(null)

// Open Publication Dialog
const openPublicationDialog = (type) => {
  publicationForm.value = {
    title: '',
    type: type,
    authors: '',
    research_fields: '',
    journal: '',
    volume: '',
    issue: '',
    year: 0,
    abstract: '',
    keywords: '',
    external_url: '',
    local_file_path: '',
    created_by: ''
  }
  activeTabName.value = 'single'
  dialogPublicationVisible.value = true
}

// Validate and Submit Publication
const validateAndSubmitPublication = async () => {
  if (!publicationForm.value.type) {
    ElMessage.error('Please select a type')
    return
  }
  
  if (!publicationForm.value.title) {
    ElMessage.error('Please enter title')
    return
  }
  
  if (!publicationForm.value.authors) {
    ElMessage.error('Please enter authors')
    return
  }
  
  if (!publicationForm.value.research_fields) {
    ElMessage.error('Please enter research fields')
    return
  }

  await submitPublication()
}

const submitPublication = async () => {
  try {
    const userId = internalData.$cookies.get('userId');
    const authors = publicationForm.value.authors;
    
    const verificationResult = await CheckAuthorOwnership(userId, authors);
    
    if (!verificationResult.is_owner) {
      ElMessage.error(verificationResult.message || 'You are not in the author list. Only authors can submit publications.');
      return;
    }
    
    publicationForm.value.created_by = userId;
    
    // 使用封装的post方法
    const res = await CreateNewPublication(publicationForm.value);
    
    // 检查返回结果
    if (res.status === "error") {
      throw new Error(res.error?.message || 'Publication submission failed');
    }
    
    ElMessage.success('Publication submitted');
    dialogPublicationVisible.value = false;

    const promise = PostProductionAfter(userId, 0, 1);
    promise.then((result) => {
      if(!result.success){
        ElMessage.error(result.message);
      }
    });

  } catch (error) {
    console.error('Publication submission failed:', error);
    const errorMessage = error.message || 'Failed to submit publication';
    const prefix = error.response?.status === 403 ? 'Authorization failed:' : 'Submission failed:';
    ElMessage.error(`${prefix} ${errorMessage}`);
  }
  window.location.reload()
}

const handleUploadSuccess = (res, file) => {
  if (res && res.file_path) {
    publicationForm.value.local_file_path = res.file_path
  }
}
const beforeUpload = async (file) => {
  // 1. 检查文件类型和大小
  const isPDF = file.type === 'application/pdf'
  if (!isPDF) {
    ElMessage.error('Only PDF files allowed')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('File size exceeds 10MB limit')
    return false
  }
}

// Download Template
const downloadTemplate = () => {
  window.open('/publication_import_template.xlsx')
}

// Bulk Upload
const batchUploadRef = ref(null)
const excelData = ref({
  title: '',
  type: '',
  authors: '',
  research_fields: '',
  journal: '',
  volume: '',
  issue: '',
  year: 0,
  abstract: '',
  keywords: '',
  external_url: '',
  local_file_path: '',
  created_by: ''
})
const currentIndex = ref(0)
const totalCount = ref(0)
const uploadPercent = ref(0)
const uploading = ref(false)
const uploadResult = ref(null)

// Parse Excel Data
const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const data = new Uint8Array(e.target.result)
    const workbook = XLSX.read(data, { type: 'array' })
    const firstSheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[firstSheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet)
    if (!jsonData.length) {
      ElMessage.error('Excel file is empty or format error')
      excelData.value = []
      return
    }
    excelData.value = jsonData
    totalCount.value = jsonData.length
    uploadResult.value = null
    ElMessage.success(`Successfully parsed ${jsonData.length} records`)
  }
  reader.readAsArrayBuffer(file.raw)
  return false
}

const beforeBatchUpload = (file) => {
  const isExcel = file.type === 'application/vnd.ms-excel' || 
    file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  if (!isExcel) {
    ElMessage.error('Only Excel files allowed')
  }
  return isExcel
}

const allFieldsDefaults = {
  pub_id: '',
  title: '',
  type: '',
  authors: '',
  research_fields: '',
  journal: '',
  volume: '',
  issue: '',
  year: 0,
  abstract: '',
  keywords: '',
  external_url: '',
  local_file_path: '',
  created_by: internalData.$cookies.get('userId')
}

function fillDefaults(rawData) {
  const payload = {}
  for (const key in allFieldsDefaults) {
    if (Object.prototype.hasOwnProperty.call(allFieldsDefaults, key)) {
      let val = rawData[key]
      if (val === undefined || val === null || val === '') {
        payload[key] = allFieldsDefaults[key]
      } else {
        if (key === 'year') {
          const n = parseInt(val, 10)
          payload.year = isNaN(n) ? allFieldsDefaults.year : n
        } else if(key != 'created_by'){
          payload[key] = String(val)
        }
      }
    }
  }
  return payload
}
const startBatchUpload = async () => {
  if (!excelData.value.length) {
    ElMessage.warning('Please upload an Excel file first')
    return
  }
  uploading.value = true
  uploadResult.value = { success: 0, failed: 0, failDetails: [] }
  currentIndex.value = 0

  for (let i = 0; i < excelData.value.length; i++) {
    const rawItem = excelData.value[i]
    const item = fillDefaults(rawItem)
    try {
      // 使用封装的post方法
      const res = await CreateNewPublication(item);
      
      // 检查返回结果
      if (res.status === "error") {
        throw new Error(res.error?.message || 'Record upload failed');
      }
      
      uploadResult.value.success++
    } catch (e) {
      uploadResult.value.failed++
      uploadResult.value.failDetails.push(`Record ${i + 1} failed: ${e.message || 'Unknown error'}`)
    }
    currentIndex.value = i
    uploadPercent.value = Math.round(((i + 1) / excelData.value.length) * 100)
  }

  uploading.value = false
  ElMessage.success('Bulk upload completed')

  const promise = PostProductionAfter(userId.value, 1, excelData.value.length)
  promise.then((result) => {
    if(!result.success){
      ElMessage.error(result.message)
    }
  });
  
  setTimeout(() => {
    if (uploadResult.value.failed === 0) {
      dialogPublicationVisible.value = false
    }
  }, 3000)
}

// Open Other Dialogs
const openQuestionDialog = () => { 
  questionTitle.value = ""
  questionDescription.value = ""
  questionField.value = ""
  dialogQuestionVisible.value = true 
  drawer.value = false
}
const openProjectDialog = () => { 
  projectTitle.value = ""
  projectDescription.value = ""
  projectField.value = ""
  dialogProjectVisible.value = true 
  drawer.value = false
}

// Literature Upload
const dialogLiteratureVisible = ref(false)
const literatureForm = ref({
  title: '',
  authors: '',
  research_fields: '', 
  localFilePath: '',
  journal: '',
  year: null,
  abstract: '',
  keywords: ''
})

// Open Literature Dialog
const openLiteratureDialog = () => {
  literatureForm.value = {
    title: '',
    authors: '',
    research_fields: '',
    localFilePath: '',
    journal: '',
    year: null,
    abstract: '',
    keywords: ''
  }
  dialogLiteratureVisible.value = true
  drawer.value = false
}

// Literature Upload Validation
const beforeLiteratureUpload = (file) => {
  const isPDF = file.type === 'application/pdf'
  if (!isPDF) {
    ElMessage.error('Only PDF files allowed')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('File size exceeds 10MB limit')
    return false
  }
  return true
}

// Handle Literature Upload Success
const handleLiteratureUploadSuccess = (res, file) => {
  if (res && res.file_path) {
    literatureForm.value.localFilePath = res.file_path
    ElMessage.success('File uploaded')
  }
}

// Submit Literature
const submitLiterature = async () => {
  if (!literatureForm.value.title) {
    ElMessage.error('Please enter title')
    return
  }
  if (!literatureForm.value.authors) {
    ElMessage.error('Please enter authors')
    return
  }

  if (!literatureForm.value.research_fields) {
    ElMessage.error('Please enter research fields')
    return
  }
  
  if (!literatureForm.value.localFilePath) {
    ElMessage.error('Please upload file')
    return
  }
  const checkResult = await checkDuplicateTitle(literatureForm.value.title);

    if (checkResult.exists) {
      ElMessage.warning(checkResult.message || 'A document with the same title already exists.');
      return;
    }
  try {
    const payload = {
      userId: userId.value,
      title: literatureForm.value.title,
      authors: literatureForm.value.authors,
      research_fields: literatureForm.value.research_fields,
      localFilePath: literatureForm.value.localFilePath,
      journal: literatureForm.value.journal || '',
      year: literatureForm.value.year ? parseInt(literatureForm.value.year) : null,
      abstract: literatureForm.value.abstract || '',
      keywords: literatureForm.value.keywords || ''
    }
    
    // 使用封装的post方法
    const response = await PostNewLiterature(payload);
    
    // 检查返回结果
    if (response.status === "error") {
      throw new Error(response.error?.message || 'Literature upload failed');
    }
    if (response.success === true) {
      ElMessage.success('Literature uploaded')
      dialogLiteratureVisible.value = false
    } else {
      ElMessage.error(`Upload failed: ${response.message}`)
    }
  } catch (error) {
    ElMessage.error(`Upload failed: ${error.message || 'Unknown error'}`)
  }
  window.location.reload()
}

// Active Menu Tab
const route = useRoute()
const activeTab = ref(route.path)

watch(
  () => route.path,
  (newPath) => {
    activeTab.value = newPath
  }
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
.navbar { background: #fff; border:1px solid #d1d1d2; display:flex; }
.navbar .el-header { display:flex; align-items:center; justify-content:space-between; }
.logo {
  color: #333;
  font-size: 28px;
  font-family: 'Orbitron', 'Montserrat', 'Segoe UI', 'Arial Black', sans-serif;
  font-weight: 900;
  letter-spacing: 2px;
  cursor: pointer;
  text-shadow: 0 2px 8px rgba(80,120,255,0.08);
  transition: color 0.2s;
}
.my-menu { width:25vw; font-family:楷体_GB2312; }
.my-menu .el-menu-item.is-active,
.my-menu .el-menu-item:hover { border-bottom:3px solid #409EFF!important; background:#fff; }
.search-box { min-width:20vw; }
.search-box .select-box {
  position: absolute;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 1px solid #d1d1d2;
  padding: 1vh;
  min-width:20vw;
  font-size: 15px;
  color:#606266;
  z-index: 1000;
}
.choice-box { 
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 1%;
}
.choice-box:hover {
  background: #F0F2F5;
}
.button-box { display:flex; align-items:center; margin-left:5vw; color:#333; }
.button-box .el-avatar {
  cursor: pointer;
}
.add-new-button { margin:1vw; font-size:14px; background:rgb(0,109,217); }
.add-new-button:hover { background:rgb(0,57,113); }
.drawer-title { font-size:35px; font-weight:lighter; font-family:'Montserrat'; margin:2vh 0 2vh 5vw; }
.menu-box { width:100%; padding:1vw; }

.menu-box .el-menu-item.is-active {
  color: #000;
  
}
.menu-box .el-menu-item:hover { background:#E4E7ED; color:#000; }
.custom-dialog .el-form-item { margin-bottom:16px; }
.dialog-footer { display:flex; justify-content:flex-end; gap:10px; }

:deep(.el-dropdown-menu__item:hover) {
  background: #F0F2F5 !important;
  color:#606266;
}

.publication-dialog :deep(.el-dialog__body) {
  padding: 0 20px !important;
}

.scroll-container {
  max-height: 50vh;
  overflow-y: auto;
  padding: 10px 15px;
}

.tabs-header {
  margin-top: -20px;
  margin-bottom: 10px;
}

.batch-upload-container {
  min-height: 300px;
  padding: 10px;
}

.form-row {
  display: flex;
  gap: 10px;
}

.el-menu-item [class^="lucide-"] {
  margin-right: 8px;
}
.big-upload .el-button {
  font-size: 16px;
  padding: 18px 24px;
}
.bulk-upload {
  font-size: 18px;
}

.bulk-upload .el-button {
  font-size: 16px;
  padding: 16px 18px;
}

.bulk-upload .el-form-item__label {
  font-size: 18px;
}

.bulk-upload .el-input__inner {
  font-size: 18px;
  height: 42px;
}

.required-item .el-form-item__label::before {
  content: "*";
  color: #f56c6c;
  margin-right: 4px;
}

:deep(.el-form-item__error) {
  color: #f56c6c;
  font-size: 12px;
  line-height: 1;
  padding-top: 4px;
  position: relative;
  top: 0;
  left: 0;
}
.required-star {
  color: red;
  margin-right: 4px;
}
</style>