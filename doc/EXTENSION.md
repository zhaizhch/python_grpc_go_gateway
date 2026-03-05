# 项目扩展开发指南

> [!NOTE]
> **🤖 AI 生成声明**
> 本文档内容由 AI 自动生成并整理。在阅读和使用过程中，请结合实际项目情况进行人工复核。

本项目设计遵循高内聚低耦合原则，通过分层架构简化了新功能的扩展。以下是添加新业务模块的典型流程。

## 1. 定义接口 (Protobuf)

在 `proto/agent/v1/constructionprogress/` 目录下创建或修改 `.proto` 文件。

### 开发规范

- **代码样式指南**：请严格遵循 [Protobuf Style Guide](https://protobuf.dev/programming-guides/style/)。命名应使用 `Snake_Case` (字段名) 和 `PascalCase` (消息名)。
- **接口校验 (PGV)**：本项目集成了 [protoc-gen-validate (PGV)](https://github.com/bufbuild/protoc-gen-validate)。
  - **用途**：通过在 `.proto` 文件中声明约束（如 `(validate.rules).string.min_len = 5`），可以自动生成多语言的参数校验逻辑。
  - **优势**：将参数校验前置到接口定义层，减少业务代码中的重复判断。

### 操作步骤

1. 定义新的 `message`（请求和响应），并添加必要的 PGV 校验规则。
2. 在 `service` 中添加新的 `rpc` 方法。
3. 添加 `google.api.http` 注解以映射到 RESTful 接口。

运行以下命令重新生成代码：
```bash
make pbgen
```

## 2. 数据库模型扩展 (SQLAlchemy)
在 `src/models/` 目录下操作：
1. 创建新的模型类，并继承 `src.models.base.BaseModel`。
2. 定义字段（使用 `Column`）。
3. 如果需要，运行数据库迁移脚本（或由服务自动创建表）。

## 3. 数据访问层实现 (CRUD)
在 `src/crud/` 目录下操作：
1. 让你的 CRUD 类继承 `src.crud.base.CRUDBase`。
2. 利用父类提供的 `get`, `get_multi`, `create`, `update`, `remove` 方法。
3. 如果有复杂的 SQL 逻辑，在子类中单独实现。

## 4. 业务逻辑开发 (Service)
在 `src/services/` 目录下实现 gRPC Servicer：
1. 继承生成的 `*_pb2_grpc.*Servicer` 类。
2. **核心原则**：必须使用 `src.core.database.pgsql.session_scope` 上下文管理器来管理数据库事务。
   ```python
   with session_scope() as session:
       self.crud.create(session, obj_in=data)
   ```

## 5. 网关注册 (Go)

如果新增了全新的 Service（即新的 proto 文件）：

1. 在 `main.go` 中导入新生成的包。
2. 在 `main` 函数中使用 `RegisterXXXXHandler` 注册新的处理器到 `gwMux`。

## 6. API 设计与开发规范

### RESTful 风格参考

在定义接口（特别是 Protobuf 中的 HTTP 映射）时，请遵循以下约定：

| 动作 | URL 示例 | 说明 |
| :--- | :--- | :--- |
| **POST** | `/api/v1/schedules` | 创建资源（非幂等，后端生成 ID） |
| **PUT** | `/api/v1/schedules/{id}` | 创建资源（幂等，前端指定 ID） |
| **GET** | `/api/v1/schedules` | 获取资源列表 |
| **GET** | `/api/v1/schedules/{id}` | 获取资源详情 |
| **PUT** | `/api/v1/schedules/{id}` | 更新资源（全量更新） |
| **PATCH** | `/api/v1/schedules/{id}` | 更新资源（增量更新） |
| **DELETE** | `/api/v1/schedules/{id}` | 删除资源 |

### 认证方式

在 HTTP Header 中添加以下任一方式：

- **Basic Auth**: `Authorization: Basic {用户名:密码的base64编码}`
- **Bearer Token**: `Authorization: Bearer {api_key或者token}`

### 常见状态码

- **200**: 操作成功
- **202**: 异步操作成功（前端需要轮询状态）
- **400**: 请求参数错误
- **401**: 认证错误
- **403**: 权限校验错误
- **404**: 资源未找到 (Not Found)
- **500**: 服务端内部错误

> 更多参考资料：[MDN HTTP Status Codes](https://developer.mozilla.org/zh-CN/docs/Web/HTTP)

## 7. 镜像构建与发布

构建的镜像请推送到 Harbor 的 `ai-solutions` 项目下：

```bash
# 构建镜像
docker build -t hub.bjuci.io/ai-solutions/name:tag .

# 登录 Harbor
docker login hub.bjuci.io

# 推送镜像
docker push hub.bjuci.io/ai-solutions/name:tag
```

## 8. CI/CD 流程

本项目的 CI/CD 定义可参考以下现有配置：

- [GitLab CI 配置参考](https://gitlab.bjuci.com.cn/ai-platform/platform-be/-/blob/main/.gitlab-ci.yml?ref_type=heads)

## 9. 代码规范建议

- **代码风格**：遵循官方 [Protobuf Style Guide](https://protobuf.dev/programming-guides/style/)，保持 API 定义的整洁与一致性。
- **校验先行**：优先使用 [PGV](https://github.com/bufbuild/protoc-gen-validate) 声明参数约束，而不是在 Python 业务逻辑中编写大量 `if` 判断。
- **枚举处理**：Proto 中的枚举与 Python 中的存储尽量保持 ID 对应。
- **时间处理**：内部统一使用 `UTC` 时间，返回给前端时通过 `google.protobuf.Timestamp` 转换。
- **安全性**：敏感配置请通过 `os.getenv()` 获取，不要硬编码在代码中。
