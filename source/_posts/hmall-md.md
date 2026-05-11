---
title: hmall.md
date: 2025-09-13 15:49:26
tags: [微服务]
---

# 1.MyBatis-Plus 入门

## 1.1. 什么是 MyBatis-Plus

MyBatis-Plus 是一个基于 MyBatis 的增强工具包，旨在简化 MyBatis 的使用，提供了许多便捷的功能，如自动生成 CRUD 代码、分页查询、代码生成器等。它通过注解和配置文件的方式，极大地减少了开发者的工作量，提高了开发效率。

## 1.2. MyBatis-Plus 的安装与配置

1. **添加依赖**：在项目的 `pom.xml` 文件中添加 MyBatis-Plus 的依赖。

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.3.1</version>
</dependency>
```

2. **配置数据源**：在 `application.yml` 或 `application.properties` 文件中配置数据库连接信息。

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/mp?useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&serverTimezone=Asia/Shanghai
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 1234
```

3. 在 `mapper`接口中继承 `BaseMapper<T>`，其中 `T` 是实体类。

```java
public interface UserMapper extends BaseMapper<User>
{
}
```

## 1.3. 常用注解

- 类名驼峰转下划线作为表名
- 字段名驼峰转下划线作为列名
- id 为主键，自动增长
- @TableName(value = "user"): 指定表名
- @TableId(type = IdType.AUTO): 指定主键生成策略(不指定默认雪花算法)
  - IDType.AUTO: 自增
  - IDType.INPUT: 手动输入
  - IDType.ASSIGN_ID: 雪花算法
- @TableField(value = "age"): 指定表中字段信息
  - 成员变量名和表中字段名不一致
  - 成员变量是 is 开头的布尔类型(Boolean isMarried)
  - 成员变量和数据库关键字冲突(如 order)
  - 成员变量不需要映射到数据库中(@TableField(exist = false))

## 1.4 常用配置

```yaml
mybatis-plus:
  type-aliases-package: com.itheima.mp.domain.po
  global-config:
    db-config:
      id-type: auto
  mapper-locations: classpath*:/mapper/**/*.xml
```

# 2. MyBatis-Plus 核心功能

## 2.1 条件构造器

```java
    // 查询名字中包含 "o" 且余额大于等于 1000 的用户
    @Test
    void testQueryWrapper() {
        QueryWrapper<User> wrapper = new QueryWrapper<User>()
                .select("id", "username", "info", "balance")
                .like("username", "o")
                .ge("balance", 1000);
        List<User> users = userMapper.selectList(wrapper);
        users.forEach(System.out::println);
    }
    // 使用 Lambda 表达式查询名字中包含 "o" 且余额大于等于 1000 的用户
    @Test
    void testLambdaQueryWrapper() {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<User>()
                .select(User::getId, User::getUsername, User::getInfo, User::getBalance)
                .like(User::getUsername, "o")
                .ge(User::getBalance, 1000);
        List<User> users = userMapper.selectList(wrapper);
        users.forEach(System.out::println);
    }

    // 更新用户名为 "jack" 的用户余额为 2000
    @Test
    void testUpdateByQueryWrapper() {
        User user = new User();
        user.setBalance(2000);
        QueryWrapper<User> wrapper = new QueryWrapper<User>().eq("username", "jack");
        userMapper.update(user, wrapper);
    }
    // 将 id 在 1,2,3 之内的用户余额减少 100
    @Test
    void testUpdateWrapper() {
        UpdateWrapper<User> wrapper = new UpdateWrapper<User>()
                .setSql("balance = balance - 100")
                .in("id", List.of(1, 2, 3));
        userMapper.update(null, wrapper);
    }

```

## 2.2 自定义 SQL

```java
    @Test
    void testCustomSqlUpdate(){
        // 更新条件
        List<Integer> ids = List.of(1, 2, 3);
        int amount = 200;
        // 定义条件
        QueryWrapper<User> wrapper = new QueryWrapper<User>().in("id", ids);
        // 调用自定义sql方法
        userMapper.updateBalanceByIds(wrapper, amount);
    }

```

在 `UserMapper` 接口中定义自定义 SQL 方法：

```java
void updateBalanceByIds(@Param(Constants.WRAPPER) QueryWrapper<User> wrapper, @Param("amount") int amount);
```

在对应的 XML 映射文件中编写 SQL 语句：

```xml
<update id="updateBalanceByIds">
    update user set balance = balance - #{amount} ${ew.customSqlSegment}
</update>
```

## 2.3 Service 接口

自定义接口 Service，继承 IService<T>，其中 T 是实体类

```
public interface IUserService extends IService<User> {

}

```

在 Service 实现类中继承 ServiceImpl<Mapper, T>，其中 Mapper 是 Mapper 接口，T 是实体类

```java
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements IUserService {

}
```

Swagger 配置

```yaml
knife4j:
  enable: true
  openapi:
    title: 用户管理接口文档
    description: "用户管理接口文档"
    email: zhanghuyi@itcast.cn
    concat: 虎哥
    url: https://www.itcast.cn
    version: v1.0.0
    group:
      default:
        group-name: default
        api-rule: package
        api-rule-resources:
          - com.itheima.mp.controller
```

Controller 示例

```java

@Api(tags = "用户管理接口")
@RequestMapping("/users")
@RestController
@RequiredArgsConstructor
public class UserController {

    private final IUserService userService;


    @ApiOperation(value = "新增用户接口")
    @PostMapping
    public void saveUser(@RequestBody UserFormDTO userDTO){

        User user = BeanUtil.copyProperties(userDTO, User.class);
        userService.save(user);
    }

    @ApiOperation(value = "删除用户接口")
    @DeleteMapping("/{id}")
    public void deleteUserById(@ApiParam("用户ID") @PathVariable Long id){
        userService.removeById(id);
    }

    @ApiOperation(value = "根据id查询用户接口")
    @GetMapping("/{id}")
    public UserVO queryUserById(@ApiParam("用户ID") @PathVariable Long id){
        User user = userService.getById(id);
        return BeanUtil.copyProperties(user, UserVO.class);
    }

    @ApiOperation(value = "根据id批量查询用户接口")
    @GetMapping
    public List<UserVO> queryUserByIds(@ApiParam("用户id集合") @PathVariable("ids") List<Long> ids){
        List<User> users = userService.listByIds(ids);
        return BeanUtil.copyToList(users, UserVO.class);
    }
}

```

## 2.4 Iservice 的 Lambda 查询

UserServiceImpl 中复杂条件的查询

```java
@Override
public List<User> queryUsers(UserQuery query) {
    return lambdaQuery().like(query.getName() != null, User::getUsername, query.getName())
            .eq(query.getStatus() != null, User::getStatus, query.getStatus())
            .ge(query.getMinBalance() != null, User::getBalance, query.getMinBalance())
            .le(query.getMaxBalance() != null, User::getBalance, query.getMaxBalance())
            .list();
}
```

## 2.5 Iservice 的批量插入

开启 rewriteBatchedStatements=true 参数

```yaml
spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/mp?useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&serverTimezone=Asia/Shanghai&rewriteBatchedStatements=true
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: MySQL123
```

## 2.6 扩展功能

### 2.6.1 MyBatisPlus 插件

打开 tools-> Configdatabase
![alt text](/img/image.png)
之后选择 Code Generator
![alt text](/img/image-1.png)

### 2.6.2 Db 静态工具

```java
@Override
public UserVO queryUserAndAdressesById(Long id) {
    // 1.查询用户
    User user = getById(id);
    if(user == null || user.getStatus() == 2){
        throw new RuntimeException("用户状态异常");
    }
    List<Address> list = Db.lambdaQuery(Address.class)
            .eq(Address::getUserId, id).list();
    UserVO userVO = BeanUtil.copyProperties(user, UserVO.class);
    if(CollUtil.isNotEmpty(list)){
      userVO.setAddresses(BeanUtil.copyToList(list, AddressVO.class));
    }
    return userVO;
}
```

### 2.6.3 逻辑删除

逻辑删除就是在数据库中不真正删除数据，而是通过一个标志位来表示数据是否被删除。这样可以保留数据的完整性，方便后续的数据恢复和审计。

MybatisPlus 生成的 SQL 语句才支持自动的逻辑删除，自定义 SQL 需要自己手动处理逻辑删除。

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted # 全局逻辑删除的实体字段名(since 3.3.0,配置后可以忽略不配置步骤2)
      logic-delete-value: 1 # 逻辑已删除值(默认为 1)
      logic-not-delete-value: 0 # 逻辑未删除值(默认为 0)
```

### 2.6.4 枚举处理器

```java

@Getter
public enum UserStatus {
    NORMAL(1, "正常"),
    FROZEN(2, "冻结"),
        ;
    @EnumValue
    private final int value;
    @JsonValue
    private final String desc;
    UserStatus(int value, String desc){
        this.value = value;
        this.desc = desc;
    }
}
```

### 2.6.5 JSON 处理器

UserInfo.java

```java
package com.itheima.mp.domain.po;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor(staticName = "of") // 提供静态工厂方法
public class UserInfo {
    private Integer age;
    private String intro;
    private String gender;
}
```

```java
@TableName(value = "user", autoResultMap = true) // autoResultMap = true 开启自动映射
public class User {
  @TableField(typeHandler = JacksonTypeHandler.class) // 指定 JSON 类型处理器
    private UserInfo info;
}
```

## 2.7 插件功能

### 2.7.1 分页插件

配置分页插件

```java
@Configuration
public class MybatisConfig {
    @Bean
    public MybatisPlusInterceptor mybatisPlusInterceptor() {
        // 初始化核心插件
        MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
        PaginationInnerInterceptor paginationInnerInterceptor = new PaginationInnerInterceptor(DbType.MYSQL); // 设置数据库类型
        paginationInnerInterceptor.setMaxLimit(1000L); // 设置单页最大限制数量
        // 添加分页插件
        interceptor.addInnerInterceptor(paginationInnerInterceptor);
        return interceptor;
    }
}
```

查询

```java
@Test
    void testPageQuery(){
        int pageNo = 1, pageSize = 2;
        Page<User> page = Page.of(pageNo, pageSize);
        // 排序条件
        page.addOrder(new OrderItem("balance", true));
        page.addOrder(new OrderItem("id", true));
        // 分页查询
        Page<User> p = userService.page(page);
        // 解析
        long total = p.getTotal();
        long pages = p.getPages();
        System.out.println(total);
        System.out.println(pages);
        p.getRecords().forEach(System.out::println);
    }
```

pageDTO

```java

@Data
@ApiModel(description = "分页结果")
public class PageDTO<T> {
    @ApiModelProperty("总记录数")
    private Long total;
    @ApiModelProperty("总页数")
    private Long pages;
    @ApiModelProperty("集合")
    private List<T> list;
}
```

UserServiceImpl

```java
@Override
    public PageDTO<UserVO> queryUsersPage(UserQuery query) {
        // 构建分页条件
        Page<User> page = Page.of(query.getPageNo(), query.getPageSize());
        if(StrUtil.isNotBlank(query.getSortBy())) {
            page.addOrder(new OrderItem(query.getSortBy(), query.getIsAsc()));
        }
        else{
            page.addOrder(new OrderItem("update_time", false));
        }
        // 分页查询
        Page<User> p = lambdaQuery().like(query.getName() != null, User::getUsername, query.getName())
                .eq(query.getStatus() != null, User::getStatus, query.getStatus())
                .page(page);
        PageDTO<UserVO> dto = new PageDTO<>();
        dto.setTotal(p.getTotal());
        dto.setPages(p.getPages());
        List<User> records = p.getRecords();
        if(CollUtil.isEmpty(records)){
            dto.setList(Collections.emptyList());
            return dto;
        }
        List<UserVO> vos = BeanUtil.copyToList(records, UserVO.class);
        dto.setList(vos);
        return dto;
    }
```

在刚才的代码中，从 PageQuery 到 MybatisPlus 的 Page 之间转换的过程还是比较麻烦的。
可以在 PageQuery 这个实体中定义一个工具方法，简化开发。

```java

@Data
public class PageQuery {
    @ApiModelProperty("页码")
    private Integer pageNo;
    @ApiModelProperty("每页记录数")
    private Integer pageSize;
    @ApiModelProperty("排序字段")
    private String sortBy;
    @ApiModelProperty("是否升序")
    private Boolean isAsc;

    public <T>  Page<T> toMpPage(OrderItem ... orders){
        // 1.分页条件
        Page<T> p = Page.of(pageNo, pageSize);
        // 2.排序条件
        // 2.1.先看前端有没有传排序字段
        if (sortBy != null) {
            p.addOrder(new OrderItem(sortBy, isAsc));
            return p;
        }
        // 2.2.再看有没有手动指定排序字段
        if(orders != null){
            p.addOrder(orders);
        }
        return p;
    }

    public <T> Page<T> toMpPage(String defaultSortBy, boolean isAsc){
        return this.toMpPage(new OrderItem(defaultSortBy, isAsc));
    }

    public <T> Page<T> toMpPageDefaultSortByCreateTimeDesc() {
        return toMpPage("create_time", false);
    }

    public <T> Page<T> toMpPageDefaultSortByUpdateTimeDesc() {
        return toMpPage("update_time", false);
    }
}

```
