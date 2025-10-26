// 注意事件生命周期问题

document.addEventListener('DOMContentLoaded', () => {
    const footerContainer = document.querySelector('.footer-container');
    const dotsContainer = document.querySelector('.footer-dots');
    const dotSpacing = 18;      // 圆点间距, px, default: 20
    const baseAlpha = 0;        // default: 0.15
    const maxAlpha = 1;
    const maxDistance = 120;    // 渲染距离, default: 150
    let dots = [];

    const R = 0;        // default: 139
    const G = 204;      // default: 92
    const B = 255;      // default: 246

    function generateDots() {
        dotsContainer.innerHTML = '';
        dots = [];
        const containerWidth = dotsContainer.offsetWidth;
        const containerHeight = dotsContainer.offsetHeight;
        const cols = Math.ceil((containerWidth * 2) / dotSpacing);
        const rows = Math.ceil((containerHeight * 2) / dotSpacing);
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const dot = document.createElement('div');
                dot.classList.add('dot');
                const x = col * dotSpacing;
                const y = row * dotSpacing;
                dot.style.left = `${x}px`;
                dot.style.top = `${y}px`;
                dotsContainer.appendChild(dot);
                dots.push(dot);
            }
        }
    }
    const viewportWidth = window.innerWidth;
    if (viewportWidth >= 768) {
        generateDots();
    }
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
    footerContainer.addEventListener('mouseleave', () => {
        dots.forEach(dot => {
            dot.style.backgroundColor = `rgba(${R}, ${G}, ${B}, ${baseAlpha})`;
        });
    });
    function cleanupDots() {
        dotsContainer.innerHTML = '';
        dots = [];
    }
    let resizeTimeout;
    window.addEventListener('resize', () => {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 768) {
            clearTimeout(resizeTimeout);
            cleanupDots();
            return;
        }
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            generateDots();
        }, 100);    // wait for resize
    });
});
