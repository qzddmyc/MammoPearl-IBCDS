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

    if (window.updateScrollIndicator) window.updateScrollIndicator();
    else updateScrollIndicator();
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