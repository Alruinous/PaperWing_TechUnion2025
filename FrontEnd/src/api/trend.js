import { post,get } from "./api"

export function IsGenerated(userId){
    let data = {};
    data.userId = userId;
    return get("/documents/isgenerated/", data);
}

export function GetTrendResultById(userId){
    let data = {};
    data.userId = userId;
    return get("/documents/getanalysis/", data);
}

export function PostTrendAnalysis(userId, keyword, frequency){
    let data = {};
    data.userId = userId;
    data.keyword = keyword;
    data.frequency = frequency;
    return post("/documents/analysisrequest/", data);
}