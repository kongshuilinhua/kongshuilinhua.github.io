---
title: redis高级
date: 2026-01-20 15:26:53
tags:
---

# 分布式缓存

## 1.redis持久化

Redis 持久化策略主要有两种：**RDB (Redis Database)** 和 **AOF (Append Only File)**。通常情况下，**两种策略会结合使用**，以达到数据持久化和高可用性的最佳平衡。

### 1.1 RDB (Redis Database)

- **是什么**：RDB 是一种**快照**机制。它会定期将当前时刻的数据库数据完整地保存到磁盘的一个二进制文件中（默认为 `dump.rdb`）。
- **原理**：
  1.  Redis 主进程调用 `fork()` 系统调用，创建一个子进程。
  2.  子进程独立地读取内存中的所有数据，将其写入一个临时的 RDB 文件。
  3.  当子进程完成写入后，会原子地将临时文件重命名为最终的 RDB 文件（覆盖旧的）。
  4.  在这个过程中，主进程可以继续提供服务，只有在 `fork()` 的那一瞬间会有短暂的阻塞。
- **优点**：
  - **文件紧凑**：RDB 文件是一个压缩的二进制文件，非常小巧。
  - **恢复速度快**：加载 RDB 文件恢复数据速度很快。
  - **适合备份**：适合进行冷备份。
- **缺点**：
  - **数据丢失风险**：RDB 是**周期性**的快照，如果在两次快照之间发生宕机，期间的修改会丢失。
  - **fork 开销**：在内存数据量巨大时，fork 操作可能会阻塞主进程一段时间。
- **如何配置**：
  在 `redis.conf` 配置文件中：
  - `save <seconds> <changes>`：设置自动保存的规则。例如 `save 900 1` 表示如果 900 秒内有至少 1 个 key 被修改，则执行 `bgsave`。可以设置多条规则。
  - `dbfilename dump.rdb`：RDB 文件的名字。
  - `dir ./`：RDB 文件保存的路径。
  - `stop-writes-on-bgsave-error yes`：如果后台保存失败，是否停止主进程写入。

### 1.2 AOF (Append Only File)

- **是什么**：AOF 记录的是 Redis **服务器接收到的所有写命令**。
- **原理**：
  1.  Redis 主进程将所有写操作（如 `SET`, `DEL`, `INCR` 等）以**追加**的方式写入一个日志文件。
  2.  当 Redis 重启时，会重新执行 AOF 文件中的命令来恢复数据。
- **优点**：
  - **数据持久性高**：AOF 可以设置不同的 `appendfsync` 策略，比如 `everysec`（每秒fsync一次）可以做到最多丢失 1 秒的数据。`always`（每次写都fsync）虽然最安全但性能损失较大。
  - **数据不丢失**：相比 RDB，AOF 更能保证数据的完整性。
- **缺点**：
  - **文件体积大**：AOF 文件记录的是命令，所以体积通常比 RDB 大。
  - **恢复速度慢**：恢复时需要逐条执行命令，对大数据量恢复较慢。
  - **AOF 重写 (Rewrite)**：为了解决 AOF 文件体积过大的问题，Redis 会有 AOF 重写机制，将当前内存状态“重写”到一个新的、更小的 AOF 文件。

- **如何配置**：
  在 `redis.conf` 配置文件中：
  - `appendonly yes`：开启 AOF 功能。
  - `appendfilename "appendonly.aof"`：AOF 文件的名字。
  - `appendfsync everysec`：设置 fsync 策略。可选值有 `no`, `everysec`, `always`。`everysec` 是推荐的折中选项。
  - `no-appendfsync-on-rewrite yes`：重写 AOF 时是否跳过 fsync（提高重写速度）。

### 1.3 怎么选择？

- **RDB 仅用于备份**：如果你只关心冷备份，定期存档，RDB 就够了。
- **AOF 仅用于持久化**：如果你非常看重数据不丢失，需要尽可能多的保存写入操作，并且不介意 AOF 文件体积大和恢复慢，可以用 AOF。
- **RDB + AOF (推荐)**：
  - **RDB** 负责**快速的冷备份**，适合快速启动和恢复。
  - **AOF** 负责**持续的持久化**，防止数据丢失。
  - 在 Redis 重启时，会先加载 RDB，然后加载 AOF，这样能同时满足速度和安全性的要求。

**生产环境中，通常推荐 RDB + AOF 结合使用。**

- RDB 备份：例如每小时或每天一个快照。
- AOF：`appendfsync everysec`。

这样可以结合两者的优点，既保证了高可用（通过 RDB 快速启动），又最大限度地减少了数据丢失（AOF `everysec` 策略）。

## 2. Redis 主从复制

主从复制（Replication）是 Redis 分布式的基础，它允许将一个 Redis 服务器（Master）的数据复制到多个 Redis 服务器（Slave）。通过主从架构，可以实现**读写分离**，提高系统的并发能力和数据冗余。

### 2.1 主从架构与作用

- **架构**：通常是一个 Master 节点负责处理**写请求**（以及读请求），多个 Slave 节点负责处理**读请求**。Slave 节点的数据是 Master 节点的副本。
- **作用**：
  - **读写分离**：Master 写，Slave 读，分担 Master 压力，提高并发读取能力。
  - **数据冗余**：Slave 是 Master 的热备，Master 宕机时，数据依然存在于 Slave 中。
  - **故障恢复**：虽然主从本身不具备自动故障转移能力（需要配合哨兵），但它是高可用的基础。

  ![alt text](/img/image-21.png)

### 2.2 数据同步原理

Redis 主从同步主要分为**全量同步**和**增量同步**两个阶段。

#### 2.2.1 全量同步 (Full Synchronization)

- **触发时机**：
  - Slave 节点**第一次**连接 Master 节点时。
  - Slave 节点断开连接时间过长，导致 Master 的 `repl_backlog`（复制积压缓冲区）中的数据被覆盖，无法进行增量同步时。
- **流程**：
  1.  **建立连接**：Slave 发送 `PSYNC` 命令给 Master，携带自己的 Replication ID 和 Offset（第一次为 -1）。
  2.  **判断同步方式**：Master 判断 Slave 传来的 ID 与自己不一致（或是新节点），决定执行全量同步。
  3.  **生成快照**：Master 执行 `bgsave`，生成 RDB 文件。
  4.  **发送数据**：Master 将生成的 RDB 文件发送给 Slave。
  5.  **加载数据**：Slave 清空本地数据，加载接收到的 RDB 文件。
  6.  **同步缓存命令**：在生成和传输 RDB 期间，Master 接收到的新写命令会存入 `repl_backlog`，最后 Master 将这些增量命令发送给 Slave 执行，保证数据一致。

![alt text](/img/image-22.png)

#### 2.2.2 增量同步 (Partial Synchronization)

- **触发时机**：
  - Slave 节点短暂断开连接后重连。
  - Master 的 `repl_backlog` 中依然保存着 Slave 断开期间的数据。
- **流程**：
  1.  **请求同步**：Slave 重连后发送 `PSYNC` 命令，携带自己的 Replication ID 和 Offset。
  2.  **检查偏移量**：Master 检查 Slave 的 Offset 是否在自己的 `repl_backlog` 范围内。
  3.  **发送增量**：如果 Offset 在范围内，Master 直接将 `repl_backlog` 中从 Offset 开始的后续命令发送给 Slave。
  4.  **执行命令**：Slave 执行接收到的命令，追平数据。

### 2.3 `repl_backlog` 原理

- **是什么**：Master 节点维护的一个**固定大小的环形数组**（缓冲区）。
- **作用**：
  - 存储最近接收到的写命令。
  - 记录 Master 当前的 Offset。
  - 用来判断 Slave 是否可以进行增量同步。
- **环形机制**：因为是环形数组，写满后会覆盖最早的数据。如果 Slave 断开太久，它需要的 Offset 已经被覆盖了，就必须触发全量同步。
  ![alt text](/img/image-23.png)

### 2.4 主从同步优化

为了保证主从集群的稳定性和性能，通常采取以下优化措施：

- **无磁盘复制**：在 `redis.conf` 中配置 `repl-diskless-sync yes`。Master 生成 RDB 后不写入磁盘，而是直接通过网络发送给 Slave，减少磁盘 IO。
- **控制内存大小**：限制 Redis 单节点内存（例如 10GB 以内），减少 RDB 生成和传输的时间，降低全量同步的成本。
- **增大 backlog**：适当调大 `repl-backlog-size`，尽量避免因为网络短暂抖动导致的 Offset 被覆盖，从而引发不必要的全量同步。
- **链式结构**：如果 Slave 太多，Master 同步压力会很大。可以采用 **Master -> Slave -> Slave** 的链式结构，让部分 Slave 从其他 Slave 同步数据，分担 Master 压力。

主从从架构：
![alt text](/img/image-24.png)

## 3. Redis 哨兵 (Sentinel)

Redis 哨兵（Sentinel）机制用于实现主从集群的**高可用**和**自动故障恢复**。

### 3.1 哨兵作用

- **监控 (Monitoring)**：Sentinel 会不断检查 master 和 slave 是否按预期工作。
- **自动故障恢复 (Automatic Failover)**：如果 master 故障，Sentinel 会将一个 slave 提升为 master。当故障实例恢复后，也会作为 slave 加入集群。
- **通知 (Notification)**：Sentinel 充当 Redis 客户端的服务发现来源，当集群发生故障转移时，会将最新信息推送给 Redis 客户端。

![alt text](/img/image-25.png)

### 3.2 监控原理

Sentinel 基于**心跳机制**监测服务状态，每隔 1 秒向集群的每个实例发送 `ping` 命令：

- **主观下线 (Subjective Down)**：如果某 sentinel 节点发现某实例未在规定时间响应，则认为该实例**主观下线**。
- **客观下线 (Objective Down)**：若超过指定数量（quorum）的 sentinel 都认为该实例主观下线，则该实例**客观下线**。quorum 值最好超过 Sentinel 实例数量的一半。

![alt text](/img/image-26.png)

### 3.3 故障恢复原理

#### 3.3.1 选主规则

一旦发现 master 故障，Sentinel 需要在 slave 中选择一个作为新的 master，选择依据如下（按顺序）：

1.  **断开时间**：排除与 master 断开时间超过指定值 (`down-after-milliseconds * 10`) 的 slave。
2.  **优先级**：判断 `slave-priority` 值，越小优先级越高（0 表示不参与选举）。
3.  **offset**：判断 `offset` 值，越大说明数据越新，优先级越高。
4.  **运行 ID**：判断运行 ID 大小，越小优先级越高。

#### 3.3.2 切换流程

1.  Sentinel 给选中的 slave 发送 `slaveof no one` 命令，让其成为 master。
2.  Sentinel 给所有其他 slave 发送 `slaveof <new_master_ip> <new_master_port>` 命令，让它们成为新 master 的从节点。
3.  Sentinel 将故障节点标记为 slave，当故障节点恢复后，会自动成为新 master 的 slave。

![alt text](/img/image-27.png)

### 3.4 RedisTemplate 集成

Spring Data Redis 提供了对 Sentinel 的支持，通过配置即可实现自动感知主从切换。

- **引入依赖**：`spring-boot-starter-data-redis`
- **配置地址**：在 `application.yml` 中配置 `spring.redis.sentinel.master` 和 `nodes`。
- **读写分离**：通过 `LettuceClientConfigurationBuilderCustomizer` 配置读写策略（如 `REPLICA_PREFERRED`）。

## 4. Redis 分片集群

分片集群（Cluster）用于解决**海量数据存储**和**高并发写**的问题。

![alt text](/img/image-28.png)

### 4.1 集群特征

- 集群中有多个 master，每个 master 保存不同数据。
- 每个 master 都可以有多个 slave 节点。
- master 之间通过 `ping` 监测彼此健康状态。
- 客户端请求可以访问集群任意节点，最终都会被转发到正确节点。

### 4.2 散列插槽 (Hash Slot)

Redis Cluster 使用散列插槽来管理数据分布，集群共有 **16384** 个插槽。

- **映射原理**：Redis 根据 key 的有效部分计算哈希值，对 16384 取余，余数即为插槽值。
  - **有效部分**：如果 key 包含 `{}`，则 `{}` 内部为有效部分；否则整个 key 为有效部分。
  - **目的**：可以将同一类数据（如 `{user:1}:name` 和 `{user:1}:age`）固定保存在同一个 Redis 实例。
- **节点分配**：每个 master 节点负责维护一部分插槽，数据根据插槽值存储到对应的 master。

### 4.3 集群伸缩

Redis 提供了 `redis-cli --cluster` 命令来管理集群，包括添加节点和重新分配插槽。

- **添加节点**：使用 `add-node` 命令将新节点加入集群（默认为 master，但无插槽）。
- **转移插槽**：使用 `reshard` 命令将部分插槽从旧节点转移到新节点，实现数据迁移和负载均衡。

### 4.4 故障转移

- **自动故障转移**：当 master 宕机，其对应的 slave 会自动提升为 master。原 master 恢复后变为 slave。
- **手动故障转移**：使用 `cluster failover` 命令，可以人为地让 slave 升级为 master，常用于维护或升级场景，实现无感知的数据迁移。

### 4.5 RedisTemplate 集成

Spring Data Redis 同样支持分片集群。

在项目的pom文件中引入依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

配置Redis地址，然后在配置文件application.yml中指定redis的sentinel相关信息：

```java
spring:
  redis:
    sentinel:
      master: mymaster
      nodes:
        - 192.168.150.101:27001
        - 192.168.150.101:27002
        - 192.168.150.101:27003
```

配置读写分离，在项目的启动类中，添加一个新的bean：

```java
@Bean
public LettuceClientConfigurationBuilderCustomizer clientConfigurationBuilderCustomizer(){
    return clientConfigurationBuilder -> clientConfigurationBuilder.readFrom(ReadFrom.REPLICA_PREFERRED);
}
```

这个bean中配置的就是读写策略，包括四种：

- MASTER：从主节点读取
- MASTER_PREFERRED：优先从master节点读取，master不可用才读取replica
- REPLICA：从slave（replica）节点读取
- REPLICA \_PREFERRED：优先从slave（replica）节点读取，所有的slave都不可用才读取master
