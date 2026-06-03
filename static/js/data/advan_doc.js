/**
 * 将所有需要的文本放在此文件，即可被自动渲染至advan.html页面
 * 规则：
 *  - 每个对象需要包含一个type键，其值只能为title、txt、img
 *  - 当type为title或txt时，需要包含content项，表示文本内容
 *      - type为title时，会被自动加上序号
 *  - 当type为img时，需要包含url与title键，url存放的是图片名称，title存放的是图片介绍
 *      - 其中，图片文件必须放在/static/assets/img文件夹下
 *      - 若图片不需要介绍内容，保持title的键为空字符串即可
 */

export const Advans = [
    {
        type: 'title',
        content: '乳腺 X 光图像专项预处理'
    },
    {
        type: 'txt',
        content: '原始乳腺钼靶影像在送入深度学习模型之前，预先经过三步专项预处理以消除噪声干扰、凸显细微病灶。'
    },
    {
        type: 'txt',
        content: '第一步，利用 Otsu 自动阈值分割配合最大轮廓掩膜提取乳腺有效区域，去除背景黑边与扫描仪人工标记，使后续模型聚焦真正的腺体组织。第二步，应用双边滤波进行结构保边降噪，在平滑随机噪声的同时保留病灶边缘与微小钙化点的锐利轮廓，避免过度模糊导致细节丢失。第三步，通过 CLAHE（对比度受限自适应直方图均衡化）进行局部对比度增强，使隐匿于高密度腺体内的早期微小病灶在视觉与特征层面均得到有效凸显，为模型提供质量更高的输入信号。'
    },
    {
        type: 'title',
        content: '两阶段级联分类架构'
    },
    {
        type: 'txt',
        content: '本项目深度学习路线采用"粗筛 + 精分"的两阶段级联设计，在高召回率与精细病变分型之间取得最优平衡。'
    },
    {
        type: 'txt',
        content: 'Stage 1 对每张乳腺 X 光图像进行全图二分类（有无病变），以 F2 分数为验证监控指标，将漏检惩罚权重放大为准确率的两倍，在 0.10 概率阈值下 Recall 约达 95.5%，确保绝大多数阳性病例不被漏筛。Stage 2 仅对 Stage 1 判定为阳性的图像运行，对病变类型进行三分类细分：Mass（肿块）、Calcification（可疑钙化）、Asymmetry_Distortion（不对称/结构扭曲，含皮肤及其他），以三类 macro F1 作为 checkpoint 保存判据。两阶段设计让系统同时满足"尽量不漏诊"与"提供可用病变类型"的双重临床需求，Stage 2 在训练时也纳入阴性图像，使其能将 Stage 1 的误报重新纠正为 No Finding，进一步提升流水线整体精度。'
    },
    {
        type: 'title',
        content: 'EfficientNet-B4 骨干网络与分层学习率'
    },
    {
        type: 'txt',
        content: 'EfficientNet-B4 是两个阶段共用的主干网络，其核心创新在于对网络宽度、深度与输入分辨率进行联合复合缩放，以较少参数量取得远超同规模网络的特征提取能力。本项目以 ImageNet 预训练权重初始化，采用分层学习率策略进行微调。'
    },
    {
        type: 'txt',
        content: 'Backbone（features 层）的学习率设定为基础学习率的 0.1 倍，分类头使用完整学习率。这一策略防止 ImageNet 预学到的通用视觉特征被快速覆盖，同时让新增分类头迅速适配乳腺病变分布，在医疗影像小样本场景下显著降低过拟合风险。结合 CosineAnnealingLR 调度和 Early Stopping（patience=8~10），模型可在有限轮次内稳定收敛至最优检查点。'
    },
    {
        type: 'title',
        content: '类别不平衡处理：WeightedRandomSampler'
    },
    {
        type: 'txt',
        content: '乳腺 X 光数据集存在极度类别不平衡：无病变图像与各病变类别的数量比约为 44 : 2.5 : 0.7 : 1（No Finding : Mass : Calcification : Asymmetry_Distortion）。若直接训练，模型将陷入"全部预测为阴性"的退化态，使病变漏检率居高不下。'
    },
    {
        type: 'txt',
        content: '本项目在两个训练阶段均引入 WeightedRandomSampler，根据每张图像所属类别的逆频率动态计算采样权重，使每个 mini-batch 中各类别样本趋于均衡，从源头上解决训练信号失衡问题。在 Stage 1 中，WeightedRandomSampler 与 BCEWithLogitsLoss（pos_weight=1.0）配合使用——由于采样层已完成平衡，损失函数无需再做额外的正样本补偿，避免双重矫枉过正；Stage 2 同理处理三类病变之间的比例差异。'
    },
    {
        type: 'title',
        content: 'bfloat16 混合精度训练与训练稳定性保障'
    },
    {
        type: 'txt',
        content: '本项目充分利用 NVIDIA RTX 4090 的 bfloat16 硬件加速能力，通过 PyTorch AMP 实现混合精度训练。'
    },
    {
        type: 'txt',
        content: '与 float16 相比，bfloat16 保留了与 float32 相同的指数位宽（8 位），数值范围更广，训练过程无需额外的损失缩放调参即可保持数值稳定。开启混合精度后，显存占用减少约 30–40%，使单卡 24 GB VRAM 环境下可将 batch size 提升至 16，并以 512×512 分辨率充分利用乳腺钼靶影像的细节纹理。此外，配合梯度裁剪（clip_grad_norm=1.0）防止梯度爆炸，以及 CosineAnnealingLR 学习率退火调度，进一步保证训练全程的数值稳定性。'
    },
    {
        type: 'title',
        content: 'GradCAM 可解释性与端到端推理接口'
    },
    {
        type: 'txt',
        content: '为提升模型决策的可解释性，Stage 1 测试阶段集成了 GradCAM（梯度加权类激活映射）热图功能。GradCAM 利用目标类别对最后一个卷积层的梯度，计算每个空间位置对分类结果的权重贡献，生成与原始图像像素对齐的热力图叠加可视化。通过热图可直观验证模型是否真正关注了病灶区域，而非依赖无关背景（如扫描仪边框标记）做出预测，帮助快速定位训练数据或预处理的潜在问题。该功能作为可选模块集成（基于 pytorch-grad-cam），不影响核心训练与推理流程。'
    },
    {
        type: 'txt',
        content: '在部署接口层面，项目提供了 MammoPearlPredictor 推理类，将两阶段流水线封装为单一调用入口，支持图片路径与原始字节两种输入方式。模型在初始化时一次性加载至设备，重复调用无额外开销，适合批量处理场景。推理结果以结构化对象返回，包含 has_lesion（是否检出病变）、stage1_prob（病变概率）、lesion_type（病变类型字符串）、lesion_type_id（类型 ID）和 lesion_type_probs（三类概率字典）五项关键字段，接口设计清晰，便于与上层应用系统集成对接。'
    }
];