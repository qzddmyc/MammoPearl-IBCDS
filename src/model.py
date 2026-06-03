r"""
MammoPearl 推理接口

两阶段乳腺 X 光病变检测：
  Stage 1：全图二分类（有无病变，BCEWithLogitsLoss 单 logit）
  Stage 2：条件病变类型分类（Mass / Calcification / Asymmetry_Distortion，仅在 Stage 1 判断为阳性时运行）

PredictionResult 字段：
    has_lesion        bool     Stage 1 判断结果（prob >= threshold）
    stage1_prob       float    Stage 1 输出的病变概率（0~1）
    lesion_type       str|None 预测病变类型；has_lesion=False 时为 None
    lesion_type_probs dict     各病变类型概率；has_lesion=False 时三项均为 0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision.models import EfficientNet_B4_Weights, efficientnet_b4

# 常量

_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

_LESION_TYPE_NAMES = {0: "Mass", 1: "Calcification", 2: "Asymmetry_Distortion"}

_DEFAULT_S1_CKPT = str(Path("models") / "clf_efficientnet_b4.pth")
_DEFAULT_S2_CKPT = str(Path("models") / "clf2_cond_efficientnet_b4.pth")


# 返回值类型

@dataclass
class PredictionResult:
    """单张图像的检测结果。"""

    has_lesion: bool
    """Stage 1 判断结果：prob >= threshold 为 True。"""

    stage1_prob: float
    """Stage 1 输出的病变概率（0~1）。"""

    lesion_type: str | None = None
    """预测的病变类型；has_lesion=False 时为 None。
    可能的值：'Mass' / 'Calcification' / 'Asymmetry_Distortion'"""

    lesion_type_probs: dict[str, float] = field(default_factory=lambda: {
        "Mass": 0.0,
        "Calcification": 0.0,
        "Asymmetry_Distortion": 0.0,
    })
    """Stage 2 输出的各病变类型概率；has_lesion=False 时三项均为 0.0。"""

    def __repr__(self) -> str:  # noqa: D105
        if not self.has_lesion:
            return f"PredictionResult(has_lesion=False, stage1_prob={self.stage1_prob:.4f})"
        probs = ", ".join(f"{k}={v:.4f}" for k, v in self.lesion_type_probs.items())
        return (
            f"PredictionResult(has_lesion=True, stage1_prob={self.stage1_prob:.4f}, "
            f"lesion_type='{self.lesion_type}', probs=[{probs}])"
        )


# 模型构建

def _build_stage1_model(pretrained: bool = True, in_channels: int = 3) -> nn.Module:
    """构建 Stage 1 EfficientNet-B4，输出单 logit（BCEWithLogitsLoss）。"""
    weights = EfficientNet_B4_Weights.DEFAULT if pretrained else None
    model = efficientnet_b4(weights=weights)

    if in_channels != 3:
        first_conv = model.features[0][0]
        new_conv = nn.Conv2d(
            in_channels,
            first_conv.out_channels,
            kernel_size=first_conv.kernel_size,
            stride=first_conv.stride,
            padding=first_conv.padding,
            bias=first_conv.bias is not None,
        )
        with torch.no_grad():
            new_conv.weight[:, :3, :, :] = first_conv.weight
            if in_channels > 3:
                new_conv.weight[:, 3:, :, :] = first_conv.weight[:, :in_channels - 3, :, :]
        model.features[0][0] = new_conv

    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 1),
    )
    return model


def _build_stage2_model(pretrained: bool = True, num_classes: int = 3) -> nn.Module:
    """构建 Stage 2 EfficientNet-B4，输出 num_classes 个 logit（CrossEntropyLoss）。"""
    weights = EfficientNet_B4_Weights.DEFAULT if pretrained else None
    model = efficientnet_b4(weights=weights)
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, num_classes),
    )
    return model


# 内部工具

def _preprocess_image(
        image: Union[str, bytes],
        input_h: int,
        input_w: int,
) -> torch.Tensor:
    """将图片（路径或字节）预处理为模型输入 Tensor（灰度 → letterbox → ImageNet 归一化）。"""
    if isinstance(image, str):
        raw = np.fromfile(image, dtype=np.uint8)
    elif isinstance(image, bytes):
        raw = np.frombuffer(image, dtype=np.uint8)
    else:
        raise TypeError(f"image 须为 str（路径）或 bytes，实际类型：{type(image).__name__}")

    img = cv2.imdecode(raw, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("图像解码失败，请确认文件格式正确。")

    # 转灰度
    if img.ndim == 2:
        gray = img
    elif img.shape[2] >= 4:
        gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 等比缩放 + letterbox 填充
    h, w = gray.shape
    scale = min(input_h / h, input_w / w)
    nh = int(round(h * scale))
    nw = int(round(w * scale))
    resized = cv2.resize(gray, (nw, nh), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((input_h, input_w), dtype=resized.dtype)
    pad_top = (input_h - nh) // 2
    pad_left = (input_w - nw) // 2
    canvas[pad_top: pad_top + nh, pad_left: pad_left + nw] = resized

    if canvas.dtype != np.uint8:
        canvas = cv2.normalize(canvas, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # 灰度 → RGB 3 通道
    rgb = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)  # (H, W, 3) uint8

    # ImageNet 归一化
    img_f = rgb.astype(np.float32) / 255.0
    img_f = (img_f - _IMAGENET_MEAN) / _IMAGENET_STD
    tensor = torch.from_numpy(img_f.transpose(2, 0, 1))  # (3, H, W) float32
    return tensor


def _load_stage1_model(ckpt_path: str, device: torch.device):
    """加载 Stage 1 模型及其超参数。返回 (model, input_h, input_w)。"""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    ckpt_args = ckpt.get("args", {})
    input_h = ckpt_args.get("input_h", 512)
    input_w = ckpt_args.get("input_w", 512)
    in_ch = ckpt_args.get("in_channels", 3)

    model = _build_stage1_model(pretrained=False, in_channels=in_ch)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()
    return model, input_h, input_w


def _load_stage2_model(ckpt_path: str, device: torch.device):
    """加载 Stage 2 模型及其超参数。返回 (model, input_h, input_w)。"""
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    ckpt_args = ckpt.get("args", {})
    input_h = ckpt_args.get("input_h", 512)
    input_w = ckpt_args.get("input_w", 512)
    num_classes = ckpt.get("num_classes", 3)

    model = _build_stage2_model(pretrained=False, num_classes=num_classes)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)
    model.eval()
    return model, input_h, input_w


# 主类

class MammoPearlPredictor:
    """两阶段乳腺 X 光病变检测器。

    建议在程序启动时初始化一次（模型加载耗时约 1~3 秒），
    之后重复调用 predict() 进行推理。

    Parameters
    ----------
    stage1_ckpt        : Stage 1 检查点路径
    stage2_ckpt        : Stage 2 检查点路径
    stage1_threshold   : Stage 1 阳性判定阈值（默认 0.1）
    device             : "cuda" / "cpu" / None（自动检测）
    """

    def __init__(
            self,
            stage1_ckpt: str = _DEFAULT_S1_CKPT,
            stage2_ckpt: str = _DEFAULT_S2_CKPT,
            stage1_threshold: float = 0.1,
            device: str | None = None,
    ) -> None:
        if device is None:
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self._device = torch.device(device)

        self._threshold = stage1_threshold

        self._s1_model, self._s1_h, self._s1_w = _load_stage1_model(
            stage1_ckpt, self._device
        )
        self._s2_model, self._s2_h, self._s2_w = _load_stage2_model(
            stage2_ckpt, self._device
        )

    def predict(self, *, image: Union[str, bytes]) -> PredictionResult:
        """对单张图像进行两阶段检测。image 为文件路径（str）或字节数据（bytes）。"""
        # Stage 1
        t1 = _preprocess_image(image, self._s1_h, self._s1_w)
        inp1 = t1.unsqueeze(0).to(self._device)

        with torch.no_grad():
            logit = self._s1_model(inp1).squeeze()  # scalar logit
            s1_prob = torch.sigmoid(logit.float()).item()

        has_lesion = s1_prob >= self._threshold

        if not has_lesion:
            return PredictionResult(
                has_lesion=False,
                stage1_prob=s1_prob,
            )

        # Stage 2
        t2 = _preprocess_image(image, self._s2_h, self._s2_w)
        inp2 = t2.unsqueeze(0).to(self._device)

        with torch.no_grad():
            logits = self._s2_model(inp2)  # (1, 3)
            probs = torch.softmax(logits.float(), dim=1).squeeze(0).cpu().numpy()

        pred_id = int(np.argmax(probs))
        pred_name = _LESION_TYPE_NAMES[pred_id]

        return PredictionResult(
            has_lesion=True,
            stage1_prob=s1_prob,
            lesion_type=pred_name,
            lesion_type_probs={
                "Mass": float(probs[0]),
                "Calcification": float(probs[1]),
                "Asymmetry_Distortion": float(probs[2]),
            },
        )
