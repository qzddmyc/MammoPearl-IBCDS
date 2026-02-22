import { LocalStorage_DataName } from "./data/vars.js";
import { decodeTokenToUserName } from "./tools/decodeToken.js";
import { Log } from "./tools/log.js";

// 在header.js之后引入

!function () {
    const doms = {
        banner_btn: document.querySelector('.button-to-detect'),
        container: document.querySelector('.container'),
        header: document.querySelector('.main-header'),
        feature_card_container: document.querySelector('.features'),
        feature_card_h2: document.querySelector('.info-section h2'),
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

    // g(t) = 4(t - 0.5)², for t in (0.5, 1)
    function gt(t) {
        if (t <= 0.5) return 0;
        if (t >= 1) return 1;
        return 4 * Math.pow(t - 0.5, 2);
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
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 500) {
            const ratio = viewportWidth / 500 * 0.8;
            doms.banner_btn.style.transform = `scale(${ratio})`;
        } else {
            doms.banner_btn.style.transform = '';
        }

        if (viewportWidth < 560) {
            doms.container.style.marginTop = (doms.header.clientHeight + 48) * f_ex1(viewportWidth / 560) + 'px';
        } else {
            doms.container.style.marginTop = '';
        }

        if (viewportWidth < 615) {
            let Z = 0;
            if (viewportWidth >= 280) {
                Z = hx(viewportWidth / 615);
                doms.feature_card_container.style.zoom = Z;
                doms.container.style.minHeight = '';
            } else {
                Z = viewportWidth / 480;
                doms.feature_card_container.style.zoom = Z;
                doms.container.style.minHeight = 'auto';
            }
            doms.container.style.marginBottom = 35 * gt(Z) + 15 + 'px';
        } else {
            doms.feature_card_container.style.zoom = '';
            doms.container.style.minHeight = '';
            doms.container.style.marginBottom = '';
        }

        if (viewportWidth <= 768) {
            doms.feature_card_h2.style.fontSize = f_ex1(0.0416 * viewportWidth / 32) * 32 + 'px';
            doms.feature_card_h2.style.zoom = 1.2;
        } else {
            doms.feature_card_h2.style.fontSize = '';
            doms.feature_card_h2.style.zoom = '';
        }

        if (viewportWidth <= 768 && viewportWidth > 425) {
            doms.feature_card_p_oneline.style.fontSize = f_ex1(0.0208 * viewportWidth / 16) * 16 + 'px';
            doms.feature_card_p_oneline.style.zoom = 1.2;
        } else {
            doms.feature_card_p_oneline.style.fontSize = '';
            doms.feature_card_p_oneline.style.zoom = '';
        }

        if (viewportWidth <= 425) {
            // Uses .disappear in header.css: display: none !important
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

        if (viewportWidth <= 480) {
            const ratio = viewportWidth / 480;
            doms.footer_content.style.zoom = ratio;
            doms.footer_container.style.paddingTop = ratio * 50 + 'px';
            doms.footer_container.style.paddingBottom = ratio * 50 + 'px';
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
}();

!async function () {
    const doms = {
        logins: document.querySelectorAll('.login-door'),
        logouts: document.querySelectorAll('.logout-door'),
    };

    const infoGotFromLocalStorage = localStorage.getItem(LocalStorage_DataName);
    let usrInfo = await decodeTokenToUserName(infoGotFromLocalStorage);
    if (infoGotFromLocalStorage && !usrInfo) {
        localStorage.removeItem(LocalStorage_DataName);
        Log.warning("User modified token which lead to a logout.")
        const r = confirm("检测到你的登录信息有误，是否重新登录？");
        if (r) window.location.href = "/login.html";
    }

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
            item.title = `当前用户：${usrInfo}`;
        });
    }
    function refreshLoginButtons() {
        if (usrInfo) { showLogout_hideLogin(); }
        else { showLogin_hideLogout(); }
    }
    refreshLoginButtons();
    function clearLocalUsrInfo() {
        const check = confirm("确认退出账号？");
        if (!check) return;
        localStorage.removeItem(LocalStorage_DataName);
        Log.info("User logged out manually.");
        usrInfo = null;
        console.log("用户账号已退出。");    // No more use alert, use log instead.
        refreshLoginButtons();
    }

    doms.logouts.forEach(item => {
        item.addEventListener('click', () => {
            if (item.classList.contains(classNameForHide)) return;
            clearLocalUsrInfo();
        });
    });
}();
