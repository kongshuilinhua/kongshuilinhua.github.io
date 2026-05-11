---
title: Redis
date: 2025-03-19 14:21:16
tags: redis, database, caching
categories: database
---

# 1.Redis 入门

## 1.1 Redis 配置

### 1.1.1 常用配置项说明

```yaml
# 允许访问的地址，默认是 127.0.0.1，会导致只能在本地访问。修改为 0.0.0.0 则可以在任意 IP 访问，生产环境不要设置为 0.0.0.0
bind 0.0.0.0
# 守护进程，修改为 yes 后即可后台运行
daemonize yes
# 密码，设置后访问 Redis 必须输入密码
requirepass 123321
# 监听的端口
port 6379
# 工作目录，默认是当前目录，也就是运行redis-server时的命令，日志、持久化等文件会保存在这个目录
dir .
# 数据库数量，设置为1，代表只使用1个库，默认有16个库，编号0~15
databases 1
# 设置redis能够使用的最大内存
maxmemory 512mb
# 日志文件，默认为空，不记录日志，可以指定日志文件名
logfile "redis.log"
```

### 1.1.2 开机自启动 Redis 服务

首先，新建一个系统服务文件：

```
vi /etc/systemd/system/redis.service
```

内容如下：

```
[Unit]
Description=redis-server
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/redis-server /usr/local/src/redis-6.2.6/redis.conf
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

然后重载系统服务：

```
systemctl daemon-reload
```

现在，我们可以用下面这组命令来操作 redis 了：

```yaml
# 启动
systemctl start redis
# 停止
systemctl stop redis
# 重启
systemctl restart redis
# 查看状态
systemctl status redis
# 设置开机自启动
systemctl enable redis
```

# 2 Redis 常用命令

## 2.1 通用命令

```yaml
- KEYS：查看符合模板的所有key
- DEL：删除一个指定的key
- EXISTS：判断key是否存在
- EXPIRE：给一个key设置有效期，有效期到期时该key会被自动删除
- TTL：查看一个KEY的剩余有效期
```

## 2.2 String 命令

String 类型，也就是字符串类型，是 Redis 中最简单的存储类型。

其 value 是字符串，不过根据字符串的格式不同，又可以分为 3 类：

- string：普通字符串
- int：整数类型，可以做自增、自减操作
- float：浮点类型，可以做自增、自减操作

不管是哪种格式，底层都是字节数组形式存储，只不过是编码方式不同。字符串类型的最大空间不能超过 512m.

### 2.2.1 String 常用命令

```bash
String的常见命令有：

- SET：添加或者修改已经存在的一个String类型的键值对
- GET：根据key获取String类型的value
- MSET：批量添加多个String类型的键值对  (mset k1 v1 k2 v2 ...)
- MGET：根据多个key获取多个String类型的value (mget k1 k2 k3 ...)
- INCR：让一个整型的key自增1
- INCRBY:让一个整型的key自增并指定步长，例如：incrby num 2 让num值自增2
- INCRBYFLOAT：让一个浮点类型的数字自增并指定步长
- SETNX：添加一个String类型的键值对，前提是这个key不存在，否则不执行(set + nx)
- SETEX：添加一个String类型的键值对，并且指定有效期 (set + expire)
```

### 2.2.2 Key 结构

Redis 没有类似 MySQL 中的 Table 的概念，我们该如何区分不同类型的 key 呢？

我们可以通过给 key 添加前缀加以区分，不过这个前缀不是随便加的，有一定的规范：

Redis 的 key 允许有多个单词形成层级结构，多个单词之间用':'隔开，格式如下：

```
	项目名:业务名:类型:id
```

如果 Value 是一个 Java 对象，例如一个 User 对象，则可以将对象序列化为 JSON 字符串后存储：

| **KEY**         | **VALUE**                                  |
| --------------- | ------------------------------------------ |
| heima:user:1    | {"id":1, "name": "Jack", "age": 21}        |
| heima:product:1 | {"id":1, "name": "小米 11", "price": 4999} |

## 2.3 Hash 命令

Hash 类型，也叫散列，其 value 是一个无序字典，类似于 Java 中的 HashMap 结构。

String 结构是将对象序列化为 JSON 字符串后存储，当需要修改对象某个字段时很不方便,Hash 结构可以将对象中的每个字段独立存储，可以针对单个字段做 CRUD。
![alt text](/img/image-2.png)

常见命令有

```
- HSET key field value：添加或者修改hash类型key的field的值

- HGET key field：获取一个hash类型key的field的值

- HMSET：批量添加多个hash类型key的field的值

- HMGET：批量获取多个hash类型key的field的值

- HGETALL：获取一个hash类型的key中的所有的field和value
- HKEYS：获取一个hash类型的key中的所有的field
- HINCRBY:让一个hash类型key的字段值自增并指定步长
- HSETNX：添加一个hash类型的key的field值，前提是这个field不存在，否则不执行
```

## 2.4 List 命令

Redis 中的 List 类型与 Java 中的 LinkedList 类似，可以看做是一个双向链表结构。既可以支持正向检索和也可以支持反向检索。

特征也与 LinkedList 类似：

- 有序
- 元素可以重复
- 插入和删除快
- 查询速度一般

常用来存储一个有序数据，例如：朋友圈点赞列表，评论列表等。

List 的常见命令有：

- LPUSH key element ... ：向列表左侧插入一个或多个元素（lpush users 1 2 3,得到 3 2 1）
- LPOP key：移除并返回列表左侧的第一个元素，没有则返回 nil
- RPUSH key element ... ：向列表右侧插入一个或多个元素
- RPOP key：移除并返回列表右侧的第一个元素
- LRANGE key star end：返回一段角标范围内的所有元素（0 index）
- BLPOP 和 BRPOP：与 LPOP 和 RPOP 类似，只不过在没有元素时等待指定时间，而不是直接返回 nil（阻塞）

模拟栈（出入口在同一边）
模拟队列（出入口在两边）

## 2.5 Set 命令

Redis 的 Set 结构与 Java 中的 HashSet 类似，可以看做是一个 value 为 null 的 HashMap。因为也是一个 hash 表，因此具备与 HashSet 类似的特征：

- 无序

- 元素不可重复

- 查找快

- 支持交集、并集、差集等功能

Set 的常见命令有：

- SADD key member ... ：向 set 中添加一个或多个元素
- SREM key member ... : 移除 set 中的指定元素
- SCARD key： 返回 set 中元素的个数
- SISMEMBER key member：判断一个元素是否存在于 set 中
- SMEMBERS：获取 set 中的所有元素
- SINTER key1 key2 ... ：求 key1 与 key2 的交集
- SDIFF key1 key2 ... ：求 key1 与 key2 的差集
- SUNION key1 key2 ... ：求 key1 与 key2 的并集

## 2.6 Sorted Set 命令

Redis 的 SortedSet 是一个可排序的 set 集合，与 Java 中的 TreeSet 有些类似，但底层数据结构却差别很大。SortedSet 中的每一个元素都带有一个 score 属性，可以基于 score 属性对元素排序，底层的实现是一个跳表（SkipList）加 hash 表。

SortedSet 具备下列特性：

- 可排序
- 元素不重复
- 查询速度快

因为 SortedSet 的可排序特性，经常被用来实现排行榜这样的功能。

SortedSet 的常见命令有：

- ZADD key score member：添加一个或多个元素到 sorted set ，如果已经存在则更新其 score 值 (zadd stus 85 Jack 89 Lucy 82 Rose 95 Tom 78 Jerry 92 Amy 76 Miles
  )
- ZREM key member：删除 sorted set 中的一个指定元素
- ZSCORE key member : 获取 sorted set 中的指定元素的 score 值
- ZRANK key member：获取 sorted set 中的指定元素的排名(0-index)
- ZCARD key：获取 sorted set 中的元素个数
- ZCOUNT key min max：统计 score 值在给定范围内的所有元素的个数
- ZINCRBY key increment member：让 sorted set 中的指定元素自增，步长为指定的 increment 值
- ZRANGE key min max：按照 score 排序后，获取指定排名范围内的元素
- ZRANGEBYSCORE key min max：按照 score 排序后，获取指定 score 范围内的元素
- ZDIFF、ZINTER、ZUNION：求差集、交集、并集

注意：所有的排名默认都是升序，如果要降序则在命令的 Z 后面添加 REV 即可，例如：

- **升序**获取 sorted set 中的指定元素的排名：ZRANK key member

- **降序**获取 sorted set 中的指定元素的排名：ZREVRANK key memeber

# 3. Redis 的 Java 客户端使用

## 3.1 Jedis 引入依赖

```xml
<!--jedis-->
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>3.7.0</version>
</dependency>
```

Jedis 本身是线程不安全的，并且频繁的创建和销毁连接会有性能损耗，因此我们推荐大家使用 Jedis 连接池代替 Jedis 的直连方式。

```java
package com.heima.jedis.util;

import redis.clients.jedis.*;

public class JedisConnectionFactory {

    private static JedisPool jedisPool;

    static {
        // 配置连接池
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(8);
        poolConfig.setMaxIdle(8);
        poolConfig.setMinIdle(0);
        poolConfig.setMaxWaitMillis(1000);
        // 创建连接池对象，参数：连接池配置、服务端ip、服务端端口、超时时间、密码
        jedisPool = new JedisPool(poolConfig, "192.168.30.128", 6379, 1000);
    }

    public static Jedis getJedis(){
        return jedisPool.getResource();
    }
}
```

## 3.2 SpringDataRedis 客户端

SpringData 是 Spring 中数据操作的模块，包含对各种数据库的集成，其中对 Redis 的集成模块就叫做 SpringDataRedis

- 提供了对不同 Redis 客户端的整合（Lettuce 和 Jedis）
- 提供了 RedisTemplate 统一 API 来操作 Redis
- 支持 Redis 的发布订阅模型
- 支持 Redis 哨兵和 Redis 集群
- 支持基于 Lettuce 的响应式编程
- 支持基于 JDK、JSON、字符串、Spring 对象的数据序列化及反序列化
- 支持基于 Redis 的 JDKCollection 实现
  SpringDataRedis 中提供了 RedisTemplate 工具类，其中封装了各种对 Redis 的操作。并且将不同数据类型的操作 API 封装到了不同的类型中：
  ![alt text](/img/image-3.png)

### 3.2.1 引入依赖

springboot 勾选 nosql 选项会自动引入 spring-data-redis 依赖，如果是普通的 spring 项目，则需要手动引入如下依赖：

```xml
<!--redis依赖-->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-redis</artifactId>
    </dependency>
    <!--common-pool-->
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-pool2</artifactId>
    </dependency>
```

### 3.2.2 序列化

RedisTemplate 可以接收任意 Object 作为值写入 Redis，只不过写入前会把 Object 序列化为字节形式，默认是采用 JDK 序列化，得到的值也是字节数组形式。可读性较差，占用空间较大。

自定义序列化器

```java
@Configuration
public class RedisConfig {

    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory){
        // 创建RedisTemplate对象
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        // 设置连接工厂
        template.setConnectionFactory(connectionFactory);
        // 创建JSON序列化工具
        GenericJackson2JsonRedisSerializer jsonRedisSerializer =
            							new GenericJackson2JsonRedisSerializer();
        // 设置Key的序列化
        template.setKeySerializer(RedisSerializer.string());
        template.setHashKeySerializer(RedisSerializer.string());
        // 设置Value的序列化
        template.setValueSerializer(jsonRedisSerializer);
        template.setHashValueSerializer(jsonRedisSerializer);
        // 返回
        return template;
    }
}
```

需要引入 Jackson 依赖

```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

整体可读性有了很大提升，并且能将 Java 对象自动的序列化为 JSON 字符串，并且查询时能自动把 JSON 反序列化为 Java 对象。不过，其中记录了序列化时对应的 class 名称，目的是为了查询时实现自动反序列化。这会带来额外的内存开销。

### 3.2.3 StringRedisTemplate

为了节省内存空间，我们可以不使用 JSON 序列化器来处理 value，而是统一使用 String 序列化器，要求只能存储 String 类型的 key 和 value。当需要存储 Java 对象时，手动完成对象的序列化和反序列化。

因为存入和读取时的序列化及反序列化都是我们自己实现的，SpringDataRedis 就不会将 class 信息写入 Redis 了。
这种用法比较普遍，因此 SpringDataRedis 就提供了 RedisTemplate 的子类：StringRedisTemplate，它的 key 和 value 的序列化方式默认就是 String 方式。

```java
@Autowired
private StringRedisTemplate stringRedisTemplate;
// JSON序列化工具
private static final ObjectMapper mapper = new ObjectMapper();

@Test
void testSaveUser() throws JsonProcessingException {
    // 创建对象
    User user = new User("虎哥", 21);
    // 手动序列化
    String json = mapper.writeValueAsString(user);
    // 写入数据
    stringRedisTemplate.opsForValue().set("user:200", json);

    // 获取数据
    String jsonUser = stringRedisTemplate.opsForValue().get("user:200");
    // 手动反序列化
    User user1 = mapper.readValue(jsonUser, User.class);
    System.out.println("user1 = " + user1);
}

```

# 4. 短信登录

pass

# 5.缓存

## 5.1 缓存穿透问题的解决思路

缓存穿透 ：缓存穿透是指客户端请求的数据在缓存中和数据库中都不存在，这样缓存永远不会生效，这些请求都会打到数据库。

常见的解决方案有两种：

- 缓存空对象
  - 优点：实现简单，维护方便
  - 缺点：
    - 额外的内存消耗
    - 可能造成短期的不一致
- 布隆过滤
  - 优点：内存占用较少，没有多余 key
  - 缺点：
    - 实现复杂
    - 存在误判可能

**缓存空对象思路分析：**当我们客户端访问不存在的数据时，先请求 redis，但是此时 redis 中没有数据，此时会访问到数据库，但是数据库中也没有数据，这个数据穿透了缓存，直击数据库，我们都知道数据库能够承载的并发不如 redis 这么高，如果大量的请求同时过来访问这种不存在的数据，这些请求就都会访问到数据库，简单的解决方案就是哪怕这个数据在数据库中也不存在，我们也把这个数据存入到 redis 中去，这样，下次用户过来访问这个不存在的数据，那么在 redis 中也能找到这个数据就不会进入到缓存了

**布隆过滤：**布隆过滤器其实采用的是哈希思想来解决这个问题，通过一个庞大的二进制数组，走哈希思想去判断当前这个要查询的这个数据是否存在，如果布隆过滤器判断存在，则放行，这个请求会去访问 redis，哪怕此时 redis 中的数据过期了，但是数据库中一定存在这个数据，在数据库中查询出来这个数据后，再将其放入到 redis 中，

假设布隆过滤器判断这个数据不存在，则直接返回

这种方式优点在于节约内存空间，存在误判，误判原因在于：布隆过滤器走的是哈希思想，只要哈希思想，就可能存在哈希冲突
![alt text](/img/image-4.png)

**小总结：**

缓存穿透产生的原因是什么？

- 用户请求的数据在缓存中和数据库中都不存在，不断发起这样的请求，给数据库带来巨大压力

缓存穿透的解决方案有哪些？

- 缓存 null 值
- 布隆过滤
- 增强 id 的复杂度，避免被猜测 id 规律
- 做好数据的基础格式校验
- 加强用户权限校验
- 做好热点参数的限流

## 5.2 缓存雪崩问题的解决思路

缓存雪崩是指在同一时段大量的缓存 key 同时失效或者 Redis 服务宕机，导致大量请求到达数据库，带来巨大压力。

解决方案：

- 给不同的 Key 的 TTL 添加随机值
- 利用 Redis 集群提高服务的可用性
- 给缓存业务添加降级限流策略
- 给业务添加多级缓存
  ![alt text](/img/image-5.png)

## 5.3 缓存击穿问题及解决思路

缓存击穿问题也叫热点 Key 问题，就是一个被高并发访问并且缓存重建业务较复杂的 key 突然失效了，无数的请求访问会在瞬间给数据库带来巨大的冲击。

常见的解决方案有两种：

- 互斥锁
- 逻辑过期

逻辑分析：假设线程 1 在查询缓存之后，本来应该去查询数据库，然后把这个数据重新加载到缓存的，此时只要线程 1 走完这个逻辑，其他线程就都能从缓存中加载这些数据了，但是假设在线程 1 没有走完的时候，后续的线程 2，线程 3，线程 4 同时过来访问当前这个方法， 那么这些线程都不能从缓存中查询到数据，那么他们就会同一时刻来访问查询缓存，都没查到，接着同一时间去访问数据库，同时的去执行数据库代码，对数据库访问压力过大

![alt text](/img/image-6.png)

解决方案一、使用锁来解决：

因为锁能实现互斥性。假设线程过来，只能一个人一个人的来访问数据库，从而避免对于数据库访问压力过大，但这也会影响查询的性能，因为此时会让查询的性能从并行变成了串行，我们可以采用 tryLock 方法 + double check 来解决这样的问题。

假设现在线程 1 过来访问，他查询缓存没有命中，但是此时他获得到了锁的资源，那么线程 1 就会一个人去执行逻辑，假设现在线程 2 过来，线程 2 在执行过程中，并没有获得到锁，那么线程 2 就可以进行到休眠，直到线程 1 把锁释放后，线程 2 获得到锁，然后再来执行逻辑，此时就能够从缓存中拿到数据了。

![alt text](/img/image-7.png)

解决方案二、逻辑过期方案

方案分析：我们之所以会出现这个缓存击穿问题，主要原因是在于我们对 key 设置了过期时间，假设我们不设置过期时间，其实就不会有缓存击穿的问题，但是不设置过期时间，这样数据不就一直占用我们内存了吗，我们可以采用逻辑过期方案。

我们把过期时间设置在 redis 的 value 中，注意：这个过期时间并不会直接作用于 redis，而是我们后续通过逻辑去处理。假设线程 1 去查询缓存，然后从 value 中判断出来当前的数据已经过期了，此时线程 1 去获得互斥锁，那么其他线程会进行阻塞，获得了锁的线程他会开启一个 线程去进行 以前的重构数据的逻辑，直到新开的线程完成这个逻辑后，才释放锁， 而线程 1 直接进行返回，假设现在线程 3 过来访问，由于线程线程 2 持有着锁，所以线程 3 无法获得锁，线程 3 也直接返回数据，只有等到新开的线程 2 把重建数据构建完后，其他线程才能走返回正确的数据。

这种方案巧妙在于，异步的构建缓存，缺点在于在构建完缓存之前，返回的都是脏数据。

![alt text](/img/image-8.png)

进行对比

**互斥锁方案：** 由于保证了互斥性，所以数据一致，且实现简单，因为仅仅只需要加一把锁而已，也没其他的事情需要操心，所以没有额外的内存消耗，缺点在于有锁就有死锁问题的发生，且只能串行执行性能肯定受到影响

**逻辑过期方案：** 线程读取过程中不需要等待，性能好，有一个额外的线程持有锁去进行重构数据，但是在重构数据完成前，其他的线程只能返回之前的数据，且实现起来麻烦

![alt text](/img/image-9.png)

# 6. 优惠卷

## 6.1 lua 脚本

Lua 脚本是 Redis 提供的一种服务器端脚本语言，可以用来实现复杂的原子操作。Lua 脚本在 Redis 中运行时是单线程的，因此可以保证脚本中的所有命令都是原子执行的。
更为极端的误删逻辑说明：

线程 1 现在持有锁之后，在执行业务逻辑过程中，他正准备删除锁，而且已经走到了条件判断的过程中，比如他已经拿到了当前这把锁确实是属于他自己的，正准备删除锁，但是此时他的锁到期了，那么此时线程 2 进来，但是线程 1 他会接着往后执行，当他卡顿结束后，他直接就会执行删除锁那行代码，相当于条件判断并没有起到作用，这就是删锁时的原子性问题，之所以有这个问题，是因为线程 1 的拿锁，比锁，删锁，实际上并不是原子性的，我们要防止刚才的情况发生，
![alt text](/img/image-10.png)

这里重点介绍 Redis 提供的调用函数，语法如下：

```lua
redis.call('命令名称', 'key', '其它参数', ...)
```

例如，我们要执行 set name jack，则脚本是这样：

```lua
# 执行 set name jack
redis.call('set', 'name', 'jack')
```

例如，我们要先执行 set name Rose，再执行 get name，则脚本如下：

```lua
# 先执行 set name jack
redis.call('set', 'name', 'Rose')
# 再执行 get name
local name = redis.call('get', 'name')
# 返回
return name
```

写好脚本以后，需要用 Redis 命令来调用脚本，调用脚本的常见命令如下：
![alt text](/img/image-11.png)
例如，我们要执行 redis.call('set', 'name', 'jack') 这个脚本，语法如下：
![alt text](/img/image-12.png)
如果脚本中的 key、value 不想写死，可以作为参数传递。key 类型参数会放入 KEYS 数组，其它参数会放入 ARGV 数组，在脚本中可以从 KEYS 和 ARGV 数组获取这些参数：
![alt text](/img/image-13.png)

接下来我们来回一下我们释放锁的逻辑：

释放锁的业务流程是这样的

​ 1、获取锁中的线程标示

​ 2、判断是否与指定的标示（当前线程标示）一致

​ 3、如果一致则释放锁（删除）

​ 4、如果不一致则什么都不做

如果用 Lua 脚本来表示则是这样的：

最终我们操作 redis 的拿锁比锁删锁的 lua 脚本就会变成这样

```lua
-- 这里的 KEYS[1] 就是锁的 key，这里的 ARGV[1] 就是当前线程标示
-- 获取锁中的标示，判断是否与当前线程标示一致
if (redis.call('GET', KEYS[1]) == ARGV[1]) then
-- 一致，则删除锁
return redis.call('DEL', KEYS[1])
end
-- 不一致，则直接返回
return 0
```

## 6.2 java 调用 lua 脚本

![alt text](/img/image-14.png)

```java
private static final DefaultRedisScript<Long> UNLOCK_SCRIPT;
    static {
        UNLOCK_SCRIPT = new DefaultRedisScript<>();
        UNLOCK_SCRIPT.setLocation(new ClassPathResource("unlock.lua"));
        UNLOCK_SCRIPT.setResultType(Long.class);
    }

public void unlock() {
    // 调用lua脚本
    stringRedisTemplate.execute(
            UNLOCK_SCRIPT,
            Collections.singletonList(KEY_PREFIX + name),
            ID_PREFIX + Thread.currentThread().getId());
}
经过以上代码改造后，我们就能够实现 拿锁比锁删锁的原子性动作了~
```

## 6.3 分布式锁总结

基于 Redis 的分布式锁实现思路：

- 利用 set nx ex 获取锁，并设置过期时间，保存线程标示
- 释放锁时先判断线程标示是否与自己一致，一致则删除锁
  - 特性：
    - 利用 set nx 满足互斥性
    - 利用 set ex 保证故障时锁依然能释放，避免死锁，提高安全性
    - 利用 Redis 集群保证高可用和高并发特性

笔者总结：我们一路走来，利用添加过期时间，防止死锁问题的发生，但是有了过期时间之后，可能出现误删别人锁的问题，这个问题我们开始是利用删之前 通过拿锁，比锁，删锁这个逻辑来解决的，也就是删之前判断一下当前这把锁是否是属于自己的，但是现在还有原子性问题，也就是我们没法保证拿锁比锁删锁是一个原子性的动作，最后通过 lua 表达式来解决这个问题

但是目前还剩下一个问题锁不住，什么是锁不住呢，你想一想，如果当过期时间到了之后，我们可以给他续期一下，比如续个 30s，就好像是网吧上网， 网费到了之后，然后说，来，网管，再给我来 10 块的，是不是后边的问题都不会发生了，那么续期问题怎么解决呢，可以依赖于我们接下来要学习 redission 啦

**测试逻辑：**

第一个线程进来，得到了锁，手动删除锁，模拟锁超时了，其他线程会执行 lua 来抢锁，当第一天线程利用 lua 删除锁时，lua 能保证他不能删除他的锁，第二个线程删除锁时，利用 lua 同样可以保证不会删除别人的锁，同时还能保证原子性。

# 7. Redission 分布式锁

## 7.1 分布式锁-redission 功能介绍

基于 setnx 实现的分布式锁存在下面的问题：

**重入问题**：重入问题是指 获得锁的线程可以再次进入到相同的锁的代码块中，可重入锁的意义在于防止死锁，比如 HashTable 这样的代码中，他的方法都是使用 synchronized 修饰的，假如他在一个方法内，调用另一个方法，那么此时如果是不可重入的，不就死锁了吗？所以可重入锁他的主要意义是防止死锁，我们的 synchronized 和 Lock 锁都是可重入的。

**不可重试**：是指目前的分布式只能尝试一次，我们认为合理的情况是：当线程在获得锁失败后，他应该能再次尝试获得锁。

**超时释放：**我们在加锁时增加了过期时间，这样的我们可以防止死锁，但是如果卡顿的时间超长，虽然我们采用了 lua 表达式防止删锁的时候，误删别人的锁，但是毕竟没有锁住，有安全隐患

**主从一致性：** 如果 Redis 提供了主从集群，当我们向集群写数据时，主机需要异步的将数据同步给从机，而万一在同步过去之前，主机宕机了，就会出现死锁问题。

![alt text](/img/image-15.png)

那么什么是 Redission 呢

Redisson 是一个在 Redis 的基础上实现的 Java 驻内存数据网格（In-Memory Data Grid）。它不仅提供了一系列的分布式的 Java 常用对象，还提供了许多分布式服务，其中就包含了各种分布式锁的实现。

Redission 提供了分布式锁的多种多样的功能

![alt text](/img/image-16.png)

## 7.2 Redission 入门

引入依赖

```xml
<dependency>
	<groupId>org.redisson</groupId>
	<artifactId>redisson</artifactId>
	<version>3.13.6</version>
</dependency>
```

配置 Redisson 客户端：

```java
@Configuration
public class RedissonConfig {

    @Bean
    public RedissonClient redissonClient(){
        // 配置
        Config config = new Config();
        config.useSingleServer().setAddress("redis://192.168.150.101:6379")
            .setPassword("123321");
        // 创建RedissonClient对象
        return Redisson.create(config);
    }
}
```

如何使用 Redission 的分布式锁

```java
@Resource
private RedissionClient redissonClient;

@Test
void testRedisson() throws Exception{
    //获取锁(可重入)，指定锁的名称
    RLock lock = redissonClient.getLock("anyLock");
    //尝试获取锁，参数分别是：获取锁的最大等待时间(期间会重试)，锁自动释放时间，时间单位
    boolean isLock = lock.tryLock(1,10,TimeUnit.SECONDS);
    //判断获取锁成功
    if(isLock){
        try{
            System.out.println("执行业务");
        }finally{
            //释放锁
            lock.unlock();
        }

    }
}
```

## 7.3 Redission 原理

在 Lock 锁中，他是借助于底层的一个 voaltile 的一个 state 变量来记录重入的状态的，比如当前没有人持有这把锁，那么 state=0，假如有人持有这把锁，那么 state=1，如果持有这把锁的人再次持有这把锁，那么 state 就会+1 ，如果是对于 synchronized 而言，他在 c 语言代码中会有一个 count，原理和 state 类似，也是重入一次就加一，释放一次就-1 ，直到减少成 0 时，表示当前这把锁没有被人持有。

在 redission 中，我们的也支持支持可重入锁

在分布式锁中，他采用 hash 结构用来存储锁，其中大 key 表示表示这把锁是否存在，用小 key 表示当前这把锁被哪个线程持有，所以接下来我们一起分析一下当前的这个 lua 表达式

这个地方一共有 3 个参数

**KEYS[1] ： 锁名称**

**ARGV[1]： 锁失效时间**

**ARGV[2]： id + ":" + threadId; 锁的小 key**

exists: 判断数据是否存在 name：是 lock 是否存在,如果==0，就表示当前这把锁不存在

redis.call('hset', KEYS[1], ARGV[2], 1);此时他就开始往 redis 里边去写数据 ，写成一个 hash 结构

Lock{

​ id + **":"** + threadId : 1

}

如果当前这把锁存在，则第一个条件不满足，再判断

redis.call('hexists', KEYS[1], ARGV[2]) == 1

此时需要通过大 key+小 key 判断当前这把锁是否是属于自己的，如果是自己的，则进行

redis.call('hincrby', KEYS[1], ARGV[2], 1)

将当前这个锁的 value 进行+1 ，redis.call('pexpire', KEYS[1], ARGV[1]); 然后再对其设置过期时间，如果以上两个条件都不满足，则表示当前这把锁抢锁失败，最后返回 pttl，即为当前这把锁的失效时间

看了前边的源码， 你会发现他会去判断当前这个方法的返回值是否为 null，如果是 null，则对应则前两个 if 对应的条件，退出抢锁逻辑，如果返回的不是 null，即走了第三个分支，在源码处会进行 while(true)的自旋抢锁。

```lua
"if (redis.call('exists', KEYS[1]) == 0) then " +
                  "redis.call('hset', KEYS[1], ARGV[2], 1); " +
                  "redis.call('pexpire', KEYS[1], ARGV[1]); " +
                  "return nil; " +
              "end; " +
              "if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then " +
                  "redis.call('hincrby', KEYS[1], ARGV[2], 1); " +
                  "redis.call('pexpire', KEYS[1], ARGV[1]); " +
                  "return nil; " +
              "end; " +
              "return redis.call('pttl', KEYS[1]);"
```

![alt text](/img/image-17.png)

## 7.4 分布式锁-redission 锁重试和 WatchDog 机制

**说明**：由于课程中已经说明了有关 tryLock 的源码解析以及其看门狗原理，所以笔者在这里给大家分析 lock()方法的源码解析，希望大家在学习过程中，能够掌握更多的知识

抢锁过程中，获得当前线程，通过 tryAcquire 进行抢锁，该抢锁逻辑和之前逻辑相同

1、先判断当前这把锁是否存在，如果不存在，插入一把锁，返回 null

2、判断当前这把锁是否是属于当前线程，如果是，则返回 null

所以如果返回是 null，则代表着当前这哥们已经抢锁完毕，或者可重入完毕，但是如果以上两个条件都不满足，则进入到第三个条件，返回的是锁的失效时间，同学们可以自行往下翻一点点，你能发现有个 while( true) 再次进行 tryAcquire 进行抢锁

```java
long threadId = Thread.currentThread().getId();
Long ttl = tryAcquire(-1, leaseTime, unit, threadId);
// lock acquired
if (ttl == null) {
    return;
}

```

接下来会有一个条件分支，因为 lock 方法有重载方法，一个是带参数，一个是不带参数，如果带带参数传入的值是-1，如果传入参数，则 leaseTime 是他本身，所以如果传入了参数，此时 leaseTime != -1 则会进去抢锁，抢锁的逻辑就是之前说的那三个逻辑

```java
if (leaseTime != -1) {
    return tryLockInnerAsync(waitTime, leaseTime, unit, threadId, RedisCommands.EVAL_LONG);
}
```

如果是没有传入时间，则此时也会进行抢锁， 而且抢锁时间是默认看门狗时间 commandExecutor.getConnectionManager().getCfg().getLockWatchdogTimeout()

ttlRemainingFuture.onComplete((ttlRemaining, e) 这句话相当于对以上抢锁进行了监听，也就是说当上边抢锁完毕后，此方法会被调用，具体调用的逻辑就是去后台开启一个线程，进行续约逻辑，也就是看门狗线程

```java
RFuture<Long> ttlRemainingFuture = tryLockInnerAsync(waitTime,
                                        commandExecutor.getConnectionManager().getCfg().getLockWatchdogTimeout(),
                                        TimeUnit.MILLISECONDS, threadId, RedisCommands.EVAL_LONG);
ttlRemainingFuture.onComplete((ttlRemaining, e) -> {
    if (e != null) {
        return;
    }

    // lock acquired
    if (ttlRemaining == null) {
        scheduleExpirationRenewal(threadId);
    }
});
return ttlRemainingFuture;
```

此逻辑就是续约逻辑，注意看 commandExecutor.getConnectionManager().newTimeout（） 此方法

Method( **new** TimerTask() {},参数 2 ，参数 3 )

指的是：通过参数 2，参数 3 去描述什么时候去做参数 1 的事情，现在的情况是：10s 之后去做参数一的事情

因为锁的失效时间是 30s，当 10s 之后，此时这个 timeTask 就触发了，他就去进行续约，把当前这把锁续约成 30s，如果操作成功，那么此时就会递归调用自己，再重新设置一个 timeTask()，于是再过 10s 后又再设置一个 timerTask，完成不停的续约

那么大家可以想一想，假设我们的线程出现了宕机他还会续约吗？当然不会，因为没有人再去调用 renewExpiration 这个方法，所以等到时间之后自然就释放了。

```java
private void renewExpiration() {
    ExpirationEntry ee = EXPIRATION_RENEWAL_MAP.get(getEntryName());
    if (ee == null) {
        return;
    }

    Timeout task = commandExecutor.getConnectionManager().newTimeout(new TimerTask() {
        @Override
        public void run(Timeout timeout) throws Exception {
            ExpirationEntry ent = EXPIRATION_RENEWAL_MAP.get(getEntryName());
            if (ent == null) {
                return;
            }
            Long threadId = ent.getFirstThreadId();
            if (threadId == null) {
                return;
            }

            RFuture<Boolean> future = renewExpirationAsync(threadId);
            future.onComplete((res, e) -> {
                if (e != null) {
                    log.error("Can't update lock " + getName() + " expiration", e);
                    return;
                }

                if (res) {
                    // reschedule itself
                    renewExpiration();
                }
            });
        }
    }, internalLockLeaseTime / 3, TimeUnit.MILLISECONDS);

    ee.setTimeout(task);
}
```

## 7.5 分布式锁-redission 锁的 MutiLock 原理

为了提高 redis 的可用性，我们会搭建集群或者主从，现在以主从为例

此时我们去写命令，写在主机上， 主机会将数据同步给从机，但是假设在主机还没有来得及把数据写入到从机去的时候，此时主机宕机，哨兵会发现主机宕机，并且选举一个 slave 变成 master，而此时新的 master 中实际上并没有锁信息，此时锁信息就已经丢掉了。

为了解决这个问题，redission 提出来了 MutiLock 锁，使用这把锁咱们就不使用主从了，每个节点的地位都是一样的， 这把锁加锁的逻辑需要写入到每一个主丛节点上，只有所有的服务器都写入成功，此时才是加锁成功，假设现在某个节点挂了，那么他去获得锁的时候，只要有一个节点拿不到，都不能算是加锁成功，就保证了加锁的可靠性。

当我们去设置了多个锁时，redission 会将多个锁添加到一个集合中，然后用 while 循环去不停去尝试拿锁，但是会有一个总共的加锁时间，这个时间是用需要加锁的个数 \* 1500ms ，假设有 3 个锁，那么时间就是 4500ms，假设在这 4500ms 内，所有的锁都加锁成功， 那么此时才算是加锁成功，如果在 4500ms 有线程加锁失败，则会再次去进行重试.

![alt text](/img/image-18.png)

# 8. BitMap 命令

Redis中是利用string类型数据结构实现BitMap，因此最大上限是512M，转换为bit则是 2^32个bit位。
![alt text](/img/image-19.png)

BitMap的操作命令有：

- SETBIT：向指定位置（offset）存入一个0或1 (setbit mybitmap 10 1, 将mybitmap的第10个bit位置为1, 即第11天签到)
- GETBIT ：获取指定位置（offset）的bit值 (getbit mybitmap 10, 获取mybitmap的第10个bit位的值)
- BITCOUNT ：统计BitMap中值为1的bit位的数量 （bitcount mybitmap）
- BITFIELD ：操作（查询、修改、自增）BitMap中bit数组中的指定位置（offset）的值 （bitfield mybitmap GET u5 0, 表示获取无符号的5个比特位，从0开始）
- BITFIELD_RO ：获取BitMap中bit数组，并以十进制形式返回 （bitfield_ro mybitmap GET u5 0, 表示获取无符号的5个比特位，从0开始）
- BITOP ：将多个BitMap的结果做位运算（与 、或、异或）
- BITPOS ：查找bit数组中指定范围内第一个0或1出现的位置

# 9. HyperLogLog 命令

首先我们搞懂两个概念：

- UV：全称Unique Visitor，也叫独立访客量，是指通过互联网访问、浏览这个网页的自然人。1天内同一个用户多次访问该网站，只记录1次。
- PV：全称Page View，也叫页面访问量或点击量，用户每访问网站的一个页面，记录1次PV，用户多次打开页面，则记录多次PV。往往用来衡量网站的流量。

通常来说UV会比PV大很多，所以衡量同一个网站的访问量，我们需要综合考虑很多因素，所以我们只是单纯的把这两个值作为一个参考值

UV统计在服务端做会比较麻烦，因为要判断该用户是否已经统计过了，需要将统计过的用户信息保存。但是如果每个访问的用户都保存到Redis中，数据量会非常恐怖，那怎么处理呢？

Hyperloglog(HLL)是从Loglog算法派生的概率算法，用于确定非常大的集合的基数，而不需要存储其所有值。相关算法原理大家可以参考：https://juejin.cn/post/6844903785744056333#heading-0
Redis中的HLL是基于string结构实现的，单个HLL的内存**永远小于16kb**，**内存占用低**的令人发指！作为代价，其测量结果是概率性的，**有小于0.81％的误差**。不过对于UV统计来说，这完全可以忽略。

![alt text](/img/image-20.png)
