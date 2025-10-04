# 运行单个测试的方法

## 🎯 快速参考

### 方法 1: 使用完整路径（最精确）

```bash
# 运行单个测试方法
pytest tests/test_users.py::TestUserAPI::test_get_users_list -v

# 显示详细输出和打印语句
pytest tests/test_users.py::TestUserAPI::test_get_users_list -vv -s

# 显示完整错误追踪
pytest tests/test_users.py::TestUserAPI::test_get_users_list -vv --tb=long
```

### 方法 2: 使用关键字匹配

```bash
# 匹配测试名称中包含 "get_users" 的所有测试
pytest tests/test_users.py -k "get_users" -v

# 匹配 "get_users_list" 的测试
pytest tests/test_users.py -k "test_get_users_list" -v

# 使用 OR 匹配多个
pytest tests/test_users.py -k "get_users or create_user" -v
```

### 方法 3: 运行整个测试类

```bash
# 运行 TestUserAPI 类中的所有测试
pytest tests/test_users.py::TestUserAPI -v
```

### 方法 4: 使用辅助脚本

```bash
# 使用我们创建的脚本
./run_single_test.sh tests/test_users.py::TestUserAPI::test_get_users_list

# 运行整个类
./run_single_test.sh tests/test_users.py::TestUserAPI

# 使用关键字
./run_single_test.sh tests/test_users.py -k get_users
```

## 📋 常用选项

| 选项 | 说明 |
|------|------|
| `-v` | 显示详细测试名称 |
| `-vv` | 显示更详细的输出 |
| `-s` | 显示打印语句（print） |
| `--tb=short` | 简短的错误追踪 |
| `--tb=long` | 完整的错误追踪 |
| `--tb=no` | 不显示错误追踪 |
| `-x` | 遇到第一个失败就停止 |
| `--pdb` | 失败时进入调试器 |
| `-l` | 显示局部变量 |
| `--lf` | 只运行上次失败的测试 |
| `--ff` | 先运行上次失败的测试 |

## 🔍 调试单个测试

```bash
# 1. 显示所有输出
pytest tests/test_users.py::TestUserAPI::test_get_users_list -vv -s

# 2. 失败时进入调试器
pytest tests/test_users.py::TestUserAPI::test_get_users_list --pdb

# 3. 显示局部变量
pytest tests/test_users.py::TestUserAPI::test_get_users_list -vv -l

# 4. 不捕获输出（实时显示）
pytest tests/test_users.py::TestUserAPI::test_get_users_list -s --capture=no
```

## 💡 实用技巧

### 1. 在 VS Code 中运行

在 VS Code 中，你可以：
1. 打开 `tests/test_users.py`
2. 在测试函数旁边会出现 ▶️ 运行按钮
3. 点击即可运行单个测试

或者在终端面板中直接运行：
```bash
pytest tests/test_users.py::TestUserAPI::test_get_users_list -vv
```

### 2. 使用别名（添加到 ~/.zshrc 或 ~/.bashrc）

```bash
# 添加到配置文件
alias pytest-one='pytest -vv -s --tb=short'

# 使用
pytest-one tests/test_users.py::TestUserAPI::test_get_users_list
```

### 3. 快速重运行失败的测试

```bash
# 第一次运行所有测试
pytest tests/test_users.py -v

# 只重运行失败的
pytest tests/test_users.py --lf -v
```

## 📊 测试输出说明

```
=================== test session starts ===================
platform darwin -- Python 3.12.11, pytest-8.4.2
collected 1 item                          ← 收集到 1 个测试

tests/test_users.py::TestUserAPI::test_get_users_list PASSED [100%]
                                                       ↑        ↑
                                                    测试通过   进度

============= 1 passed, 11 warnings in 0.69s ==============
           ↑               ↑                  ↑
        通过数量         警告数量          耗时
```

## 🎨 彩色输出

pytest 默认支持彩色输出：
- ✅ 绿色 = 通过
- ❌ 红色 = 失败
- 🟡 黄色 = 警告
- 🔵 蓝色 = 跳过

如果没有颜色，可以强制启用：
```bash
pytest tests/test_users.py::TestUserAPI::test_get_users_list --color=yes
```

## 🚀 性能分析

```bash
# 显示最慢的 5 个测试
pytest tests/test_users.py --durations=5

# 只针对单个测试
pytest tests/test_users.py::TestUserAPI::test_get_users_list --durations=0
```

## 📝 生成报告

```bash
# 生成 HTML 报告
pytest tests/test_users.py::TestUserAPI::test_get_users_list --html=report.html

# 生成 JUnit XML 报告（用于 CI/CD）
pytest tests/test_users.py::TestUserAPI::test_get_users_list --junit-xml=report.xml
```

## 🎯 运行结果示例

### ✅ 成功示例
```
tests/test_users.py::TestUserAPI::test_get_users_list PASSED [100%]

============= 1 passed in 0.69s ==============
```

### ❌ 失败示例
```
tests/test_users.py::TestUserAPI::test_get_users_list FAILED [100%]

================= FAILURES =================
___ TestUserAPI.test_get_users_list ___

    @pytest.mark.asyncio
    async def test_get_users_list(self, client: AsyncClient, test_user, superuser_headers):
        response = await client.get("/api/v1/users/", headers=superuser_headers)
>       assert response.status_code == 200
E       assert 500 == 200

tests/test_users.py:18: AssertionError
============= 1 failed in 0.69s ==============
```

## 💡 常见问题

### Q: 如何只运行失败的测试？
```bash
pytest --lf  # last-failed
```

### Q: 如何跳过某个测试？
```python
@pytest.mark.skip(reason="暂时跳过")
async def test_get_users_list(self, ...):
    pass
```

### Q: 如何标记慢速测试？
```python
@pytest.mark.slow
async def test_get_users_list(self, ...):
    pass

# 跳过慢速测试
pytest -m "not slow"
```

## 🔗 相关命令

```bash
# 列出所有测试（不运行）
pytest tests/test_users.py --collect-only

# 显示测试覆盖率
pytest tests/test_users.py --cov=app

# 并行运行（需要 pytest-xdist）
pytest tests/test_users.py -n auto

# 持续监控文件变化
pytest-watch tests/test_users.py
```

## 📚 更多资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [Pytest 快速参考](https://docs.pytest.org/en/stable/reference/reference.html)
- [项目测试文档](docs/TESTING.md)
