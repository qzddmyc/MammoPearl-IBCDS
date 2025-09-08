// 最好在header.js之后引入！

document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        banner_btn: document.querySelector('.button-to-detect'),
        container: document.querySelector('.container'),
        header: document.querySelector('.main-header'),
        feature_card_container: document.querySelector('.features'),
        feature_card_h2: document.querySelector('.info-section h2'),
        // feature_card_p: document.querySelectorAll('.info-section>p'),
        feature_card_p_oneline: document.querySelector('.info-section .p-1'),
        feature_card_p_twolines: document.querySelectorAll('.info-section .p-2'),
        footer_content: document.querySelector('.footer-content'),
        footer_container: document.querySelector('.footer-container'),
        footer_bottom: document.querySelector('.footer-bottom'),
        footer_copyright: document.querySelector('.footer-copyright'),
    };

    // f(x) = e ^ (x - 1), for x in (0, 1)
    function f_ex1(x) {
        if (x <= 0 || x >= 1) {
            console.error('f(x) = e ^ (x - 1) Error.');
            return 100;
        }
        return Math.exp(x - 1);
    }

    // g(t) = -4(t - 1)² + 1, for t in (0.5, 1)
    function gt(t) {
        if (t <= 0.5) return 0;
        if (t >= 1) return 1;
        return -4 * Math.pow(t - 1, 2) + 1;
    }

    // h(x) = 0.3x + 0.7, through (0.7, 0) and (1, 1)
    function hx(x) {
        if (x <= 0 || x >= 1) {
            console.error('h(x) = 0.3x + 0.7 error');
            return 100;
        }
        return 0.3 * x + 0.7;
    }

    function handleViewportResize() {
        // 获取当前视口宽度
        const viewportWidth = window.innerWidth;

        // banner的按钮缩放
        if (viewportWidth < 500) {
            const ratio = viewportWidth / 500 * 0.8;
            doms.banner_btn.style.transform = `scale(${ratio})`;

        } else {
            doms.banner_btn.style.transform = '';
        }

        // banner的margin-top
        if (viewportWidth < 560) {
            doms.container.style.marginTop = (doms.header.clientHeight + 48) * f_ex1(viewportWidth / 560) + 'px';
        } else {
            doms.container.style.marginTop = '';
        }

        // 底下三个feature的缩放
        if (viewportWidth < 615) {
            if (viewportWidth >= 280) {
                doms.feature_card_container.style.zoom = hx(viewportWidth / 615);
                doms.container.style.minHeight = '';
            } else {
                doms.feature_card_container.style.zoom = viewportWidth / 480;
                doms.container.style.minHeight = 'auto';
            }
        } else {
            doms.feature_card_container.style.zoom = '';
            doms.container.style.minHeight = '';
        }

        // container的margin-bottom的缩放
        if (viewportWidth < 425) {
            doms.container.style.marginBottom = 100 * (viewportWidth / 425) + 'px';
        } else {
            doms.container.style.marginBottom = '';
        }

        // "精准医学检验解决方案"的缩放
        if (viewportWidth <= 768) {
            doms.feature_card_h2.style.fontSize = f_ex1(0.0416 * viewportWidth / 32) * 32 + 'px';
            doms.feature_card_h2.style.zoom = 1.2;
        } else {
            doms.feature_card_h2.style.fontSize = '';
            doms.feature_card_h2.style.zoom = '';
        }

        // "精准医学检验解决方案"下方的一行时的p元素的缩放
        if (viewportWidth <= 768 && viewportWidth > 425) {
            doms.feature_card_p_oneline.style.fontSize = f_ex1(0.0208 * viewportWidth / 16) * 16 + 'px';
            doms.feature_card_p_oneline.style.zoom = 1.2;
        } else {
            doms.feature_card_p_oneline.style.fontSize = '';
            doms.feature_card_p_oneline.style.zoom = '';
        }

        // 控制p是一行还是两（或更多）行
        if (viewportWidth <= 425) {
            // 借用header.css中的disappear类, display: none !important
            doms.feature_card_p_oneline.classList.add('disappear');
            doms.feature_card_p_twolines.forEach(p => {
                p.classList.remove('disappear');
            });

            doms.feature_card_p_twolines.forEach(p => {
                p.style.fontSize = 13 + 'px';
            });
        } else {
            doms.feature_card_p_oneline.classList.remove('disappear');
            doms.feature_card_p_twolines.forEach(p => {
                p.classList.add('disappear');
            });

            doms.feature_card_p_twolines.forEach(p => {
                p.style.fontSize = '';
            });
        }

        // footer内容区与padding的缩放
        if (viewportWidth <= 480) {
            const ratio = viewportWidth / 480;

            doms.footer_content.style.zoom = ratio;
            doms.footer_container.style.paddingTop = ratio * 50 + 'px';
            doms.footer_container.style.paddingBottom = ratio * 30 + 'px';
            doms.footer_bottom.style.paddingTop = '0px';
            doms.footer_copyright.style.zoom = ratio;
        } else {
            doms.footer_content.style.zoom = '';
            doms.footer_container.style.paddingTop = '';
            doms.footer_bottom.style.paddingTop = '';
            doms.footer_copyright.style.zoom = '';
        }

    }

    handleViewportResize();

    window.addEventListener('resize', handleViewportResize);
});

document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        logins: document.querySelectorAll('.login-door'),
        logouts: document.querySelectorAll('.logout-door'),
    };

    let usrInfo = localStorage.getItem(LocalStorage_DataName);
    const classNameForHide = 'hide-me';

    function showLogin_hideLogout() {
        doms.logins.forEach(item => {
            item.classList.remove(classNameForHide);
        });
        doms.logouts.forEach(item => {
            item.classList.add(classNameForHide);
        });
    }

    function showLogout_hideLogin() {
        doms.logins.forEach(item => {
            item.classList.add(classNameForHide);
        });
        doms.logouts.forEach(item => {
            item.classList.remove(classNameForHide);
        });
    }

    function refreshLoginButtons() {
        if (usrInfo) { showLogout_hideLogin(); }
        else { showLogin_hideLogout(); }
    }

    refreshLoginButtons();

    function clearLocalUsrInfo() {
        /* 清除用户登录信息，包含了二次确认与刷新页面的按钮操作。 */
        const check = confirm("确认退出账号？");
        if (!check) return;
        localStorage.removeItem(LocalStorage_DataName);
        usrInfo = null;
        alert('账户已退出。');
        refreshLoginButtons();
    }

    doms.logouts.forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains(classNameForHide)) return;
            clearLocalUsrInfo();
        });
    });
});
