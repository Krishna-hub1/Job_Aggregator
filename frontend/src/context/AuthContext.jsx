import { createContext,useContext,useEffect,useState } from 'react';
import {api,setAuthToken} from '../services/api';
const AuthContext=createContext(null);
export function AuthProvider({children}){const[user,setUser]=useState(null);const[loading,setLoading]=useState(true);
 useEffect(()=>{const token=localStorage.getItem('jobhub_token');
    if(!token){setLoading(false);
        return}setAuthToken(token);
        api.getMe().then(r=>setUser(r.data.user)).catch(()=>{localStorage.removeItem('jobhub_token');
            setAuthToken(null)}).finally(()=>setLoading(false))},[]);
 const authenticate=async(fn)=>{const{data}=await fn();
 localStorage.setItem('jobhub_token',data.token);
 setAuthToken(data.token);setUser(data.user);return data.user};
 const login=(e,p)=>authenticate(()=>api.login(e,p)); const register=(n,e,p)=>authenticate(()=>api.register(n,e,p)); 
 const logout=()=>{localStorage.removeItem('jobhub_token');setAuthToken(null);setUser(null)};
 return <AuthContext.Provider value={{user,loading,login,register,logout}}>{children}</AuthContext.Provider>}
export const useAuth=()=>useContext(AuthContext);
