> 一个对codeforces polygon的拙劣模仿

# 安装

```
pip install .
```

# 使用
```
hexagon [create|build|validate]
create:     'create problem-name' to create a new problem
build:      'build contest-name' to build a contest statement
            'build problem-name' to build a problem statement
            if no argument is given, then build the statement for the problem in the current directory
validate:   same as build, but doing validations instead
```

## create

创建一个新的题目文件夹

其中，
* testcases里面需要以`1`,`2`,`3`...以及`sample1`,`sample2`...的形式命名，存储输入文件。无需手动创建输出文件，会自动生成
* solutions里面存储各种程序，推荐以程序的期望得分来命名。其中必须要有一个名为`100.cpp`的标程。
* testlib里面存储validator和checker，详见[这里](https://github.com/MikeMirzayanov/testlib/tree/master)。一般来说，checker不需要手动修改，validator需要根据题目的输入格式来修改。

## build

* 对于题目，会根据输入文件以及标程生成样例。build之后可以使用xelatex编译statement.tex生成题面
* 对于比赛，会根据比赛的yaml描述文件生成比赛的题面
```yaml
title:
  那天我在学校门口捡到了一块砖
subtitle:
  "{\\rmfamily Div 1} 模拟赛"
date:
  2024 年 5 月 25 日
start:
  "13:00"
end:
  "16:00"
problems:
  - crt
  - crt
  - crt
```
请将这个文件命名为`xxx.yaml`然后放在与题目所在的根文件夹中，然后使用`build xxx.yaml`即可生成比赛题面

## validate

* 检测所有的输入文件是否能通过validator的测试
* 输出所有程序的得分以及在各个测试点上的运行情况
