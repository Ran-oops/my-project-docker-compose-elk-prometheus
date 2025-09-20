# Docker Compose ELK + Prometheus 监控平台

一个基于 Docker Compose 的一体化可观测性平台，集成了 ELK Stack（Elasticsearch、Logstash、Filebeat）、Prometheus、Alertmanager、Grafana 和 FastAPI 应用。

## 项目简介

本项目是一个容器化的监控和日志分析解决方案，旨在提供完整的系统可观测性功能。通过集成多种开源工具，实现了日志收集、指标监控、告警通知和数据可视化。

主要组件：
- **FastAPI 应用**：模拟业务服务，产生日志和指标数据
- **ELK Stack**：用于日志收集、处理和存储
- **Prometheus**：用于指标收集和存储
- **Alertmanager**：处理告警通知
- **Grafana**：提供数据可视化界面
- **Nginx**：作为反向代理服务器

## 功能特性

- 实时日志收集与分析（Filebeat → Logstash → Elasticsearch）
- 系统和服务指标监控（Prometheus）
- 可视化仪表板（Grafana）
- 告警机制（Alertmanager）
- 容器化部署，易于扩展和维护
- 结构化日志处理
- 可配置的监控告警规则

## 目录结构

```
.
├── alertmanager         # Alertmanager 配置
├── elk                  # ELK 相关配置
│   ├── elasticsearch    # Elasticsearch 配置
│   ├── filebeat         # Filebeat 配置
│   └── logstash         # Logstash 配置
├── fastapi_app          # FastAPI 应用源码
├── grafana              # Grafana 配置
├── nginx                # Nginx 配置
├── prometheus           # Prometheus 配置
└── docker-compose.yml   # Docker Compose 编排文件
```

## 系统架构

```
┌─────────────────┐    日志     ┌──────────┐    ┌──────────┐    ┌──────────────┐
│   FastAPI应用   ├───────────→│ Filebeat ├────┤ Logstash ├────┤ Elasticsearch│
└─────────────────┘            └──────────┘    └──────────┘    └──────────────┘
       │                              ↓                                │
       │                           ┌────────┐                          │
       ├──────────────────────────→│Kafka(可选)                        │
       │                           └────────┘                          │
       │                              ↓                                │
       │                         ┌────────────┐                       │
       │                         │Kafka Consumer│                      │
       │                         └────────────┘                       │
       │                              ↓                                │
指标   │                        日志处理与分析                         │
       ↓                              ↓                                ↓
┌─────────────┐                 ┌──────────┐                     ┌─────────┐
│ Prometheus  │←────────────────┤ Grafana  │←────────────────────┤Kibana(可选)
└─────────────┘   数据可视化    └──────────┘   数据可视化        └─────────┘
       ↓
┌──────────────┐
│ Alertmanager │
└──────────────┘
```

## 快速开始

### 环境要求

- Docker Engine >= 20.10
- Docker Compose Plugin >= 2.0
- 至少 4GB 可用内存

### 安装与运行

1. 克隆项目到本地：

```bash
git clone <项目地址>
cd my-project-docker-compose-elk-prometheus
```

2. 构建并启动所有服务：

```bash
docker-compose up -d
```

3. 等待服务启动完成（首次启动可能需要几分钟时间下载镜像和初始化）。

### 访问各组件

服务启动后，可以通过以下端口访问各组件：

- **FastAPI 应用**: http://localhost:8000
- **Nginx**: http://localhost/
- **Elasticsearch**: http://localhost:9200
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Grafana**: http://localhost:3000
- **Kibana**: http://localhost:5601 (如果启用)

### 服务说明

#### FastAPI 应用
位于 [fastapi_app](fastapi_app) 目录，包含：
- 主应用 [main.py](fastapi_app/app/main.py)
- 日志配置 [logging_config.py](fastapi_app/app/logging_config.py)
- Kafka 生产者/消费者模块（预留功能）
- 中间件 [middlewares.py](fastapi_app/app/middlewares.py)

#### ELK Stack
- **Filebeat**: 配置文件在 [elk/filebeat/filebeat.yml](elk/filebeat/filebeat.yml)，负责收集 FastAPI 应用日志
- **Logstash**: 配置文件在 [elk/logstash/pipeline/logstash.conf](elk/logstash/pipeline/logstash.conf)，负责处理和转换日志数据
- **Elasticsearch**: 配置文件在 [elk/elasticsearch/config/elasticsearch.yml](elk/elasticsearch/config/elasticsearch.yml)，负责存储日志数据

#### Prometheus 监控
- 配置文件在 [prometheus/prometheus.yml](prometheus/prometheus.yml)
- 告警规则在 [prometheus/alert.rules.yml](prometheus/alert.rules.yml)

#### Alertmanager 告警
- 配置文件在 [alertmanager/alertmanager.yml](alertmanager/alertmanager.yml)

#### Grafana 可视化
- 配置文件在 [grafana/provisioning/](grafana/provisioning/) 目录
- 包含数据源和仪表板预配置

#### Nginx 反向代理
- 配置文件在 [nginx/nginx.conf](nginx/nginx.conf)

## 配置说明

### 自定义配置

1. 修改各组件配置文件以满足特定需求
2. 重新构建并启动服务：

```bash
docker-compose down
docker-compose up -d
```

### 添加监控目标

在 [prometheus/prometheus.yml](prometheus/prometheus.yml) 中添加新的 job 来监控其他服务。

### 自定义告警规则

在 [prometheus/alert.rules.yml](prometheus/alert.rules.yml) 中添加自定义告警规则。

### 配置告警通知

修改 [alertmanager/alertmanager.yml](alertmanager/alertmanager.yml) 来配置告警通知方式，如邮件、Slack、Webhook 等。

## 故障排除

### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f <service_name>
```

### 常见问题

1. **Elasticsearch 启动失败**：
   - 检查系统内存是否充足
   - 在 Linux 系统上可能需要调整 `vm.max_map_count`：
     ```bash
     sysctl -w vm.max_map_count=262144
     ```

2. **服务无法访问**：
   - 检查端口是否被占用
   - 确认服务是否正常启动：`docker-compose ps`

3. **Grafana 数据源连接失败**：
   - 检查 Prometheus 是否正常运行
   - 确认网络连接是否正常

## 扩展功能

### 集成 Kafka

项目中包含 Kafka 生产者和消费者模块，可根据需要启用 Kafka 服务来进行更复杂的消息处理。

### 添加 Kibana

虽然项目中未包含 Kibana，但可以轻松添加：
1. 在 `docker-compose.yml` 中添加 Kibana 服务
2. 配置 Kibana 连接 Elasticsearch

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

## 许可证

请根据实际情况添加许可证信息。

## 更多笔记信息： https://app.yinxiang.com/fx/d3a1bbaf-9703-4273-8736-944a1cf00b00