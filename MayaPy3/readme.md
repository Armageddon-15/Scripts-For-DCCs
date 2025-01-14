# Maya Script

For maya 2024 using python 3.10

# 插件简介

本质上是自用的插件，所以并适配其他版本的优先级并不高。只不过有时间后也能也会适配其他版本

# 安装前准备

请确定maya已经安装了pymel

# 插件安装

下载好文件先解压到你觉得合适的路径，比如：

    E:\Python-Scripts-For-DCCs\MayaPy3

之后到我的文档：

    用户名\我的文档\maya\modules

中增加文件 `Armageddon.mod`

并在其中添加这样一段文字：

    + MayaPy3 0.0.2 E:\Python-Scripts-For-DCCs\MayaPy3

其中 `E:\Python-Scripts-For-DCCs` 更换为你刚才解压的路径
 
接着打开maya（如果之前打开过就关闭后重开），先打开插件管理器，开启插件Armageddon.py

再在代码编辑器中执行 python 语句：

    import armageddon.MainWindow as armw
    armw.show()

或者：

    import maya.cmds as cmds
    cmds.armageddon()

二者任选其一，可以全选后拖拽到shelf保存

如果能看到gui界面说明安装成功（但不保证功能正常）

# GUI功能

可以在左上角的settings中从scroll和tab中更换布局

可以停靠在多数maya窗口旁

# 主要功能

多数功能在鼠标停留到按钮上会有详细描述，这里仅粗略介绍

[视频介绍](https://www.bilibili.com/video/BV1BV411w7hA)

## 变换和包围盒

在transform层级的，通过碰撞盒进行一些平移操作

可以自定义以碰撞盒任意轴的最大、中间或最小为参考移动当前位置或枢轴，甚至可以忽略任意方向

这个并不只是maya自带的获取碰撞盒的方式，还有修复了获取在旋转之后的transform碰撞盒会得到旋转之后的shape碰撞盒的碰撞盒（比较绕，总之就是自带的不精准）

也可以批量操作，省时省力

## 建模

组件层级的一些操作（长远来看后面肯定会分开）

### 对齐

点对齐线和点对齐面，其中点对齐面可以自定义方向，比较方便

### 更好的法线

更可控的法线

看我视频来的应该都是为了这个功能，视频已经有详细介绍了，没看过先看看视频吧

[[Maya] 自制python插件 更可控的法线](https://www.bilibili.com/video/BV1Eh4y1C711)

这也是我第一个用OpenMaya2写的功能（上面都是pymel），om2的例子其实还挺舒服的，配合c++文档理解并不难

### 重对称顶点

[视频介绍](https://www.bilibili.com/video/BV1xacteUEc5/)

与拓扑无关的对称方法，不会改变UV，适合补救用


## 管状模型坐标对齐

专门用来对齐枢轴的

对长得像管道的、完全由4边面组成、两边有洞的几何体效果最佳

但对任意多边形来说也会有一部分功能会与预期相符，可以慢慢探索

## 烘焙准备

目前只有一个独立材质的功能

## 命名

绑定时会创建很多级的骨骼，整个功能可以在骨骼后面加序号防止重名

## ADV辅助

做动画时会选中很多控制器一起移动，除了让绑定再加个控制器或者选择集，也可以用这个功能快速选择像手指一样的控制器
