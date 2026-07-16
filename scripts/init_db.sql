-- ============================================
-- AI 智能客服综合平台 — 数据库初始化脚本
-- 数据库: ai_customer
-- ============================================

CREATE DATABASE IF NOT EXISTS `ai_customer` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `ai_customer`;

-- ============================================
-- 学生表
-- ============================================
DROP TABLE IF EXISTS `student`;
CREATE TABLE `student` (
    `student_id`   INT          NOT NULL AUTO_INCREMENT COMMENT '学生ID',
    `student_name` VARCHAR(50)  NOT NULL COMMENT '学生姓名',
    `gender`       VARCHAR(10)  DEFAULT NULL COMMENT '性别',
    `email`        VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `phone`        VARCHAR(20)  DEFAULT NULL COMMENT '手机号',
    `grade`        DECIMAL(5,2) DEFAULT NULL COMMENT '绩点',
    `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`student_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- ============================================
-- 教师表
-- ============================================
DROP TABLE IF EXISTS `teacher`;
CREATE TABLE `teacher` (
    `teacher_id`   INT          NOT NULL AUTO_INCREMENT COMMENT '教师ID',
    `teacher_name` VARCHAR(50)  NOT NULL COMMENT '教师姓名',
    `gender`       VARCHAR(10)  DEFAULT NULL COMMENT '性别',
    `phone`        VARCHAR(20)  DEFAULT NULL COMMENT '手机号',
    `email`        VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    `salary`       DECIMAL(10,2) DEFAULT NULL COMMENT '薪资',
    `hire_date`    DATE         DEFAULT NULL COMMENT '入职日期',
    `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`teacher_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='教师表';

-- ============================================
-- 课程表
-- ============================================
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
    `course_id`    INT          NOT NULL AUTO_INCREMENT COMMENT '课程ID',
    `course_name`  VARCHAR(100) NOT NULL COMMENT '课程名称',
    `teacher_id`   INT          DEFAULT NULL COMMENT '授课教师ID',
    `capacity`     INT          DEFAULT 0 COMMENT '课程容量',
    `total_hours`  INT          DEFAULT 0 COMMENT '总课时',
    `created_at`   DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`course_id`),
    KEY `idx_teacher_id` (`teacher_id`),
    CONSTRAINT `fk_course_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- ============================================
-- 预约表
-- ============================================
DROP TABLE IF EXISTS `reservation`;
CREATE TABLE `reservation` (
    `reservation_id`   INT      NOT NULL AUTO_INCREMENT COMMENT '预约ID',
    `student_id`       INT      NOT NULL COMMENT '学生ID',
    `course_id`        INT      NOT NULL COMMENT '课程ID',
    `reservation_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '预约时间',
    `status`           VARCHAR(20) DEFAULT '已预约' COMMENT '预约状态(已预约/已取消/已完成)',
    `created_at`       DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`reservation_id`),
    KEY `idx_student_id` (`student_id`),
    KEY `idx_course_id` (`course_id`),
    CONSTRAINT `fk_reservation_student` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reservation_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约表';

-- ============================================
-- 题目表（用于 AI 阅卷）
-- ============================================
DROP TABLE IF EXISTS `question`;
CREATE TABLE `question` (
    `id`       INT          NOT NULL AUTO_INCREMENT COMMENT '题目ID',
    `question` TEXT         NOT NULL COMMENT '题目内容',
    `answer`   TEXT         NOT NULL COMMENT '标准答案',
    `score`    INT          DEFAULT 0 COMMENT '分值',
    `created_at` DATETIME  DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='题目表';

-- ============================================
-- 插入测试数据
-- ============================================

-- 学生数据
INSERT INTO `student` (`student_name`, `gender`, `email`, `phone`, `grade`) VALUES
('小明', '男', 'xiaoming@163.com', '13800138001', 3.8),
('小红', '女', 'xiaohong@qq.com', '13800138002', 3.5),
('小刚', '男', 'xiaogang@gmail.com', '13800138003', 3.2),
('小丽', '女', 'xiaoli@163.com', '13800138004', 3.9),
('小华', '男', 'xiaohua@qq.com', '13800138005', 2.8),
('小强', '男', 'xiaoqiang@163.com', '13800138006', 3.6),
('小美', '女', 'xiaomei@gmail.com', '13800138007', 4.0),
('小军', '男', 'xiaojun@qq.com', '13800138008', 3.1),
('小芳', '女', 'xiaofang@163.com', '13800138009', 3.7),
('小杰', '男', 'xiaojie@gmail.com', '13800138010', 2.5);

-- 教师数据
INSERT INTO `teacher` (`teacher_name`, `gender`, `phone`, `email`, `salary`, `hire_date`) VALUES
('张三', '男', '13900139001', 'zhangsan@edu.com', 12000.00, '2018-03-01'),
('李四', '女', '13900139002', 'lisi@edu.com', 15000.00, '2016-06-15'),
('王五', '男', '13900139003', 'wangwu@edu.com', 18000.00, '2015-09-01'),
('赵六', '女', '13900139004', 'zhaoliu@edu.com', 10000.00, '2020-01-10'),
('孙七', '男', '13900139005', 'sunqi@edu.com', 9000.00, '2021-07-20'),
('周八', '女', '13900139006', 'zhouba@edu.com', 16000.00, '2017-04-01'),
('吴九', '男', '13900139007', 'wujiu@edu.com', 13000.00, '2019-08-15'),
('郑十', '女', '13900139008', 'zhengshi@edu.com', 11000.00, '2020-11-01');

-- 课程数据
INSERT INTO `course` (`course_name`, `teacher_id`, `capacity`, `total_hours`) VALUES
('高等数学', 1, 100, 64),
('线性代数', 1, 80, 48),
('大学英语', 2, 120, 64),
('Python编程', 3, 60, 48),
('数据结构', 3, 50, 48),
('大学物理', 4, 90, 56),
('体育健身', 5, 100, 32),
('艺术鉴赏', 6, 80, 32),
('经济学基础', 7, 70, 48),
('心理学入门', 8, 60, 32);

-- 预约数据
INSERT INTO `reservation` (`student_id`, `course_id`, `reservation_time`, `status`) VALUES
(1, 1, '2025-09-01 08:00:00', '已预约'),
(1, 3, '2025-09-01 08:30:00', '已预约'),
(2, 1, '2025-09-01 09:00:00', '已预约'),
(2, 4, '2025-09-01 09:30:00', '已预约'),
(3, 2, '2025-09-01 10:00:00', '已取消'),
(3, 5, '2025-09-01 10:30:00', '已预约'),
(4, 3, '2025-09-01 11:00:00', '已预约'),
(4, 6, '2025-09-01 11:30:00', '已预约'),
(5, 1, '2025-09-01 14:00:00', '已取消'),
(5, 7, '2025-09-01 14:30:00', '已预约'),
(6, 4, '2025-09-02 08:00:00', '已预约'),
(6, 8, '2025-09-02 08:30:00', '已预约'),
(7, 2, '2025-09-02 09:00:00', '已预约'),
(7, 5, '2025-09-02 09:30:00', '已预约'),
(8, 3, '2025-09-02 10:00:00', '已预约'),
(8, 9, '2025-09-02 10:30:00', '已预约'),
(9, 6, '2025-09-02 11:00:00', '已预约'),
(9, 10, '2025-09-02 11:30:00', '已预约'),
(10, 1, '2025-09-02 14:00:00', '已预约'),
(10, 7, '2025-09-02 14:30:00', '已预约');

-- 题目数据（用于 AI 阅卷）
INSERT INTO `question` (`question`, `answer`, `score`) VALUES
('请列举 Vue 生命周期的四个阶段及其对应的钩子函数', 'Vue生命周期分为四个阶段：1. 创建阶段（beforeCreate、created）；2. 挂载阶段（beforeMount、mounted）；3. 更新阶段（beforeUpdate、updated）；4. 销毁阶段（beforeDestroy、destroyed）', 20),
('请简述 HTTP 和 HTTPS 的区别', '1. HTTP 是明文传输，HTTPS 是加密传输；2. HTTPS 需要 SSL 证书；3. HTTPS 默认端口 443，HTTP 默认端口 80；4. HTTPS 更安全但性能略低于 HTTP', 15),
('什么是 RESTful API？请列举其设计原则', 'RESTful API 是一种符合 REST 架构风格的 API 设计规范。原则：1. 资源通过 URL 定位；2. 使用 HTTP 方法（GET/POST/PUT/DELETE）操作资源；3. 无状态通信；4. 统一接口；5. 使用 JSON/XML 作为数据格式', 15);