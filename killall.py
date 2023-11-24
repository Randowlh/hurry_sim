import subprocess
import os
import signal

def kill_processes_by_command(command):
    try:
        # 获取所有进程信息
        proc = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        output, _ = proc.communicate()

        # 遍历每一行输出
        for line in output.splitlines():
            # 检查进程命令是否匹配
            if command in str(line):
                # 提取进程ID
                pid = int(line.split(None, 2)[1])
                # 杀死进程
                os.kill(pid, signal.SIGKILL)
                print(f"进程 {pid} 被杀死")

    except Exception as e:
        print(f"发生错误: {e}")

# 定义特定的命令参数
commands = [
    'main.py',
]

# 对每个命令调用杀死进程的函数
for cmd in commands:
    kill_processes_by_command(cmd)
