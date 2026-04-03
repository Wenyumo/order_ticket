# 北理班车抢票助手 - 安卓版

基于 Kivy 框架开发的安卓应用，实现了与桌面版相同的抢票功能。

## 功能特点

- 路线选择和班次查询
- 智能抢票（自动等待开售时间）
- 预查询座位信息，提高抢票成功率
- 实时日志显示
- 配置管理（API密钥、Cookie等）

## 项目结构

```
android/
├── app.py              # 主应用文件
├── ticketapp.kv        # Kivy UI界面定义
├── buildozer.spec      # Buildozer打包配置
├── requirements.txt    # Python依赖
├── icon.png           # 应用图标
├── presplash.png      # 启动画面
└── README.md          # 本文档
```

## 安装依赖

### Windows系统

1. 安装Python 3.8+
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

### Linux系统（用于打包）

```bash
sudo apt-get update
sudo apt-get install -y build-essential git python3 python3-dev python3-pip openjdk-8-jdk
pip3 install --user --upgrade Cython virtualenv
pip3 install --user buildozer
```

## 运行应用

### 在电脑上测试

```bash
cd android
python app.py
```

### 在安卓设备上运行

#### 方法1：使用 Buildozer 打包APK（推荐）

1. 进入android目录：
```bash
cd android
```

2. 初始化Buildozer（首次运行）：
```bash
buildozer init
```

3. 编辑 `buildozer.spec` 文件，配置应用信息

4. 打包APK：
```bash
buildozer -v android debug
```

5. 生成的APK文件位于 `bin/` 目录

6. 将APK传输到安卓设备并安装

#### 方法2：使用 Kivy Launcher

1. 在Google Play商店安装 "Kivy Launcher"
2. 将项目文件夹复制到手机的 `/sdcard/kivy/` 目录
3. 在Kivy Launcher中运行应用

## 配置说明

首次运行应用时，需要配置以下参数：

### 配置参数

1. **API_KEY**: API密钥
2. **USER_ID**: 钉钉用户ID
3. **COOKIE_STR**: Cookie字符串
4. **XSRF_TOKEN**: XSRF令牌

### 获取配置信息

1. 使用抓包工具（如Fiddler、Charles）抓取钉钉班车系统的请求
2. 从请求头中提取上述参数
3. 在应用中点击"配置"按钮，填入参数

## 使用方法

### 1. 查询班次

1. 选择路线
2. 选择日期
3. 点击"查询"按钮
4. 从列表中选择班次

### 2. 开始抢票

1. 选择班次后，点击"开始抢票"按钮
2. 应用会自动等待到开售时间
3. 开售前2秒预查询座位信息
4. 开售瞬间自动下单

### 3. 查看日志

- 日志区域实时显示抢票过程
- 包含时间戳和详细操作信息

## 技术特点

### 代码复用

- 直接复用了原有的 `api.py` 和 `config.py`
- 保持了与桌面版相同的业务逻辑
- 只需要修改UI层适配移动端

### 性能优化

- 使用线程进行后台抢票
- 预查询座位减少开售时的请求延迟
- 精确等待开售时间（毫秒级）

### UI设计

- 适配移动端屏幕尺寸
- 简洁直观的操作界面
- 支持触摸操作

## 故障排除

### 打包失败

1. 确保已安装所有依赖
2. 检查Java版本（需要JDK 8或更高）
3. 清理缓存：`buildozer android clean`
4. 查看详细日志：`buildozer -v android debug`

### 应用崩溃

1. 检查配置参数是否正确
2. 查看日志输出
3. 确保网络连接正常
4. 检查Cookie是否过期

### 抢票失败

1. 确认开售时间是否正确
2. 检查网络延迟
3. 验证Cookie有效性
4. 查看服务器返回的错误信息

## 注意事项

1. **Cookie有效期**: Cookie会过期，需要定期更新
2. **网络要求**: 需要稳定的网络连接
3. **时间同步**: 确保设备时间准确
4. **合法使用**: 请遵守学校班车系统的使用规则

## 更新日志

### v1.0.0 (2024-04-03)

- 初始版本
- 实现基本抢票功能
- 支持配置管理
- 添加日志显示

## 开发说明

### 修改UI

编辑 `ticketapp.kv` 文件修改界面布局

### 修改逻辑

编辑 `app.py` 文件修改业务逻辑

### 添加功能

1. 在 `app.py` 中添加新功能
2. 在 `ticketapp.kv` 中添加对应的UI元素
3. 重新打包APK测试

## 许可证

本项目仅供学习和个人使用，请勿用于商业用途。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件

## 致谢

感谢 Kivy 团队提供的优秀框架
感谢 Buildozer 工具简化了Android打包流程
