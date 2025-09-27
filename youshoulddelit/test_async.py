import asyncio
import time


async def task(name, duration):
    print(f"任务 {name} 开始...")
    await asyncio.sleep(duration)
    print(f"任务 {name} 完成！耗时 {duration}s")
    return duration


def handle_results(future):
    """
    future 参数是已经完成的 _GatheringFuture 对象。
    """
    try:
        results = future.result()  # 获取 asyncio.gather 的结果
        print("\n[回调函数] 所有任务已完成！")
        print(f"[回调函数] 结果: {results}")
    except Exception as e:
        print(f"\n[回调函数] 任务执行失败: {e}")


async def main():
    start_time = time.time()

    # 1. 创建基础任务
    task1 = asyncio.create_task(task("A", 3))
    task2 = asyncio.create_task(task("B", 2))

    # 2. 直接调用 asyncio.gather，得到一个可等待的 future 对象
    gather_future = asyncio.gather(task1, task2)

    # 3. 为这个 gather_future 注册一个回调函数
    gather_future.add_done_callback(handle_results)

    print("所有任务已提交给事件循环，注册了回调函数。主线程可以做其他事...")

    # 模拟主线程做其他工作
    await asyncio.sleep(4)
    print("\n主线程模拟工作完成。此时回调函数应该已经执行过了。")

    # 关键：我们必须等待 gather_future 完成，否则 main 协程结束后程序会退出
    # 即使我们有回调，也需要确保事件循环在任务完成前不被关闭
    # 这里的 await 会确保 main 协程一直等到所有任务都处理完毕

    await gather_future
    print('abc')

    end_time = time.time()
    print(f"\n程序总耗时: {end_time - start_time:.2f}s")


asyncio.run(main())
