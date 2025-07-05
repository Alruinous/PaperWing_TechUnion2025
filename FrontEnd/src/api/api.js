import axios from "axios";
//const serveAddress = "http://10.251.254.221:8000";
//const serveAddress = "http://127.0.0.1:8000";

const serveAddress = '/api';
export function post(url,data){
    return new Promise((resolve,reject) => {
        axios
            .post(serveAddress+url,data, {
                withCredentials: true,
            })
            .then((response) => {
                resolve(response.data);
            })
            .catch((error) => {
                resolve({error:error,status:"error"});
            })
    });
}

// param 请求类型的 api
export function get(url,param){
    return new Promise((resolve,reject) => {
        axios
            .get(serveAddress+url,{
                params:param,
                withCredentials: true, // xjs写的， 巨关键，见到的给他磕一个
            })
            .then((response) => {
                resolve(response.data);
            })
            .catch((error) => {
                resolve({error:error,status:"error"});
            })
    });
}