import {request,post} from './client';import type {Specimen} from '../types/domain';export const list=(collection_id:number)=>request<Specimen[]>('/specimens'+`?collection_id=${collection_id}`);export const create=(data:unknown)=>post<Specimen>('/specimens',data);
export const update=(id:number,data:unknown)=>request<Specimen>('/specimens/'+id,{method:'PUT',body:JSON.stringify(data)});
