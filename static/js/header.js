// .container的缩放不包含在此文件内

document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        banner: document.querySelector('.banner'),
        header: document.querySelector('.main-header'),
    }

    if (!doms.banner) {
        doms.banner = document.querySelector('.container');
    }

    // console.log('scroll' + scroll_threshold);

    let lastScrollTop = 0;

    function handleScroll() {
        const banner_top = doms.banner.offsetTop;
        const header_height = doms.header.clientHeight;
        const scroll_threshold = banner_top - header_height - 5;

        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        // console.log(scrollTop);
        // console.log((scroll_threshold < 0 && scrollTop > 0));

        if ((scroll_threshold < 0 && scrollTop > 0) || (scroll_threshold >= 0 && scrollTop >= scroll_threshold)) {
            doms.header.classList.add('scroll-out');
        }
        else {
            doms.header.classList.remove('scroll-out');
        }

        // 向上滚动时显示header
        if (scrollTop < lastScrollTop && scrollTop > 0) {
            doms.header.classList.remove('scroll-out');
        }
        // 更新上一次滚动位置
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;

    }

    // 防抖函数包装，设置延迟时间为100ms
    const debouncedScroll = debounce(handleScroll, 100);

    // 绑定scroll事件
    window.addEventListener('scroll', debouncedScroll);
});


document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        header_left: document.querySelector('.main-header-left'),
        header_right: document.querySelector('.main-header-right'),
        container: document.querySelector('.container'),
        header: document.querySelector('.main-header'),
        zipped_options: document.querySelector('.mobile-menu-container'),
    };

    // g(t) = -4(t - 1)² + 1, for t in (0.5, 1)
    function quadraticFunction(t) {
        if (t <= 0.5) return 0;
        if (t >= 1) return 1;
        return -4 * Math.pow(t - 1, 2) + 1;
    }

    // 定义处理视口变化的函数
    function handleViewportResize() {
        // 获取当前视口宽度
        const viewportWidth = window.innerWidth;

        if (viewportWidth < 560) {
            // 占比
            const ratio = viewportWidth / 560;

            const paddingTopAndBottom = quadraticFunction(ratio) * 20;

            doms.header_left.style.transform = `scale(${ratio})`;
            doms.header.style.padding = `${paddingTopAndBottom}px 5vw`;
            doms.header.style.paddingRight = '0px';

            doms.zipped_options.style.transform = `scale(${ratio})`;
            doms.zipped_options.style.top = paddingTopAndBottom + 2 + 'px';
            doms.zipped_options.style.right = '5vw';
        } else {
            doms.header_left.style.transform = 'none';
            doms.zipped_options.style.transform = 'none';

            // 清除内联样式
            doms.header.style.padding = '';
            doms.zipped_options.style.top = '';
            doms.zipped_options.style.right = '';
        }

        if (viewportWidth < 1024) {
            doms.header_right.classList.add('disappear');
            doms.zipped_options.classList.remove('disappear');
        } else {
            doms.header_right.classList.remove('disappear');
            doms.zipped_options.classList.add('disappear');
        }
    }

    // 初始执行一次
    handleViewportResize();

    window.addEventListener('resize', handleViewportResize);

});


// 移动端菜单交互逻辑
document.addEventListener('DOMContentLoaded', function () {
    const menuContainer = document.querySelector('.mobile-menu-container');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    // const menuContent = document.querySelector('.mobile-menu-content');
    const html = document.documentElement;

    // 切换菜单状态
    menuBtn.addEventListener('click', function (e) {
        e.stopPropagation(); // 防止事件冒泡
        menuContainer.classList.toggle('active');

        // 添加/移除阻止页面滚动的类
        if (menuContainer.classList.contains('active')) {
            html.classList.add('menu-open');
        } else {
            html.classList.remove('menu-open');
        }
    });

    // 点击菜单项关闭菜单
    document.querySelectorAll('.mobile-menu-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.stopPropagation();
            // console.log('点击了:', this.textContent.trim());
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        });
    });

    // 点击页面其他区域关闭菜单
    document.addEventListener('click', function (e) {
        if (menuContainer.classList.contains('active') && !menuContainer.contains(e.target)) {
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        }
    });

    // 监听窗口大小变化，确保在大屏幕上菜单是关闭的
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 1025 && menuContainer.classList.contains('active')) {
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        }
    });
});