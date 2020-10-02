# Video Viewer 视频查看器

## 安装
请把编译好的ffmpeg可执行文件(ffmpeg.exe)放到和 main.py 相同的目录下.
支持 python3. python2 不知道.
使用 pip 安装依赖:  tkinter, termcolor, imageio, PIL, winregistry, ffmpy

## 使用方法

View video / pictures frame by frame.

主要用来逐帧看视频/动图.

左键, 右键, A, D 逐帧查看.
上, 下, W, S 跳 5 倍帧数查看.
空格暂停/播放.

+, - 键调整跳帧倍数.

键盘输入数字然后按回车, 可以跳到给定帧数. 回车之前的输入的数字在状态栏有显示.

R 重置缩放视图大小和位置.

以管理员身份运行命令行, 在这个命令行内用 python 运行 registerContextMenu 脚本, 可以右键菜单打开 Video Viewer.
同样以管理员身份运行 removeContextMenu 可以移除这一菜单.
如果重装 Python 且路径被改变了, 那么需要重新运行 registerContextMenu, 运行注册表.
