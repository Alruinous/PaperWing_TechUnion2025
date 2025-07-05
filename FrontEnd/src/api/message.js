import { post,get } from './api'

// 发送消息
export function sendMessage(data) {
  return post('/conversation/sendMessages/', data)
}
export function fetchMessages(data) {
  return post('/conversation/getMessages/', data)  // 根据后端接口地址调整
}

export function sendInvitationMessage({ senderId, receiverId, projectId, content }) {
  const now = new Date();
  const timestamp = `${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}/${now.getHours()}/${now.getMinutes()}`;

  return post('/conversation/sendMessages/', {
    senderId,
    receiverId,
    type: 'invitation',
    content,
    projectId,
    resultId: 0,
    timestamp
  });
}

export function respondInvitation(data) {
  return post('/discussions/respondInvitation/', data);
}
export function respondClaimRequest(data) {
  return post('/publications/respond_claim/', data);
}

export function respondApplyRequest(data) {
  return post('/publications/respond_apply/', data);
}