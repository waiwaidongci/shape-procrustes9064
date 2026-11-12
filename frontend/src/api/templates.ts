import {request,post} from './client';import type {Template} from '../types/domain';export const list=()=>request<Template[]>('/templates'+'');export const create=(data:unknown)=>post<Template>('/templates',data);
export const update=(id:number,data:unknown)=>request<Template>('/templates/'+id,{method:'PUT',body:JSON.stringify(data)});
