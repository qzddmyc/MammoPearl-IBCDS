document.addEventListener('DOMContentLoaded', function () {
    const qa_container = document.querySelector('.qa-container');
    qa_container.innerHTML = '';

    let html = '';
    qas.forEach(qa => {
        html = html + `
            <div class="qa-item question-item">
                <div class="question">
                    <div class="message-content">
                        <h3>${qa.q_title}</h3>
                        <p>${qa.q_content}</p>
                    </div>
                </div>
                <div class="avatar q-avatar">Q</div>
            </div>

            <div class="qa-item answer-item">
                <div class="avatar a-avatar">A</div>
                <div class="answer">
                    <div class="message-content">
                        <p>${qa.a_content}</p>
                    </div>
                </div>
            </div>
        `;
    });

    qa_container.innerHTML = html;
});


// 滚动触发动画效果
document.addEventListener('DOMContentLoaded', function () {
    // 获取所有问答项并转换为数组
    const qaItems = Array.from(document.querySelectorAll('.qa-item'));
    const observerOptions = {
        root: null,
        rootMargin: '0px 0px 100px 0px', // 底部额外100px触发区域
        threshold: 0.1
    };

    // 使用IntersectionObserver监测元素可见性
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.classList.contains('visible')) {
                // 为每个可见元素添加延迟，创建顺序动画
                const index = qaItems.indexOf(entry.target);
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 50);

                // 只观察一次
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // 观察所有问答项
    qaItems.forEach(item => {
        observer.observe(item);
    });
});

// container随着header的缩小而缩小
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