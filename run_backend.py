"""后端启动脚本:带崩溃自愈。

长期运行时 uvicorn 可能因异常/资源问题静默退出,导致网页与 API 不可用。
本脚本以子进程方式运行 uvicorn,异常退出后间隔数秒自动重启,重启日志写入 backend.log。
"""

import logging
import os
import socket
import subprocess
import sys
import time

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "backend.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("run_backend")

HOST = os.getenv("BACKEND_HOST", "127.0.0.1")  # 容器/局域网部署设 0.0.0.0
PORT = int(os.getenv("BACKEND_PORT", "8100"))
RESTART_DELAY_SECONDS = 5
# 端口等待上限:重启场景下旧实例正在退出,等待它释放端口而不是立刻放弃
PORT_WAIT_SECONDS = 30
LOG_HANDLE = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
GUARD_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_backend.lock")
_GUARD_FD: int | None = None


def _acquire_guard() -> bool:
    """守护单例锁:用文件字节锁。

    系统在进程退出/崩溃时自动释放锁,因此不受 PID 复用、残留 PID、
    半死进程(OpenProcess 可打开但进程名查询失败)的干扰——这些情况
    会让基于 PID 的存活判断永久误判为"守护仍在"。
    """
    global _GUARD_FD
    fd = os.open(GUARD_LOCK_FILE, os.O_CREAT | os.O_RDWR)
    try:
        if os.name == "nt":
            import msvcrt
            # 锁区放在 4096 字节处,避免锁住 PID 文本导致锁文件不可读
            os.lseek(fd, 4096, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        os.close(fd)
        return False
    os.lseek(fd, 0, os.SEEK_SET)
    os.truncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("ascii"))
    _GUARD_FD = fd  # 持有到进程结束,由系统释放
    return True


def _port_in_use(port: int) -> bool:
    """端口是否已有服务监听(避免多守护互相抢端口造成重启死循环)。"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def main():
    if not _acquire_guard():
        logger.info("守护已存在(run_backend.lock),本实例退出")
        return
    logger.info("启动后端守护(%s:%s)", HOST, PORT)
    while True:
        # 端口占用检测:有界等待,给"旧实例正在退出"的重启场景留出释放时间;
        # 若端口持续被别的服务占用,则本守护退出,避免双服务互抢端口
        for _ in range(PORT_WAIT_SECONDS):
            if not _port_in_use(PORT):
                break
            time.sleep(1)
        else:
            logger.info("端口 %s 持续被占用(%ss),本守护退出", PORT, PORT_WAIT_SECONDS)
            return
        try:
            # 通过环境变量告知子进程"我被守护监管",供 /api/admin/restart 判断
            # 重启该由守护完成还是自行派生守护
            child_env = dict(os.environ, BACKEND_DAEMON_PID=str(os.getpid()))
            proc = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "backend.main:app",
                 "--host", HOST, "--port", str(PORT)],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                env=child_env,
                stdout=LOG_HANDLE, stderr=subprocess.STDOUT,
            )
        except Exception as e:
            logger.error("启动 uvicorn 失败: %s", e)
            time.sleep(RESTART_DELAY_SECONDS)
            continue
        rc = proc.wait()
        if rc == 0:
            # 正常退出(如 Ctrl+C 停 uvicorn):退出守护,避免无谓重启
            logger.info("uvicorn 正常退出(rc=0),守护结束")
            return
        logger.info("uvicorn 异常退出(rc=%s),%ss 后重启", rc, RESTART_DELAY_SECONDS)
        time.sleep(RESTART_DELAY_SECONDS)


if __name__ == "__main__":
    main()
