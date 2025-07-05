<template>
  <div class="card-container">
    <div class="circle1"></div>
    <div class="circle2"></div>
    <div class="watermark">PAPERWING</div>

    <el-card class="register-card">
      <el-steps :active="step" finish-status="success" align-center>
        <el-step title="Research Institution" />
        <el-step title="Basic Information" />
        <el-step title="Research Fields" />
      </el-steps>

      <!-- Step 1: Research Institution -->
      <div v-show="step === 0" class="step-form">
        <el-form :model="formStep1" :rules="rulesStep1" ref="form1" label-width="180px">
          <el-form-item label="Research Institution" prop="institution">
            <el-input 
              v-model="formStep1.institution" 
              placeholder="Optional"
              maxlength="100"
            />
          </el-form-item>
          <el-form-item label="Department" prop="department">
            <el-input 
              v-model="formStep1.department" 
              placeholder="Optional"
              maxlength="50"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: Basic Information -->
      <div v-show="step === 1" class="step-form">
        <el-form :model="formStep2" :rules="rulesStep2" ref="form2" label-width="180px">
          <el-form-item label="Full Name" prop="name">
            <el-input 
            v-model="formStep2.name" 
            maxlength="50"
            placeholder="Required"
          />
          </el-form-item>
          <el-form-item label="Country/Region" prop="region">
            <el-select
              v-model="formStep2.region"
              placeholder="Select country/region"
              filterable
              allow-create
              default-first-option
              style="width: 100%"
            >
              <el-option
                v-for="country in countryOptions"
                :key="country"
                :label="country"
                :value="country"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Institutional Email" prop="email">
            <el-input 
              v-model="formStep2.email" 
              maxlength="100"
            />
          </el-form-item>
          <el-form-item label="Password" prop="password">
            <el-input
              v-model="formStep2.password"
              type="password"
              maxlength="32"
              @input="() => form2.value?.validateField('confirmPassword')"
            />
          </el-form-item>
          <el-form-item label="Confirm Password" prop="confirmPassword">
            <el-input 
              v-model="formStep2.confirmPassword" 
              type="password"
              maxlength="32"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 3: Research Fields -->
      <div v-show="step === 2" class="step-form">
        <el-form :model="formStep3" :rules="rulesStep3" ref="form3" label-width="180px">
          <el-form-item label="Discipline" prop="discipline">
            <el-select 
              v-model="formStep3.discipline" 
              placeholder="Select discipline (optional)"
              style="width: 100%"
            >
              <el-option v-for="item in disciplines" :key="item" :label="item" :value="item" />
            </el-select>
          </el-form-item>
          <el-form-item label="Research Expertise" prop="expertise">
            <el-input 
              v-model="formStep3.expertise" 
              placeholder="Optional"
              maxlength="100"
            />
          </el-form-item>
        </el-form>
      </div>

      <div class="register-actions">
        <el-button @click="prevStep" :disabled="step === 0">Previous</el-button>
        
        <el-button 
          v-if="step === 0 || step === 2" 
          type="info" 
          @click="skipStep"
        >
          Skip
        </el-button>
        
        <el-button 
          v-if="step < 2" 
          type="primary" 
          @click="nextStep"
          :loading="step === 1 && checking"  
          :disabled="step === 1 && checking"  
        >
          {{ step === 1 && checking ? 'Verifying...' : 'Next' }}
        </el-button>
        
        <el-button 
          v-if="step === 2" 
          type="success" 
          @click="submitAll"
          :loading="submitting"
        >
          {{ submitting ? 'Submitting...' : 'Register' }}
        </el-button>
      </div>

      <div v-if="(step === 1 && checking) || submitting" class="loading-overlay">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p v-if="step === 1 && checking">Verifying email, please wait...</p>
          <p v-if="submitting">Submitting registration, please wait...</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { Register, checkAccountOrEmail } from "@/api/user";
import { useRouter } from "vue-router";

const router = useRouter();
const step = ref(0);
const checking = ref(false); 
const submitting = ref(false); 
const form1 = ref();
const form2 = ref();
const form3 = ref();

const formStep1 = ref({
  institution: "",
  department: "",
});

const formStep2 = ref({
  name: "",
  region: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const formStep3 = ref({
  discipline: "",
  expertise: "",
});

const disciplines = ["Biology", "Chemistry", "Physics", "Mathematics", "Computer Science", "Materials Science", "Medicine", "Engineering", "Earth Sciences", "Environmental Science", "Psychology", "Sociology", "Economics", "Education", "Linguistics", "Philosophy", "History", "Law"];
const countryOptions = ["China", "United States", "Japan", "Germany", "United Kingdom", "France", "Italy", "Canada", "South Korea", "Australia", "India", "Russia", "Singapore", "Brazil", "South Africa", "Netherlands", "Switzerland", "Sweden", "Spain", "Norway"];

const academicEmailSuffixes = [
  "edu.cn", "edu.com", "ac.cn", "ac.uk", "ac.jp", "ac.kr", "ac.in", "ac.nz", "cas.cn",
  "nasa.gov", "nih.gov", "nsf.gov", "cnic.cn", "sciencenet.cn", "sinica.edu.tw",
  "unimelb.edu.au", "uq.edu.au", "harvard.edu", "mit.edu", "ox.ac.uk", "cam.ac.uk"
];

function isAcademicEmail(email: string): boolean {
  const domain = email.split("@")[1]?.toLowerCase();
  return academicEmailSuffixes.some(suffix => domain?.endsWith(suffix));
}

const rulesStep1 = {
  institution: [{ required: false, max: 100, message: "Max 100 characters", trigger: "blur" }],
  department: [{ required: false, max: 50, message: "Max 50 characters", trigger: "blur" }],
};

const rulesStep2 = {
  name: [
    { 
      required: true, 
      validator: (_, value, callback) => {
        if (!value || value.trim() === '') {
          callback(new Error("Please enter your full name"));
        } else if (value.length > 50) {
          callback(new Error("Max 50 characters"));
        } else {
          callback();
        }
      },
      trigger: "blur"
    }
  ],
  email: [
    { required: true, message: "Please enter a valid email", trigger: "blur" },
    { max: 100, message: "Max 100 characters", trigger: "blur" },
    {
      validator(_, value, callback) {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!pattern.test(value)) {
          callback(new Error("Invalid email format"));
        } else if (!isAcademicEmail(value)) {
          callback(new Error("Please use academic institution email"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "Please enter password", trigger: "blur" },
    { 
      min: 8, 
      message: "At least 8 characters", 
      trigger: "blur" 
    },
    { 
      max: 32, 
      message: "Max 32 characters", 
      trigger: "blur" 
    },
    {
      validator: (_, value, callback) => {
        if (value.length < 8) {
          callback(new Error("Password must be at least 8 characters"));
        } else {
          callback();
        }
      },
      trigger: "blur"
    }
  ],
  confirmPassword: [
    { required: true, message: "Please confirm password", trigger: "blur" },
    {
      validator(_, value, callback) {
        if (value !== formStep2.value.password) {
          callback(new Error("Passwords do not match"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const rulesStep3 = {
  discipline: [{ required: false }],
  expertise: [{ required: false, max: 100, message: "Max 100 characters", trigger: "blur" }],
};

const nextStep = async () => {
  const formRef = [form1, form2][step.value];
  if (!formRef.value) return;

  formRef.value.validate(async (valid: boolean) => {
    if (!valid) return;

    if (step.value === 1) {
      checking.value = true;
      
      try {
        const res = await checkAccountOrEmail({
          email: formStep2.value.email,
        });
        
        if (res.exists) {
          ElMessage.error("Email already registered");
        } else {
          step.value++;
        }
      } catch (err) {
        ElMessage.error("Email verification failed");
      } finally {
        checking.value = false;
      }
    } else {
      step.value++;
    }
  });
};

const prevStep = () => {
  if (step.value > 0) step.value--;
};

const skipStep = () => {
  if (step.value === 0) {
    formStep1.value.institution = "";
    formStep1.value.department = "";
    step.value++;
  } else if (step.value === 2) {
    formStep3.value.discipline = "";
    formStep3.value.expertise = "";
    submitAll();
  }
};

const getResearchFields = () => {
  const fields = [];
  if (formStep3.value.discipline.trim()) fields.push(formStep3.value.discipline.trim());
  if (formStep3.value.expertise.trim()) fields.push(formStep3.value.expertise.trim());
  return fields.join(", ");
};

const submitAll = () => {
  submitting.value = true;
  
  // 对姓名进行trim处理
  const trimmedName = formStep2.value.name.trim();
  
  const allData = {
    name: trimmedName,  // 使用trim后的姓名
    email: formStep2.value.email.trim(),
    password: formStep2.value.password,
    institution: formStep1.value.institution || "",
    department: formStep1.value.department || "",
    region: formStep2.value.region || "",
    research_fields: getResearchFields() || "",
  };

  Register(allData)
    .then(result => {
      if (result.status === "success") {
        ElMessage.success("Registration successful");
        router.push("/login");
      } else {
        ElMessage.error(result.message || "Registration failed");
      }
    })
    .catch(err => {
      ElMessage.error("Registration request failed");
    })
    .finally(() => {
      submitting.value = false;
    });
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Monoton&family=Press+Start+2P&family=Anton&display=swap');
.card-container {
  width: 100vw;
  height: 100vh;
  background: #f0f4fc;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 20px;
  box-sizing: border-box;
}

.register-card {
  width: 720px;              /* 适中宽度 */
  min-height: 260px;         /* 适中高度 */
  border-radius: 14px;
  box-shadow: 0 5px 22px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(7px);
  background-color: rgba(255, 255, 255, 0.7);
  position: relative;
  z-index: 10;
  padding: 40px 48px;
  
  /* 统一缩放 */
  transform: scale(1.12);  
  transform-origin: top center;

  font-family: 'Segoe UI', sans-serif;
  font-size: 15.5px;        /* 字号也微微放大 */
  line-height: 1.55;
  color: #222;
}

.el-steps {
  margin-bottom: 24px;
}

.step-form {
  margin-bottom: 24px;
}

/* 水印文字 */
.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-20deg);
  font-size: 200px;
  font-weight: bold;
  font-family: 'Monoton', 'Orbiran', 'Anton', sans-serif;
  letter-spacing: 20px;
  color: rgba(183, 225, 243, 0.863);
  user-select: none;
  pointer-events: none;
  z-index: 0;
  text-shadow:
    1px 1px 0 rgba(0, 0, 0, 0.05),
    2px 2px 0 rgba(0, 0, 0, 0.04),
    3px 3px 0 rgba(255, 255, 255, 0.12),
    4px 4px 6px rgba(0, 0, 0, 0.06),
    -1px -1px 1px rgba(255, 255, 255, 0.15);
}

.circle1,
.circle2 {
  height: 80px;
  width: 80px;
  border-radius: 50%;
  position: absolute;
  z-index: 0;
}

.circle1 {
  background-color: #2879f3;
  top: 60px;
  left: 60px;
}

.circle2 {
  background-color: #f37e10;
  bottom: 60px;
  right: 60px;
}

.register-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

/* Loading overlay 和 spinner 样式保持你原有代码即可 */
.loading-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  border-radius: 16px;
}

.loading-spinner {
  text-align: center;
  color: #2879f3;
  font-weight: 600;
}

.spinner {
  margin: 0 auto 10px auto;
  width: 36px;
  height: 36px;
  border: 4px solid #2879f3;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden;  /* 防止横向滚动 */
  background-color: #f0f2f5; /* 页面背景色 */
}
</style>