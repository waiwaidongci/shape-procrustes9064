# 汀澜纸模裁片形状册

核对8个同源二维角点，去掉平移、正尺度与旋转，保留镜像和形变；把GPA配准及PCA线性模态交回复验讨论。

## 场景与角色

汀澜纸模工艺组有13位形状分析员。上游提供 `TL-DRIFT_8landmarks_mm.csv`：同一类纸模按边界固定L1–L8，每点x/y单位mm。过去分析员在CAD叠图时把摆放、尺寸和形变混在一起，镜像当旋转消掉，又把主轴端点当作可直接制造的工艺变更。本册替代角点核对、配准、形变留档与复验批注的一段，下游是实物裁片和同源角点的独立复测。

| 角色 | 页面 | 权限 | 典型动作 |
|---|---|---|---|
| admin 复验负责人 | 六页全部 | 写入、排队、说明、批准/退回、导出 | 批注角点与制造约束复验 |
| analyst 形状分析员 | 六页全部 | 集合/模板/裁片维护、排队、提出说明、导出已批准说明 | 比较原始轮廓、配准及模态 |
| viewer 纸模观察员 | 六页全部 | 只读与已批准CSV下载，写入/审批403 | 阅读同源口径和分发依据 |

账号：`admin@tinglan.local`、`analyst@tinglan.local`、`viewer@tinglan.local`；共同密码 `Tinglan2026!`。

## 一天的研究剧本

1. 09:00 林澜以analyst打开 `TL-DRIFT 折角展开 · 正常形变集合`，查看30份真实输入的原始摆放叠图，朱砂角点为当前裁片。
2. 09:05 在“角点与基准”核对8×2坐标与L1–L8顺序。集合另有 `TL-MIRROR 镜像混入`、`TL-DEGEN 退化角点`，共90份形状/720个二维点，3个同源模板。
3. 09:15 核对参考朝向，明确不循环换位、不反转顺序、不用镜像配准。模板和原始点由上游负责真实同源，本系统不自动检测对应。
4. 09:20 配置“折角展开 · GPA与模态研究”，请求3模态、容差1e−12，冻结集合/模板/原始点后排队；seed不预置计算结果。
5. 09:22 真实主研究4步收敛，目标0.01445663→0.0139458776747，det(R)≈1；GPA均值范数1，PCA算术均值范数0.9997675687，两均值差0.00023243129。左右画布各自等比例缩放，不以像素比较物理尺寸。
6. 09:25 查看PC1/2/3真实奇异值0.09730803/0.06469489/0.008383326，解释率67.9050%、30.0154%、0.5040%，累计98.4245%。同画布画算术均值及±2sd端点，端点未再单位化。
7. 09:30 选择TL23，保留3模态重建残差0.00403665。写明实物角点复测、镜像方向与制造约束，不能直接把线性模态作为切割图。
8. 10:00 沈汀用admin留批注并同意复验；叶禾用viewer下载 `inspection-note-<id>.csv`，含审批、配准摘要、30份轮廓的原始/对齐/重建坐标、两种均值与模态端点。新点需新建冻结研究，不回写历史结果。

数值来自固定seed输入的真实API/worker计算；镜像集合最大GPA距离约1.03168，仍保留差异。全同形校验有浮点残差约2.08e−15且没有假模态。

## 批量接收

上游补发同一集合的裁片修订表时，在“角点与基准”页的“批量接收”页签粘贴修订行JSON数组（每行code/name/source_note/labels/points）。`POST /intake/preview`按编号核对八个角点与模板标签顺序，预览新增、更新、未变及坏行原因；坏行改正后重新生成预览即可。`POST /intake/{token}/confirm`仅写入通过的行，更新在原地进行、保留裁片ID，坏行跳过不写入。预览以SHA256指纹冻结集合/模板/裁片状态；确认时指纹不符或新增后超过每集合120份容量，整批拒绝并提示重验。同一token重复确认返回首次落库结果，不重复写入。接收只写shape_specimens，既有冻结研究快照与已批准说明保持原样；`GET /intake`按集合列出接收留档供页面核对。

## 启动

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d --build
docker compose ps
docker compose exec -T backend python -m scripts.seed_demo
```

前端 http://localhost:18234，后端文档 http://localhost:19234/docs，PostgreSQL localhost:17734。库/用户shapes；密码见.env.example。/health检查DB SELECT1与Redis ping。

SEED_DEMO=true启动只补齐缺项，失败记日志不阻塞应用。自然键为账号email、模板code、集合code、裁片collection_id+code；重复seed不覆盖人工协议、模板点/标签/说明或裁片点/来源。固定seed20261112；3集合各30份8点。镜像集合有3份反射，退化集合首份零centroid-size导致明确失败，不擅自丢掉坏样本。

## 五服务与环境

| 服务 | 技术/职责 | 健康条件 |
|---|---|---|
| frontend | React18.3.1、TypeScript、Vite6.4.6，Nginx1.27 | HTTP 127.0.0.1 |
| backend | Python3.11、FastAPI、SQLAlchemy2、PyJWT、NumPy | DB SELECT1与Redis ping |
| worker | 同后端镜像，数据库队列扫描/Redis唤醒 | 30秒内心跳文件 |
| db | PostgreSQL16 | pg_isready |
| redis | Redis7 AOF，唤醒与登录限流 | redis-cli ping |

恰好5服务，健康依赖、数据库/Redis/共享artifacts命名卷。坐标/矩阵/结果JSON保留Python双精度；收敛tolerance使用DOUBLE PRECISION。Nginx剥离一次/api/，Python路由不重复添加前缀。

| 环境变量 | 默认与用途 |
|---|---|
| COMPOSE_PROJECT_NAME | shape-procrustes，容器前缀 |
| FRONTEND_PORT/BACKEND_PORT/DB_PORT | 18234/19234/17734 |
| DB_PASSWORD | shapes-demo-local，仅本地示例 |
| JWT_SECRET | 本地示例，部署前更换独立随机键 |
| SEED_DEMO | true，补齐输入seed |
| DATABASE_URL/REDIS_URL | Compose内部地址，本地可覆盖 |
| OMP_NUM_THREADS/OPENBLAS_NUM_THREADS | 1，限制数值线程 |

JWT8小时，PBKDF2-SHA256存密码；角色授权、写入/审批/导出审计、全局错误处理与每IP每分钟30次登录限流。安全422只返loc/msg，不回显NaN/Inf输入。单任务2–120份形状、8点、最多100步、请求1–5模态；全局最多3项活动任务。数据库是任务状态权威，Redis唤醒失败仍扫描；单worker中断按冻结输入重算。

## 数学口径

每份行点矩阵X先减centroid，以centroid-size `sqrt(sum(X_centered²))`标准化为单位形状。尺度计算先缩放再求范数；零尺度、不可表示或二维秩在机器精度内退化的轮廓拒绝。

对当前目标Y，SVD `X.T @ Y = U S Vt`，只取 `R = U diag(1, sign(det(U Vt))) Vt`，行点右乘R。与允许反射的普通orthogonal Procrustes不同，本册det(R)固定+1，不改变同源顺序。

GPA交替：逐份旋转到当前均值→取算术均值→单位化→将均值旋转到参考朝向，同时旋转全部样本。目标为Σ||aligned_i−unit_mean||²，保存初始化及全部迭代原始值。有限精度舍入可引入极小增加，保留roundoff_increase和64eps×N（单位形状相对尺度）误差界，不钳制；超过界失败。均值变化达到有效容差才停止，否则100步失败。主研究目标实际全程下降。

PCA另取所有对齐坐标flatten后的算术均值μ，不把单位GPA均值当μ。对A=flatten(aligned)−μ做SVD；特征值s²/(n−1)、解释率s²/Σs²，端点 `μ ± 2 sqrt(lambda) loading`，逐份保存保留k模态重建和欧氏残差。

有效秩阈值为 `eps * max(A.shape) * ||flatten(aligned)||F`，相对于单位对齐数据的机器精度，不用大绝对方差阈值。保存全部真实奇异值/特征值；未解析出方差时没有PCA轴、得分或±2sd模态，解释率不报告。1e−9的真实微形变在独立oracle中保留。计算定义参考 [NumPy SVD](https://numpy.org/doc/stable/reference/generated/numpy.linalg.svd.html)；[SciPy orthogonal_procrustes](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.orthogonal_procrustes.html)本身允许反射，不能直接替代这里的SO(2)约束。

符号以最大绝对载荷为正固定，只消除符号不确定性。近重复奇异值时模态方向/顺序不唯一，单轴不具物理唯一性；子空间重建和累计解释率更稳。PCA是对齐形状的外在线性描述，端点不强制单位形状、无自交或制造约束，不保证可制造，也不证明工艺成因。

SHA256覆盖算法版本、完整冻结集合/模板/裁片、保留数和容差。按裁片代码规范排序，同输入顺序改变整份结果相同；数据库ID/文字来源变化会改变指纹。结果存数据库和/artifacts/run-<id>.json。对称形状、重复谱方向需按上述不唯一性理解，固定参考并不提供物理因果识别。

## 代码与本地开发

ShapeCollection、Template、ShapeSpecimen、AlignmentRun、InspectionNote、IntakeBatch各有独立model/schema/service/controller/route/API。collectionStore管理集合/基准、specimenStore管理原始点、researchStore管理任务/批注。六页为索引、来源、运行、结果、批注、留痕，登录另计；ShapeCanvas复用于索引/模板/配准/模态，同画布保持等比例。PageHeading/StatusBadge/ErrorNotice等共享，useTask/usePolling与format工具复用。宽表只局部滚动，grid使用minmax(0,1fr)/min-width:0；结果选择按真实加载数据同步。

目录为backend/src/{models,schemas,services,controllers,routes,config,constants,middlewares,utils}，数学services/{geometry,gpa,deformation}.py，seed与初始migrations；frontend/src/{api,stores,types,constants,components/common,hooks,pages,router,utils}。

共享Role/RunStatus/NoteStatus在backend/src/constants/enums.py和frontend/src/constants/enums.ts，角色类型在frontend/src/types/domain.ts；RunStatus用于service/worker，NoteStatus用于schema/service，前端用于账户、状态及页面。

```bash
docker compose up -d db redis
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://shapes:shapes-demo-local@localhost:17734/shapes'
export REDIS_URL='redis://localhost:6379/0'
export SEED_DEMO=true
uvicorn src.main:app --host 0.0.0.0 --port 19234
# backend另一终端，相同环境
python -m src.worker
# frontend另一终端
npm ci
npm run dev -- --port 18234
```

本地worker需可写/artifacts，推荐Compose卷。metadata.create_all只建缺表，初始DDL供审阅，没有生产版本迁移工具。Google Fonts DM Sans/Noto Sans SC/Noto Serif SC，离线回退serif。来源文件名为溯源元数据；没有任意CSV自动导入或自动同源点识别，新增模板可用API，UI核对/修改已有基准。测试/截图/已知差异在独立test-artifacts/gb-0030。收尾docker compose down -v --remove-orphans删除本题数据/结果卷。MIT License。
