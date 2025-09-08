// 不再使用，替换为buttons.js组件直接绑定事件

document.addEventListener('DOMContentLoaded', function () {
    const doms = {
        loading: document.querySelector('.loading'),
        btnToDetect: document.querySelector('.button-to-detect'),
    }

    doms.btnToDetect.addEventListener('click', function () {
        doms.loading.classList.add('show');
        setTimeout(function () {
            const a = document.createElement('a');
            a.href = './detect.html';
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.remove(a);
        }, 1100);
    });
});