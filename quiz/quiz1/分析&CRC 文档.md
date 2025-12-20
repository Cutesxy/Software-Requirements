# 分析&CRC 文档

## 1. 需求分析与抽象 (Requirement Analysis)

通过对问题描述的分析，我们采用名词提取法和动词分析法来识别系统中的关键概念。

### 1.1 关键名词提取与映射

- **原文**：“订房人”、“旅客” $\rightarrow$ **抽象为 `Guest` (旅客类)**。
- **原文**：“客房”、“指定客房” $\rightarrow$ **抽象为 `Room` (客房实体类)**。鉴于客房有不同的规格（如标间、大床），且预订时通常针对类型而非具体房号，**新增 `RoomType` (房型类)** 以减少耦合。
- **原文**：“柜台工作人员” $\rightarrow$ **抽象为 `Receptionist` (前台类)**。
- **原文**：“宾馆管理人员” $\rightarrow$ **抽象为 `Manager` (经理类)**。
- **原文**：“预订”、“更改预定信息” $\rightarrow$ **抽象为 `Reservation` (预订记录类)**。
- **原文**：“入住单”、“登记旅客信息” $\rightarrow$ **抽象为 `CheckInRecord` (入住记录类)**。
- **原文**：“预交押金”、“退房结账” $\rightarrow$ **抽象为 `Payment` (支付记录类)**，以支持多笔资金流水（押金+尾款）。

### 1.2 关键业务规则梳理

1. **预订与入住分离**：旅客可能先预订再入住，也可能直接面对面（Walk-in）入住。因此 `Reservation` 和 `CheckInRecord` 是关联关系，而非强绑定。
2. **房型与房间分离**：预订阶段锁定的是“房型”（RoomType），只有在办理入住（Check-in）时，前台才会分配具体的“房间”（Room）。
3. **资金流转**：入住包含“押金”和“结账”两个财务动作，需要独立的 `Payment` 类来记录每一笔交易，而不是简单地在订单上记一个总价。

------

## 2. CRC 卡片建模 (Class-Responsibility-Collaborator)

为了验证类的职责分配是否合理，设计了以下核心 CRC 卡片：

### 卡片 1：Receptionist (前台接待)

| **Class: Receptionist**     | **(系统主要操作者)**         |
| --------------------------- | ---------------------------- |
| **Responsibilities (职责)** | **Collaborators (协作者)**   |
| 1. 处理旅客预订请求         | Guest, Reservation, RoomType |
| 2. 办理入住手续（分配房间） | Guest, Room, CheckInRecord   |
| 3. 收取押金或结账款项       | Payment, CheckInRecord       |
| 4. 办理退房手续             | CheckInRecord, Room          |

### 卡片 2：CheckInRecord (入住单/核心业务对象)

| **Class: CheckInRecord**      | **(生命周期：入住 -> 退房)** |
| ----------------------------- | ---------------------------- |
| **Responsibilities (职责)**   | **Collaborators (协作者)**   |
| 1. 记录实际入住和退房时间     | -                            |
| 2. 关联具体的房间             | Room                         |
| 3. 关联对应的旅客             | Guest                        |
| 4. 记录资金流水（押金与结算） | Payment                      |
| 5. 计算最终账单               | Payment                      |

### 卡片 3：Reservation (预订记录)

| **Class: Reservation**      | **(生命周期：创建 -> 使用/取消)** |
| --------------------------- | --------------------------------- |
| **Responsibilities (职责)** | **Collaborators (协作者)**        |
| 1. 记录预订的日期范围       | -                                 |
| 2. 锁定所需的房型           | RoomType                          |
| 3. 允许修改预订信息         | -                                 |
| 4. 确认或取消预订状态       | ReservationStatus                 |

### 卡片 4：HotelSystem (系统门面)

| **Class: HotelSystem**      | **(信息查询入口)**         |
| --------------------------- | -------------------------- |
| **Responsibilities (职责)** | **Collaborators (协作者)** |
| 1. 查询客房实时状态         | Room, RoomStatus           |
| 2. 搜索可用房型             | RoomType                   |
| 3. 检索旅客历史信息         | Guest                      |

------

## 3. 详细设计与逻辑优化 (Detailed Design Rationale)

基于 CRC 分析，我们在最终的类图中进行了以下逻辑优化：

### 3.1 引入枚举类型 (Enumerations)

为了规范业务状态，防止非法输入，定义了以下枚举：

- **`RoomStatus`**：明确区分空闲、占用、打扫中等状态。
- **`BookingSource`**：区分电话、网络等预订来源（响应题目要求）。
- **`PaymentType`**：明确区分押金和结账款，便于财务统计。

### 3.2 关系设计的合理性

- **Guest (1) <--> (0..\*) Reservation**：一个旅客可以有多个预订记录，也可以没有（直接入住）。
- **Reservation (0..\*) <--> (1) RoomType**：预订是基于“类型”的，而不是基于“具体房间号”的。
- **CheckInRecord (1) <--> (1) Room**：实际入住单必须绑定一个具体的物理房间。
- **CheckInRecord (0..1) <--> (0..1) Reservation**：入住单**可以**基于一个预订生成，也**可以**独立生成（Walk-in 模式），这体现了业务的灵活性。