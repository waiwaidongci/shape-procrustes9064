import {useEffect,useState} from 'react';
import {authStore,canEdit} from '../stores/auth';
import {useTask} from '../hooks/useTask';
import * as api from '../api/intake';
import {date} from '../utils/format';
import ErrorNotice from './common/ErrorNotice';
import StatusBadge from './common/StatusBadge';
import type {Collection,Template,IntakeBatch} from '../types/domain';

const actionLabel:Record<string,string>={created:'已新增',updated:'已更新',unchanged:'未变',skipped:'已跳过'};
const changeLabel:Record<string,string>={name:'名称',points:'角点',source_note:'来源说明'};

function WrittenRows({batch}:{batch:IntakeBatch}){
  const written=batch.result.written||[];
  return <div className="table-scroll"><table><thead><tr><th>编号</th><th>处理</th><th>裁片ID</th></tr></thead><tbody>{written.map((w,i)=><tr key={i}><td><b>{w.code}</b></td><td>{actionLabel[w.action]||w.action}{w.reason&&<small className="error-text">{w.reason}</small>}</td><td>{w.id??'—'}</td></tr>)}</tbody></table></div>;
}

function PreviewBlock({batch,busy,onConfirm}:{batch:IntakeBatch;busy:boolean;onConfirm:()=>void}){
  const s=batch.summary,cap=s.capacity,passing=s.new+s.update+s.unchanged;
  return <div className="intake-preview">
    <h2 className="ruled-title">核对预览 <small>批次 {batch.token.slice(0,8)}</small><StatusBadge status={batch.status}/></h2>
    <div className="result-metrics">
      <div><small>新增</small><strong>{s.new}</strong></div>
      <div><small>更新</small><strong>{s.update}</strong></div>
      <div><small>未变</small><strong>{s.unchanged}</strong></div>
      <div><small>坏行</small><strong>{s.error}</strong></div>
    </div>
    <p className="muted">容量：现有{cap.current}份 ＋ 新增{s.new}份 ＝ {cap.after} / 上限{cap.limit}{!cap.sufficient&&<span className="error-text">；容量不足，确认将整批拒绝，请删减后重新预览</span>}</p>
    {batch.status==='rejected'&&<p className="error-text">{batch.result.reason}</p>}
    <div className="table-scroll"><table><thead><tr><th>行</th><th>编号</th><th>核对</th><th>说明</th></tr></thead><tbody>{batch.rows.map(r=><tr key={r.index}>
      <td>{r.index+1}</td>
      <td><b>{r.code||'—'}</b>{r.specimen_id!=null&&<small>现有ID {r.specimen_id}</small>}</td>
      <td><StatusBadge status={r.status}/></td>
      <td>{r.status==='error'?<span className="error-text">{r.reason}</span>:r.status==='update'?<small>改动：{r.changes.map(c=>changeLabel[c]||c).join('、')}；身份保留</small>:r.status==='new'?<small>集合内新编号</small>:<small>与现有裁片一致，不写入</small>}</td>
    </tr>)}</tbody></table></div>
    {batch.status==='previewed'&&<div className="button-row">
      <button className="primary" disabled={busy||!passing||!cap.sufficient} onClick={onConfirm}>确认写入{passing}份通过裁片 →</button>
      {s.error>0&&<span className="muted">坏行{s.error}行不写入；改正后请重新生成预览。</span>}
    </div>}
    {batch.status==='confirmed'&&<><h2 className="ruled-title">写入结果</h2><WrittenRows batch={batch}/></>}
  </div>;
}

export default function IntakePanel({collection,template,onConfirmed}:{collection:Collection;template?:Template;onConfirmed:()=>Promise<unknown>}){
  const{user}=authStore.use(),{busy,error,perform}=useTask();
  const[draft,setDraft]=useState(''),[batch,setBatch]=useState<IntakeBatch|null>(null),[history,setHistory]=useState<IntakeBatch[]>([]),[message,setMessage]=useState('');
  const reload=async()=>setHistory(await api.list(collection.id));
  useEffect(()=>{setBatch(null);setDraft('');setMessage('');reload().catch(()=>{})},[collection.id]);
  const preview=()=>perform(async()=>{
    let rows:unknown;
    try{rows=JSON.parse(draft)}catch{throw new Error('修订表须为JSON数组，每行一份裁片')}
    if(!Array.isArray(rows)||!rows.length)throw new Error('修订表须为非空JSON数组');
    setMessage('');setBatch(await api.preview({collection_id:collection.id,rows}));await reload();
  });
  const confirm=()=>perform(async()=>{
    if(!batch)return;
    try{
      const b=await api.confirm(batch.token);setBatch(b);
      if(b.status==='confirmed'){const c=b.result.counts||{};setMessage(`接收完成：新增${c.created||0}、更新${c.updated||0}、未变${c.unchanged||0}、跳过坏行${c.skipped||0}；裁片身份保留，历史研究与已批准说明保持原样。`);await onConfirmed();}
    }catch(e){setBatch(await api.detail(batch.token).catch(()=>batch));throw e}
    finally{await reload()}
  });
  return <div className="run-spread intake-spread">
    <section>
      <h2 className="ruled-title">批量接收修订表</h2>
      {canEdit(user)?<>
        <form onSubmit={e=>{e.preventDefault();preview()}}>
          <label>按{template?.labels.join(' → ')}顺序的修订行JSON数组（每行含 code / name / source_note / labels / points）<textarea value={draft} onChange={e=>setDraft(e.target.value)} rows={10} required placeholder='[{"code":"TL31","name":"纸模裁片 31","source_note":"…","labels":["L1",…],"points":[[x,y],…]}]'/></label>
          <div className="button-row">
            <button className="primary" disabled={busy}>核对并生成预览 →</button>
            <button type="button" disabled={busy} onClick={()=>setDraft(JSON.stringify([{code:'TL31',name:'纸模裁片 31',source_note:collection.source_file,labels:template?.labels||[],points:template?.points||[]}],null,2))}>填入示例行</button>
          </div>
        </form>
        <ErrorNotice error={error}/>
        {message&&<p className="success" role="status">{message}</p>}
        {batch&&<PreviewBlock batch={batch} busy={busy} onConfirm={confirm}/>}
      </>:<p className="muted">观察员只读；批量接收由形状分析员核对与确认。</p>}
      <aside className="margin-note">按编号核对八个角点与标签顺序；仅预览通过的行可写入，坏行改正后重新生成预览。预览后集合、模板或裁片被改动，或容量不足时整批拒绝并提示重验；同一批次重复确认不会重复落库。</aside>
    </section>
    <section>
      <h2 className="ruled-title">接收留档 <small>{history.length}批</small></h2>
      {!history.length&&<div className="empty">尚无接收批次。上游补发修订表时，在左侧粘贴并生成核对预览。</div>}
      {history.map(b=><article className="run-entry" key={b.id}>
        <div className="entry-line"><small>INTAKE {b.id} · {b.token.slice(0,8)}</small><StatusBadge status={b.status}/></div>
        <p>新增{b.summary.new} / 更新{b.summary.update} / 未变{b.summary.unchanged} / 坏行{b.summary.error}，共{b.summary.total}行</p>
        <small>{b.actor} / {date(b.created_at)}{b.confirmed_at?' / 确认于 '+date(b.confirmed_at):''}</small>
        {b.status==='rejected'&&<p className="error-text">{b.result.reason}</p>}
        {b.status==='confirmed'&&b.result.written&&<details className="edit-fold"><summary>核对写入明细（{b.result.written.length}行）</summary><WrittenRows batch={b}/></details>}
      </article>)}
    </section>
  </div>;
}
