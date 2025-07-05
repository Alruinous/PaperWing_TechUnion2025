import { post,get } from "./api"

export function GetProjectDetail(projId){
    let data = {};
    data.projId = projId;
    return get("/discussions/projectdetail/", data);
}

export function GetStatus(userId, projectId){
    let data = {};
    data.userId = userId;
    data.projectId = projectId;
    return post("/discussions/getParticipantStatus/", data);
}

export function GetProjectReplies(projId){
    let data = {};
    data.projId = projId;
    return get("/discussions/projectreplies/", data);
}

export function PostProjectReply(userId, projId, reply){
    let data = {};
    data.userId = userId;
    data.projId = projId;
    data.reply = reply;
    return post("/discussions/postreply/", data);
}

export function GetQuestionDetail(questionId){
    let data = {};
    data.questionId = questionId;
    return get("/discussions/questiondetail/", data);
}

export function GetQuestionReplies(questionId){
    let data = {};
    data.questionId = questionId;
    return get("/discussions/questionreplies/", data);
}

export function GetQuestions(user_id){
    let data = {};
    data.user_id = user_id;
    return get("/discussions/forum/", data);
}

export function PostFollow(question_id,user_id) {
    let data = {};
    data.question_id = question_id;
    data.user_id = user_id;
    return post("/discussions/followQuestion/", data);
}

export function PostCancelFollow(question_id,user_id) { 
    let data = {};
    data.question_id = question_id;
    data.user_id = user_id;
    return post("/discussions/unfollowQuestion/", data);
}

export function searchUsers(name, projectId) {
    let data = {};
    data.name = name;
    data.projectId = projectId;
    return get("/users/search/", data);
}

export function RemoveMember(userId, projId) { 
    let data = {};
    data.userId = userId;
    data.projId = projId;
    return post("/discussions/deleteMembers/", data);
}
