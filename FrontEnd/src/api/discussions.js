import { post,get } from "./api"

export function fetchCreatedProjects(userId) {
    return post('/discussions/getCreatedProjects/', { userId })
        .then(res => {
            if (res.success === true) {
                const { projects, total } = res.data || {}
                return { projects, total }
            } else {
                throw new Error(`接口响应失败，success: ${res.data?.success}`)
            }
        })
        .catch(err => {
            console.error('请求用户创建的项目列表失败:', err)
            throw err
        })
}

export function fetchParticipantStatus(userId, projectId) {
    return post('/discussions/getParticipantStatus/', { userId, projectId })
        .then(res => {
            if (res.success === true) {
                return res.data?.status || null
            } else {
                throw new Error(`接口响应失败，success: ${res.success}`)
            }
        })
        .catch(err => {
            console.error('请求用户参与状态失败:', err)
            return null
        })
}

export function projectSummary(project_id){
    return get('/discussions/projectAI/', { project_id: project_id })
}