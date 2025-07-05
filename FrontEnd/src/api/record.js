import { post,get } from './api'

export async function addHistory({ publicationId, userId }) {
  return post('/publications/add_reading_history/', {
    publicationId,
    userId
  })
}
export async function addDocHistory({ documentId, userId }) {
  return post('/documents/add_reading_history/', {
    documentId,
    userId
  })
}

export function getUserHistory({ userId, page = 1, pageSize = 10 }) {
  return get('/users/reading-history/', {
    userId,
    page,
    pageSize
  })
}