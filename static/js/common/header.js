import { debounce } from "../tools/debounce.js";

// .container的缩放不包含在此文件内

!function () {
    const doms = {
        banner: document.querySelector('.banner'),
        header: document.querySelector('.main-header'),
    }
    if (!doms.banner) {
        doms.banner = document.querySelector('.container');
    }
    let lastScrollTop = 0;
    function handleScroll() {
        const banner_top = doms.banner.offsetTop;
        const header_height = doms.header.clientHeight;
        const scroll_threshold = banner_top - header_height - 5;
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        if (scrollTop === 0) {
            doms.header.classList.remove('scroll-out');
            lastScrollTop = 0;
            return;
        }
        if ((scroll_threshold < 0 && scrollTop > 0) || (scroll_threshold >= 0 && scrollTop >= scroll_threshold)) {
            doms.header.classList.add('scroll-out');
        }
        else {
            doms.header.classList.remove('scroll-out');
        }
        if (scrollTop < lastScrollTop && scrollTop > 0) {
            doms.header.classList.remove('scroll-out');
        }
        lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
    }
    const debouncedScroll = debounce(handleScroll, 100);    // 防抖
    window.addEventListener('scroll', debouncedScroll);
}();

!function () {
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

    function handleViewportResize() {
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 560) {
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
    handleViewportResize();
    window.addEventListener('resize', handleViewportResize);
}();

!function () {
    const menuContainer = document.querySelector('.mobile-menu-container');
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const html = document.documentElement;
    menuBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        menuContainer.classList.toggle('active');
        if (menuContainer.classList.contains('active')) {
            html.classList.add('menu-open');
        } else {
            html.classList.remove('menu-open');
        }
    });
    document.querySelectorAll('.mobile-menu-item').forEach(item => {
        item.addEventListener('click', function (e) {
            e.stopPropagation();
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        });
    });
    document.addEventListener('click', function (e) {
        if (menuContainer.classList.contains('active') && !menuContainer.contains(e.target)) {
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        }
    });
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 1025 && menuContainer.classList.contains('active')) {
            menuContainer.classList.remove('active');
            html.classList.remove('menu-open');
        }
    });
}();