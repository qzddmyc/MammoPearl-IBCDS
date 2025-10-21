// 事件生命周期

document.addEventListener('DOMContentLoaded', () => {
    const footerContainer = document.querySelector('.footer-container');
    const dotsContainer = document.querySelector('.footer-dots');
    const dotSpacing = 18; // 圆点间距, px, default: 20
    const baseAlpha = 0;     // default: 0.15
    const maxAlpha = 1;
    const maxDistance = 120;    // 渲染距离, default: 150
    let dots = []; // 存储圆点元素的数组

    const R = 0;        // default: 139
    const G = 204;      // default: 92
    const B = 255;      // default: 246

    // 生成网格状圆点的函数
    function generateDots() {
        // 清空现有圆点
        dotsContainer.innerHTML = '';
        dots = [];

        const containerWidth = dotsContainer.offsetWidth;
        const containerHeight = dotsContainer.offsetHeight;

        // 计算网格行列数（扩展1倍范围）
        const cols = Math.ceil((containerWidth * 2) / dotSpacing);
        const rows = Math.ceil((containerHeight * 2) / dotSpacing);

        // 生成网格状排列的圆点
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const dot = document.createElement('div');
                dot.classList.add('dot');

                // 计算网格中每个点的精确坐标
                const x = col * dotSpacing;
                const y = row * dotSpacing;

                dot.style.left = `${x}px`;
                dot.style.top = `${y}px`;

                dotsContainer.appendChild(dot);
                dots.push(dot);
            }
        }
    }

    // 初始化生成圆点
    const viewportWidth = window.innerWidth;
    if (viewportWidth >= 768) {
        generateDots();
    }

    // 鼠标移动事件处理
    footerContainer.addEventListener('mousemove', (e) => {
        const rect = dotsContainer.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        dots.forEach(dot => {
            const dotRect = dot.getBoundingClientRect();
            const dotX = dotRect.left - rect.left + 0.5;
            const dotY = dotRect.top - rect.top + 0.5;

            const distance = Math.sqrt(
                Math.pow(mouseX - dotX, 2) +
                Math.pow(mouseY - dotY, 2)
            );

            if (distance < maxDistance) {
                const intensity = 1 - Math.pow(distance / maxDistance, 2);
                const alpha = baseAlpha + (intensity * (maxAlpha - baseAlpha));
                dot.style.backgroundColor = `rgba(${R}, ${G}, ${B}, ${alpha})`;
            } else {
                dot.style.backgroundColor = `rgba(${R}, ${G}, ${B}, ${baseAlpha})`;
            }
        });
    });

    // 鼠标离开事件
    footerContainer.addEventListener('mouseleave', () => {
        dots.forEach(dot => {
            dot.style.backgroundColor = `rgba(${R}, ${G}, ${B}, ${baseAlpha})`;
        });
    });

    function cleanupDots() {
        // 移除所有圆点元素
        dotsContainer.innerHTML = '';
        dots = [];
    }

    // 监听窗口大小变化，重新生成圆点
    let resizeTimeout;
    window.addEventListener('resize', () => {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 768) {
            clearTimeout(resizeTimeout);
            cleanupDots();
            return;
        }
        // 防抖
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            generateDots();
        }, 100); // 100ms延迟，等待 resize 完成
    });
});
