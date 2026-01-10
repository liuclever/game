import http from './http'

export function fetchHandbookIndex({ pacename = 1, page = 1, pageSize = 10 } = {}) {
  return http.get('/handbook/index', {
    params: { pacename, page, pageSize },
  })
}

export function fetchHandbookPetDetail(petId, { evolution = 0 } = {}) {
  return http.get(`/handbook/pets/${petId}`, {
    params: { evolution },
  })
}

export function fetchHandbookSkillDetail(skillKey) {
  return http.get(`/handbook/skills/${skillKey}`)
}


