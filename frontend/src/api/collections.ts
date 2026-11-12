import {request,post} from './client';import type {Collection} from '../types/domain';export const list=()=>request<Collection[]>('/collections'+'');export const create=(data:unknown)=>post<Collection>('/collections',data);
export const update=(id:number,data:unknown)=>request<Collection>('/collections/'+id,{method:'PUT',body:JSON.stringify(data)});
