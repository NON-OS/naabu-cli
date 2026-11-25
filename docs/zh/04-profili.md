# 配置与被禁标志

🌐 [Italiano](../04-profili.md) · [English](../en/04-profili.md) · **中文**

> ⚠️ 本页为机器翻译草稿，正式发布前需母语者校对。

| 配置 | 作用 | 噪声 | Root |
|---|---|---|---|
| `base` | 最常见的 100 个端口（naabu 默认）。 | 低 | 否 |
| `connect` | 显式的 connect 扫描。 | 低 | 否 |
| `syn` | SYN 扫描。 | 中 | 是 |
| `top1000` | 最常见的 1000 个端口。 | 中 | 否 |
| `web` | Web 服务常见的端口。 | 低 | 否 |
| `completo` | 全部 65535 个端口。 | 高 | 否 |
| `prudente` | 1000 个端口，带频率限制和验证。 | 中 | 否 |
| `lento` | 与 prudente 相同，但更慢。 | 低 | 否 |
| `jsonl` | 1000 个端口，以 JSON 输出。 | 中 | 否 |

`naabu-cli profili` 会打印每个配置的具体标志。

## 各配置的作用

**base** (`-silent`). 最常见的 100 个端口（naabu 默认）。 快速初步查看。使用 connect 扫描，无需 root 权限。

**connect** (`-s c -silent`). 显式的 connect 扫描。 无需特权。会完成握手，因此会留在服务的日志中。

**syn** (`-s s -silent`). SYN 扫描。 更快且对服务更隐蔽。需要 root 权限。

**top1000** (`-top-ports 1000 -silent`). 最常见的 1000 个端口。 覆盖面不错，又无需扫描所有端口。

**web** (`-p 80,443,8080,8443,3000,5000,8000,8888 -silent`). Web 服务常见的端口。 当你只关心哪些端口提供 HTTP 服务时，在进入 httpx 之前使用。

**completo** (`-p - -silent`). 全部 65535 个端口。 在单个主机上使用，当需要不遗漏高位和冷门端口时。在大量主机上开销很大。

**prudente** (`-top-ports 1000 -s c -rate 300 -c 25 -timeout 1000 -retries 1 -verify -silent`). 1000 个端口，带频率限制和验证。 在客户网络上默认使用的配置：低频率、结果经过验证。

**lento** (`-top-ports 1000 -s c -rate 150 -c 10 -timeout 2000 -retries 2 -verify -silent`). 与 prudente 相同，但更慢。 用于脆弱的网络或慢速链路：每秒发送更少的数据包，超时更宽松。

**jsonl** (`-top-ports 1000 -json -silent`). 1000 个端口，以 JSON 输出。 用于使用其他工具处理结果。

## 手动传入标志

`--` 之后写的所有内容都会追加在配置标志之后传给 naabu，前提是不在被禁清单中。比对时不区分大小写，`-flag valore` 和 `-flag=valore` 两种写法都能识别，一个或两个短横线均可。

```sh
naabu-cli lancia prudente 192.0.2.10 --scope scope.toml -- -timeout 5
```

## 被禁标志清单

| 标志 | 原因 |
|---|---|
| `-host`, `-list`, `-l` | 目标来自经过作用域校验的文件 |
| `-o`, `-output` | 输出由 naabu-cli 管理 |
| `-sa`, `-scan-all-ips` | 扫描一个主机名的所有 IP：可能超出作用域 |
| `-nmap-cli` | 对结果执行任意 nmap 命令 |
| `-resume` | 会恢复一次未经过作用域检查的任务 |
| `-passive` | 会把目标地址发送给第三方 Shodan |
| `-nmap` | 对结果执行 nmap，且不再做其他检查 |
| `-up`, `-update` | 程序更新应单独进行，而不是在一次授权任务中进行 |

## 过滤器做不到的事

它不是沙箱。想绕过它并不难，比如直接调用 `naabu`。它的作用是拦住失误和坏习惯，而不是拦住一个已经能访问你终端的恶意人员。如果某项与客户约定好的活动需要用到被禁标志，请直接使用 naabu，并在项目记录中注明这一选择。
