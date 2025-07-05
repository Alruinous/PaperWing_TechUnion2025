# 完整版数据库

### 1. 用户与社交模块

### `User`（科研人员）

- `user_id`：主键，自增整数（PK, AUTO_INCREMENT）
- `account`：用户账号（VARCHAR(100)，非空）
- `email`：邮箱地址（VARCHAR(255)，UNIQUE, NOT NULL）
- `password_hash`：密码哈希值（VARCHAR(255)，NOT NULL）
- `name`：真实姓名（VARCHAR(100)，NOT NULL）
- `title`：职称（VARCHAR(100)，可选）
- `education`：学历（VARCHAR(100)，可选）
- `institution`：所属单位（VARCHAR(255)，可选）
- `avatar_url`：头像链接地址（VARCHAR(255)，可选）
- `bio`：个人简介（TEXT，可选）
- `research_fields`：研究方向（TEXT，可选）
- `status`：用户状态（ENUM，默认 `'active'`）
- `register_time`：注册时间（DATETIME，默认当前时间）

### `UserFollow`

- `follower_id`：关注者用户ID（INT，FK → User.user_id）
- `followee_id`：被关注的用户ID（INT，FK → User.user_id）
- 联合主键（PK）：(`follower_id`, `followee_id`)

------

### 2. 消息系统与讨论模块

### `Conversation`（讨论单元）

- `conversation_id`：主键，自增整数（PK, AUTO_INCREMENT）
- `title`：讨论主题（VARCHAR(255)，可选）
- `initiator_id`：发起人用户ID（INT，FK → User.user_id，可为空）
- `type`：讨论类型（ENUM，取值 'forum'、'project'）

### `Message`（消息细则）

- `message_id`：主键，自增整数（PK, AUTO_INCREMENT）
- `conversation_id`：所属讨论单元ID（INT，FK → Conversation.conversation_id，可为空）
- `sender_id`：发送者ID（INT，FK → User.user_id）
- `receiver_id`：接收者ID（INT，FK → User.user_id，可为空）
- `content`：消息正文（TEXT，非空）

### `ConversationParticipant`（项目参与记录）

- `conversation_id`：所属讨论单元ID（INT，FK → Conversation.conversation_id）
- `user_id`：用户ID（INT，FK → User.user_id）
- `status`：状态（ENUM，'pending_approval'、'invited'、'approved'）
- 联合主键：(`conversation_id`, `user_id`)

### `ConversationFollow`（用户关注讨论单元）

- `user_id`：用户ID（INT，FK → User.user_id）
- `conversation_id`：讨论单元ID（INT，FK → Conversation.conversation_id）
- 联合主键（PK）：(`user_id`, `conversation_id`)

------

### 3. 学术成果模块

### `Publication`（科研成果）

- `pub_id`：主键，自增整数（PK, AUTO_INCREMENT）
- `title`：成果标题（VARCHAR(500)，非空）
- `type`：成果类型（VARCHAR(50)，可选）
- `authors`：作者列表（TEXT，非空）
- `journal`：期刊/会议/出版单位名称（VARCHAR(200)，可选）
- `volume`：卷号（VARCHAR(50)，可选）
- `issue`：期号（VARCHAR(50)，可选）
- `year`：发表年份（SMALLINT）
- `abstract`：摘要内容（TEXT，可选）
- `keywords`：关键词列表（TEXT，可选）
- `external_url`：外部成果链接（VARCHAR(255)，可选）
- `local_file_path`：本地上传文件路径（VARCHAR(255)，可选）
- `created_by`：上传者用户ID（INT，FK → User.user_id）

### `PublicationUser`（成果与用户关联）

- `pub_id`：成果ID（INT，FK → Publication.pub_id）
- `user_id`：用户ID（INT，FK → User.user_id）
- 联合主键（PK）：(`pub_id`, `user_id`)

### `PublicationKeyword`

- `pub_id`：成果ID（INT，FK → Publication.pub_id）
- `keyword`：关键词（VARCHAR(100)）
- 联合主键（PK）：(`pub_id`, `keyword`)

### `PublicationLike`（成果点赞）

- `user_id`：用户ID（INT，FK → User.user_id）
- `pub_id`：成果ID（INT，FK → Publication.pub_id）
- 联合主键（PK）：(`user_id`, `pub_id`)

### `PublicationComment`（成果评论）

- `comment_id`：主键，自增整数（PK, AUTO_INCREMENT）
- `pub_id`：成果ID（INT，FK → Publication.pub_id）
- `user_id`：用户ID（INT，FK → User.user_id）
- `content`：评论内容（TEXT，非空）

### `ReadingHistory`（用户阅读记录）

- `user_id`：用户 ID（INT，FK → User.user_id）
- `pub_id`：成果 ID（INT，FK → Publication.pub_id）
- `read_time`：阅读时间（DATETIME，默认当前时间）
- 联合主键（可选）：(`user_id`, `pub_id`, `read_time`)

------