# Fight应用使用说明

## 快速开始

### 1. 环境准备

确保你已经安装了Python 3.8+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制`.env.example`为`.env`并配置必要的环境变量：

```bash
cp .env.example .env
```

编辑`.env`文件，填入以下必需的配置：

```bash
# Anthropic AI API密钥 (必需)
ANTHROPIC_API_KEY=你的Anthropic_API密钥

# agents_memory数据库连接 (必需)
AGENTS_MEMORY_DSN=postgresql://am_app:password@localhost:5432/agents_memory

# agents_memory API密钥 (必需)
AGENTS_MEMORY_API_KEY=sk_am_你的API密钥
```

### 3. 获取API密钥

#### Anthropic API密钥
- 访问 [Anthropic Console](https://console.anthropic.com/)
- 创建API密钥
- 将密钥添加到`.env`文件中的`ANTHROPIC_API_KEY`

#### agents_memory配置
- 确保agents_memory数据库正在运行
- 使用agents_memory提供的DSN和API密钥
- 参考agents_memory项目的README获取配置详情

### 4. 运行应用

有两种运行方式：

#### 方式一：使用启动脚本（推荐）
```bash
./run.sh
```

#### 方式二：直接运行Python模块
```bash
# 确保环境变量已加载
source .env

# 运行应用
python -m fight.cli
```

## 使用流程

### 开始辩论

1. 启动应用后，选择`1. 开始新的辩论`
2. 输入要决策的主题，例如："是否应该换工作"
3. 输入你的初始立场，例如："我认为应该换工作，因为现在的职位没有成长空间"

### 进行辩论

应用会生成AI的初始对立立场，然后进入辩论循环：

```
[你] 我认为新公司的发展前景更好，薪资也更高。
[AI智能体] 但是新公司的不确定性很高，你可能面临适应新环境的挑战，而且现有的工作稳定性如何权衡？

[你] 我觉得稳定性和成长性相比，成长性更重要。
[AI智能体] 这是一个合理的观点，但也要考虑职业转换的成本和风险，包括可能需要适应新的团队文化和工作流程。
```

### 可用命令

在辩论过程中，你可以使用以下命令：

- `quit` - 结束辩论
- `summary` - 查看辩论摘要
- `decision` - 生成最终决策建议

### 生成决策

当你觉得辩论充分时，输入`decision`，系统会：

1. 分析整个辩论过程
2. 基于双方论点生成决策建议
3. 评估决策的置信度
4. 识别主要风险因素

## 高级功能

### 记忆存储

Fight应用使用agents_memory存储：
- 所有辩论论点
- 证据和引用
- 辩论历史
- 决策依据

这些信息可以在后续会话中重新访问和分析。

### 辩论策略

为了获得最好的决策建议：

1. **保持具体** - 提供具体的论点和事实
2. **多角度思考** - 考虑不同的视角和可能的后果
3. **深入讨论** - 不要急于求成，让辩论充分展开
4. **诚实表达** - 诚实地表达你的真实想法和担忧

### 理解决策结果

系统生成的决策包含：

- **建议** - 基于辩论的具体建议
- **置信度** - 对建议的确信程度（0-100%）
- **推理过程** - 得出建议的逻辑
- **主要风险** - 需要注意的风险因素

## 故障排除

### 常见问题

1. **无法连接到数据库**
   - 检查`AGENTS_MEMORY_DSN`是否正确
   - 确保agents_memory数据库正在运行
   - 验证网络连接

2. **AI API调用失败**
   - 检查`ANTHROPIC_API_KEY`是否有效
   - 确认API账户有足够的额度
   - 检查网络连接

3. **模块导入错误**
   - 确保所有依赖都已安装：`pip install -r requirements.txt`
   - 检查Python版本（需要3.8+）

### 测试环境

运行基础功能测试：

```bash
python fight/test_simple.py
```

## 开发和扩展

### 项目结构

```
fight/
├── fight/
│   ├── __init__.py          # 包初始化
│   ├── cli.py               # CLI界面
│   ├── debate_manager.py    # 辩论逻辑管理
│   ├── memory_store.py      # 记忆存储集成
│   └── test_simple.py       # 基础测试
├── README.md                # 项目说明
├── USAGE.md                 # 使用说明
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量模板
└── run.sh                  # 启动脚本
```

### 自定义配置

你可以通过修改以下组件来定制应用：

1. **AI模型选择** - 在`debate_manager.py`中修改使用的Claude模型
2. **辩论策略** - 调整提示词以改变AI的辩论风格
3. **记忆存储** - 扩展`memory_store.py`以支持更多存储功能

## 贡献

欢迎提交问题和改进建议！

## 许可证

MIT License - 详见LICENSE文件