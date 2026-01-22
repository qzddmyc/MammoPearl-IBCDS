document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('dotsCanvas');
    const container = document.querySelector('.footer-dots');
    const footer = document.querySelector('.footer-container');

    if (!canvas || !container || !footer) return;

    const ctx = canvas.getContext('2d');
    const config = {
        dotSpacing: 18,
        baseAlpha: 0,
        maxAlpha: 1,
        maxDistance: 120,
        R: 0, G: 204, B: 255
    };

    let dots = [];
    let mouse = { x: -1000, y: -1000 };
    let isAnimating = false;

    function initCanvas() {
        const dpr = window.devicePixelRatio || 1;
        const rect = container.getBoundingClientRect();
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        ctx.scale(dpr, dpr);

        dots = [];
        for (let x = 0; x < rect.width; x += config.dotSpacing) {
            for (let y = 0; y < rect.height; y += config.dotSpacing) {
                dots.push({ x, y });
            }
        }
        if (!isAnimating) renderFrame();
    }

    function renderFrame() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        dots.forEach(dot => {
            const dx = mouse.x - dot.x;
            const dy = mouse.y - dot.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < config.maxDistance) {
                const intensity = 1 - Math.pow(distance / config.maxDistance, 2);
                const alpha = config.baseAlpha + (intensity * (config.maxAlpha - config.baseAlpha));
                ctx.fillStyle = `rgba(${config.R}, ${config.G}, ${config.B}, ${alpha})`;
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, 0.85, 0, Math.PI * 2);
                ctx.fill();
            } else if (config.baseAlpha > 0) {
                ctx.fillStyle = `rgba(${config.R}, ${config.G}, ${config.B}, ${config.baseAlpha})`;
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, 0.85, 0, Math.PI * 2);
                ctx.fill();
            }
        });
    }

    function loop() {
        if (!isAnimating) return;
        renderFrame();
        requestAnimationFrame(loop);
    }

    function startAnimation() {
        if (!isAnimating) {
            isAnimating = true;
            loop();
        }
    }

    function stopAnimation() {
        isAnimating = false;
    }

    footer.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
        startAnimation();
    });

    footer.addEventListener('mouseleave', () => {
        mouse.x = -1000;
        mouse.y = -1000;
        renderFrame();
        stopAnimation();
    });

    window.addEventListener('resize', initCanvas);
    if (window.innerWidth >= 768 && window.matchMedia("(hover: hover)").matches) initCanvas();
});