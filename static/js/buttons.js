// 为button元素或是添加了i-should-be-a-button类的元素实现自动跳转
// 该元素必须包含data-action自定义属性，否则不生效
// 生效时，将cursor设置为pointer

// data-action: page-skip, 页面跳转。跳转至data-msg所指向的页面，无此属性不生效。
// data-action: scroll-to-top, 滚动至页面顶部

document.addEventListener('DOMContentLoaded', function () {
    const btns = document.querySelectorAll('button, .i-should-be-a-button');
    btns.forEach(btn => {
        if (!btn.dataset.action) {
            return;
        }

        btn.style.cursor = 'pointer';

        if (btn.dataset.action === 'page-skip') {
            if (!btn.dataset.msg) return;
            btn.addEventListener('click', () => {
                const url = btn.dataset.msg;
                const a = document.createElement('a');
                a.href = url;
                a.style.display = 'none';
                document.body.appendChild(a);
                a.click();
                document.body.remove(a);
            });

        } else if (btn.dataset.action === 'form-submit') {
            return;
        } else if (btn.dataset.action === 'scroll-to-top') {
            btn.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        } else {
            return;
        }
    });
});