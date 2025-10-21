document.addEventListener('DOMContentLoaded', () => {
    const maps = {
        'txt': 'p',
        'img': 'img',
        'title': 'h2',
    }
    // Ensure the visibility of images in all conditions, and use local path here.
    const baseImgPath = '../static/assets/img/';
    const writeZone = document.getElementById('write');
    writeZone.innerHTML = '';

    function validateAdvans(advans) {
        if (!Array.isArray(advans)) {
            console.log('错误：Advans不是数组');
            return false;
        }
        for (let i = 0; i < advans.length; i++) {
            const item = advans[i];
            if (typeof item !== 'object' || item === null || Array.isArray(item)) {
                console.log(`错误：索引为${i}的元素不是对象`);
                return false;
            }
            const keys = Object.keys(item);
            if (keys.length !== 2) {
                console.log(`错误：索引为${i}的对象包含${keys.length}个键，应仅包含type和content`);
                return false;
            }
            if (!keys.includes('type') || !keys.includes('content')) {
                console.log(`错误：索引为${i}的对象缺少type或content键`);
                return false;
            }
            const validTypes = ['title', 'txt', 'img'];
            if (!validTypes.includes(item.type)) {
                console.log(`错误：索引为${i}的对象type值无效，当前值为${item.type}，允许值为${validTypes.join('、')}`);
                return false;
            }
        }
        return true;
    }

    if (!validateAdvans(Advans)) {
        alert('Warning: Advans Doc 校验错误');
        return;
    }

    const fragment = document.createDocumentFragment();
    Advans.forEach(e => {
        const type = maps[e.type];
        const dom = document.createElement(type);
        if (type === 'img') dom.src = baseImgPath + e.content;
        else dom.textContent = e.content;
        fragment.appendChild(dom);
    });
    writeZone.appendChild(fragment);

    setTimeout(() => {
        if (window.updateScrollIndicator) window.updateScrollIndicator();
        else updateScrollIndicator();
    }, 0);
});

document.addEventListener('DOMContentLoaded', function () {
    doms = {
        header: document.querySelector('.main-header'),
        container: document.querySelector('.container'),
    }

    // f(x) = e ^ (x - 1), for x in (0, 1)
    function f_ex1(x) {
        if (x <= 0 || x >= 1) {
            console.error('f(x) = e ^ (x - 1) Error.');
            return 100;
        }
        return Math.exp(x - 1);
    }

    function handleViewportResize() {
        // 获取当前视口宽度
        const viewportWidth = window.innerWidth;

        if (viewportWidth < 560) {
            doms.container.style.marginTop = (doms.header.clientHeight + 18) * f_ex1(viewportWidth / 560) + 'px';
        } else {
            doms.container.style.marginTop = '';
        }
    }

    handleViewportResize();

    window.addEventListener('resize', handleViewportResize);
});