import axios from 'axios';

const client = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api', timeout: 15000 });
export const setAuthToken = (token) => token ? (client.defaults.headers.common.Authorization = `Bearer ${token}`) : delete client.defaults.headers.common.Authorization;
client.interceptors.request.use((config) => { const token = localStorage.getItem('jobhub_token'); if (token) config.headers.Authorization = `Bearer ${token}`; return config; });
client.interceptors.response.use(r => r, err => { if (err.response?.status === 401) { localStorage.removeItem('jobhub_token'); setAuthToken(null); } return Promise.reject(err); });

export const api = {
  login:(email,password)=>client.post('/auth/login',{email,password}), register:(name,email,password)=>client.post('/auth/register',{name,email,password}), getMe:()=>client.get('/auth/me'), changePassword:(current_password,new_password)=>client.post('/auth/change-password',{current_password,new_password}),
  getJobs:(params)=>client.get('/jobs',{params}), getLocations:(country='')=>client.get('/locations',{params: country ? {country} : {}}), getJob:(id)=>client.get(`/jobs/${id}`), saveJob:(id)=>client.post(`/jobs/${id}/save`), applyJob:(id)=>client.post(`/jobs/${id}/apply`),
  getSavedJobs:()=>client.get('/saved'), updateSavedJob:(id,data)=>client.patch(`/saved/${id}`,data), deleteSavedJob:(id)=>client.delete(`/saved/${id}`), getApplications:()=>client.get('/applications'),
  getStats:()=>client.get('/stats'), getCompanies:(search='')=>client.get('/companies',{params:{search}}), getCompany:(id)=>client.get(`/companies/${id}`),
  getProfile:()=>client.get('/profile'), updateProfile:(data)=>client.patch('/profile',data), getResumes:()=>client.get('/resumes'), uploadResume:(file)=>{const f=new FormData();f.append('resume',file);return client.post('/resumes',f,{headers:{'Content-Type':'multipart/form-data'}})}, deleteResume:(id)=>client.delete(`/resumes/${id}`), downloadResume:(id)=>client.get(`/resumes/${id}/download`,{responseType:'blob'}),
  adminDashboard:()=>client.get('/admin/dashboard'), adminUsers:()=>client.get('/admin/users'), adminUpdateUser:(id,data)=>client.patch(`/admin/users/${id}`,data), adminJobs:()=>client.get('/admin/jobs'), adminUpdateJob:(id,data)=>client.patch(`/admin/jobs/${id}`,data), adminScrape:()=>client.post('/scrape'),
  getAlerts:()=>client.get('/alerts'), createAlert:(data)=>client.post('/alerts',data), updateAlert:(id,data)=>client.patch(`/alerts/${id}`,data), deleteAlert:(id)=>client.delete(`/alerts/${id}`),
};
