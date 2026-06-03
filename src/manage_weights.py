"""
该文件用于模型权重文件的拆分与重组
"""

import os
import sys

# 模型权重文件列表
WEIGHT_FILES = [
    "static/assets/pth/clf_efficientnet_b4.pth",
    "static/assets/pth/clf2_cond_efficientnet_b4.pth"
]

# 每个分片的大小：设置为 40MB
CHUNK_SIZE = 40 * 1024 * 1024


def split_files():
    for file_path in WEIGHT_FILES:
        if not os.path.exists(file_path):
            print("[Warning] File not exist while splitting:", file_path)
            continue

        with open(file_path, 'rb') as f:
            chunk_num = 0
            while True:
                chunk_data = f.read(CHUNK_SIZE)
                if not chunk_data:
                    break
                # 分片文件名，形如 clf_efficientnet_b4.pth.part_00
                chunk_name = f"{file_path}.part_{chunk_num:02d}"
                with open(chunk_name, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)
                chunk_num += 1
    print("[Info] Split successfully.")


def merge_files():
    for file_path in WEIGHT_FILES:
        # 寻找属于该文件的所有分片
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)

        # 确保目标目录存在
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        chunks = sorted([
            os.path.join(dir_name, f) for f in os.listdir(dir_name or '.')
            if f.startswith(base_name + ".part_")
        ])

        if not chunks:
            print("[Warning] No chunks found for", base_name)
            continue

        with open(file_path, 'wb') as target_file:
            for chunk in chunks:
                with open(chunk, 'rb') as f:
                    target_file.write(f.read())
    print("[Info] Merge completed.")
