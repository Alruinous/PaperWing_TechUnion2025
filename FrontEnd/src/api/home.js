import { post,get } from "./api"

export function GetAuthors(userId){
    let data = {};
    data.userId = userId;
    return get("/users/authors/", data);
}

export function GetMessages(userId){
    let data = {};
    data.userId = userId;
    return get("/users/messages/", data);
}

export function FollowUser(followerid, followeeid){
    let data = {};
    data.followeeid = followeeid;
    data.followerid = followerid;
    return post("/users/follow/", data);
}

export function UnfollowUser(followerid, followeeid){
    let data = {};
    data.followeeid = followeeid;
    data.followerid = followerid;
    return post("/users/unfollow/", data);
}

export function GetCollection(userId){
    let data = {};
    data.userId = userId;
    return post("/documents/getCollection/", data);
}

export function DoFavorite(userId, docId){
    let data = {};
    data.userId = userId;
    data.docId = docId;
    return post("/documents/addFavorite/", data);
}