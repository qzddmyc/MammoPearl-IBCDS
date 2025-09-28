// 需要在 scrollbar.js 之后引入

document.addEventListener('DOMContentLoaded', async function () {
    const qaContainer = document.querySelector('.qa-container');
    const aiQaContainer = document.querySelector('.ai-qa-container');
    const aiBtn = document.querySelectorAll('.qa-ai');
    const normalBtn = document.querySelectorAll('.qa-normal');
    const addConversationBtn = document.querySelector('.add-conversation-btn');
    const questionInputContainer = document.querySelector('.question-input-container');
    const cancelBtn = document.querySelector('.cancel-btn');
    const pageTitle = document.querySelector('.page-title h1');
    const textarea = document.querySelector('.question-input');

    const initialPageTitle = pageTitle.innerHTML;
    let observer = null;    // normal-observer
    let observerAI = null;

    // 初始化AI问答内容
    async function initAIQAs() {
        let ai_qas = [];
        try {
            const response = await fetch('api/get_full_json');
            const result = await response.json();
            if (!result.success) {
                alert("获取初始问答列表失败: " + result.data);
            } else {
                ai_qas = result.data;
            }
        } catch (error) {
            alert("获取初始问答列表失败: " + error);
        }

        ai_qas = Array.from(ai_qas).filter(each => each.flag === Flags.finish);

        let html = '';
        if (ai_qas.length === 0) {
            html += '<h3>暂无内容，请点击“添加对话”进行添加</h3>';
        }
        ai_qas.forEach(qa => {
            html += `
                <div class="ai-qa-item question-item">
                    <div class="ai-question">
                        <div class="message-content">
                            <p>${qa.ask}</p>
                        </div>
                    </div>
                    <div class="ai-avatar ai-q-avatar">You</div>
                </div>

                <div class="ai-qa-item answer-item">
                    <div class="ai-avatar ai-a-avatar">AI</div>
                    <div class="ai-answer">
                        <div class="message-content">
                            <p>${qa.reply}</p>
                        </div>
                    </div>
                </div>
            `;
        });

        // 将生成的内容添加到AI问答容器（添加按钮下方）
        if (addConversationBtn) {
            addConversationBtn.insertAdjacentHTML('afterend', html);
        } else {
            aiQaContainer.innerHTML = html;
        }

        // 为AI问答项添加滚动动画
        initAIQaAnimation();
    }

    // 初始化AI问答项的滚动动画（保持原逻辑）
    function initAIQaAnimation() {
        const aiQaItems = Array.from(document.querySelectorAll('.ai-qa-item'));
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px 100px 0px',
            threshold: 0.1
        };

        if (observerAI) {
            observerAI.disconnect();
            observerAI = null;
        }

        observerAI = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !entry.target.classList.contains('visible')) {
                    const index = aiQaItems.indexOf(entry.target);
                    setTimeout(() => {
                        entry.target.classList.add('visible');
                    }, index * 50);
                    observerAI.unobserve(entry.target);
                }
            });
        }, observerOptions);

        aiQaItems.forEach(item => {
            observerAI.observe(item);
        });
    }

    function initNormalQaAnimation() {
        // 获取所有问答项并转换为数组
        const qaItems = Array.from(document.querySelectorAll('.qa-item'));
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px 100px 0px', // 底部额外100px触发区域
            threshold: 0.1
        };

        if (observer) {
            observer.disconnect();
            observer = null;
        }

        // 使用IntersectionObserver监测元素可见性
        observer = new IntersectionObserver((entries) => {
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
    }


    // 切换到AI问答：隐藏普通问答，显示AI问答
    function switchToAIQA() {
        qaContainer.classList.add('hide'); // 隐藏普通问答
        aiQaContainer.classList.remove('hide'); // 显示AI问答

        aiBtn.forEach(e => e.classList.add('hide')); // 隐藏"AI问答"按钮
        normalBtn.forEach(e => e.classList.remove('hide')); // 显示"普通问答"按钮
        pageTitle.innerHTML = 'AI 解答';

        document.querySelectorAll('.ai-qa-item').forEach(item => {
            item.classList.remove('visible');
        });

        initAIQaAnimation();
        if (window.updateScrollIndicator) window.updateScrollIndicator();
        else updateScrollIndicator();
    }

    // 切换到普通问答：隐藏AI问答，显示普通问答
    function switchToNormalQA() {
        aiQaContainer.classList.add('hide'); // 隐藏AI问答
        qaContainer.classList.remove('hide'); // 显示普通问答

        normalBtn.forEach(e => e.classList.add('hide')); // 隐藏"普通问答"按钮
        aiBtn.forEach(e => e.classList.remove('hide')); // 显示"AI问答"按钮
        pageTitle.innerHTML = initialPageTitle;

        questionInputContainer.classList.add('hide'); // 切换时隐藏问题输入框

        document.querySelectorAll('.qa-item').forEach(item => {
            item.classList.remove('visible');
        });
        initNormalQaAnimation();

        if (window.updateScrollIndicator) window.updateScrollIndicator();
        else updateScrollIndicator();
    }

    // 显示问题输入区域：移除hide类
    function showQuestionInput() {
        questionInputContainer.classList.remove('hide');
    }

    // 隐藏问题输入区域：添加hide类并清空内容
    function hideQuestionInput() {
        questionInputContainer.classList.add('hide');
        const questionInput = document.querySelector('.question-input');
        if (questionInput) questionInput.value = '';
    }

    // 绑定事件监听
    if (aiBtn) aiBtn.forEach(e => e.addEventListener('click', switchToAIQA));
    if (normalBtn) normalBtn.forEach(e => e.addEventListener('click', switchToNormalQA));
    if (addConversationBtn) addConversationBtn.addEventListener('click', showQuestionInput);
    if (cancelBtn) cancelBtn.addEventListener('click', hideQuestionInput);

    document.getElementById('ai-confirm-btn').addEventListener('click', async function (e) {
        e.preventDefault();
        const usrInput = textarea.value;
        async function sendUsrIptToAI(msg) {
            try {
                const response = await fetch('api/send_msg_to_ai', {
                    method: 'POST',
                    body: msg,
                    headers: {
                        'Content-Type': 'text/plain'
                    }
                });
                const result = await response.json();
                return {
                    success: result.success,
                    data: result.data,
                }

            } catch (error) {
                return {
                    success: false,
                    data: error
                };
            }
        }
        const reply = await sendUsrIptToAI(usrInput);
        if (reply.success) {
            textarea.value = '';
        }
        console.log(reply);
        console.log(reply.success, reply.data);
    })

    await initAIQAs();
    initNormalQaAnimation();
});