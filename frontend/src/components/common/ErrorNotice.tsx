export default function ErrorNotice({error}:{error:string}){return error?<div className="error-notice" role="alert"><b>请核对后重试</b><span>{error}</span></div>:null}
