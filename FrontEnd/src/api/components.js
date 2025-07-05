import { post,get } from "./api"

export function PostNewProjectOrQuestion(userId, title, abstract, field, type){
    let data = {};
    data.user_id = userId;
    data.title = title;
    data.abstract = abstract;   
    data.field = field;
    data.type = type;
    return post("/discussions/createProjectOrQuestion/", data);
}

export function PostNewLiterature(payload){
    return post('/documents/upload/', payload);
}
export function PostProductionAfter(userId, type, number){
    let data = {};
    data.userId = userId;
    data.type = type;
    data.number = number;
    return post("/publications/sendemail/", data);
}

export const CheckAuthorOwnership = (userId, authors) => {
    return post('/users/check_author_ownership/', {
        userId: userId,
        authors: authors
    });
}

export const CreateNewPublication = (payload) => {
    return post('/publications/create/', payload);
}