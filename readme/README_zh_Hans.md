# AstrBot Midjourney 图片插件

通过您自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成一组 Midjourney 图片。`midjourney_imagine` 提交一次任务，`midjourney_get_task` 用同一个任务 ID 查询最终的四宫格。

[English guide](../README.md) · [Imagine 接口](https://platform.acedata.cloud/documents/midjourney-imagine) · [任务接口](https://platform.acedata.cloud/documents/midjourney-tasks) · [当前价格](https://platform.acedata.cloud/services/midjourney)

## 查找与安装

在 AstrBot WebUI 中打开 **扩展 → 插件 → AstrBot 插件市场**，搜索 **Midjourney**。核对卡片名称 **Midjourney by Ace Data Cloud**、作者 **acedatacloud** 和[当前服务图标](https://cdn.acedata.cloud/wto43b.png)，安装后在**已安装**页检查加载状态。

官方 AstrBot Cloud 上架仍待完成。源码合并后，可通过**已安装 → 安装 (+) → 从 URL 安装**并填写 `https://github.com/AceDataCloud/MidjourneyAstrBot` 预览。通过 URL 安装不代表已在官方市场上架。

## 配置密钥

在 [Ace Data Cloud 应用管理](https://platform.acedata.cloud/console/applications)复制生成 API Key，或创建同时允许 `/midjourney/imagine` 与 `/midjourney/tasks` 的 Key。先确认账号具有 Midjourney 访问权限，再核对当前价格和余额。将 Key 填入插件的 **Ace Data Cloud generation API key with Midjourney access** 配置项，不要添加 `Bearer `，也不要使用 `platform-...` 管理令牌。AstrBot WebUI 会遮蔽显示此字段，但原值保存在数据目录中，请保护该目录。

选择支持工具调用的对话模型，并在当前对话的 profile 与 persona 中允许两个 Midjourney 工具。

## 生成一次，然后查询

可以对机器人说：

> 用 `midjourney_imagine` 生成纯蓝背景上的黄色纸船，版本 `8.1`。只提交一次并告诉我任务 ID。

工具以 fast 模式和标准分辨率异步提交一次 `POST /midjourney/imagine` 请求，返回 `status: submitted` 和任务 ID。这时还不能认为四宫格已经完成。保存 ID，随后说：

> 用 `midjourney_get_task` 查询准确的任务 ID `<task_id>`，告诉我状态与最终四宫格图片链接，不要重新生成。

如果仍是 pending，稍后继续查询同一个 ID。只有 `status: succeeded`、`success: true` 和最终 HTTPS 四宫格链接同时出现才算完成。插件不会自动重试付费提交。

首版支持公开版本 `8.1`、`8`、`7`、`6.1`、`6` 和 `5.2`，默认 `8.1`、fast、非 HD。请通过 `version` 参数选择模型；插件会拒绝 `--v`、`--q`、`--sref` 等改变模型或计费的行内标记。启用 `split_images: true` 后，若接口提供分图链接，也会返回。放大、变体、编辑、融合、视频及其他影响计费的控制尚未覆盖。实际价格取决于选择的版本和选项。

## 核验与排查

在 Ace Data Cloud 用量记录中优先按返回的 trace ID 核对。任务结果可能包含以 Credits 计的公开 `cost` 字段；以实时用量记录为扣费依据。任务查询只读取已有任务，不会再次生成。

| 现象 | 检查 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**加载失败的插件**和**数据与日志 → 日志**。 |
| 看不到工具 | 插件启用、当前 profile 与 persona 允许两个工具、对话模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 API 路径的权限和账号访问权限。 |
| 提交后网络报错 | 再次生成前先看请求历史；超时也可能已创建付费任务。 |
| 任务仍在进行 | 稍后查询同一个任务 ID。 |
| 任务失败 | 用任务 ID 或 trace ID 查请求历史。 |

Key 只会发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件只把最终图片链接和公开费用字段交给对话模型，不返回内部原始数据。运行时仅用 Python 标准库。

## 验收与品牌图标

在官方 AstrBot `v4.28.2` 的隔离实例中，editable 安装成功注册两个工具。ChatUI 用 V8.1 fast 标准档提交了一次四宫格任务，并通过 `midjourney_get_task` 查询同一个 ID 两次：首次 pending，第二次成功，没有重复生成。最终 PNG 返回 HTTP 200、`image/png`，尺寸 1024×1024。准确 trace ID 对应一条成功的 `/midjourney/imagine` 用量记录，原价和实扣均为 0.216 Credits。见[脱敏实测证据](../tests/e2e-results.json)。其他版本和分图输出仅做结构校验，未实际生成。这只是本地 editable 安装；Cloud 审核、市场安装以及市场包的首次调用仍待完成。

`logo.png` 是[当前 Midjourney 服务图标](https://cdn.acedata.cloud/wto43b.png)的原文件，256×256，SHA-256 为 `6fe0ba60d32bd4f6da7ead89c0a3d8d318261ad08e02a619bd87a91d2218cb92`。
