import { DISABLE_INTERACTION_global, LocalStorage_DataName } from "./data/vars.js";
import { encryptString } from "./tools/cryptoTools.js";

!async function () {
    const val = localStorage.getItem(LocalStorage_DataName);
    if (val) {
        window.location.replace('/');
        return;
    }

    const circle1 = document.querySelector('.circle1');
    const circle2 = document.querySelector('.circle2');
    const leftDecoration = document.querySelector('.left-decoration');

    const symmetryOffset = {
        x: 80,
        y: 60
    };

    function getLeftCenter() {
        const rect = leftDecoration.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2,
            relativeX: rect.width / 2,
            relativeY: rect.height / 2
        };
    }

    function initCirclePosition() {
        const center = getLeftCenter();
        circle1.style.left = `${center.relativeX - symmetryOffset.x - circle1.offsetWidth / 2}px`;
        circle1.style.top = `${center.relativeY - symmetryOffset.y - circle1.offsetHeight / 2}px`;
        circle2.style.left = `${center.relativeX + symmetryOffset.x - circle2.offsetWidth / 2}px`;
        circle2.style.top = `${center.relativeY + symmetryOffset.y - circle2.offsetHeight / 2}px`;
    }

    function updateCircleByMouse(e) {
        const center = getLeftCenter();
        const mouseOffsetRatio = {
            x: (e.clientX - center.x) / center.relativeX * 0.5,
            y: (e.clientY - center.y) / center.relativeY * 0.5
        };
        const circle1FinalX = center.relativeX - symmetryOffset.x - circle1.offsetWidth / 2 + mouseOffsetRatio.x * 100;
        const circle1FinalY = center.relativeY - symmetryOffset.y - circle1.offsetHeight / 2 + mouseOffsetRatio.y * 100;
        const circle2FinalX = center.relativeX + symmetryOffset.x - circle2.offsetWidth / 2 - mouseOffsetRatio.x * 100;
        const circle2FinalY = center.relativeY + symmetryOffset.y - circle2.offsetHeight / 2 - mouseOffsetRatio.y * 100;
        circle1.style.left = `${circle1FinalX}px`;
        circle1.style.top = `${circle1FinalY}px`;
        circle2.style.left = `${circle2FinalX}px`;
        circle2.style.top = `${circle2FinalY}px`;
        const distanceFromCenter = Math.sqrt(
            Math.pow(e.clientX - center.x, 2) + Math.pow(e.clientY - center.y, 2)
        );
        const scaleRatio = 1 + (200 - distanceFromCenter) / 200 * 0.3;
        circle1.style.transform = `scale(${scaleRatio})`;
        circle2.style.transform = `scale(${scaleRatio})`;
    }
    initCirclePosition();
    window.addEventListener('resize', initCirclePosition);
    document.addEventListener('mousemove', updateCircleByMouse);

    await F();
}();

async function F() {
    const doms = {
        form: document.querySelector('#form-login'),
        ipt_usrName: document.querySelector('#username'),
        ipt_usrPwd: document.querySelector('#password'),
        login_btn: document.getElementById('submit-btn'),
        register_btn: document.getElementById('register-btn'),
    }
    let DISABLE_INTERACTION = DISABLE_INTERACTION_global;
    async function check_connection() {
        try {
            const response = await fetch('/api/check_conn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain'
                },
                body: 'hello'
            });
            const result = await response.json();
            if (result.success) {
                return true;
            }
            return false;
        } catch (error) {
            return false;
        }
    }
    if (!DISABLE_INTERACTION) {
        const res = await check_connection();
        if (res) {
            console.log("服务器连接成功");
        } else {
            alert("请使用 python app.py 开启服务器。");
            console.warn("Warning: 服务器连接失败");
            DISABLE_INTERACTION = true;
        }
    }

    let toastTimer = null;
    let currentToast = null;
    function clearToast() {
        if (toastTimer) {
            clearTimeout(toastTimer);
            toastTimer = null;
        }
        if (currentToast) {
            currentToast.remove();
            currentToast = null;
        }
    }
    function showTopToast(message, time = 3) {
        /* The unit of 'time' is second */
        clearToast();
        const toast = document.createElement('div');
        toast.className = 'top-toast';
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => { toast.classList.add('active'); }, 10);
        currentToast = toast;
        toastTimer = setTimeout(() => {
            toast.classList.remove('active');
            setTimeout(() => {
                if (currentToast) {
                    currentToast.remove();
                    currentToast = null;
                }
                toastTimer = null;
            }, 300);
        }, +time * 1000);
    }

    function regTest(reg, str) {
        return reg.test(str);
    }

    function shake(dom) {
        if (dom.classList.contains('shake')) return;
        dom.classList.add('shake');
        setTimeout(() => {
            dom.classList.remove('shake');
        }, 1100);
    }

    const Lock = {
        locked: false,
        unlock() {
            this.locked = false;
        },
        lock() {
            this.locked = true;
        },
        isLocked() {
            return this.locked;
        }
    };

    function handleInfoSubmit() {
        clearToast();
        const formData = new FormData(doms.form);
        const data = Object.fromEntries(formData.entries());
        const { usrName, usrPwd } = data;
        if (!usrName || !usrPwd) {
            if (!usrName) shake(doms.ipt_usrName);
            if (!usrPwd) shake(doms.ipt_usrPwd);
            showTopToast("用户名或密码不可为空");
            return { success: false };
        }
        if (!regTest(/^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,10}$/, usrName)) {
            shake(doms.ipt_usrName);
            showTopToast("用户名只能为至多10位的中文、英文、数字、下划线、减号", 5);
            return { success: false };
        }
        if (!regTest(/^[a-zA-Z0-9_]{6,18}$/, usrPwd)) {
            shake(doms.ipt_usrPwd);
            showTopToast("密码需要6-18位的英文、数字、下划线", 5);
            return { success: false };
        }
        if (DISABLE_INTERACTION) {
            showTopToast('当前环境仅展示页面，无法提交数据。');
            return { success: false };
        }
        return {
            success: true,
            data,
        }
    }

    async function encodeStrings(data) {
        try {
            const resp = await fetch('/api/get_secret_key');
            const { key, iv } = await resp.json();
            const { usrName, usrPwd } = data;

            const s_uname = encryptString(usrName, key, iv);
            const s_upwd = encryptString(usrPwd, key, iv);
            return { s_uname, s_upwd, key, iv }
        } catch (err) {
            clearToast();
            showTopToast("FATAL: EncodeStrings Error! Fail to get the encode key!", 8);
            console.error(err);
            doms.form.reset();
            return null;
        }
    }

    doms.login_btn.addEventListener('click', async e => {
        e.preventDefault();

        if (Lock.isLocked()) {
            clearToast();
            showTopToast('请求处理中，请稍候...');
            return;
        }
        Lock.lock();

        const resp = handleInfoSubmit();
        if (!resp.success) {
            Lock.unlock();
            return;
        };

        const { data } = resp;
        const secret_data = await encodeStrings(data);

        if (!secret_data) {
            Lock.unlock();
            return;
        }

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(secret_data),
            });
            const result = await response.json();
            if (result.success) {
                localStorage.setItem(LocalStorage_DataName, result.token);
                alert(result.message);
                window.location.replace('./index.html');
            } else {
                clearToast();
                showTopToast(result.message, 5);
                shake(doms.ipt_usrName);
                shake(doms.ipt_usrPwd);
            }
        } catch (error) {
            clearToast();
            showTopToast('Error in: /api/login');
            console.error('Error in: /api/login');
        } finally {
            Lock.unlock();
        }
    });

    doms.register_btn.addEventListener('click', async e => {
        e.preventDefault();

        if (Lock.isLocked()) {
            clearToast();
            showTopToast('请求处理中，请稍候...');
            return;
        }
        Lock.lock();

        const resp = handleInfoSubmit();
        if (!resp.success) {
            Lock.unlock();
            return;
        };
        const { data } = resp;
        const secret_data = await encodeStrings(data);

        if (!secret_data) {
            Lock.unlock();
            return;
        }

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(secret_data),
            });
            const result = await response.json();
            clearToast();
            showTopToast(result.message, 5);
            if (result.success) {
                doms.form.reset();
            } else {
                shake(doms.ipt_usrName);
                shake(doms.ipt_usrPwd);
            }
        } catch (error) {
            clearToast();
            showTopToast('Error in: /api/register');
            console.error('Error in: /api/register');
        } finally {
            Lock.unlock();
        }
    });
};