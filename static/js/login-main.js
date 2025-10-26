document.addEventListener('DOMContentLoaded', function () {
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
});

document.addEventListener('DOMContentLoaded', async function () {
    const doms = {
        form: document.querySelector('#form-login'),
        ipt_usrName: document.querySelector('#username'),
        ipt_usrPwd: document.querySelector('#password'),
    }
    let DISABLE_INTERACTION = DISABLE_INTERACTION_global;
    async function check_connection() {
        try {
            const response = await fetch('api/check_conn', {
                method: 'POST',
                body: 'hello',
                headers: {
                    'Content-Type': 'text/plain'
                }
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

    doms.form.addEventListener('submit', async e => {
        e.preventDefault();
        clearToast();
        const usrName = e.target.elements.usrName.value;
        const usrPwd = e.target.elements.usrPwd.value;
        if (!usrName || !usrPwd) {
            if (!usrName) shake(doms.ipt_usrName);
            if (!usrPwd) shake(doms.ipt_usrPwd);
            showTopToast("用户名或密码不可为空");
            return;
        }
        if (!regTest(/^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,10}$/, usrName)) {
            shake(doms.ipt_usrName);
            showTopToast("用户名只能为至多10位的中文、英文、数字、下划线、减号", 5);
            return;
        }
        if (!regTest(/^[a-zA-Z0-9_]{6,18}$/, usrPwd)) {
            shake(doms.ipt_usrPwd);
            showTopToast("密码需要6-18位的英文、数字、下划线", 5);
            return;
        }
        if (DISABLE_INTERACTION) {
            showTopToast('当前环境仅展示页面，无法提交数据。');
            return;
        }
        const formData = new FormData(e.target);
        try {
            const response = await fetch('api/login', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.success) {
                localStorage.setItem(LocalStorage_DataName, usrName);
                alert(result.message);
                window.location.replace('./index.html');
            } else {
                showTopToast(result.message, 5);
                shake(doms.ipt_usrName);
                shake(doms.ipt_usrPwd);
            }
        } catch (error) {
            showTopToast('Error in: api/login');
            console.error('Error in: api/login');
        }
    });
});