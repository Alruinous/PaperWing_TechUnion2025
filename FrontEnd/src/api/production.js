import { post,get } from "./api"

export function GetProduction(pub_id,user_id){
    let data = {};
    data.pub_id = pub_id;
    data.user_id = user_id;
    return get("/publications/get_article/",data);
}

export function GetComments(pub_id){
    let data = {};
    data.pub_id = pub_id;
    return get("/publications/comments/",data);
}

export function PostFavor(pub_id,user_id){
    let data = {}
    data.pub_id = pub_id;
    data.user_id = user_id;
    return post("/publications/favour/",data);
}

export function PostComment(pub_id,user_id,comment){
    let data = {}
    data.pub_id = pub_id;
    data.user_id = user_id;
    data.comment = comment;
    return post("/publications/comment/",data);
}

export function PostRequest(senderId,receiverId,type,content,projectId,resultId,timestamp){
    let data = {};
    data.senderId = senderId;
    data.receiverId = receiverId;
    data.type = type;
    data.content = content;
    data.projectId = projectId;
    data.resultId = resultId;
    data.timestamp = timestamp;
    return post("/conversation/sendMessages/",data);
}

export function PostConcelFavor(pub_id,user_id){ 
    let data = {}
    data.pub_id = pub_id;
    data.user_id = user_id;
    return post("/publications/cancelfavor/",data);
}

export function fetchUserPublications(userId) {
    return post('/publications/user-publication/', { userId })
        .then(res => {
            if (res.success === true) {
                return res.data
            } else {
                throw new Error(res.success)
            }
        })
}

export function CheckClaimOwnership(publicationId,userId){
    let data = {}
    data.publicationId = publicationId;
    data.userId = userId;
    return post("/publications/check_claim_ownership/",data);
}

export function fetchUserCategories(userId) {
    const data = { userId }
    return post('/documents/get_favorite_category/', data).then(res => {
        if (res.success) {
            return res.data
        } else {
            throw new Error(res.message || '获取用户分类失败')
        }
    })
}

export function addUserCategory(userId, newCategory) {
    const data = { userId, newCategory }
    return post('/documents/add_favorite_category/', data)
        .then(res => {
            if (res.success) {
                return true
            } else {
                throw new Error(res.message || '添加失败')
            }
        })
}

export function fetchUserDocuments(userId) {
    const data = { userId };
    return post('/documents/get_all_docs/', data)
        .then(res => {
            if (res.success) {
                return res.data;  // 返回文献数据
            } else {
                throw new Error(res.message || '获取文献失败');
            }
        })
        .catch(error => {
            console.error('Error fetching documents:', error);
            throw error;  // 如果出错，抛出错误
        });
}

export function uploadDocument(file) {
    return post('/publications/upload/', { file })
}

export function uploadFullText(pub_id,url){
    return post('/publications/uploadFullText/', { pub_id,url })
}

export const checkDuplicateTitle = async (title) => {
    return get('/documents/check_duplicate/', { title });
  };