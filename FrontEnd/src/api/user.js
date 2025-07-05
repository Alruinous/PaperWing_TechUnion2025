import { post, get } from "./api";

export function Login(account, password) {//登录
  return post("/users/login/", { account, password });
}

export function GetScholarData(currentUserId, targetUserId) {
  return post("/authors/scholarData", {
    currentUserId: currentUserId,
    authorId: targetUserId,
  });
}

export function GetMyUserData(userId) {
  return post("/users/myUserData", { userId });
}

export function Register(payload) {//注册
  return post("/users/register/", payload);
}

export function checkAccountOrEmail(params) {//账号及邮箱重复性检查
  return post("/users/check-account-or-email/", params);
}

export function UpdateAvatar(userId, avatarIndex) {
  return post("/users/updateAvatar", { userId, avatarIndex });
}

export function fetchResults(data) {
  return post("/authors/searchscholars", data);
}

export function updateDescription(userId, description) {
  return post("/users/updateDescription", { userId, description });
}

export function platformOverview() {
  return get("/user/platform-overview");
}

export function fetchScholars(userId, condition, type) {//学者搜索
  return get("/users/searchScholar/", { user_id: userId, condition: condition, type: type });
}

export function fetchPublications(userId, condition, type) {//成果搜索
  return get("/publications/search/", { user_id: userId, condition: condition, type: type });
}

export function fetchPublicationsAI(userId, condition, type) {//成果搜索AI总结
  return get("/publications/searchAI/", { user_id: userId, condition: condition, type: type });
}

export function fetchPublicationsRecommend(userId, type) {//成果搜索推荐
  return get("/publications/recommend/", { userId: userId, type: type});
}

export function fetchUserInfo(userId) {
    return post('/users/userinfo/', { userId })
        .then(res => {
            if (res.status === 200) {
                return res.data;
            } else {
                throw new Error(res.status);
            }
        })
        .catch(err => {
            console.error('请求用户信息失败:', err);
            throw err;
        });
}
export function updateUserInfo(editData) {
    return post('/users/updateinfo/', editData)
        .then(res => {
            if (res.status === "success") {
                return res.data;
            } else {
                throw new Error(res.status)
            }
        })
}

export function fetchFavorites(userId) {
    return post('/documents/get_all_docs/', { userId: userId })
        .then(res => {
            if (res.success === true) {
                return res.data;
            } else {
                throw new Error(res.message || '获取收藏文献失败');
            }
        })
        .catch(err => {
            console.error('fetchFavorites error:', err);
            throw err;
        });
}

// AI辅助阅读
export function aiSummaryDoc(doc_id){
  return get('/documents/ai/', { doc_id: doc_id })
}

// user.js
export function updateDocCategory(userId, docId, newCategory) {
    return post('/documents/update_category/', {
        userId: userId,
        docId: docId,
        newCategory: newCategory
    })
        .then(res => {
            if (res.success) {
                return res;
            } else {
                throw new Error(res.message || '更新文献分类失败');
            }
        })
        .catch(err => {
            console.error('updateDocCategory error:', err);
            throw err;
        });
}

export async function fetchFollowers(userId) {
    try {
        const res = await post('/users/following/', { userId });
        if (res && res.data) {
            return res.data;
        } else {
            throw new Error(res.message || 'Failed to fetch followers');
        }
    } catch (error) {
        console.error('fetchFollowers error:', error);
        throw error;
    }
}
