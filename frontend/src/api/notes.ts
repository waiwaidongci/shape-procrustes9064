import {request,post} from './client';import type {Note} from '../types/domain';export const list=()=>request<Note[]>('/notes'+'');export const create=(data:unknown)=>post<Note>('/notes',data);
export const review=(id:number,status:string,reviewer_note:string)=>post<Note>('/notes/'+id+'/review',{status,reviewer_note});
